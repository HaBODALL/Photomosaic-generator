"""
Streamlit Web GUI application for Photomosaic Generator.
"""
import os
import tempfile
import cv2
import numpy as np
import streamlit as st
from PIL import Image

from photomosaic.core.pool import TilePool
from photomosaic.core.engine import generate_mosaic_image
from photomosaic.downloaders.wikimedia import WikimediaDownloader
from photomosaic.downloaders.archive_org import ArchiveOrgDownloader
from photomosaic.downloaders.openverse import OpenverseDownloader

st.set_page_config(
    page_title="Photomosaic Generator Studio",
    layout="wide"
)

st.title("Photomosaic Generator Studio")
st.markdown("Transform images and videos into photomosaics with custom image pools and themes.")

st.sidebar.header("Configuration")

# Tile options
stride = st.sidebar.slider("Tile Size (Stride in px)", min_value=10, max_value=100, value=30, step=5)
color_space = st.sidebar.selectbox("Color Space Matching", options=["lab", "bgr"], index=0, help="LAB offers superior perceptual color matching.")
sub_grid = st.sidebar.slider("Sub-grid Divisions (Quadrants)", min_value=1, max_value=4, value=2, help="2x2 grid analyzes sub-tile color gradients.")
anti_repetition = st.sidebar.slider("Anti-Repetition Threshold", min_value=0, max_value=10, value=2, help="Grid cell distance required before repeating the same tile.")
overlay_ratio = st.sidebar.slider("Overlay Ratio (Blend Original)", min_value=0.0, max_value=0.8, value=0.0, step=0.05)

# Tabs
tab_gen, tab_download, tab_connectors = st.tabs(["Mosaic Generator", "Theme Downloader", "Cloud Services"])

with tab_gen:
    st.subheader("1. Source Image")
    uploaded_file = st.file_uploader("Upload target image", type=["jpg", "jpeg", "png", "webp"])

    st.subheader("2. Tile Pool Selection")
    pool_choice = st.radio("Tile Source", options=["Default Repo Pool (image_pool)", "Custom Directory Path"], index=0)

    if pool_choice == "Custom Directory Path":
        pool_dir = st.text_input("Local Directory Path", value="image_pool")
    else:
        pool_dir = "image_pool"

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        col1, col2 = st.columns(2)
        with col1:
            st.image(cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB), caption="Target Image", use_container_width=True)

        if st.button("Generate Photomosaic", type="primary"):
            if not os.path.isdir(pool_dir):
                st.error(f"Tile pool directory not found: {pool_dir}")
            else:
                progress_bar = st.progress(0.0)
                status_text = st.empty()

                def update_progress(pct):
                    progress_bar.progress(int(pct) / 100.0)
                    status_text.text(f"Generating mosaic... {int(pct)}%")

                with st.spinner("Building tile pool index..."):
                    pool = TilePool(
                        tile_size=(stride, stride),
                        color_space=color_space,
                        sub_grid=sub_grid,
                        anti_repetition_threshold=anti_repetition
                    )
                    pool.load_from_directory(pool_dir)

                if len(pool.tiles) == 0:
                    st.error("Tile pool is empty! Please load images or download a theme first.")
                else:
                    status_text.text("Processing tiles...")
                    result_bgr = generate_mosaic_image(
                        input_image,
                        pool,
                        stride=stride,
                        overlay_ratio=overlay_ratio,
                        progress_callback=update_progress
                    )

                    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
                    with col2:
                        st.image(result_rgb, caption="Generated Photomosaic", use_container_width=True)

                    # Encode for download
                    _, encoded_img = cv2.imencode(".jpg", result_bgr)
                    st.download_button(
                        label="Download Result Image",
                        data=encoded_img.tobytes(),
                        file_name="photomosaic_output.jpg",
                        mime="image/jpeg"
                    )

with tab_download:
    st.subheader("Download Stock / Public Domain Images by Keyword")
    theme_query = st.text_input("Search Keyword / Theme", value="nature")
    provider = st.selectbox("Source Provider", options=["Wikimedia Commons", "Archive.org", "Openverse"])
    download_limit = st.slider("Number of images", min_value=10, max_value=100, value=30, step=10)
    target_folder = st.text_input("Save to Folder", value="image_pool")

    if st.button("Download Theme Images"):
        dl_progress = st.progress(0.0)
        dl_status = st.empty()

        def update_dl_progress(pct):
            dl_progress.progress(int(pct) / 100.0)
            dl_status.text(f"Downloading... {int(pct)}%")

        if provider == "Wikimedia Commons":
            downloader = WikimediaDownloader()
        elif provider == "Archive.org":
            downloader = ArchiveOrgDownloader()
        else:
            downloader = OpenverseDownloader()

        paths = downloader.download_by_theme(
            theme_query,
            target_folder,
            limit=download_limit,
            progress_callback=update_dl_progress
        )
        st.success(f"Successfully downloaded {len(paths)} images into '{target_folder}'!")

with tab_connectors:
    st.subheader("Connect Personal Cloud Libraries")
    st.info("Configure API keys and credentials in your `.env` file or directly below.")
    service = st.selectbox("Cloud Service", options=["Immich", "Google Photos", "WebDAV / Nextcloud"])

    if service == "Immich":
        immich_url = st.text_input("Immich Instance URL", value="http://localhost:2283")
        immich_key = st.text_input("API Key", type="password")
        if st.button("Connect Immich"):
            from photomosaic.connectors.immich import ImmichConnector
            conn = ImmichConnector(immich_url, immich_key)
            if conn.test_connection():
                st.success("Connection successful!")
            else:
                st.error("Failed to connect to Immich. Check URL and API Key.")

    elif service == "Google Photos":
        g_token = st.text_input("OAuth Access Token", type="password")
        if st.button("Connect Google Photos"):
            from photomosaic.connectors.google_photos import GooglePhotosConnector
            conn = GooglePhotosConnector(g_token)
            if conn.test_connection():
                st.success("Connection successful!")
            else:
                st.error("Failed to connect to Google Photos. Check Access Token.")

    elif service == "WebDAV / Nextcloud":
        dav_url = st.text_input("WebDAV URL", value="https://cloud.example.com/remote.php/dav/files/user/")
        dav_user = st.text_input("Username")
        dav_pass = st.text_input("Password", type="password")
        if st.button("Connect WebDAV"):
            from photomosaic.connectors.webdav import WebDAVConnector
            conn = WebDAVConnector(dav_url, dav_user, dav_pass)
            if conn.test_connection():
                st.success("Connection successful!")
            else:
                st.error("Failed to connect via WebDAV. Check credentials and URL.")
