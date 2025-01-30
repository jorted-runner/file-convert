import pillow_heif
from fpdf import FPDF
from PIL import Image

import os
import platform

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
    
    def image_to_pdf(self, dir, file_name, file_extension):
        og_path = os.path.join(dir, file_name + file_extension)
        converted = os.path.join(dir, file_name + ".pdf")

        # Open image and get original dimensions
        with Image.open(og_path) as img:
            img_width, img_height = img.size

        # Convert image dimensions from pixels to points (assuming 300 DPI)
        img_width_pts = img_width * 72 / 300
        img_height_pts = img_height * 72 / 300

        # Standard letter size in points (8.5x11 inches)
        page_width = 8.5 * 72
        page_height = 11 * 72

        # Scale image to fit within the page while maintaining aspect ratio
        scale_factor = min(page_width / img_width_pts, page_height / img_height_pts)
        new_width_pts = img_width_pts * scale_factor
        new_height_pts = img_height_pts * scale_factor

        # Calculate centered position
        x_offset = (page_width - new_width_pts) / 2
        y_offset = (page_height - new_height_pts) / 2

        # Create a PDF and add the scaled image
        pdf = FPDF(unit="pt", format=[page_width, page_height])
        pdf.add_page()
        pdf.image(og_path, x=x_offset, y=y_offset, w=new_width_pts, h=new_height_pts)
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

    def convert_docx_to_pdf(self, input_path, output_path):
        # Determine the operating system
        system = platform.system()
        
        if system == "Darwin":  # macOS is identified as "Darwin" in platform.system()
            import subprocess
            try:
                subprocess.run(
                    ['soffice', '--headless', '--convert-to', 'pdf', input_path, '--outdir', output_path.rsplit('/', 1)[0]],
                    check=True
                )
                print(f"File converted successfully: {output_path}")
            except Exception as e:
                print(f"Error converting file on mac: {e}")
        elif system == "Windows":  # Windows
            import comtypes.client
            try:
                word = comtypes.client.CreateObject('Word.Application')
                word.Visible = False
                doc = word.Documents.Open(input_path)
                doc.SaveAs(output_path, FileFormat=17)  # FileFormat=17 is PDF
                doc.Close()
                word.Quit()
                print(f"File converted successfully: {output_path}")
            except Exception as e:
                print(f"Error converting file on windows: {e}")
        else:
            print(f"Unsupported operating system: {system}")


class PDF(FPDF):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
