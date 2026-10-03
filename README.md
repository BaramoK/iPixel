<div align="center">

# 🎨 iPixel LED Controller

**Application de bureau pour contrôler vos panneaux LED Pixel Art via Bluetooth**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows)](https://microsoft.com/windows)
[![BLE](https://img.shields.io/badge/Bluetooth%20LE-Enabled-0082FC?logo=bluetooth)](https://bluetooth.com)

[📥 Installation](#-installation) • [🚀 Utilisation](#-utilisation) • [⚙️ Fonctionnalités](#%EF%B8%8F-fonctionnalités)

</div>

---

## 📖 Description

**iPixel** est une interface graphique intuitive qui te permet de contrôler des panneaux LED compatibles [`pypixelcolor`](https://github.com/Eliav2/pypixelcolor) (Divoom Pixoo, Timoo, et autres) **depuis ton PC Windows** via Bluetooth Low Energy.

Avec iPixel, tu peux envoyer des images, afficher du texte animé, régler la luminosité, configurer l'horloge, et bien plus — le tout depuis une application desktop moderne avec support du **glisser-déposer** natif.

---

## ⚙️ Fonctionnalités

| 🖼️ Images | 📝 Texte | 🔧 Réglages |
|-----------|----------|-------------|
| Glisser-déposer depuis l'explorateur | Texte personnalisé avec couleurs | Luminosité (0–100%) |
| Aperçu en temps réel | Animations : scroll, blink, fade, snowflake | Orientation 0°/90°/180°/270° |
| Redimensionnement CROP / FIT | Vitesses de défilement | Mode horloge configurable |
| Sauvegarde dans les slots | Couleurs inline `[#RRGGBB]…[/]` | Allumer / Éteindre |
| Formats PNG, JPG, BMP, GIF | Polices personnalisables | Gestion des slots mémoire |

🔍 **Scan BLE intégré** — détecte automatiquement les panneaux LED à proximité.

💾 **Persistance** — MAC address, textes, couleurs et réglages sauvegardés entre les sessions.

---

## 📦 Prérequis

- **Python 3.10+**
- **Windows 10/11** *(tkinterdnd2 utilise des bindings natifs Windows)*
- **Contrôleur Bluetooth LE** activé
- Un **panneau LED compatible** (ex. Divoom Pixoo 64, Timoo…)

---

## 🚀 Installation

```bash
git clone https://github.com/BaramoK/iPixel.git
cd iPixel
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> **Note** : `pypixelcolor` doit être disponible dans ton environnement. Si ce n'est pas le cas, consulte la [documentation officielle](https://github.com/Eliav2/pypixelcolor).

---

## ▶️ Utilisation

```bash
python app.py
```

### Connexion rapide

1. Assure-toi que ton panneau LED est **allumé et en mode BLE** (non connecté à une autre app).
2. Clique sur **🔍 Scanner** pour découvrir l'appareil, ou saisis manuellement l'adresse MAC.
3. Clique sur **🔗 Connecter** — la LED passe au statut 🟢.

### Envoyer une image

1. Va dans l'onglet **🖼️ Image**
2. Glisse une image depuis l'explorateur dans la zone sombre
3. Choisis `CROP` (rogne) ou `FIT` (conserve les proportions)
4. Définis un **slot** *(optionnel, 0 = aucun)*
5. Clique sur **📤 Envoyer**

### Envoyer du texte

1. Va dans l'onglet **📝 Texte**
2. Saisis ton texte *(ex. `(●◡●)`)*
3. Personnalise la couleur, le fond, l'animation et la vitesse
4. Clique sur **📤 Envoyer**

> **Astuce couleurs** : utilise `[#RRGGBB]texte[/]` pour des couleurs inline.

### Réglages avancés

1. Va dans l'onglet **⚙️ Réglages**
2. Règle la luminosité, l'orientation, configure l'horloge
3. Gère tes slots : affiche ou supprime du contenu enregistré

⚠️ `clear()` efface **toutes** les données du panneau — utilise avec précaution !

---

## 🏗️ Architecture

```
iPixel/
├── app.py                  → Point d'entrée (TkinterDnD.Tk)
├── requirements.txt        → Dépendances
├── config.json             → Configuration & persistance utilisateur
├── config_manager.py       → Gestionnaire JSON thread-safe
├── led_client.py           → Wrapper pypixelcolor + ThreadPoolExecutor
└── gui/
    ├── __init__.py
    ├── main_window.py      → Fenêtre principale + connexion BLE + scan
    ├── image_tab.py        → Drag & drop, aperçu Pillow, envoi image
    ├── text_tab.py         → Saisie texte, sélecteurs couleur, animation
    ├── settings_tab.py     → Horloge, luminosité, orientation, slots
    └── history_tab.py      → Historique des envois
```

### Détails techniques

| Aspect | Implémentation |
|--------|----------------|
| **Threading** | `ThreadPoolExecutor(max_workers=1)` — appels BLE en arrière-plan, UI jamais bloquée. |
| **Marshaling** | Retour au thread principal via `root.after()`. |
| **Drag & Drop** | [`tkinterdnd2`](https://github.com/Eliav2/tkinterdnd2) — bindings natifs Windows. |
| **Aperçu** | `Pillow` avec filtre `LANCZOS`. |
| **Persistance** | `config_manager.py` sauvegarde automatiquement en JSON. |

---

## 🛠️ Dépendances

| Package | Version | Rôle |
|---------|---------|------|
| `pypixelcolor` | *(préinstallé)* | Communication BLE avec le panneau LED |
| `tkinterdnd2` | ≥ 0.6.0 | Glisser-déposer natif Windows |
| `Pillow` | ≥ 9.0.0 | Aperçu et traitement d'images |

---

## ⚠️ Notes importantes

- Le **mode slot** (`save_slot`) peut provoquer des *bootloops* si les données sont corrompues. **Teste sans slot d'abord.**
- `clear()` supprime **toutes** les données et réglages du panneau sans retour possible.
- Ton panneau doit être **allumé et en mode BLE** — déconnecte-le de toute autre application (smartphone) avant d'utiliser iPixel.

---

## 📄 Licence

Ce projet est sous licence MIT.

---

<div align="center">

Made with ❤️ by [BaramoK](https://github.com/BaramoK)

</div>
