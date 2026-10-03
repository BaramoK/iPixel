"""Wrapper thread-safe autour de pypixelcolor.Client."""
from concurrent.futures import ThreadPoolExecutor
from pypixelcolor import Client, TextAnimation, ResizeMethod, scan_devices_sync
from pypixelcolor.lib.font_config import FontConfig


class LEDController:
    """Encapsule pypixelcolor.Client avec un executor pour éviter de bloquer le GUI."""

    def __init__(self, address: str | None = None):
        self.address = address
        self.client = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    # ------------------------------------------------------------------
    # Connexion
    # ------------------------------------------------------------------
    def connect(self):
        if not self.address:
            raise ValueError("Adresse MAC non définie.")
        self.client = Client(self.address)
        self.client.connect()
        return True

    def disconnect(self):
        if self.client:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

    def is_connected(self) -> bool:
        if self.client is None:
            return False
        async_client = getattr(self.client, "_async_client", None)
        if async_client is None:
            return False
        return getattr(async_client, "_connected", False)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------
    def send_image(self, path: str, resize_method=None, save_slot: int | None = None):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        kwargs = {}
        if resize_method is not None:
            kwargs["resize_method"] = resize_method
        if save_slot is not None and save_slot > 0:
            kwargs["save_slot"] = save_slot
        self.client.send_image(path, **kwargs)

    def send_text(
        self,
        text: str,
        animation=None,
        speed: int | None = None,
        color: str | None = None,
        bg_color: str | None = None,
        save_slot: int | None = None,
        font: str | FontConfig | None = None,
    ):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        kwargs = {}
        if animation is not None:
            kwargs["animation"] = animation
        if speed is not None:
            kwargs["speed"] = speed
        if color is not None:
            kwargs["color"] = color
        if bg_color is not None:
            kwargs["bg_color"] = bg_color
        if save_slot is not None and save_slot > 0:
            kwargs["save_slot"] = save_slot
        if font is not None:
            kwargs["font"] = font
        self.client.send_text(text, **kwargs)

    def send_image_hex(self, hex_string: str, file_extension: str, resize_method=None, save_slot: int | None = None):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        kwargs = {"hex_string": hex_string, "file_extension": file_extension}
        if resize_method is not None:
            kwargs["resize_method"] = resize_method
        if save_slot is not None and save_slot > 0:
            kwargs["save_slot"] = save_slot
        self.client.send_image_hex(**kwargs)

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def set_brightness(self, value: int):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.set_brightness(value)

    def set_power(self, on: bool):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.set_power(on)

    def set_orientation(self, value: int):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.set_orientation(value)

    def set_clock_mode(self, **kwargs):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.set_clock_mode(**kwargs)

    def set_time(self, **kwargs):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.set_time(**kwargs)

    # ------------------------------------------------------------------
    # Data / Slots
    # ------------------------------------------------------------------
    def show_slot(self, slot: int):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.show_slot(slot)

    def delete(self, slot: int):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.delete(slot)

    def clear(self):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.clear()

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------
    @staticmethod
    def scan_devices(timeout: float = 5.0):
        return scan_devices_sync(timeout=timeout)

    # ------------------------------------------------------------------
    # Threading helper
    # ------------------------------------------------------------------
    def submit(self, fn, *args, **kwargs):
        """Soumet une fonction à exécuter dans un thread worker."""
        return self._executor.submit(fn, *args, **kwargs)
