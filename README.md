# toreca-vtuber 使用手册

本手册基于本项目实际部署环境编写，涵盖从拉取代码到启动运行的完整流程，以及 GPT-SoVITS 本地语音合成的配置。

---

## 一、环境要求

| 组件 | 版本 / 说明 |
|---|---|
| Python | 3.10 ~ 3.12（本项目 `.python-version` 为 3.12） |
| 包管理 | 推荐 `uv`，也可用 `pip` |
| 操作系统 | Windows / Linux / macOS |
| Git | 任意较新版本 |
| FFmpeg | 系统需可用（音频处理） |

---

## 二、部署 Open-LLM-VTuber

### 1. 克隆仓库

```bash
git clone https://github.com/Amonn-1/toreca-vtuber.git
cd toreca-vtuber
```

### 2. 安装依赖

使用 uv（推荐）：

```bash
uv sync
```

或使用 pip：

```bash
pip install -r requirements.txt
```

### 3. 准备配置文件

项目根目录的 `conf.yaml` 是主配置（该文件被 `.gitignore` 忽略，不会提交）。
若没有，从模板复制：

```bash
cp conf.yaml.template conf.yaml   # 如存在模板
```

然后按下面"配置说明"修改。

### 4. 启动后端

```bash
python main.py
```

服务默认监听 `0.0.0.0:12393`（见 `conf.yaml` 的 `system_config`）。

### 5. 启动前端

前端为独立子模块（`frontend/`）。开发模式：

```bash
cd frontend
npm install
npm run dev
```

或直接使用已构建的静态资源，由后端提供。

浏览器访问前端地址即可开始对话。

---

## 三、conf.yaml 配置说明

### system_config

```yaml
system_config:
  host: 0.0.0.0      # 监听地址，0.0.0.0 表示允许局域网访问
  port: 12393        # 后端端口
```

### character_config（角色）

```yaml
character_config:
  character_name: 艾丝妲        # 角色名
  human_name: 開拓者            # 对用户的称呼
  persona_prompt: |
    ...                        # 角色人设提示词（日文）
```

- `persona_prompt` 决定 LLM 扮演的角色与说话风格。
- 本项目强制角色只用日语回复（提示词开头有【最重要規則】段落）。

### agent_config（LLM）

```yaml
agent_config:
  conversation_agent_choice: basic_memory_agent
  agent_settings:
    basic_memory_agent:
      llm_provider: deepseek_llm
  llm_configs:
    deepseek_llm:
      llm_api_key: <你的 DeepSeek Key>
      model: deepseek-chat
      temperature: 0.7
```

### asr_config（语音识别）

本项目使用 SiliconFlow ASR：

```yaml
asr_config:
  asr_model: siliconflow_asr
  siliconflow_asr:
    api_key: <你的 SiliconFlow Key>
    api_url: https://api.siliconflow.cn/v1/audio/transcriptions
    model: FunAudioLLM/SenseVoiceSmall
```

- 自动识别中 / 日 / 英。

### tts_config（语音合成）

本项目使用本地 GPT-SoVITS：

```yaml
tts_config:
  tts_model: gpt_sovits_tts
  gpt_sovits_tts:
    api_url: http://127.0.0.1:9880/tts
    text_lang: ja                       # 输入文本语言（不是参考音频语言）
    ref_audio_path: D:/GPT-SoVITS/custom_models/v2ProPlus/aista/ref_audio/happy.wav
    prompt_lang: ja
    prompt_text: ふふ、私の部下たちは優秀でしょう？   # 必须与参考音频内容一致
    text_split_method: cut5
    batch_size: '1'
    media_type: wav
    streaming_mode: 'false'
```

**关键坑：**
- `ref_audio_path` 不能含中文，需复制到纯英文路径。
- `prompt_text` 必须和参考音频实际说的内容一致，否则音色偏。
- `text_lang` 指输入文本语言，当前为 `ja`。

---

## 四、GPT-SoVITS 本地 TTS 部署

### 1. 安装位置

`D:\GPT-SoVITS`，版本 v2 Pro Plus，CPU 模式。

### 2. 模型配置

编辑 `D:\GPT-SoVITS\GPT_SoVITS\configs\tts_infer.yaml`，**只改 `custom` 段**（代码只读 `custom` 键）：

```yaml
custom:
  bert_base_path: GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
  cnhuhbert_base_path: GPT_SoVITS/pretrained_models/chinese-hubert-base
  device: cpu
  is_half: false
  t2s_weights_path: "custom_models/v2ProPlus/艾丝妲/艾丝妲-e10.ckpt"
  version: v2ProPlus
  vits_weights_path: "custom_models/v2ProPlus/艾丝妲/艾丝_e10_s150.pth"
```

### 3. 启动 API

```bash
cd /d/GPT-SoVITS
PYTHONUTF8=1 .venv/Scripts/python.exe api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
```

- `PYTHONUTF8=1` 必须设置，否则中文路径报 cp932 编码错误。
- 启动后 API 地址：`http://127.0.0.1:9880/tts`。
- 改完 yaml 必须重启才生效。

### 4. 切换声音模型步骤

1. 把 `.ckpt` + `.pth` 放到 `custom_models/v2ProPlus/模型名/`
2. 参考音频复制到纯英文路径，如 `custom_models/v2ProPlus/aista/ref_audio/happy.wav`
3. 改 `tts_infer.yaml` 的 `custom` 段两个权重路径
4. 改 `conf.yaml` 的 `character_name`、`persona_prompt`、`ref_audio_path`、`prompt_text`
5. 重启 GPT-SoVITS API

### 5. 已打的关键补丁（GPT-SoVITS 侧）

1. `torchaudio/__init__.py`：`load()` / `save()` 改为用 soundfile（绕过 torchcodec 的 FFmpeg 依赖）
2. `fast_langdetect`：把 `lid.176.ftz` 从 `.venv/.../fast_langdetect/resources/` 复制到 `GPT_SoVITS/pretrained_models/fast_langdetect/`
3. venv 需安装 `onnxruntime`（G2PW 中文多音字模型需要）
4. `G2PWModel` 目录若嵌套两层（`G2PWModel/G2PWModel/`），把内容上移一层

---

## 五、Git 工作流（toreca-vtuber）

本仓库历史已重写为干净的个人历史：

```
<你的修改提交>
chore: import Open-LLM-VTuber upstream base (v1.x)
```

- `origin` = 你自己的仓库 `https://github.com/Amonn-1/toreca-vtuber.git`（日常提交推送走这里）
- `upstream` = 原开源项目（仅用于参考，历史已不相关，合并会冲突）

日常操作：

```bash
git add <文件>
git commit -m "..."
git push origin main
```

---

## 六、常见问题排查

| 现象 | 原因 / 解决 |
|---|---|
| TTS 报 400 / 无声音 | GPT-SoVITS API 未启动；或缺 onnxruntime / G2PWModel 目录嵌套 |
| 中文路径报错 cp932 | 启动 GPT-SoVITS 时未设 `PYTHONUTF8=1` |
| 日语被念成中文 | `conf.yaml` 的 `text_lang` 设错，应为 `ja` |
| LLM 用中文回复 | persona_prompt 的日语强制规则不够强，补【最重要規則】段 |
| 端口 9880 / 12393 被占用 | 用 `powershell Stop-Process -Id <PID> -Force` 释放 |
| 本地 LLM 503 | 已内置修复：localhost 连接自动设 `NO_PROXY` |
| WebSocket 断连崩溃 | 已内置修复：统一走 `safe_websocket_send` |

---

## 七、启动顺序总结

1. 启动 GPT-SoVITS API（端口 9880）
2. 启动 Open-LLM-VTuber 后端（`python main.py`，端口 12393）
3. 启动 / 打开前端
4. 浏览器访问前端地址开始对话
