import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO
from openpyxl.styles import PatternFill
from openpyxl import load_workbook

# ---------------- EXCEL EXPORT ----------------
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Applications")

        summary = pd.DataFrame({
            "Metric": ["Total", "Saved", "Applied", "Assessment", "Interview", "Offer", "Rejected"],
            "Count": [
                len(df),
                (df["Status"]=="Saved").sum(),
                (df["Status"]=="Applied").sum(),
                (df["Status"]=="Assessment").sum(),
                (df["Status"]=="Interview").sum(),
                (df["Status"]=="Offer").sum(),
                (df["Status"]=="Rejected").sum(),
            ]
        })

        summary.to_excel(writer, index=False, sheet_name="Summary")

    output.seek(0)
    wb = load_workbook(output)
    ws = wb["Summary"]

    color_map = {
        "Saved": "ADD8E6",
        "Applied": "FFA500",
        "Assessment": "FFFF00",
        "Interview": "00BFFF",
        "Offer": "90EE90",
        "Rejected": "FF7F7F"
    }

    for row in ws.iter_rows(min_row=2, max_row=8, min_col=1, max_col=2):
        metric = row[0].value
        if metric in color_map:
            fill = PatternFill(start_color=color_map[metric], end_color=color_map[metric], fill_type="solid")
            for cell in row:
                cell.fill = fill

    final_output = BytesIO()
    wb.save(final_output)
    return final_output.getvalue()


# ---------------- PDF EXPORT (FPDF FIXED) ----------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_text_color(0, 0, 180)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 12, txt="Job Applications", ln=True)
    pdf.ln(4)

    # 10 columns width
    col_widths = [
        20,  # ID
        35,  # Company
        45,  # Job Title
        25,  # Country
        20,  # Salary
        20,  # Currency
        20,  # Visa
        60,  # Job URL
        30,  # Application Date
        25   # Status
    ]

    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)

    # Header
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=11)

    # Rows
    for _, row in df.iterrows():
        row_values = [str(v) for v in row]

        heights = []
        for i, value in enumerate(row_values):
            lines = pdf.multi_cell(col_widths[i], 10, value, border=0, split_only=True)
            heights.append(len(lines) * 10)
        max_height = max(heights)

        for i, value in enumerate(row_values):
            pdf.multi_cell(col_widths[i], 10, value, border=1)
        pdf.ln(max_height)

    return pdf.output(dest="S").encode("latin-1", "replace")


# ---------------- WORD EXPORT (NO add_field — FIXED) ----------------
def export_word(df):
    doc = Document()

    # Header
    section = doc.sections[0]
    header = section.header
    header_p = header.paragraphs[0]
    header_p.text = "Smart Job Application Tracker"
    header_p.style.font.name = "Calibri"
    header_p.style.font.size = Pt(12)

    # Footer (FIXED — remove add_field)
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.text = "Page"   # Streamlit Cloud docx version does NOT support add_field()

    footer_p.style.font.name = "Calibri"
    footer_p.style.font.size = Pt(11)

    # Title
    title = doc.add_heading("Job Applications", level=1)
    title.style.font.name = "Calibri"
    title.style.font.size = Pt(20)

    # Table
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.autofit = True
    hdr_cells = table.rows[0].cells

    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
        run = hdr_cells[i].paragraphs[0].runs[0]
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.bold = True

    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, value in enumerate(row):
            row_cells[i].text = str(value)
            run = row_cells[i].paragraphs[0].runs[0]
            run.font.name = "Calibri"
            run.font.size = Pt(11)

    output = BytesIO()
    doc.save(output)
    return output.getvalue()
