import io
import wave
import numpy as np
import aiohttp
from loguru import logger
from .asr_interface import ASRInterface


class VoiceRecognition(ASRInterface):
    def __init__(self, api_key: str, api_url: str, model: str):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def transcribe_np(self, audio: np.ndarray) -> str:
        import requests

        wav_bytes = self._nparray_to_wav_bytes(audio, self.SAMPLE_RATE)
        files = {"file": ("audio.wav", wav_bytes, "audio/wav")}
        data = {"model": self.model}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(self.api_url, files=files, data=data, headers=headers)
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception as e:
            logger.error(f"SiliconFlow ASR error: {e}")
            return ""

    async def async_transcribe_np(self, audio: np.ndarray) -> str:
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        wav_bytes = self._nparray_to_wav_bytes(audio, self.SAMPLE_RATE)
        headers = {"Authorization": f"Bearer {self.api_key}"}

        form_data = aiohttp.FormData()
        form_data.add_field("file", wav_bytes, filename="audio.wav", content_type="audio/wav")
        form_data.add_field("model", self.model)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=form_data, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result.get("text", "")
        except Exception as e:
            logger.error(f"SiliconFlow ASR error: {e}")
            return ""

    def _nparray_to_wav_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        audio = np.clip(audio, -1, 1)
        audio_int16 = (audio * 32767).astype(np.int16)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())
        return buffer.getvalue()
