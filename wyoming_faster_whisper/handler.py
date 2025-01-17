"""Event handler for clients of the server."""
import argparse
import asyncio
import logging
import os
import tempfile
import wave
from typing import Optional, Any

from mlx_whisper import transcribe
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

_LOGGER = logging.getLogger(__name__)


class FasterWhisperEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model_path: str,
        model_lock: asyncio.Lock,
        *args,
        initial_prompt: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model_path = model_path  # Store the model path
        self.model_lock = model_lock
        self._language = self.cli_args.language
        self._wav_dir = tempfile.TemporaryDirectory()
        self._wav_path = os.path.join(self._wav_dir.name, "speech.wav")
        self._wav_file: Optional[wave.Wave_write] = None

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)

            if self._wav_file is None:
                self._wav_file = wave.open(self._wav_path, "wb")
                self._wav_file.setframerate(chunk.rate)
                self._wav_file.setsampwidth(chunk.width)
                self._wav_file.setnchannels(chunk.channels)

            self._wav_file.writeframes(chunk.audio)
            return True

        if AudioStop.is_type(event.type):

            assert self._wav_file is not None

            self._wav_file.close()
            self._wav_file = None
            decode_options=dict(language="it")

            async with self.model_lock:
                # Let transcribe() handle model loading via path_or_hf_repo
                result = transcribe(
                    audio=self._wav_path,
                    path_or_hf_repo=self.model_path,  # Pass the model path instead of model
                    condition_on_previous_text=True,
                    temperature=0.0,
                    verbose=False,
                    **decode_options,
                )

            text = result["text"].strip()
            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            return False

        if Transcribe.is_type(event.type):
            transcribe_ev = Transcribe.from_event(event)
            if transcribe_ev.language:
                self._language = transcribe_ev.language
                _LOGGER.debug("Language set to %s", transcribe_ev.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
