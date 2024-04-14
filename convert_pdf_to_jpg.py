import os
import sys
from pdf2image import convert_from_path

def convert_pdf_folder_to_jpg(folder_path):
    # Define the output folder
    output_folder = os.path.join(folder_path, 'convertedJPGs')

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all PDF files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)
            # Convert the PDF to a list of images
            images = convert_from_path(file_path, dpi=300)

            for i, image in enumerate(images):
                # Construct the output filename (with page number if multiple pages)
                base_filename = os.path.splitext(filename)[0]
                output_filename = f"{base_filename}_page_{i + 1}.jpg"
                output_path = os.path.join(output_folder, output_filename)

                # Save the image
                image.save(output_path, 'JPEG')

    print(f"Conversion complete. JPG files are located in {output_folder}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_pdf_to_jpg.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    convert_pdf_folder_to_jpg(folder_path)
