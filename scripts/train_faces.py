#!/usr/bin/env python3
import os
import sys
import subprocess
import pkg_resources
from packaging import version

# 1. VERSION MANAGEMENT SYSTEM
def enforce_versions():
    """Ensure correct package versions are installed"""
    required = {
        'numpy': '1.26.4',
        'opencv-python': '4.11.0.86',
        'dlib': '19.24.0',
        'face-recognition': '1.3.0',
        'Pillow': '10.3.0'
    }

    print("\n=== Verifying Dependencies ===")
    
    # First install numpy 1.26.4 explicitly
    subprocess.call([
        sys.executable, "-m", "pip", "install",
        "numpy==1.26.4",
        "--force-reinstall",
        "--no-cache-dir",
        "--ignore-installed"
    ])
    
    # Then install OpenCV with constraints
    subprocess.call([
        sys.executable, "-m", "pip", "install",
        "opencv-python==4.11.0.86",
        "--no-deps",  # Prevent automatic numpy upgrade
        "--force-reinstall"
    ])
    
    # Verify installations
    for pkg, req_ver in required.items():
        try:
            installed = pkg_resources.get_distribution(pkg).version
            if version.parse(installed) != version.parse(req_ver):
                print(f"ERROR: {pkg} {installed} != required {req_ver}")
                print(f"Fixing with: pip install {pkg}=={req_ver} --force-reinstall")
                subprocess.call([
                    sys.executable, "-m", "pip", "install",
                    f"{pkg}=={req_ver}",
                    "--force-reinstall",
                    "--no-deps"
                ])
        except Exception as e:
            print(f"Error checking {pkg}: {str(e)}")
            sys.exit(1)

    print("Dependencies verified successfully\n")

# 2. IMAGE PROCESSING WITH VERSION AWARE FALLBACKS
def load_image(image_path):
    """Safe image loader with OpenCV/PIL fallback"""
    try:
        # Try with OpenCV first if available
        import cv2
        img = cv2.imread(image_path)
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except:
        pass
    
    # Fallback to PIL
    from PIL import Image
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return np.array(img)
    except Exception as e:
        print(f"Failed to load {image_path}: {str(e)}")
        return None

# 3. MAIN TRAINING FUNCTION
def train_faces():
    enforce_versions()
    
    # Import after version enforcement
    import numpy as np
    import face_recognition
    import pickle
    from tqdm import tqdm
    
    encodings = []
    names = []
    
    print("=== Starting Face Encoding ===")
    
    for person in tqdm(os.listdir("dataset"), desc="Processing"):
        person_dir = os.path.join("dataset", person)
        
        for img_file in tqdm(os.listdir(person_dir), desc=person):
            img_path = os.path.join(person_dir, img_file)
            rgb_img = load_image(img_path)
            
            if rgb_img is None:
                continue
                
            try:
                # Use HOG model for Raspberry Pi compatibility
                face_locs = face_recognition.face_locations(
                    rgb_img,
                    model="hog",
                    number_of_times_to_upsample=1
                )
                
                if face_locs:
                    encodings.extend(face_recognition.face_encodings(
                        rgb_img,
                        face_locs,
                        num_jitters=1
                    ))
                    names.extend([person] * len(face_locs))
                    
            except Exception as e:
                print(f"Error on {img_file}: {str(e)}")
                continue
    
    # Save with protocol 4 for Pi compatibility
    os.makedirs("trained_data", exist_ok=True)
    with open("trained_data/encodings.pkl", "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f, protocol=4)
    
    print(f"\nCompleted! Saved {len(encodings)} face encodings")

if __name__ == "__main__":
    train_faces()
