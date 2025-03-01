from PIL import Image, ImageOps
import os
import logging

# Set up logging
logging.basicConfig(filename="resize_errors.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

def resize_and_pad(image_path, output_path, target_size=(768, 768)):
    """Resize image to fit within target_size while maintaining aspect ratio and padding."""
    try:
        img = Image.open(image_path).convert("RGB")

        # Resize while keeping aspect ratio
        img.thumbnail(target_size, Image.Resampling.LANCZOS)  # FIX: Replaced ANTIALIAS

        # Create a new blank white image and paste the resized image onto it (centered)
        new_img = Image.new("RGB", target_size, (255, 255, 255))  # Use (0,0,0) for black padding
        paste_x = (target_size[0] - img.size[0]) // 2
        paste_y = (target_size[1] - img.size[1]) // 2
        new_img.paste(img, (paste_x, paste_y))

        # Save the resized image
        new_img.save(output_path, "JPEG")
    except Exception as e:
        logging.error(f"Failed to process {image_path}: {e}")

# Folder Paths
input_folder = "Data"
output_folder = "Formatted_Data"
os.makedirs(output_folder, exist_ok=True)

# Get list of image files
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
total_images = len(image_files)

if total_images == 0:
    print("No images found in Data/ directory.")
    exit()

# Progress Tracker
progress_intervals = [int(total_images * (i / 10)) for i in range(1, 11)]  # 10% increments
progress_count = 0

# Process Images
for index, file in enumerate(image_files):
    input_path = os.path.join(input_folder, file)
    output_path = os.path.join(output_folder, file)
    resize_and_pad(input_path, output_path)

    # Update Progress Bar
    progress_count += 1
    if progress_count in progress_intervals:
        percentage = (progress_intervals.index(progress_count) + 1) * 10
        print(f"Progress: {percentage}% completed...")

print("✅ Image formatting complete! Check `Formatted_Data/` for resized images.")
print("🔍 If any images failed, check `resize_errors.log` for details.")
