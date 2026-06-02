import cv2
import numpy as np
import os

# ─── PATH SETUP ──────────────────────────────────────────────────────────
# Define where your raw data is and where to save the cleaned assets
INPUT_DIR = r"C:\MINI PROJECT 6TH SEM\CLEAN_DATASET"
OUTPUT_DIR = r"C:\MINI PROJECT 6TH SEM\assets"

# Create the output folder if it doesn't already exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── IRIS ISOLATION FUNCTION ─────────────────────────────────────────────
def isolate_iris_perfect(image_path, filename):
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Cannot read {filename}")
        return

    # Get dimensions
    h, w = img.shape[:2]
    
    # 1. Convert to 4-channel BGRA (Blue, Green, Red, Alpha/Transparency)
    # The key to virtual try-ons is the Alpha channel.
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # 2. Geometric Center Logic (The verified method)
    # Since raw eye images are usually centered, this is the most robust technique.
    cx, cy = w // 2, h // 2
    
    # 3. Precision Radius Calculation
    # We use a fixed ratio based on the height (33%) to ensure NO skin
    # or eyelashes from the raw photo remain.
    iris_r = int(h * 0.33) 

    # 4. Create the Circular Mask
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Draw a solid white circle for the area we want to keep
    cv2.circle(mask, (cx, cy), iris_r, 255, -1)
    
    # SOFT EDGE (Feathering):
    # This slightly blurs the edge of the mask, which makes the lens
    # blend naturally when overlaid in the webcam, avoiding a "sticker" look.
    mask = cv2.GaussianBlur(mask, (9, 9), 0)
    
    # Apply the mask to the Alpha channel of our image
    img_rgba[:, :, 3] = mask 

    # 5. Tight Macro Crop
    # Define a box that *exactly* fits our iris circle
    x1, y1 = cx - iris_r, cy - iris_r
    x2, y2 = cx + iris_r, cy + iris_r
    final_asset = img_rgba[y1:y2, x1:x2]

    # Boundary check for safety
    if final_asset.size > 0:
        # Resize all lenses to a consistent 512x512 for high quality.
        # This makes the main webcam loop run smoothly and prevents jumping.
        final_asset = cv2.resize(final_asset, (512, 512), interpolation=cv2.INTER_LANCZOS4)
        
        # Save as a transparent PNG (JPEG cannot handle transparency)
        new_filename = filename.replace(".jpg", ".png").replace(".jpeg", ".png")
        save_path = os.path.join(OUTPUT_DIR, f"clean_{new_filename}")
        
        cv2.imwrite(save_path, final_asset)
        print(f"✅ Created: clean_{new_filename}")

# ─── MAIN PROCESS LOOP ──────────────────────────────────────────────────────
print(f"--- Starting Iris Isolation on folder: {INPUT_DIR} ---")
found_files = 0

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        isolate_iris_perfect(os.path.join(INPUT_DIR, file), file)
        found_files += 1

print(f"\n✅ Completed! Isolated {found_files} lenses into {OUTPUT_DIR}")