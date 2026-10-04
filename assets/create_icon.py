#!/usr/bin/env python3
"""Crée une icône représentant un panneau LED pour l'application iPixel."""

import io
import math
import os
import struct
from typing import Dict

from PIL import Image, ImageDraw


def create_led_panel_icon(size: int) -> Image.Image:
    """Dessine un panneau LED sur une image carrée `size x size`."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Marges
    margin = max(2, size // 10)
    panel_left = margin
    panel_top = margin
    panel_right = size - margin
    panel_bottom = size - margin

    radius = max(2, size // 10)

    # --- Cadre du panneau LED ---
    frame_color = (74, 74, 106, 255)   # gris métallique foncé
    frame_highlight = (120, 120, 150, 255)
    draw.rounded_rectangle(
        [(panel_left, panel_top), (panel_right, panel_bottom)],
        radius=radius,
        fill=frame_color,
        outline=frame_highlight,
        width=max(1, size // 32),
    )

    # Zone d'affichage (noir)
    inner_margin = max(3, size // 8)
    screen_left = panel_left + inner_margin
    screen_top = panel_top + inner_margin
    screen_right = panel_right - inner_margin
    screen_bottom = panel_bottom - inner_margin

    screen_radius = max(1, radius // 3)
    draw.rounded_rectangle(
        [(screen_left, screen_top), (screen_right, screen_bottom)],
        radius=screen_radius,
        fill=(10, 10, 20, 255),
        outline=(30, 30, 50, 255),
        width=max(1, size // 64),
    )

    # --- Grille de LEDs ---
    led_count = max(3, size // 8)   # nombre de LEDs par ligne/colonne
    led_diam = max(1, (screen_right - screen_left) // (led_count * 2))
    led_radius = led_diam / 2

    # Ajustement centré
    total_w = led_count * led_diam + (led_count - 1) * led_diam
    total_h = led_count * led_diam + (led_count - 1) * led_diam
    start_x = screen_left + (screen_right - screen_left - total_w) / 2 + led_radius
    start_y = screen_top + (screen_bottom - screen_top - total_h) / 2 + led_radius

    # Couleurs : gris lumineux par défaut, quelques accents RGBW
    colors = [
        (255, 255, 255, 255),   # blanc
        (255, 50, 50, 255),     # rouge
        (50, 255, 50, 255),     # vert
        (50, 50, 255, 255),     # bleu
        (255, 200, 50, 255),    # jaune
        (255, 100, 200, 255),   # rose
        (50, 255, 255, 255),    # cyan
    ]

    # Motif aléatoire distribué
    pattern = [
        [6, 0, 1, 0, 0, 2, 0],
        [0, 3, 0, 1, 0, 0, 4],
        [1, 0, 5, 0, 2, 0, 0],
        [0, 0, 0, 3, 0, 1, 0],
        [0, 4, 0, 0, 6, 0, 3],
        [2, 0, 1, 0, 0, 5, 0],
        [0, 0, 0, 2, 0, 0, 1],
    ]

    # Ajustement de la matrice pour led_count
    while len(pattern) > led_count:
        pattern.pop()
    while len(pattern) < led_count:
        pattern.append(pattern[len(pattern) % len(pattern)][:])
    for row in pattern:
        while len(row) > led_count:
            row.pop()
        while len(row) < led_count:
            row.append(0)

    for row in range(led_count):
        for col in range(led_count):
            cx = start_x + col * (2 * led_diam)
            cy = start_y + row * (2 * led_diam)
            color_idx = pattern[row][col]

            # Si 0, LED "éteinte" et petite ; sinon plus lumineuse
            if color_idx == 0:
                color = (60, 60, 70, 255)
                r = led_radius * 0.5
            else:
                color = colors[color_idx % len(colors)]
                r = led_radius * 0.85

            # Effet lueur pour les LEDs allumées
            if color_idx != 0:
                glow_r = r * 2.5
                for g in range(3, 0, -1):
                    alpha = int(40 / g)
                    glow_color = (color[0], color[1], color[2], alpha)
                    draw.ellipse(
                        [(cx - glow_r / g, cy - glow_r / g),
                         (cx + glow_r / g, cy + glow_r / g)],
                        fill=glow_color,
                    )

            draw.ellipse(
                [(cx - r, cy - r), (cx + r, cy + r)],
                fill=color,
            )

            # Petit reflet blanc
            if color_idx != 0:
                tiny_r = r * 0.25
                offset = r * 0.35
                draw.ellipse(
                    [(cx - offset - tiny_r, cy - offset - tiny_r),
                     (cx - offset + tiny_r, cy - offset + tiny_r)],
                    fill=(255, 255, 255, 200),
                )

    return img


def _create_multi_res_ico(icon_path: str, images_by_size: Dict[int, Image.Image]) -> None:
    """
    Écrit manuellement un fichier .ico multi-résolutions.
    Utilise le format PNG pour chaque image (supporté depuis Windows Vista).
    """
    sizes = sorted(images_by_size.keys())
    count = len(sizes)

    # --- ICO Header ---
    header = struct.pack("<HHH", 0, 1, count)  # reserved, type=icon, count

    # --- ICONDIRENTRY ---
    entries = b""
    data_payload = b""
    offset = 6 + 16 * count  # après header + toutes les entrées

    for size in sizes:
        img = images_by_size[size].convert("RGBA")

        # Encode chaque image en PNG (mémoire)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        png_bytes = buf.getvalue()

        # ICONDIRENTRY
        w = size if size < 256 else 0
        h = size if size < 256 else 0
        entries += struct.pack(
            "<BBBBHHII",
            w, h,    # bWidth, bHeight  (0 = 256)
            0,       # bColorCount
            0,       # bReserved
            1,       # wPlanes
            32,      # wBitCount
            len(png_bytes),   # dwBytesInRes
            offset,  # dwImageOffset
        )

        data_payload += png_bytes
        offset += len(png_bytes)

    with open(icon_path, "wb") as f:
        f.write(header + entries + data_payload)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    icon_path = os.path.join(assets_dir, "app_icon.ico")

    sizes = [16, 32, 48, 64, 128, 256]
    images = {s: create_led_panel_icon(s) for s in sizes}

    _create_multi_res_ico(icon_path, images)

    print(f"Icône multi-résolution générée : {icon_path}")
    print(f"Taille fichier : {os.path.getsize(icon_path):,} octets")

    # Vérification des résolutions réellement contenues
    ico_check = Image.open(icon_path)
    n_frames = getattr(ico_check, "n_frames", 1)
    print(f"\nVérification des {n_frames} résolutions contenues :")
    for i in range(n_frames):
        ico_check.seek(i)
        print(f"  Frame {i}: {ico_check.size[0]}x{ico_check.size[1]}")


if __name__ == "__main__":
    main()
