# iPixel LED Controller

Application graphique de contrôle pour panneaux LED Pixel Art compatibles [`pypixelcolor`](https://github.com/Eliav2/pypixelcolor).

Permet d'envoyer des **images**, du **texte**, et de gérer les **réglages** du panneau via une interface intuitive avec support du **glisser-déposer** (drag & drop).

---

## ✨ Fonctionnalités

- 🖼️ **Envoi d'images** (PNG, JPG, BMP, GIF) avec redimensionnement (`CROP` / `FIT`)
- 📝 **Envoi de texte** avec couleurs, animations et vitesses personnalisables
- 🖱️ **Glisser-déposer** d'images depuis l'explorateur Windows
- 🔍 **Scan BLE** intégré pour découvrir automatiquement le panneau
- ⚙️ **Réglages** : luminosité, orientation, alimentation, mode horloge
- 💾 **Slots** : sauvegarde et affichage rapide de contenus pré-enregistrés
- 🎨 **Sélecteur de couleurs** intégré
- 💾 **Persistance** : adresse MAC, textes, couleurs et réglages mémorisés

---

## 📦 Prérequis

- **Python 3.10+**
- Windows 10/11 (utilise `tkinterdnd2` pour le glisser-déposer natif)
- Un **contrôleur BLE** (Bluetooth Low Energy) activé sur votre PC
- Un panneau LED compatible `pypixelcolor` (ex. Divoom Pixoo/Timoo…)

---

## 🚀 Installation

```bash
cd c:\Users\BaramoK\Documents\Git\iPixel
pip install -r requirements.txt
```

> `pypixelcolor` est supposé déjà installé dans votre environnement.  
> Si ce n'est pas le cas, consultez la documentation officielle.

---

## ▶️ Lancement

```bash
python app.py
```

La fenêtre principale s'ouvre. Saisissez l'adresse MAC de votre panneau, ou appuyez sur **🔍 Scanner** pour le découvrir automatiquement.

---

## 🖥️ Interface

### Barre de connexion
| Élément | Description |
|---------|-------------|
| `Adresse MAC` | Adresse BLE du panneau (ex. `A4:34:F1:XX:XX:XX`) |
| `🔗 Connecter` | Établit la connexion BLE |
| `⛓️‍💥 Déconnecter` | Coupe la connexion proprement |
| `🔍 Scanner` | Recherche les appareils LED à proximité |
| Liste déroulante | Appareils découverts (sélection automatique du MAC) |

---

### 🖼️ Onglet Image
- **Glissez une image** dans la zone sombre
- L'aperçu s'affiche automatiquement
- Choisissez le mode de redimensionnement :
  - `CROP` — rogne pour remplir l'écran
  - `FIT` — conserve le ratio avec bandes noires
- Définissez un **slot** de sauvegarde (0 = aucun)
- Cliquez sur **📤 Envoyer au panneau**

### 📝 Onglet Texte
- Saisissez votre texte dans le champ de saisie
- Personnalisez :
  - **Couleur** du texte (hex, sélecteur 🎨)
  - **Couleur de fond** (hex, sélecteur 🎨)
  - **Animation** : `STATIC`, `SCROLL_LEFT`, `SCROLL_RIGHT`, `BLINK`, `FADE`, `SNOWFLAKE`…
  - **Vitesse** de défilement (0–100)
  - **Slot** de sauvegarde
- Astuce : couleurs inline avec `[#RRGGBB]…[/]`

### ⚙️ Onglet Réglages
| Section | Actions possibles |
|---------|-------------------|
| **Luminosité** | Slider 0–100% |
| **Orientation** | 0° / 90° / 180° / 270° |
| **Alimentation** | Allumer / Éteindre le panneau |
| **Horloge** | Style, format 24h, affichage de la date |
| **Gestion des slots** | Afficher (`show_slot`) ou Supprimer (`delete`) un slot |
| **Danger Zone** | `clear()` — efface TOUTES les données du panneau |

---

## 🗂️ Structure du projet

```
iPixel/
├── app.py                  → Point d'entrée
├── requirements.txt        → Dépendances Python
├── config.json             → Configuration utilisateur (auto-généré)
├── config_manager.py       → Persistance JSON des réglages
├── led_client.py           → Wrapper pypixelcolor thread-safe
└── gui/
    ├── __init__.py
    ├── main_window.py      → Fenêtre principale + connexion BLE
    ├── image_tab.py        → Glisser-déposer + aperçu image
    ├── text_tab.py         → Saisie texte + couleurs + animations
    └── settings_tab.py     → Horloge, luminosité, slots, clear
```

---

## 🔌 Fonctionnement technique

- **Threading** : toutes les opérations BLE sont exécutées dans un worker thread (`ThreadPoolExecutor`) pour ne jamais bloquer l'interface Tkinter.
- **Marshaling** : les résultats retournent dans le thread principal via `after()`.
- **Drag & Drop** : implémenté avec [`tkinterdnd2`](https://github.com/Eliav2/tkinterdnd2), wrapper Python de l'extension Tk `tkdnd`.
- **Aperçu** : redimensionnement dynamique via `Pillow` (`LANCZOS`).

---

## ⚠️ Notes

- Le **mode slot** (`save_slot`) peut provoquer des *bootloops* si les données envoyées sont corrompues. Testez sans slot avant d'utiliser cette fonctionnalité.
- `clear()` supprime **toutes** les données et réglages du panneau. Utilisez avec précaution.
- Assurez-vous que votre panneau est **allumé et en mode BLE** (non connecté à une autre application simultanément).

---

## 🛠️ Dépendances

| Package | Version | Rôle |
|---------|---------|------|
| `pypixelcolor` | *préinstallé* | Communication BLE avec le panneau |
| `tkinterdnd2` | ≥ 0.6.0 | Glisser-déposer natif |
| `Pillow` | ≥ 9.0.0 | Aperçu et redimensionnement des images |

---

*Projet créé pour faciliter l'envoi de contenus personnalisés sur panneau LED via Bluetooth.*
