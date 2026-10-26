# 🖼️ Photomosaic Generator Studio

> **[English version available here](README.md)**

Générateur de photomosaïques haute performance et convivial en Python pour images et vidéos, propulsé par la correspondance de couleurs CIELAB, l'indexation spatiale cKDTree, des algorithmes d'anti-répétition, un téléchargeur d'images par thème et des connecteurs cloud personnels.

---

## ⚠️ AVERTISSEMENT VIBE CODING & SÉCURITÉ

> **À LIRE ATTENTIVEMENT AVANT UTILISATION**
>
> Ce dépôt a été restructuré et enrichi dans le cadre d'une **expérience de "vibe coding"** (développement rapide assisté par IA). Bien que le code soit structuré et testé, les utilisateurs **DOIVENT** faire preuve d'une grande prudence concernant la sécurité, les requêtes réseau et la gestion des identifiants d'API.

### Bonnes Pratiques de Sécurité :
1. **Clés API & Secrets :** Ne jamais inscrire en dur de clés d'API, jetons d'accès OAuth ou mots de passe WebDAV directement dans les scripts ni les publier sur un dépôt Git public.
2. **Variables d'Environnement :** Utilisez toujours un fichier `.env` (ignoré par le fichier `.gitignore`) ou des variables d'environnement système pour stocker vos secrets.
3. **Sécurité HTTP & SSL :** Assurez-vous que tous vos points d'accès distants (Immich, Nextcloud/WebDAV, API externes) utilisent le protocole sécurisé HTTPS en production.
4. **Services Tiers :** Vérifiez les limites de requêtes (*rate limits*) et les conditions d'utilisation lors du téléchargement massif d'images.

---

## ✨ Fonctionnalités

- **🎨 Correspondance de Couleurs Avancée :**
  - **Espace de Couleur CIELAB (L\*a\*b\*) :** Calcul de distance chromatique basé sur la perception visuelle humaine.
  - **Analyse par Sous-Quadrants :** Découpage 2x2 (ou personnalisé) capturant les dégradés et textures internes de chaque tuile.
  - **Recherche Rapide cKDTree :** Recherche ultra-rapide des meilleures tuiles via `scipy.spatial.cKDTree`.
  - **Pénalité d'Anti-Répétition :** Empêche la réutilisation répétitive de la même tuile à proximité.
  - **Superposition Réglable (Overlay) :** Mélange doux entre l'image cible originale et les tuiles de la mosaïque.

- **📥 Téléchargeur d'Images par Thème (`photomosaic.downloaders`) :**
  - **Wikimedia Commons** (Domaine public & licences libres)
  - **Archive.org** (Archives d'images du domaine public)
  - **Openverse** (Recherche de médias Creative Commons)
  - **API Unsplash, Pexels, Pixabay**

- **🔌 Connecteurs de Médias Cloud (`photomosaic.connectors`) :**
  - **Immich** (Gestionnaire de photos auto-hébergé)
  - **API REST Google Photos**
  - **WebDAV / Nextcloud**

- **🚀 Interface Web Studio & CLI Conviviale :**
  - **Interface Web Interactive Streamlit (`app.py`) :** Glisser-déposer, curseurs en direct, prévisualisation et téléchargement par thème.
  - **Interface en Ligne de Commande (`photomosaic` CLI) :** CLI scriptable pour l'automatisation.
  - **Compatibilité des Anciens Scripts :** Prise en charge complète de `image2image.py` et `video2video.py`.

---

## ⚙️ Installation

### Prérequis
- **Python 3.9+ / 3.12+**
- Git

### Étapes
```bash
# 1. Cloner le dépôt
git clone https://github.com/HaBODALL/Photomosaic-generator.git
cd Photomosaic-generator

# 2. Installer le package en mode éditable
pip install -e .

# Optionnel : Copier la configuration d'environnement
cp .env.example .env
```

---

## 💻 Utilisation

### 1. Interface Web Interactive (Streamlit)
Lancez l'interface Web conviviale dans votre navigateur :
```bash
streamlit run app.py
```

### 2. Interface en Ligne de Commande (CLI)
```bash
# Générer une image mosaïque
photomosaic image -i data/input.jpg -o data/output.jpg -p image_pool -s 30 --color_space lab --anti_repetition 2

# Générer une vidéo mosaïque
photomosaic video -i data/input.mp4 -o data/output.mp4 -p image_pool -s 20

# Télécharger des images par thème depuis Wikimedia Commons
photomosaic download -t "nature" -o image_pool --source wikimedia --limit 50
```

### 3. Utilisation des Anciens Scripts
```bash
# Image à Image
python image2image.py --input data/input.jpg --output data/output.jpg --pool image_pool --stride 30

# Vidéo à Vidéo
python video2video.py --input data/input.mp4 --output data/output.mp4 --pool image_pool --stride 20
```

---

## 🧪 Tests Automatisés

Pour exécuter la suite de tests unitaires :
```bash
pytest
```

---

## 📜 Licence

Distribué sous la licence MIT. Voir le fichier `LICENSE` pour plus de détails.
