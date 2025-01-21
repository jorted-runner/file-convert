from fpdf import FPDF
import os

class Utils:
   
    def fetch_all_files(self, folder_save_point):
        target_files = []
        for path, subdirs, files in os.walk(folder_save_point):
            for name in files:
                target_files.append(os.path.join(path, name))
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

class PDF(FPDF):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name