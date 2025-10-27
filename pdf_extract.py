import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Input and output files
input_pdf = "input.pdf"
output_pdf = "output.pdf"

# Step 1: Extract content from old PDF (ignoring header/footer by position)
doc = fitz.open(input_pdf)
page_contents = []

for page in doc:
    text_blocks = page.get_text("blocks")  # text with positions
    cleaned_text = []
    for block in text_blocks:
        x0, y0, x1, y1, content, *_ = block
        # filter: remove text too close to top (header) or bottom (footer)
        if y0 > 50 and y1 < (page.rect.height - 50):
            cleaned_text.append(content.strip())
    page_contents.append("\n".join(cleaned_text))

doc.close()

# Step 2: Create new PDF with cleaned content
c = canvas.Canvas(output_pdf, pagesize=A4)
width, height = A4

for page_text in page_contents:
    text_obj = c.beginText(50, height - 80)
    text_obj.setFont("Helvetica", 11)
    for line in page_text.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()

c.save()

print(f"New PDF saved as: {output_pdf}")
