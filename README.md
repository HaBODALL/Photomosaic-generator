# 🖼️ Photomosaic Generator Studio

> **[Version Française disponible ici](README_FR.md)** | **[🌐 Explore Live GitHub Pages Demo](https://habodall.github.io/Photomosaic-generator/)**

High-performance, user-friendly Python photomosaic art generator for images and videos, powered by CIELAB color matching, cKDTree spatial indexing, anti-repetition algorithms, theme downloaders, and personal media cloud connectors.

---

## 📸 Example Result

<p align="center">
  <img src="demo/input.jpg" width="45%" alt="Input Image">
  <img src="demo/example_mosaic.jpg" width="45%" alt="Photomosaic Output">
  <br>
  <i>Left: Input Target Image | Right: Generated Photomosaic (CIELAB 2x2 Sub-Grid, Stride 20px)</i>
</p>

---

## ⚠️ VIBE CODING & SECURITY WARNING

> **PLEASE READ CAREFULLY BEFORE USE**
>
> This repository was refactored and expanded as an **experimental "vibe coding" project** (AI-assisted rapid software iteration). While the code has been structured and tested, users **MUST** exercise caution regarding security, network requests, and API credential management.

### Security Best Practices:
1. **API Keys & Secrets:** NEVER hardcode API keys, OAuth access tokens, or WebDAV passwords directly into scripts or push them to public Git repositories.
2. **Environment Variables:** Always use a `.env` file (which is ignored by `.gitignore`) or system environment variables to store credentials securely.
3. **HTTP & SSL Security:** Ensure all remote endpoints (Immich, Nextcloud/WebDAV, stock APIs) use HTTPS in production.
4. **Third-Party Services:** Verify rate limits and terms of service when downloading large quantities of stock photos or syncing personal cloud libraries.

---

## ✨ Features

- **🎨 Advanced Color Matching:**
  - **CIELAB (L\*a\*b\*) Color Space:** Perceptual color distance calculation mimicking human visual perception.
  - **Sub-Quadrant Analysis:** 2x2 (or custom) sub-grid division capturing color gradients and internal textures within each tile.
  - **cKDTree Fast Nearest-Neighbor Search:** Ultra-fast tile retrieval powered by `scipy.spatial.cKDTree`.
  - **Anti-Repetition Penalty:** Prevents neighboring cells from reusing the same tile repeatedly.
  - **Overlay Blending:** Smooth blending ratio option between original image and mosaic tiles.

- **📥 Keyword/Theme Image Downloaders (`photomosaic.downloaders`):**
  - **Wikimedia Commons** (Public Domain & Open License)
  - **Archive.org** (Public Domain Image Archives)
  - **Openverse** (Creative Commons Media Search)
  - **Unsplash API, Pexels API, Pixabay API**

- **🔌 Personal Cloud Media Connectors (`photomosaic.connectors`):**
  - **Immich** (Self-hosted media API)
  - **Google Photos REST API**
  - **WebDAV / Nextcloud**

- **🚀 User-Friendly Web GUI & CLI:**
  - **Streamlit Web Application (`app.py`):** Interactive UI with drag-and-drop, real-time sliders, live preview, and theme downloading.
  - **Command-Line Interface (`photomosaic` CLI):** Scriptable CLI for automation and server environments.
  - **Legacy Script Compatibility:** Full support for `image2image.py` and `video2video.py`.

---

## 🌐 GitHub Pages Exploration

You can explore the project showcase online via GitHub Pages:
👉 **[https://habodall.github.io/Photomosaic-generator/](https://habodall.github.io/Photomosaic-generator/)**

*To activate GitHub Pages for your fork/repo:*
1. Go to repository **Settings** > **Pages**.
2. Under **Build and deployment**, select **Branch**: `main` (or default branch) and folder `/docs`.
3. Save to publish the interactive showcase site!

---

## ⚙️ Installation

### Prerequisites
- **Python 3.9+ / 3.12+**
- Git

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/HaBODALL/Photomosaic-generator.git
cd Photomosaic-generator

# 2. Install package in editable mode
pip install -e .

# Optional: Copy environment configuration
cp .env.example .env
```

---

## 💻 Usage

### 1. Interactive Web Interface (Streamlit)
Launch the user-friendly Web Studio in your browser:
```bash
streamlit run app.py
```

### 2. Command-Line Interface (CLI)
```bash
# Generate mosaic image
photomosaic image -i data/input.jpg -o data/output.jpg -p image_pool -s 30 --color_space lab --anti_repetition 2

# Generate mosaic video
photomosaic video -i data/input.mp4 -o data/output.mp4 -p image_pool -s 20

# Download theme images from Wikimedia Commons
photomosaic download -t "nature" -o image_pool --source wikimedia --limit 50
```

### 3. Legacy Script Entry Points
```bash
# Image to Image
python image2image.py --input data/input.jpg --output data/output.jpg --pool image_pool --stride 30

# Video to Video
python video2video.py --input data/input.mp4 --output data/output.mp4 --pool image_pool --stride 20
```

---

## 🧪 Running Tests

To run the automated pytest test suite:
```bash
pytest
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
