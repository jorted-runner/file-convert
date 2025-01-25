import pillow_heif
from fpdf import FPDF
from PIL import Image

import os

class ConvertBrain:
    # Take txt file and convert it PDF
    def txt_to_pdf(self, path, file_name, file_extension):
        og_path = os.path.join(path, file_name + file_extension)
        converted = os.path.join(path, file_name + ".pdf")
        pdf = PDF(file_name)  
        pdf.add_page()
        pdf.add_font('FreeSerif', '', os.path.join('fonts', 'FreeSerif.ttf'), uni=True)
        pdf.set_font("FreeSerif", size = 10)
        f = open(og_path, "r", encoding='utf-8')
        for x in f:
            pdf.multi_cell(w=0, h=5, txt = x, align = 'L')
        pdf.output(converted)
    
    # Convert image file to PDF
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
    
    # Convert HEIC file to JPG
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
