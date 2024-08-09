import os
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageFile
from tqdm import tqdm  # Added for progress bar

# Increase the maximum image size limit to avoid decompression bomb errors
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Define default configuration values
DEFAULT_CONFIG = {
    "last_path": "",
    "default_output_path": "output",
    "default_resolution": 1512,
    "sharpen_factor": 1.5,
    "smooth_factor": 1.5,
    "enhance_color_factor": 1.2,
    "enhance_contrast_factor": 1.2,
    "web_max_size_kb": 200,
    "web_quality": 75,
    "reduce_max_resolution": 3840,
}

def load_config():
    # Check if config file exists, if not, create it with default values
    if not os.path.exists(".config.json"):
        save_config(DEFAULT_CONFIG)

    # Load configuration from file
    with open(".config.json", "r") as config_file:
        config = json.load(config_file)

    # Ensure all keys from default config are present
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    return config

def save_config(config):
    with open(".config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)

# Example usage in your main functions
if __name__ == "__main__":
    config = load_config()
    print("Current Settings:")
    for key, value in config.items():
        print(f"{key}: {value}")

def resize_image(image, max_resolution):
    image.thumbnail((max_resolution, max_resolution))
    return image

def apply_image_adjustments(image, config):
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(config["sharpen_factor"])
    image = image.filter(ImageFilter.SMOOTH_MORE)
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(config["enhance_color_factor"])
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(config["enhance_contrast_factor"])
    return image

def compress_image_storage_saving(image_path, output_path, config):
    try:
        img = Image.open(image_path)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')  # Convert to RGB if it has transparency
        img = apply_image_adjustments(img, config)
        img = resize_image(img, config['default_resolution'])
        
        # Save with progress bar
        quality = config['web_quality']
        with tqdm(desc=f'Compressing {os.path.basename(image_path)}', unit='image') as progress_bar:
            while True:
                img.save(output_path, 'JPEG', quality=quality)
                progress_bar.update()
                if os.path.getsize(output_path) <= config['web_max_size_kb'] * 1024 or quality <= 20:
                    break
                quality -= 5

        return True
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return False

def reduce_upscaled_image_size(image_path, output_path, config):
    try:
        img = Image.open(image_path)
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')  # Convert to RGB if it has transparency
        img = apply_image_adjustments(img, config)
        img = resize_image(img, config['reduce_max_resolution'])
        img.save(output_path, 'JPEG', quality=95)
        return True
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return False

def main_menu():
    while True:
        print("Menu:")
        print("1. Optimize for Web")
        print("2. Reduce Upscaled Image Size")
        print("3. Configuration")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            process_images(compress_image_storage_saving, "web_optimized")
        elif choice == '2':
            process_images(reduce_upscaled_image_size, "reduced_upscaled")
        elif choice == '3':
            configure_settings()
        elif choice == '4':
            break
        else:
            print("Invalid option. Please choose a valid option from the menu.")

def process_images(compression_function, output_folder):
    config = load_config()
    source_directory = input(f"Şəkillərin olduğu qovluq ({config['last_path']}): ") or config['last_path']

    if not os.path.isdir(source_directory):
        print("Invalid directory path. Please provide a valid path.")
        return

    config['last_path'] = source_directory
    save_config(config)

    file_list = os.listdir(source_directory)
    image_files = [file for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.heif', '.raw'))]

    output_path = os.path.join(config['default_output_path'], output_folder)
    os.makedirs(output_path, exist_ok=True)

    successful_compressions = []
    unsuccessful_compressions = []

    for image_file in image_files:
        input_path = os.path.join(source_directory, image_file)
        output_file = os.path.join(output_path, image_file)

        success = compression_function(input_path, output_file, config)

        if success:
            successful_compressions.append(image_file)
            print(f'\033[92mCompressed: {image_file}\033[0m')  # Print in green
        else:
            unsuccessful_compressions.append(image_file)
            print(f'\033[91mFailed to compress: {image_file}\033[0m')  # Print in red

    display_counts(len(successful_compressions), len(unsuccessful_compressions))

    with open(os.path.join(output_path, 'compressed.txt'), 'w') as file:
        file.write("Successful:\n")
        for image in successful_compressions:
            file.write(image + '\n')

        file.write("\nUnsuccessful:\n")
        for image in unsuccessful_compressions:
            file.write(image + '\n')

def configure_settings():
    config = load_config()
    print("Current Settings:")
    for key, value in config.items():
        print(f"{key}: {value}")
    
    config['default_output_path'] = input(f"Default output path [{config['default_output_path']}]: ") or config['default_output_path']
    config['default_resolution'] = int(input(f"Default resolution [{config['default_resolution']}]: ") or config['default_resolution'])
    config['sharpen_factor'] = float(input(f"Sharpen factor [{config['sharpen_factor']}]: ") or config['sharpen_factor'])
    config['smooth_factor'] = float(input(f"Smooth factor [{config['smooth_factor']}]: ") or config['smooth_factor'])
    config['enhance_color_factor'] = float(input(f"Enhance color factor [{config['enhance_color_factor']}]: ") or config['enhance_color_factor'])
    config['enhance_contrast_factor'] = float(input(f"Enhance contrast factor [{config['enhance_contrast_factor']}]: ") or config['enhance_contrast_factor'])
    config['web_max_size_kb'] = int(input(f"Max size for web images (KB) [{config['web_max_size_kb']}]: ") or config['web_max_size_kb'])
    config['web_quality'] = int(input(f"Quality for web images [{config['web_quality']}]: ") or config['web_quality'])
    config['reduce_max_resolution'] = int(input(f"Max resolution for reduced upscaled images [{config['reduce_max_resolution']}]: ") or config['reduce_max_resolution'])

    save_config(config)

def display_counts(successful_count, unsuccessful_count):
    total_images = successful_count + unsuccessful_count
    print(f"\nUğurlu: {successful_count}, Uğursuz: {unsuccessful_count}. Ümümi şəkil: {total_images}")

if __name__ == "__main__":
    main_menu()

