#.\venv310\Scripts\activate
# pip install mediapipe==0.10.11 opencv-python "numpy<2"
# pip install streamlit opencv-python pillow numpy
#streamlit run app.py
import cv2
import mediapipe as mp
import numpy as np
import os

# --- 1. SETTINGS & PATHS ---
# Keeping your specific project paths exactly as they are
INPUT_DIR = r"C:\MINI PROJECT 6TH SEM\CLEAN_DATASET"
ASSETS_DIR = r"C:\MINI PROJECT 6TH SEM\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

# --- 2. THE INVENTORY ENGINE (Your Verified Logic) ---
def build_inventory_if_empty():
    """Uses your specific zoom and masking logic to prepare assets."""
    existing_assets = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.png')]
    
    if len(existing_assets) == 0:
        print("Inventory not found. Running your extraction logic...")
        for file in os.listdir(INPUT_DIR):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = cv2.imread(os.path.join(INPUT_DIR, file))
                if img is None: continue
                
                h, w = img.shape[:2]
                img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
                
                # YOUR VERIFIED MATH: Center crop with 0.33 height ratio
                cx, cy, r = w // 2, h // 2, int(h * 0.33)
                
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, (cx, cy), r, 255, -1)
                mask = cv2.GaussianBlur(mask, (7, 7), 0) # Your soft-edge setting
                img_rgba[:, :, 3] = mask
                
                # Precise crop to the iris circle
                crop = img_rgba[cy-r:cy+r, cx-r:cx+r]
                if crop.size > 0:
                    crop = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LANCZOS4)
                    cv2.imwrite(os.path.join(ASSETS_DIR, f"lens_{file.split('.')[0]}.png"), crop)
        print("✅ Inventory built using your custom extraction settings.")

# Run the check
build_inventory_if_empty()

# Load all processed lenses
lens_files = [os.path.join(ASSETS_DIR, f) for f in os.listdir(ASSETS_DIR) if f.endswith('.png')]
if not lens_files:
    print("Error: DATASET is empty. Place your eye photos in C:\MINI PROJECT 6TH SEM\DATASET")
    exit()

current_lens_idx = 0
overlay_lens = cv2.imread(lens_files[current_lens_idx], cv2.IMREAD_UNCHANGED)

# --- 3. MEDIAPIPE & BLENDING (The Fixed Logic) ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, 
                                 min_detection_confidence=0.6, min_tracking_confidence=0.6)

def apply_lens(frame, lens, iris_landmarks):
    fh, fw = frame.shape[:2]
    points = np.array([[int(l.x * fw), int(l.y * fh)] for l in iris_landmarks])
    center = np.mean(points, axis=0).astype(int)
    
    # Calculate radius based on MediaPipe's iris detection
    diameter = int(np.linalg.norm(points[0] - points[2]) * 1.7)
    if diameter <= 0: return frame
    
    r = diameter // 2
    y1, y2, x1, x2 = center[1]-r, center[1]+r, center[0]-r, center[0]+r
    
    # Safety boundary check
    if y1 < 0 or y2 > fh or x1 < 0 or x2 > fw: return frame

    # CAPTURE THE ROI
    roi = frame[y1:y2, x1:x2]
    roi_h, roi_w = roi.shape[:2]
    
    # THE CRITICAL FIX: Match overlay shape to ROI shape exactly
    res_lens = cv2.resize(lens, (roi_w, roi_h), interpolation=cv2.INTER_AREA)
    
    # Perform Alpha Blending
    alpha = res_lens[:, :, 3] / 255.0
    alpha_inv = 1.0 - alpha

    for c in range(3):
        frame[y1:y2, x1:x2, c] = (alpha * res_lens[:, :, c] + alpha_inv * roi[:, :, c])
        
    return frame

# --- 4. EXECUTION LOOP ---
cap = cv2.VideoCapture(0)

print("\n--- APPLICATION STARTED ---")
print("Controls: 'N' = Next Lens | 'Q' = Quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            # Indices 468-472 is Left Iris, 473-477 is Right Iris
            left_iris = [landmarks.landmark[i] for i in range(468, 473)]
            right_iris = [landmarks.landmark[i] for i in range(473, 478)]
            
            frame = apply_lens(frame, overlay_lens, left_iris)
            frame = apply_lens(frame, overlay_lens, right_iris)

    # Status Display
    lens_name = os.path.basename(lens_files[current_lens_idx])
    cv2.putText(frame, f"Active: {lens_name}", (15, 30), 
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow('Mini Project: Lens Try-On System', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n'):
        current_lens_idx = (current_lens_idx + 1) % len(lens_files)
        overlay_lens = cv2.imread(lens_files[current_lens_idx], cv2.IMREAD_UNCHANGED)

cap.release()
cv2.destroyAllWindows()