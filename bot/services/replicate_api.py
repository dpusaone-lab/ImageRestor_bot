import asyncio
import io
import logging
import time
import urllib.request
from urllib.parse import urlparse

import replicate

logger = logging.getLogger(__name__)

_MODEL = "google/nano-banana-pro"
_ALLOWED_DOMAINS = {"replicate.delivery", "pbxt.replicate.delivery"}


class ReplicateUpscaleError(Exception):
    pass


class ReplicateService:
    def __init__(self, api_token: str, prompt: str) -> None:
        self._client = replicate.Client(api_token=api_token)
        self._prompt = prompt

    async def process(self, image_bytes: bytes) -> bytes:
        """Run Flux Kontext Pro image editing. Returns result bytes. Raises ReplicateUpscaleError after 3 retries."""
        return await asyncio.to_thread(self._process_sync, image_bytes)

    def _process_sync(self, image_bytes: bytes) -> bytes:
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                logger.debug("Sending to Replicate. prompt: %s", self._prompt[:80])
                output = self._client.run(
                    _MODEL,
                    input={
                        "prompt": self._prompt,
                        "image_input": [io.BytesIO(image_bytes)],
                        "resolution": "4K",
                        "aspect_ratio": "match_input_image",
                        "output_format": "jpg",
                        "safety_filter_level": "block_only_high",
                    },
                )
                url = self._extract_url(output)
                self._validate_url(url)
                logger.info("Process done successfully")
                with urllib.request.urlopen(url) as resp:
                    return resp.read()
            except ReplicateUpscaleError:
                raise
            except Exception as e:
                last_exc = e
                logger.warning("Process attempt %d/3 failed: %s", attempt + 1, e)
                if attempt < 2:
                    time.sleep(2)
        raise ReplicateUpscaleError("Processing failed after 3 attempts") from last_exc

    @staticmethod
    def _extract_url(output) -> str:
        item = output[0] if isinstance(output, list) else output
        return item.url if hasattr(item, "url") else str(item)

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in _ALLOWED_DOMAINS:
            raise ReplicateUpscaleError(f"Unexpected result URL: {url}")
