import os
from PIL import Image

def resize_images():
    source_directory = input("Şəkilllərin olduğu qovluq: ")
    max_resolution = int(input("Maksimum ölçü (px): "))

    # Check if the directory exists
    if not os.path.isdir(source_directory):
        print("Invalid directory path. Please provide a valid path.")
        return

    # List all files in the directory
    file_list = os.listdir(source_directory)

    # Filter files to only include image files (extensions can be modified as needed)
    image_files = [file for file in file_list if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]

    successful_resizes = []
    unsuccessful_resizes = []

    for image_file in image_files:
        try:
            # Open the image file
            with Image.open(os.path.join(source_directory, image_file)) as img:
                # Resize the image to have a maximum width or height of max_resolution while maintaining aspect ratio
                img.thumbnail((max_resolution, max_resolution))
                img.save(os.path.join(source_directory, image_file))
                successful_resizes.append(image_file)
                print(f'\033[92mÖlçüləndirildi: {image_file}\033[0m')  # Print in green
        except Exception as e:
            unsuccessful_resizes.append(image_file)
            print(f'\033[91mUğursuz ölçüləndirmə: {image_file} - {e}\033[0m')  # Print in red

    display_counts(len(successful_resizes), len(unsuccessful_resizes))

    # Save results to a text file
    with open('output/resized.txt', 'w') as file:
        file.write("Uğurlu:\n")
        for image in successful_resizes:
            file.write(image + '\n')

        file.write("\nUğursuz:\n")
        for image in unsuccessful_resizes:
            file.write(image + '\n')

# Function to display counts of successful and unsuccessful operations
def display_counts(successful_count, unsuccessful_count):
    total_images = successful_count + unsuccessful_count
    print(f"\nUğurlu: {successful_count}, Uğursuz: {unsuccessful_count}. Ümümi şəkil: {total_images}")

# Call the function to resize images
resize_images()
