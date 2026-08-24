import pandas as pd
from fpdf import FPDF
from docx import Document

# CSV EXPORT
def export_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# EXCEL EXPORT
def export_excel(df):
    return df.to_excel("applications.xlsx", index=False)

# PDF EXPORT
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Job Applications Report", ln=True)

    for index, row in df.iterrows():
        pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)

    return pdf.output(dest="S").encode("latin-1")

# WORD EXPORT
def export_word(df):
    doc = Document()
    doc.add_heading("Job Applications Report", level=1)

    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells

    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col

    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)

    doc.save("applications.docx")
    return open("applications.docx", "rb").read()
