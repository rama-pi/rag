import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas that uses a two-pass architecture to dynamically compute 
    the total number of pages and build clean headers/footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip rendering headers/footers on the title cover page
            
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Upper Running Header
        self.drawString(54, 750, "Employee Handbook")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, letter[0]-54, 742)
        
        # Lower Running Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 40, page_text)
        self.drawString(54, 40, "Confidential & Proprietary — All Rights Reserved")
        self.line(54, 55, letter[0]-54, 55)
        
        self.restoreState()


def generate_handbook(output_filename="generated/employee_handbook.pdf"):
    # Ensure destination directories exist
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    # Initialize Document Configuration (0.75-inch standard industrial margins)
    doc = SimpleDocTemplate(
        output_filename, 
        pagesize=letter,
        rightMargin=54, 
        leftMargin=54, 
        topMargin=72, 
        bottomMargin=72,
        title="Employee Handbook"
    )

    styles = getSampleStyleSheet()
    story = []

    # Typography & Style Architecture definitions
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=220
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True  # Prevents heading orphan artifacts at page bottom
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=12
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1A365D")
    )

    # --- 1. COVER PAGE ---
    story.append(Spacer(1, 100))
    story.append(Paragraph("EMPLOYEE HANDBOOK", title_style))
    story.append(Paragraph("Company Guidelines, Policies, and Culture Blueprint", subtitle_style))
    story.append(Spacer(1, 50))

    meta_style = ParagraphStyle('Meta', parent=body_style, alignment=1, textColor=colors.HexColor("#718096"))
    story.append(Paragraph("Published: August 2025<br/>Corporate Version 2.0", meta_style))
    story.append(PageBreak())

    # --- 2. HANDBOOK CONTENT SECTIONS ---
    story.append(Paragraph("1. Welcome & Corporate Culture", h1_style))
    story.append(Paragraph(
        "Welcome to the team! This handbook serves as a primary framework guiding our shared operations, "
        "professional values, and working expectations. We are fundamentally committed to building a cooperative, "
        "highly performant, and secure workspace where all employees can reach their maximal creative limits.", 
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Primary Employment Policies", h1_style))
    story.append(Paragraph(
        "<b>At-Will Framework:</b> Employment with our firm operates completely on an at-will basis. This "
        "denotes that both you or the firm retain the legal authority to conclude the working partnership at "
        "any given moment, with or without explicit justification, and with or without advanced notification.", 
        body_style
    ))
    story.append(Paragraph(
        "<b>Equal Opportunity (EEO):</b> We ensure equal workplace terms for all active personnel and "
        "oncoming candidates without regard to race, skin color, native origin, belief structure, gender balance, "
        "age baseline, physical limitations, or biological genetics.", 
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Standards of Professional Conduct", h1_style))
    story.append(Paragraph(
        "We prioritize maintaining a supportive, risk-free workplace ecosystem. All corporate individuals are "
        "required to interact with external clients, company vendors, and internal colleagues with fundamental "
        "courtesy and dignity. Hostile behavior, harassment, or unsafe practices will result in instant investigation.", 
        body_style
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Time Off & Benefits Matrix", h1_style))
    story.append(Paragraph(
        "Our compensation plans are optimized to support your complete well-being. Full-time personnel are eligible "
        "for unified health coverage, proactive savings accounts, and structured time off.", 
        body_style
    ))

    # Clean structured data matrix table mapping
    data = [
        [Paragraph("Benefit Categories", table_header_style), Paragraph("Eligibility & Framework Parameters", table_header_style)],
        [Paragraph("Paid Time Off (PTO)", body_style), Paragraph("17 standard days per calendar year, accrued incrementally every month.", body_style)],
        [Paragraph("Health & Wellness Plan", body_style), Paragraph("Medical and dental protection opens active on the 1st day of the upcoming month.", body_style)],
        [Paragraph("Retirement Matching", body_style), Paragraph("Up to 4.25% dollar-for-dollar direct matching company allocation options.", body_style)]
    ]
    
    # Combined width mirrors total print field (letter width 612 - 108 margin = 504 pt)
    benefit_table = Table(data, colWidths=[150, 354])
    benefit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F7FAFC")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor("#CBD5E0")),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    
    story.append(Spacer(1, 5))
    story.append(benefit_table)

    # Render Document Block
    doc.build(story, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    generate_handbook()

