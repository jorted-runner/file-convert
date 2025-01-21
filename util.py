from fpdf import FPDF

class Utils:
    def __init__(self) -> None:
        self.PDF = PDF()

    def txt_to_pdf(self, path, file_name, file_extension):
        og_path = path + "\\" + file_name + file_extension
        converted = path + "\\" + file_name + ".pdf"
        pdf = self.PDF(file_name)  
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