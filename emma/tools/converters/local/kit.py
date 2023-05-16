import json
import subprocess
from PIL import Image
import zipfile
import os
import subprocess
import img2pdf
import importlib
import sys


class ToolKit:
    def __init__(self):
        sys.path.append('../amyassistant')
        _localDataTools = importlib.import_module(
            'tools.data.local.kit')

        self.localDataTools = _localDataTools.ToolKit

    def convert_image(input_file, output_file):
        # Open the input image
        with Image.open(input_file) as img:
            # Convert the image format
            img = img.convert("RGB")

            # Save the output image
            img.save(output_file)

    def zipper(file_paths):
        for file_path, zip_path in file_paths:
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                zip_file.write(file_path, arcname=os.path.basename(file_path))

    def unzipper(file_paths, key=None):
        for file_path, extract_path in file_paths:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                if key is not None:
                    zip_file.setpassword(key.encode('utf-8'))
                zip_file.extractall(path=extract_path)

    def to_binary(filename):
        with open(filename, 'rb') as file:
            binary_data = file.read()
        return binary_data

    def unbinary(binary, filename):
        with open(filename, 'wb')as file:
            file.write(binary)

    def convert_to_pdf(input_path, output_path):
        subprocess.run(['unoconv', '-f',
                       'pdf', '-o', output_path, input_path])

    # DocFiles converter 0.1

    def convert_docfile(self, input_file, output_file):
        json_type = 'dict'
        PANDOC_FORMATS = self.localDataTools.json_loader(
            "assets\\json\\extensions.json", json_type)
        # Get the file extension
        input_extension = os.path.splitext(input_file)[1].lstrip('.')
        output_extension = os.path.splitext(output_file)[1].lstrip('.')

        # Check if the input format is supported
        if input_extension not in PANDOC_FORMATS:
            print(f"Error: Input format {input_extension} not supported")
            return

        # Check if the output format is supported
        if output_extension not in PANDOC_FORMATS:
            print(f"Error: Output format {output_extension} not supported")
            return

        # Convert the file
        pandoc_command = f"pandoc --from={PANDOC_FORMATS[input_extension]} --to={PANDOC_FORMATS[output_extension]} {input_file} -o {output_file}"
        subprocess.run(pandoc_command, shell=True)

    # Convert a PDF to an image using img2pdf
    def convert_to_image(input_path, output_path):
        with open(input_path, 'rb') as f:
            pdf_data = f.read()
            image_data = img2pdf.convert_from_bytes(pdf_data)[0].convert('RGB')
            image_data.save(output_path)

    # Resize an image if necessary
    def resize_image(input_path, output_path):
        with Image.open(input_path) as img:
            img = img.resize((800, None), Image.ANTIALIAS)
            img.save(output_path)

    # Convert multiple documents to images
    def convert_documents_to_images(self, input_path, output_path):
        # Create the output folder if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # Convert supported documents to PDFs
        for filename in os.listdir(input_path):
            if self.localDataTools.formatTarget(filename, True) != 0:
                filename = self.localDataTools.filenameTarget(filename)
                input_path = os.path.join(input_path, filename)
                output_path = os.path.join(output_path, filename + '.pdf')
                ToolKit.convert_to_pdf(input_path, output_path)

        # Convert the PDFs to images
        for filename in os.listdir(output_path):
            if filename.endswith('.pdf'):
                input_path = os.path.join(output_path, filename)
                output_path = os.path.join(
                    output_path, filename[:-4] + '.png')
                ToolKit.convert_to_image(input_path, output_path)
                ToolKit.resize_image(output_path, output_path)

    def to_json(data):
        json_data = json.dumps(data)
        return json_data


if __name__ == "__main__":
    pass
