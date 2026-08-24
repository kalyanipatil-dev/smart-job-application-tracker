import pandas as pd
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from io import BytesIO

# ---------------- EXCEL EXPORT (Two Sheets: Applications + Summary) ----------------
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

    return output.getvalue()


# ---------------- PDF EXPORT (Color + Table Format) ----------------
def export_pdf(df):
    pdf = FPDF()
    pdf.add_page()

    # Title (Blue)
    pdf.set_text_color(0, 0, 180)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 12, txt="Job Applications", ln=True)
    pdf.ln(4)

    # Column widths
    col_widths = [35, 45, 25, 20, 20, 25, 60, 25, 25]

    # Header background
    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)

    # Header row
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, fill=True)
    pdf.ln()

    # Rows
    pdf.set_font("Arial", size=11)
    for _, row in df.iterrows():
        for i, value in enumerate(row):
            pdf.cell(col_widths[i], 10, str(value), border=1)
        pdf.ln()

    return pdf.output(dest="S").encode("latin-1", "replace")


# ---------------- WORD EXPORT (Header + Footer + Calibri Table) ----------------
def export_word(df):
    doc = Document()

    # Header
    section = doc.sections[0]
    header = section.header
    header_p = header.paragraphs[0]
    header_p.text = "Smart Job Application Tracker"
    header_p.style.font.name = "Calibri"
    header_p.style.font.size = Pt(12)

    # Footer
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.text = "Page "
    footer_p.add_run().add_field('PAGE')
    footer_p.style.font.name = "Calibri"
    footer_p.style.font.size = Pt(11)

    # Title
    title = doc.add_heading("Job Applications", level=1)
    title.style.font.name = "Calibri"
    title.style.font.size = Pt(20)

    # Table
    table = doc.add_table(rows=1, cols=len(df.columns))
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
