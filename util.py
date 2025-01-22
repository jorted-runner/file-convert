from fpdf import FPDF
from PIL import Image

import os
import pillow_heif

class Utils:
   
    def fetch_all_files(self, folder_save_point):
        target_files = []
        for path, subdirs, files in os.walk(folder_save_point):
            for name in files:
                target_files.append(os.path.join(path, name))
        return target_files
    
    def fetch_all_pdf_files(folder):
        target_files = []
        for file_name in os.listdir(folder):
            if file_name.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder, file_name)):
                target_files.append(os.path.join(folder, file_name))
        return target_files

    def getFileDetails(self, file_path):
        file_name_with_ext = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(file_name_with_ext)
        return file_name, file_extension

    def txt_to_pdf(self, path, file_name, file_extension):
        og_path = os.path.join(path, file_name + file_extension)
        converted = os.path.join(path, file_name + ".pdf")
        pdf = PDF(file_name)  
        pdf.add_page()
        pdf.set_font("Arial", size = 10)
        f = open(og_path, "r", encoding='latin-1')
        for x in f:
            pdf.multi_cell(w=0, h=5, txt = x, align = 'L')
        pdf.output(converted)
    
    def image_to_pdf(dir, file_name, file_extension):
        og_path = os.path.join(dir, file_name + file_extension)
        converted = os.path.join(dir, file_name + ".pdf")
        image = Image.open(og_path)
        image.save(converted, "PDF", resolution=100.0)
        image.close()
    
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