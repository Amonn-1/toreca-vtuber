"""SiliconFlow cloud TTS client."""

import requests
from loguru import logger

from .tts_interface import TTSInterface


class SiliconFlowTTS(TTSInterface):
    """Generate speech through the SiliconFlow audio speech API."""

    def __init__(
        self,
        api_url,
        api_key,
        default_model,
        default_voice,
        sample_rate,
        response_format,
        stream,
        speed,
        gain,
    ):
        """Initialize the SiliconFlow TTS client.

        Args:
            api_url: Speech endpoint URL.
            api_key: SiliconFlow API key.
            default_model: Cloud TTS model name.
            default_voice: Voice id accepted by the selected model.
            sample_rate: Optional output sample rate. Omit for models that
                do not accept this field.
            response_format: Audio container such as mp3 or wav.
            stream: Optional streaming flag. Keep false when saving a file.
            speed: Optional speaking-rate multiplier.
            gain: Optional audio gain.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.default_model = default_model
        self.default_voice = default_voice
        self.sample_rate = sample_rate
        self.response_format = response_format
        self.stream = stream
        self.speed = speed
        self.gain = gain

    def generate_audio(self, text: str, file_name_no_ext=None) -> str:
        """Synthesize speech and write it to a cache file.

        Args:
            text: Text to synthesize.
            file_name_no_ext: Optional cache file name without extension.

        Returns:
            Path to the generated audio file, or an empty string on failure.
        """
        cache_file = self.generate_cache_file_name(
            file_name_no_ext, file_extension=self.response_format
        )
        payload = {
            "input": text,
            "response_format": self.response_format,
            "model": self.default_model,
            "voice": self.default_voice,
        }
        if self.sample_rate is not None:
            payload["sample_rate"] = self.sample_rate
        if self.stream:
            payload["stream"] = self.stream
        if self.speed is not None:
            payload["speed"] = self.speed
        if self.gain is not None:
            payload["gain"] = self.gain

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            if self.api_url is None:
                logger.error(
                    "API URL 未正确配置，请检查配置文件。The configuration is incorrect. Please check the configuration file."
                )
                return ""
            response = requests.post(
                self.api_url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()
            with open(cache_file, "wb") as f:
                f.write(response.content)
            logger.info(f"Successfully generated the audio file: {cache_file}")
            return cache_file
        except requests.RequestException as e:
            error_body = ""
            if getattr(e, "response", None) is not None:
                error_body = e.response.text
            logger.error(f"Failed to generate the audio file: {e} {error_body}")
            return ""
