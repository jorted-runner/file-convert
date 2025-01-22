from fpdf import FPDF
from PIL import Image

import os
import pillow_heif

class Utils:

    def file_exists(self, file):
        return os.path.isfile(file)
   
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

class PDF(FPDF):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name