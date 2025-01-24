from fpdf import FPDF
from PIL import Image

import os
import json
import pillow_heif
from pathlib import Path

class Utils:

    def file_exists(self, file):
        return os.path.isfile(file)
    
    def dir_exists(self, dir):
        return os.path.isdir(dir)
   
    def fetch_all_files(self, folder):
        target_files = []
        for file_name in os.listdir(folder):
            target_files.append(os.path.join(folder, file_name))
        return target_files
    
    def fetch_all_pdf_files(self, folder):
        target_files = []
        for file_name in os.listdir(folder):
            if file_name.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder, file_name)):
                target_files.append(os.path.join(folder, file_name))
        return target_files

    def get_file_details(self, file_path):
        file_name_with_ext = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(file_name_with_ext)
        return file_name, file_extension

    def txt_to_pdf(self, path, file_name, file_extension):
        og_path = os.path.join(path, file_name + file_extension)
        converted = os.path.join(path, file_name + ".pdf")
        pdf = PDF(file_name)  
        pdf.add_page()
        pdf.add_font('FreeSerif', '', 'fonts/FreeSerif.ttf', uni=True)
        pdf.set_font("FreeSerif", size = 10)
        f = open(og_path, "r", encoding='utf-8')
        for x in f:
            pdf.multi_cell(w=0, h=5, txt = x, align = 'L')
        pdf.output(converted)
    
    def image_to_pdf(self, dir, file_name, file_extension):
        og_path = os.path.join(dir, file_name + file_extension)
        converted = os.path.join(dir, file_name + ".pdf")

        with Image.open(og_path) as img:
            img_width, img_height = img.size
        
        img_width_pts = img_width * 72 / 300
        img_height_pts = img_height * 72 / 300

        # Standard letter size in points (8.5x11 inches)
        page_width = 8.5 * 72
        page_height = 11 * 72

        # Calculate the centered position
        x_offset = (page_width - img_width_pts) / 2
        y_offset = (page_height - img_height_pts) / 2

        # Create a PDF and add the centered image
        pdf = FPDF(unit="pt", format=[page_width, page_height])
        pdf.add_page()
        pdf.image(og_path, x=x_offset, y=y_offset, w=img_width_pts, h=img_height_pts)
        pdf.output(converted)
    
    def convert_heic_to_jpg(self, heic_file, jpg_file):
        heif_file = pillow_heif.read_heif(heic_file)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        image.save(jpg_file, format("jpeg"))

    def sendFile(self, filename, conn):
        try:
            # file metadata
            base_filename = Path(filename).name
            metadata = json.dumps({"filesize": os.path.getsize(filename), "filename": base_filename})
            metadata_length = len(metadata).to_bytes(4, byteorder="big")

            # Send metadata length and metadata
            conn.send(metadata_length)
            conn.send(metadata.encode('utf-8'))

            # Send file content
            with open(filename, 'rb') as f:
                while chunk := f.read(1024):
                    conn.send(chunk)
            print(f"File sent: {filename}")
        except Exception as e:
            print(f"Error in sendFile: {e}")

    def receiveFile(self, conn, save_dir):
        try:
            # Receive metadata length and metadata only
            metadata_length = conn.recv(4)  # Fixed-length header for metadata size
            if not metadata_length:
                raise ValueError("No metadata length received")
            metadata_size = int.from_bytes(metadata_length, byteorder="big")

            metadata = json.loads(conn.recv(metadata_size).decode('utf-8'))
            filesize = metadata['filesize']
            filename = metadata['filename']
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, filename)

            # Receive file content
            with open(filepath, 'wb') as f:
                totalReceived = 0
                while totalReceived < filesize:
                    data = conn.recv(1024)
                    if not data:
                        break
                    totalReceived += len(data)
                    f.write(data)
            print(f"File received: {filepath}")
        except Exception as e:
            print(f"Error in receiveFile: {e}")

class PDF(FPDF):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name