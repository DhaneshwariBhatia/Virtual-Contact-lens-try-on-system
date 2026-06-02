import cv2
import mediapipe as mp
import numpy as np
import os
import streamlit as st
from PIL import Image

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="LuxeLens AR Studio", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
    }

    .stApp {
        background-color: #f5eeea;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 2.5rem 4rem !important; max-width: 1300px !important; }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #f5eeea; }
    ::-webkit-scrollbar-thumb { background: #B97D7B; border-radius: 2px; }

    /* ─── Nav ─── */
    .luxe-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.8rem 0 1.2rem;
        border-bottom: 1px solid rgba(183,125,123,0.2);
        margin-bottom: 0;
    }
    .luxe-logo {
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 400;
        letter-spacing: 0.08em;
        color: #575527;
    }
    .luxe-logo em { font-style: italic; color: #B97D7B; }
    .luxe-nav-tagline {
        font-size: 13px;
        letter-spacing: 0.25em;
        color: #928E5E;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .luxe-nav-links {
        display: flex;
        gap: 2.5rem;
        font-size: 14px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #928E5E;
    }
    .luxe-nav-badge {
        background: #ECC4C3;
        color: #575527;
        font-size: 12px;
        letter-spacing: 0.15em;
        padding: 8px 18px;
        border-radius: 20px;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* ─── Hero text ─── */
    .hero-eyebrow {
        font-size: 13px;
        letter-spacing: 0.4em;
        color: #B97D7B;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(42px, 5vw, 68px);
        font-weight: 400;
        line-height: 1.12;
        color: #575527;
        margin-bottom: 1.5rem;
    }
    .hero-title em { font-style: italic; color: #B97D7B; }
    .hero-sub {
        font-size: 17px;
        font-weight: 300;
        color: #928E5E;
        line-height: 1.85;
        max-width: 380px;
        margin-bottom: 2.5rem;
    }

    /* ─── CTA Button ─── */
    .stButton > button {
        background: #575527 !important;
        border: none !important;
        color: #f5eeea !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        letter-spacing: 0.2em !important;
        text-transform: uppercase !important;
        padding: 18px 44px !important;
        border-radius: 40px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: #928E5E !important;
        color: #f5eeea !important;
    }

    /* ─── Stats Row ─── */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: rgba(183,125,123,0.15);
        border-radius: 12px;
        overflow: hidden;
        margin: 3rem 0;
    }
    .stat-cell {
        background: #f5eeea;
        padding: 2rem 1.5rem;
        text-align: center;
    }
    .stat-num {
        font-family: 'Playfair Display', serif;
        font-size: 40px;
        font-weight: 400;
        color: #B97D7B;
        line-height: 1;
        margin-bottom: 8px;
    }
    .stat-label {
        font-size: 13px;
        letter-spacing: 0.22em;
        color: #928E5E;
        text-transform: uppercase;
    }

    /* ─── Feature Cards ─── */
    .feature-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin: 2rem 0 4rem;
    }
    .feature-card {
        background: #DDD3C9;
        border-radius: 12px;
        padding: 2.2rem 1.8rem;
    }
    .feature-card:nth-child(2) { background: #ECC4C3; }
    .feature-card:nth-child(3) { background: #928E5E; }
    .feature-icon-box {
        width: 44px; height: 44px;
        border-radius: 10px;
        background: rgba(255,255,255,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.2rem;
        font-size: 20px;
    }
    .feature-card-title {
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        color: #575527;
        margin-bottom: 0.7rem;
    }
    .feature-card:nth-child(3) .feature-card-title { color: #f5eeea; }
    .feature-card-desc {
        font-size: 14px;
        font-weight: 300;
        color: #7a6e5f;
        line-height: 1.8;
    }
    .feature-card:nth-child(3) .feature-card-desc { color: rgba(245,238,234,0.78); }

    /* ─── Section Heading ─── */
    .section-heading {
        font-family: 'Playfair Display', serif;
        font-size: 38px;
        color: #575527;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .section-sub {
        text-align: center;
        font-size: 14px;
        color: #B97D7B;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 2.5rem;
    }

    /* ─── Tryon Top Bar ─── */
    .tryon-topbar {
        background: #DDD3C9;
        margin: 0 -2.5rem;
        padding: 1.2rem 2.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    .tryon-title {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        color: #575527;
        font-style: italic;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #ECC4C3;
        color: #575527;
        font-size: 13px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 7px 16px;
        border-radius: 20px;
        font-weight: 500;
    }
    .live-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #B97D7B;
        animation: blink 1.8s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ─── Product Panel ─── */
    .product-panel {
        background: #fff8f5;
        border: 1px solid rgba(183,125,123,0.18);
        border-radius: 16px;
        padding: 1.8rem 1.5rem;
        margin-bottom: 1rem;
    }
    .product-collection {
        font-size: 12px;
        letter-spacing: 0.35em;
        color: #B97D7B;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .product-name {
        font-family: 'Playfair Display', serif;
        font-size: 30px;
        font-weight: 400;
        color: #575527;
        margin-bottom: 4px;
    }
    .product-price {
        font-size: 24px;
        font-weight: 300;
        color: #B97D7B;
        margin-bottom: 12px;
    }
    .product-desc {
        font-size: 14px;
        font-weight: 300;
        color: #928E5E;
        line-height: 1.85;
    }
    .divider { height: 1px; background: rgba(183,125,123,0.12); margin: 1.1rem 0; }
    .spec-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 5px 0;
    }
    .spec-key { color: #B97D7B; font-weight: 300; }
    .spec-val { color: #575527; font-weight: 400; }

    /* ─── Tags ─── */
    .tags { display: flex; gap: 7px; flex-wrap: wrap; margin-top: 14px; }
    .tag {
        background: #ECC4C3;
        color: #575527;
        font-size: 11px;
        letter-spacing: 0.12em;
        padding: 6px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        font-weight: 500;
    }
    .tag.green { background: #928E5E; color: #f5eeea; }

    /* ─── Camera topbar / counter ─── */
    .cam-topbar {
        background: #DDD3C9;
        padding: 12px 18px;
        border-radius: 16px 16px 0 0;
        font-size: 14px;
        letter-spacing: 0.18em;
        color: #928E5E;
        text-transform: uppercase;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .lens-counter {
        text-align: center;
        padding: 13px 0;
        font-size: 16px;
        letter-spacing: 0.1em;
        color: #575527;
        background: #DDD3C9;
        border-radius: 0 0 16px 16px;
        font-weight: 500;
    }

    /* ─── Shade list ─── */
    .ctrl-label {
        font-size: 12px;
        letter-spacing: 0.35em;
        color: #B97D7B;
        text-transform: uppercase;
        margin: 1.5rem 0 0.8rem;
        font-weight: 500;
    }
    .ctrl-label:first-child { margin-top: 0; }
    .shade-item {
        padding: 9px 12px;
        border-radius: 8px;
        font-size: 14px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #928E5E;
    }
    .shade-item.active {
        background: #ECC4C3;
        color: #575527;
        font-weight: 500;
    }
    .shade-dot {
        width: 12px; height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .session-info {
        font-size: 14px;
        line-height: 2.1;
        color: #928E5E;
    }
    .session-info strong { color: #575527; }

    /* ─── Footer ─── */
    .luxe-footer {
        text-align: center;
        padding: 2.5rem 0 1rem;
        border-top: 1px solid rgba(183,125,123,0.15);
        margin-top: 3rem;
        font-size: 13px;
        letter-spacing: 0.25em;
        color: #B97D7B;
        text-transform: uppercase;
    }

    div[data-testid="stImage"] img { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. ASSET INIT ---
@st.cache_resource
def initialize_assets():
    INPUT_DIR  = r"C:\MINI PROJECT 6TH SEM\CLEAN_DATASET"
    ASSETS_DIR = r"C:\MINI PROJECT 6TH SEM\assets"
    os.makedirs(ASSETS_DIR, exist_ok=True)
    existing = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.png')]
    if len(existing) == 0:
        for file in os.listdir(INPUT_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = cv2.imread(os.path.join(INPUT_DIR, file))
                if img is None: continue
                h, w = img.shape[:2]
                img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                cx, cy, r = w // 2, h // 2, int(h * 0.33)
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, (cx, cy), r, 255, -1)
                mask = cv2.GaussianBlur(mask, (7, 7), 0)
                img_rgba[:, :, 3] = mask
                crop = img_rgba[cy-r:cy+r, cx-r:cx+r]
                if crop.size > 0:
                    crop = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(os.path.join(ASSETS_DIR, f"lens_{file.split('.')[0]}.png"), crop)
    return ASSETS_DIR

# --- 3. STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'lens_index' not in st.session_state:
    st.session_state.lens_index = 0

ASSETS_DIR = initialize_assets()
lens_files  = sorted([f for f in os.listdir(ASSETS_DIR) if f.endswith('.png')])

LENS_DATABASE = {
    "Sky Blue":      {"price": "₹1,200", "desc": "Bright, clear, and striking summer energy.",    "collection": "Azure",  "material": "Hydrogel Pro",  "dot": "#87ceeb"},
    "Aqua Blue":     {"price": "₹1,350", "desc": "Deep tropical cyan tones with soft blending.",  "collection": "Marine", "material": "Silicone HX",   "dot": "#5ec8c8"},
    "Amber":         {"price": "₹1,500", "desc": "Glowing honey-gold tones for a feline effect.", "collection": "Soleil", "material": "Hydrogel Pro",  "dot": "#e8b86d"},
    "Emerald Green": {"price": "₹1,400", "desc": "Deep jewel-toned green for high contrast.",     "collection": "Jardin", "material": "Silicone HX",   "dot": "#4caf72"},
    "Caramel":       {"price": "₹1,100", "desc": "Warm, buttery brown for daily natural wear.",   "collection": "Nude",   "material": "AquaComfort",   "dot": "#b97d7b"},
}

# ─── Update this to your actual hero photo path ───
HERO_IMAGE_PATH = r"C:\MINI PROJECT 6TH SEM\main_image.png"

def next_lens(): st.session_state.lens_index = (st.session_state.lens_index + 1) % len(lens_files)
def prev_lens(): st.session_state.lens_index = (st.session_state.lens_index - 1) % len(lens_files)
def go_tryon():  st.session_state.page = 'tryon'
def go_home():   st.session_state.page = 'home'


# ══════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════
if st.session_state.page == 'home':

    # ── Nav ──
    st.markdown("""
    <div class="luxe-nav">
        <div>
            <div class="luxe-logo">Luxe<em>Lens</em></div>
            <div class="luxe-nav-tagline">Virtual AR Studio</div>
        </div>
        <div class="luxe-nav-links">
            <span>Collection</span>
            <span>About</span>
            <span>Care</span>
        </div>
        <div class="luxe-nav-badge">2026 Collection</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Hero: text left | image right ──
    text_col, img_col = st.columns([1, 1], gap="large")

    with text_col:
        st.markdown("""
        <div style="padding: 3.5rem 0 2rem;">
            <div class="hero-eyebrow">Premium Coloured Contacts</div>
            <div class="hero-title">
                Discover eyes<br>that <em>bloom</em><br>with colour
            </div>
            <div class="hero-sub">
                Try every shade from our curated botanical collection
                in real time — see it on you before you buy.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch AR Try-On  →", on_click=go_tryon)

    with img_col:
        st.markdown("<div style='padding-top: 2.5rem;'>", unsafe_allow_html=True)
        if os.path.exists(HERO_IMAGE_PATH):
            # Display the actual hero image with a nice rounded frame
            hero_img = Image.open(HERO_IMAGE_PATH)
            st.image(hero_img, use_container_width=True)
            st.markdown("""
            <div style="background:#ECC4C3; border-radius:0 0 16px 16px;
                        padding:14px 20px; margin-top:-8px; display:flex;
                        align-items:center; justify-content:space-between;">
                <div>
                    <div style="font-size:12px; color:#B97D7B; letter-spacing:0.2em;
                                text-transform:uppercase; margin-bottom:2px;">Featured</div>
                    <div style="font-size:16px; color:#575527; font-weight:500;">2025 Botanical Collection</div>
                </div>
                <div style="background:#575527; color:#f5eeea; font-size:12px;
                            padding:8px 16px; border-radius:20px; letter-spacing:0.1em;
                            text-transform:uppercase;">20 Shades</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Elegant placeholder with instructions
            st.markdown("""
            <div style="background:#ECC4C3; border-radius:20px 20px 100px 20px;
                        height:480px; display:flex; flex-direction:column;
                        align-items:center; justify-content:center; position:relative; overflow:hidden;">
                <div style="position:absolute; width:260px; height:260px; border-radius:50%;
                            background:rgba(87,85,39,0.09); top:-50px; right:-60px;"></div>
                <div style="position:absolute; width:130px; height:130px; border-radius:50%;
                            background:rgba(87,85,39,0.07); bottom:30px; left:20px;"></div>
                <div style="width:160px; height:160px; border-radius:50%;
                            background:rgba(255,255,255,0.45); display:flex;
                            align-items:center; justify-content:center; z-index:1;">
                    <div style="font-family:'Playfair Display',serif; font-size:18px;
                                color:#575527; text-align:center; line-height:1.6;">
                        AR<br>Try-On<br>Studio
                    </div>
                </div>
                <div style="position:absolute; bottom:20px; left:20px;
                            background:rgba(245,238,234,0.92); border-radius:10px;
                            padding:12px 18px; font-size:14px; color:#575527; font-weight:500;">
                    <div style="font-size:11px; color:#B97D7B; letter-spacing:0.15em;
                                text-transform:uppercase; margin-bottom:3px;">Set your hero image</div>
                    Update HERO_IMAGE_PATH in the code
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Stats ──
    st.markdown("""
    <div class="stats-row">
        <div class="stat-cell">
            <div class="stat-num">20</div>
            <div class="stat-label">Shades</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">AR</div>
            <div class="stat-label">Real-time</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">5★</div>
            <div class="stat-label">Rated</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">ISO</div>
            <div class="stat-label">Certified</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature Cards ──
    st.markdown("""
    <div class="section-heading">Why LuxeLens</div>
    <div class="section-sub">Crafted for comfort, built for beauty</div>
    <div class="feature-row">
        <div class="feature-card">
            <div class="feature-icon-box">👁</div>
            <div class="feature-card-title">Real-time overlay</div>
            <div class="feature-card-desc">MediaPipe iris tracking renders lenses on your live camera with sub-frame precision and natural blending.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon-box">✦</div>
            <div class="feature-card-title">Botanical palette</div>
            <div class="feature-card-desc">Every shade is inspired by nature — petal pinks, meadow greens, and earthy mauves for every skin tone.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon-box" style="background:rgba(255,255,255,0.2);">◈</div>
            <div class="feature-card-title" style="color:#f5eeea;">Instant switch</div>
            <div class="feature-card-desc">Navigate the full collection instantly using the Previous and Next Shade buttons on the try-on screen.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="luxe-footer">© 2025 LuxeLens · ISO 13485 Certified · All Rights Reserved</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# TRY-ON PAGE
# ══════════════════════════════════════════════════
elif st.session_state.page == 'tryon':

    # ── Top bar ──
    st.markdown('<div class="tryon-topbar">', unsafe_allow_html=True)
    back_col, mid_col, badge_col = st.columns([1, 3, 1])
    with back_col:
        st.button("← Back", on_click=go_home)
    with mid_col:
        st.markdown('<div class="tryon-title">AR Try-On Studio</div>', unsafe_allow_html=True)
    with badge_col:
        st.markdown("""
        <div style="text-align:right; padding-top:8px;">
            <span class="live-badge"><span class="live-dot"></span> Live</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Current lens ──
    current_file = lens_files[st.session_state.lens_index]
    display_name = current_file.replace("lens_", "").replace(".png", "").replace("_", " ")
    lens_data    = LENS_DATABASE.get(display_name, {
        "price": "₹999", "desc": "Premium Quality Lens",
        "collection": "Signature", "material": "Hydrogel Pro", "dot": "#B97D7B"
    })
    product_thumb_path = os.path.join(ASSETS_DIR, current_file)

    info_col, cam_col, ctrl_col = st.columns([1, 2.2, 1])

    # ── PRODUCT PANEL (left) ──
    with info_col:
        st.image(product_thumb_path, use_container_width=True)
        st.markdown(f"""
        <div class="product-panel">
            <div class="product-collection">Collection · {lens_data.get('collection','Signature')}</div>
            <div class="product-name">{display_name}</div>
            <div class="product-price">{lens_data['price']}</div>
            <div class="product-desc">{lens_data['desc']}</div>
            <div class="divider"></div>
            <div class="spec-row"><span class="spec-key">Material</span><span class="spec-val">{lens_data.get('material','Hydrogel')}</span></div>
            <div class="spec-row"><span class="spec-key">Duration</span><span class="spec-val">Monthly</span></div>
            <div class="spec-row"><span class="spec-key">Water content</span><span class="spec-val">38%</span></div>
            <div class="spec-row"><span class="spec-key">Base curve</span><span class="spec-val">8.6 mm</span></div>
        </div>
        <div class="tags">
            <span class="tag">UV Shield</span>
            <span class="tag green">ISO Certified</span>
            <span class="tag">Ophthalm. Tested</span>
        </div>
        """, unsafe_allow_html=True)

    # ── CAMERA FEED (centre) ──
    with cam_col:
        # Camera topbar label
        st.markdown(f"""
        <div class="cam-topbar">
            <span>Live camera</span>
            <span style="color:#B97D7B; font-weight:500;">{display_name}</span>
        </div>
        """, unsafe_allow_html=True)

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh    = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        def apply_lens_render(frame, lens, iris_landmarks):
            fh, fw   = frame.shape[:2]
            points   = np.array([[int(l.x * fw), int(l.y * fh)] for l in iris_landmarks])
            center   = np.mean(points, axis=0).astype(int)
            diameter = int(np.linalg.norm(points[0] - points[2]) * 1.7)
            r        = diameter // 2
            y1, y2, x1, x2 = center[1]-r, center[1]+r, center[0]-r, center[0]+r
            if y1 < 0 or y2 > fh or x1 < 0 or x2 > fw: return frame
            roi      = frame[y1:y2, x1:x2]
            res_lens = cv2.resize(lens, (roi.shape[1], roi.shape[0]))
            alpha    = res_lens[:, :, 3] / 255.0
            for c in range(3):
                frame[y1:y2, x1:x2, c] = (alpha * res_lens[:, :, c] + (1-alpha) * roi[:, :, c])
            return frame

        overlay_lens = cv2.imread(os.path.join(ASSETS_DIR, current_file), cv2.IMREAD_UNCHANGED)
        FRAME_WINDOW = st.image([], use_container_width=True)

        # Shade counter strip
        st.markdown(f"""
        <div class="lens-counter">
            Shade {st.session_state.lens_index + 1} of {len(lens_files)} &nbsp;·&nbsp; {display_name}
        </div>
        """, unsafe_allow_html=True)

        # ════ PREV / NEXT BUTTONS — prominent, directly under the camera ════
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        prev_col, next_col = st.columns(2, gap="small")
        with prev_col:
            st.button("◀   Previous Shade", on_click=prev_lens,
                      use_container_width=True, key="btn_prev")
        with next_col:
            st.button("Next Shade   ▶", on_click=next_lens,
                      use_container_width=True, key="btn_next")

        # Camera loop
        cap = cv2.VideoCapture(0)
        while cap.isOpened() and st.session_state.page == 'tryon':
            ret, frame = cap.read()
            if not ret: break
            frame     = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results   = face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                for landmarks in results.multi_face_landmarks:
                    l_iris = [landmarks.landmark[i] for i in range(468, 473)]
                    r_iris = [landmarks.landmark[i] for i in range(473, 478)]
                    frame  = apply_lens_render(frame, overlay_lens, l_iris)
                    frame  = apply_lens_render(frame, overlay_lens, r_iris)
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)
        cap.release()

    # ── CONTROLS (right) ──
    with ctrl_col:
        st.markdown('<div class="ctrl-label">All shades</div>', unsafe_allow_html=True)
        for i, fname in enumerate(lens_files):
            name      = fname.replace("lens_", "").replace(".png", "").replace("_", " ")
            d         = LENS_DATABASE.get(name, {})
            dot_color = d.get("dot", "#B97D7B")
            active    = "active" if i == st.session_state.lens_index else ""
            st.markdown(f"""
            <div class="shade-item {active}">
                <span class="shade-dot" style="background:{dot_color};"></span>
                {name}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="ctrl-label" style="margin-top:1.8rem">Session</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="session-info">
            <div>Tracking &nbsp;<strong>MediaPipe Iris</strong></div>
            <div>Mode &nbsp;<strong>Real-time AR</strong></div>
            <div>Shade &nbsp;<strong>{st.session_state.lens_index + 1} / {len(lens_files)}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="luxe-footer">LuxeLens AR Studio · Premium Vision Technology</div>', unsafe_allow_html=True)