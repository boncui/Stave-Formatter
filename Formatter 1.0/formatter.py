import os
import csv
import logging
import numpy as np
from glob import glob
from PIL import Image, ImageOps, ExifTags
from multiprocessing import Pool
from tqdm import tqdm

# Configure logging (overwrite log file on each run)
logging.basicConfig(
    filename="stave_formatter.log", 
    level=logging.INFO, 
    filemode="w",  # 'w' ensures log is cleared at each run
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def resize_with_padding(img, target_size=(768, 768)):
    """Resize image while maintaining aspect ratio using padding."""
    img.thumbnail(target_size, Image.ANTIALIAS)
    delta_w = target_size[0] - img.size[0]
    delta_h = target_size[1] - img.size[1]
    padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))
    return ImageOps.expand(img, padding, fill="black")

def correct_orientation(img):
    """Correct image orientation based on EXIF data without cropping."""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                img = img.rotate(180, expand=False)  # No cropping
            elif orientation == 6:
                img = img.rotate(270, expand=False)  # No cropping
            elif orientation == 8:
                img = img.rotate(90, expand=False)  # No cropping
    except (AttributeError, KeyError, IndexError):
        pass  # Image has no EXIF orientation data
    return img

def preprocess_image(img_path, output_dir, grayscale=False):
    """Preprocess a single image."""
    try:
        img = Image.open(img_path).convert("RGB")  # Ensure RGB mode
        img = correct_orientation(img)
        img = resize_with_padding(img)
        if grayscale:
            img = img.convert("L")
        img_array = np.array(img) / 255.0  # Normalize pixel values
        img_name = os.path.basename(img_path).split('.')[0] + ".jpg"
        img.save(os.path.join(output_dir, img_name), "JPEG")
        logging.info(f"Processed {img_path}")
        return img_name
    except Exception as e:
        logging.error(f"Error processing {img_path}: {e}")
        return None

def generate_metadata_csv(output_dir, image_names, stave_counts):
    """Generate a CSV file mapping image names to stave counts."""
    with open(os.path.join(output_dir, "labels.csv"), "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Image Name", "Stave Count"])
        for img_name, count in zip(image_names, stave_counts):
            writer.writerow([img_name, count])

def process_all_images(input_dir, output_dir, grayscale=False):
    """Main function to preprocess all images in a directory using multiprocessing."""
    
    # Fix the path to Data directory
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Data"))
    output_dir = os.path.abspath(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".heic")  # Added HEIC support
    img_paths = [f for f in glob(os.path.join(input_dir, "*")) if f.lower().endswith(valid_extensions)]
    
    # Ignore specific files and folders
    img_paths = [f for f in img_paths if "stave_data_log.csv" not in f and "shit" not in f]

    if not img_paths:
        print(f"No images found in {input_dir}. Exiting.")
        logging.error(f"No images found in {input_dir}. Exiting.")
        return
    
    stave_counts = [150] * len(img_paths)  # Placeholder, replace with actual counts
    total_images = len(img_paths)
    
    image_names = []
    for i, img_path in enumerate(img_paths):
        img_name = preprocess_image(img_path, output_dir, grayscale)
        if img_name:
            image_names.append(img_name)
        
        # Print progress updates at 25% intervals only if total_images >= 4
        if total_images >= 4 and (i + 1) % (total_images // 4) == 0:
            progress = (i + 1) / total_images * 100
            print(f"Processing: {progress:.0f}% complete")
    
    generate_metadata_csv(output_dir, image_names, stave_counts)
    logging.info("Processing complete!")
    logging.shutdown()
    print("Processing complete!")

if __name__ == "__main__":
    process_all_images("Stave Project/Data", "Stave Project/Data", grayscale=False)
