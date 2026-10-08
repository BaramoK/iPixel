<div align="center">

# 🎨 iPixel LED Controller

**Application de bureau pour contrôler vos panneaux LED Pixel Art via Bluetooth**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows)](https://microsoft.com/windows)
[![BLE](https://img.shields.io/badge/Bluetooth%20LE-Enabled-0082FC?logo=bluetooth)](https://bluetooth.com)

[📥 Installation](#-installation) • [📦 Exécutable](#-exécutable-autonome) • [🏗️ Build](#%EF%B8%8F-build) • [🚀 Utilisation](#-utilisation) • [⚙️ Fonctionnalités](#%EF%B8%8F-fonctionnalités)

</div>

---

## 📖 Description

**iPixel** est une interface graphique intuitive qui te permet de contrôler des panneaux LED compatibles [`pypixelcolor`](https://github.com/lucagoc/pypixelcolor) (Divoom Pixoo, Timoo, et autres) **depuis ton PC Windows** via Bluetooth Low Energy.

Avec iPixel, tu peux envoyer des images, afficher du texte animé, régler la luminosité, configurer l'horloge, et bien plus — le tout depuis une application desktop moderne avec support du **glisser-déposer** natif.

💡 **Note sur les slots** : le rappel de slot (`show_slot`) intègre un workaround pour un bug du payload BLE upstream — le changement s'effectuera à la fin du cycle si du texte défile.

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

💾 **Persistance** — MAC address, textes, couleurs, réglages et **historique rejouable** (images copiées localement) sauvegardés entre les sessions.

---

## 📦 Prérequis

- **Python 3.10+**
- **Windows 10/11** *(tkinterdnd2 utilise des bindings natifs Windows)*
- **Contrôleur Bluetooth LE** activé
- Un **panneau LED compatible** (ex. Divoom Pixoo 64, Timoo…)

---

## 📦 Exécutable autonome (recommandé)

Pour les utilisateurs qui souhaitent simplement lancer l'application **sans installer Python ni aucune dépendance** :

1. Télécharge **`iPixel-UI-Manager.exe`** depuis la [page Releases](https://github.com/BaramoK/iPixel-UI-Manager/releases).
2. Double-clique pour lancer — aucune installation requise.

> **💡 Zéro dépendance** : l'exe embarque Python, `pypixelcolor`, `bleak`, `Pillow` et `tkinterdnd2` dans un seul fichier (~22 Mo).

---

## 📥 Installation (mode développeur)

Si tu préfères exécuter le projet depuis les sources ou contribuer au code :

```bash
git clone https://github.com/BaramoK/iPixel-UI-Manager.git
cd iPixel-UI-Manager
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> **Note** : en mode source, `pypixelcolor` doit être disponible dans ton environnement. Si ce n'est pas le cas, consulte la [documentation officielle](https://github.com/lucagoc/pypixelcolor).

---

## 🏗️ Build

Pour générer toi-même l'exécutable autonome (`--onefile`) depuis les sources :

```bash
pyinstaller --clean --noconfirm iPixel-UI-Manager.spec
```

Le fichier **`dist/iPixel-UI-Manager.exe`** est alors produit. Il contient :

| Composant | Statut |
|-----------|--------|
| `pypixelcolor` (librairie + polices) | ✅ embarqué |
| `bleak` (+ bindings WinRT natifs) | ✅ embarqué |
| `Pillow` (extensions C) | ✅ embarqué |
| `tkinterdnd2` (+ DLLs) | ✅ embarqué |
| `tkinter` / Tcl-Tk | ✅ embarqué |
| Icônes, config, assets | ✅ embarqués |

> **ProTip** : le flag `--clean` évite d'éventuels résidus d'un build précédent.

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

### 🕘 Historique

L'onglet **🕘 Historique** conserve tes envois (texte et image) pour les **rejouer** en un clic.

1. Va dans l'onglet **🕘 Historique** — la colonne **Aperçu** affiche une **miniature** de chaque image.
   Les colonnes **Slot** et **Mode** indiquent le **slot de sauvegarde** et le mode de redimensionnement
   (**FIT** / **CROP**) utilisés lors de l'envoi (slot `0` = aucun → `—` ; mode `—` pour les textes)
2. Sélectionne une entrée puis :
   - **📂 Charger dans l'onglet** — réinjecte le contenu (et son formatage) dans l'onglet Texte/Image
   - **🚀 Envoyer directement** — ré-émet immédiatement vers le panneau
3. **🗑️ Supprimer la sélection** / **💣 Vider tout l'historique** pour nettoyer

> **📦 Entrées autonomes** : chaque image envoyée est **copiée** dans `history_assets/`
> à côté de `history.json`. Le rejeu fonctionne donc même si le fichier d'origine a
> été déplacé ou supprimé. Les assets sont nettoyés automatiquement quand une entrée
> est supprimée (ou devient orpheline). Ce dossier est ignoré par Git.

> **♻️ Pas de doublon au rejeu** : si tu recharges une entrée dans son onglet
> (**📂 Charger dans l'onglet**) puis la renvoies, l'entrée **d'origine est mise à jour**
> — même `id`, même horodatage, même place dans la liste — au lieu d'en créer une
> nouvelle. L'asset copié est réutilisé (aucune nouvelle copie). Un envoi « neuf »
> (contenu non issu de l'historique) crée toujours une nouvelle entrée.

---

## 🏗️ Architecture

```
iPixel-UI-Manager/
├── app.py                  → Point d'entrée (TkinterDnD.Tk)
├── iPixel-UI-Manager.spec  → Configuration PyInstaller (build --onefile)
├── requirements.txt        → Dépendances
├── config.json             → Configuration & persistance utilisateur
├── config_manager.py       → Gestionnaire JSON thread-safe
├── history.json            → Historique des envois (métadonnées + chemins)
├── history_manager.py      → Historique : ajout / mise à jour sans doublon + copie des images (history_assets/)
├── history_assets/         → Copie locale des images (rejeu autonome, ignoré par Git)
├── led_client.py           → Wrapper pypixelcolor + ThreadPoolExecutor
├── assets/
│   ├── app_icon.ico        → Icône panneau LED personnalisée (6 résolutions)
│   └── create_icon.py      → Générateur / modificateur de l'icône
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
| **Persistance** | `config_manager.py` sauvegarde automatiquement en JSON ; `history_manager.py` copie les images dans `history_assets/` pour un rejeu autonome. |

---

## 🛠️ Dépendances

| Package | Version | Rôle |
|---------|---------|------|
| `pypixelcolor` | *(préinstallé)* | Communication BLE avec le panneau LED |
| `bleak` | 0.22+ | Layer BLE cross-platform |
| `tkinterdnd2` | ≥ 0.6.0 | Glisser-déposer natif Windows |
| `Pillow` | ≥ 9.0.0 | Aperçu et traitement d'images |
| `PyInstaller` | ≥ 6.0 | Build de l'exécutable autonome |

> En mode **exécutable autonome**, ces dépendances sont intégrées dans le `.exe` via PyInstaller — l'utilisateur final n'a aucun package à installer.

---

## ⚠️ Notes importantes

- Le **mode slot** (`save_slot`) peut provoquer des *bootloops* si les données sont corrompues. **Teste sans slot d'abord.**
- `clear()` supprime **toutes** les données et réglages du panneau sans retour possible.
- Ton panneau doit être **allumé et en mode BLE** — déconnecte-le de toute autre application (smartphone) avant d'utiliser iPixel.

---

## 🙏 Remerciements

Ce projet ne serait pas possible sans l'excellent travail de [**lucagoc**](https://github.com/lucagoc) et sa librairie [**`pypixelcolor`**](https://github.com/lucagoc/pypixelcolor) qui fournit toute la couche de communication Bluetooth Low Energy avec les panneaux LED Divoom.

Un grand merci également aux contributeurs de :
- [`tkinterdnd2`](https://github.com/Eliav2/tkinterdnd2) — pour le support du glisser-déposer natif sous Windows
- [`Pillow`](https://python-pillow.org/) — pour le traitement et l'aperçu des images

---

## 📄 Licence

Ce projet est sous licence MIT.

---

<div align="center">

Made with ❤️ by [BaramoK](https://github.com/BaramoK)

</div>
