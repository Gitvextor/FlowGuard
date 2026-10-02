"""In-memory capture of the primary screen for Windows FlowGuard."""

import io

from PIL import Image


class ScreenshotCaptureError(RuntimeError):
    pass


class ScreenshotProvider:
    def __init__(self, jpeg_quality: int = 85) -> None:
        self.jpeg_quality = jpeg_quality

    def capture_primary_screen(self) -> bytes:
        """Return primary-monitor JPEG bytes; never write a screenshot to disk."""
        try:
            import mss

            with mss.mss() as capture:
                primary_monitor = capture.monitors[1]
                frame = capture.grab(primary_monitor)
                image = Image.frombytes("RGB", frame.size, frame.rgb)
                return self._to_jpeg(image)
        except Exception as mss_error:
            # A practical fallback for Windows sessions where MSS cannot attach.
            try:
                from PIL import ImageGrab

                return self._to_jpeg(ImageGrab.grab(all_screens=False))
            except Exception as grab_error:
                raise ScreenshotCaptureError(
                    f"Primary-screen capture failed (mss: {mss_error}; Pillow: {grab_error})."
                ) from grab_error

    def _to_jpeg(self, image: Image.Image) -> bytes:
        if image.mode != "RGB":
            image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=self.jpeg_quality, optimize=True)
        return buffer.getvalue()
