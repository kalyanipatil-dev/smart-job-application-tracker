import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Pt, Inches
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


# ---------------- PDF EXPORT (WORD-STYLE PREMIUM FORMAT) ----------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()

    # Title centered
    pdf.set_text_color(0, 0, 180)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="Smart Job Application Tracker", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, txt="Job Applications", ln=True, align="L")
    pdf.ln(3)

    # Balanced column widths (Word-style)
    col_widths = [
        12,  # ID
        28,  # Company
        45,  # Job Title
        22,  # Country
        18,  # Salary
        18,  # Currency
        15,  # Visa
        60,  # Job URL
        26,  # Application Date
        20   # Status
    ]

    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 8)

    # Header row
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 8, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Arial", size=8)

    # Rows with neat wrapping
    for _, row in df.iterrows():
        row_values = [str(v) for v in row]

        heights = []
        for i, value in enumerate(row_values):
            lines = pdf.multi_cell(col_widths[i], 5, value, border=0, split_only=True)
            heights.append(len(lines) * 5)
        max_height = max(heights)

        for i, value in enumerate(row_values):
            pdf.multi_cell(col_widths[i], 5, value, border=1)
        pdf.ln(max_height)

    return pdf.output(dest="S").encode("latin-1", "replace")


# ---------------- WORD EXPORT (PREMIUM FORMAT) ----------------
def export_word(df):
    doc = Document()

    # Header
    section = doc.sections[0]
    header = section.header
    header_p = header.paragraphs[0]
    header_p.text = "Smart Job Application Tracker"
    header_p.style.font.name = "Calibri"
    header_p.style.font.size = Pt(14)

    # Footer
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.text = "Generated Report"
    footer_p.style.font.name = "Calibri"
    footer_p.style.font.size = Pt(11)

    # Title
    title = doc.add_heading("Job Applications", level=1)
    title.style.font.name = "Calibri"
    title.style.font.size = Pt(22)

    # Table
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"

    # Auto-fit margins
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

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
