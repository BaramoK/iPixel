"""Wrapper thread-safe autour de pypixelcolor.Client."""
import logging
from concurrent.futures import ThreadPoolExecutor
from pypixelcolor import Client, TextAnimation, ResizeMethod, scan_devices_sync
from pypixelcolor.lib.font_config import FontConfig
from pypixelcolor.lib.transport.send_plan import single_window_plan

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sortie du mode horloge
# ---------------------------------------------------------------------------
# La librairie pypixelcolor n'expose aucune commande de changement de canal.
# En revanche, l'enregistrement d'un contenu dans un slot force le firmware à
# quitter le canal horloge et à revenir au canal personnalisé (image/texte).
# On utilise donc un slot dédié et réservé (100 par défaut) que l'on vide juste
# après ; les slots de contenu sont limités à 99 pour éviter toute collision.
EXIT_CLOCK_SLOT = 100
# Texte minimal écrit dans le slot de sortie : son unique rôle est de déclencher
# la sortie du canal horloge ; le slot est vidé immédiatement après.
EXIT_CLOCK_TEXT = " "


def _build_show_slot_raw(number: int, cmd_type: int = 0x01):
    """Construit manuellement le payload show_slot avec un type alternatif.

    Le package pypixelcolor envoie ``(8, 0x80)`` ce qui semble incohérent
    avec ``delete`` qui utilise ``(2, 1)``.  Cette fonction permet de tester
    ``(8, 1)`` en secours.
    """
    cmd = bytes([
        0x07,
        0x00,
        0x08,
        int(cmd_type) & 0xFF,
        0x01,
        0x00,
        int(number) & 0xFF,
    ])
    return single_window_plan("show_slot_raw", cmd)


class LEDController:
    """Encapsule pypixelcolor.Client avec un executor pour éviter de bloquer le GUI."""

    def __init__(self, address: str | None = None, exit_clock_slot: int = EXIT_CLOCK_SLOT):
        self.address = address
        self.client = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._clock_mode = False
        self._last_content_state = None
        self.exit_clock_slot = exit_clock_slot

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
        # Mémorise uniquement les contenus temporaires (non sauvegardés en slot)
        if save_slot is None or save_slot <= 0:
            self._last_content_state = {"type": "image", "path": path, "resize_method": resize_method}
            self._clock_mode = False

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
        if save_slot is None or save_slot <= 0:
            self._last_content_state = {
                "type": "text",
                "text": text,
                "animation": animation,
                "speed": speed,
                "color": color,
                "bg_color": bg_color,
                "font": font,
            }
            self._clock_mode = False

    def send_image_hex(self, hex_string: str, file_extension: str, resize_method=None, save_slot: int | None = None):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        kwargs = {"hex_string": hex_string, "file_extension": file_extension}
        if resize_method is not None:
            kwargs["resize_method"] = resize_method
        if save_slot is not None and save_slot > 0:
            kwargs["save_slot"] = save_slot
        self.client.send_image_hex(**kwargs)
        if save_slot is None or save_slot <= 0:
            self._last_content_state = {
                "type": "image_hex",
                "hex_string": hex_string,
                "file_extension": file_extension,
                "resize_method": resize_method,
            }
            self._clock_mode = False

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
        self._clock_mode = True

    def is_clock_mode(self) -> bool:
        return self._clock_mode

    def restore_last_content(self):
        """Restaure le dernier contenu temporaire affiché avant l'horloge."""
        if self._last_content_state is None:
            return
        state = self._last_content_state
        content_type = state.get("type")
        if content_type == "image":
            self.send_image(state["path"], resize_method=state.get("resize_method"))
        elif content_type == "text":
            self.send_text(
                state["text"],
                animation=state.get("animation"),
                speed=state.get("speed"),
                color=state.get("color"),
                bg_color=state.get("bg_color"),
                font=state.get("font"),
            )
        elif content_type == "image_hex":
            self.send_image_hex(
                state["hex_string"],
                state["file_extension"],
                resize_method=state.get("resize_method"),
            )
        elif content_type == "show_slot":
            self.show_slot(state["slot"])
        self._clock_mode = False

    def exit_clock_mode(self):
        """Sort du mode horloge et revient à l'affichage personnalisé.

        La librairie ``pypixelcolor`` n'expose aucune commande de changement de
        canal. En revanche, enregistrer un contenu dans un slot force le
        firmware à quitter le canal horloge et à réafficher le canal
        personnalisé : on écrit donc le texte de sortie dans le slot dédié
        (``self.exit_clock_slot``, 100 par défaut), on vide ce slot, puis on
        réaffiche le dernier contenu temporaire connu, le cas échéant.
        """
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")

        slot = self.exit_clock_slot

        # 1) Écrire le texte de sortie dans le slot dédié : cette écriture force
        #    le firmware à quitter le canal horloge.
        self.send_text(EXIT_CLOCK_TEXT, save_slot=slot)

        # 2) Vider le slot de sortie : il ne sert qu'à déclencher la sortie.
        try:
            self.delete(slot)
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Nettoyage du slot de sortie %d échoué : %s", slot, exc)

        # 3) Réafficher le dernier contenu temporaire connu (best effort).
        try:
            self.restore_last_content()
        except Exception as exc:  # noqa: BLE001
            _logger.warning("Restauration du contenu après sortie d'horloge échouée : %s", exc)

        self._clock_mode = False

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

        # --- tentative 1 : commande officielle du package -----------------
        try:
            self.client.show_slot(slot)
            _logger.debug("show_slot(%d) succeeded via pypixelcolor official command", slot)
        except Exception as exc_official:  # noqa: BLE001
            _logger.warning(
                "show_slot(%d) failed with official payload (0x08 0x80): %s", slot, exc_official
            )

            # --- tentative 2 : payload corrigé (type=0x01 comme delete) -------
            async def _exec_raw():
                session = self.client._async_client._session
                return await session.execute_command(_build_show_slot_raw, slot)

            try:
                self.client._run_async(_exec_raw())
                _logger.info("show_slot(%d) succeeded with raw corrected payload (0x08 0x01)", slot)
            except Exception as exc_raw:  # noqa: BLE001
                _logger.error(
                    "show_slot(%d) also failed with raw corrected payload: %s", slot, exc_raw
                )
                raise RuntimeError(
                    f"Impossible d'afficher le slot {slot} (protocole non reconnu par le panneau)."
                ) from exc_raw
        self._last_content_state = {"type": "show_slot", "slot": slot}
        self._clock_mode = False

    def delete(self, slot: int):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.delete(slot)

    def clear(self):
        if not self.client:
            raise RuntimeError("Non connecté au panneau.")
        self.client.clear()
        self._last_content_state = None
        self._clock_mode = False

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
