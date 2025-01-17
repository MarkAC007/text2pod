"""Create a test PDF file for testing."""
from fpdf import FPDF

def create_sample_pdf():
    """Create a sample PDF with test content."""
    pdf = FPDF()
    
    # Add a page
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add some test content
    pdf.cell(200, 10, txt="Test Document", ln=1, align="C")
    pdf.cell(200, 10, txt="This is a sample PDF file for testing.", ln=1, align="L")
    pdf.cell(200, 10, txt="It contains multiple lines of text", ln=1, align="L")
    pdf.cell(200, 10, txt="to test the text extraction functionality.", ln=1, align="L")
    
    # Save the PDF
    pdf.output("tests/test_files/sample.pdf")

if __name__ == "__main__":
    create_sample_pdf() 