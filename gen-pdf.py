# Install reportlab first if you haven't already: pip install reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf(filename="sample_chunking_text.pdf"):
    # Target 1-page geometry with standard 0.75-inch margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom semantic styles for a clean layout
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor("#1A365D"), spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'DocH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor("#2B6CB0"), spaceBefore=12, spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody', parent=styles['BodyText'],
        fontName='Helvetica', fontSize=10.5, leading=15,
        textColor=colors.HexColor("#2D3748"), spaceAfter=8
    )
    
    list_style = ParagraphStyle(
        'DocList', parent=body_style,
        leftIndent=20, spaceAfter=4
    )
    
    story = []
    
    # Chapter 1
    story.append(Paragraph("Chapter 1: The AI Revolution", title_style))
    story.append(Paragraph("The landscape of modern technology changed permanently with the rise of large language models. These systems excel at processing natural language text by breaking it into smaller pieces called tokens for downstream machine learning tasks.", body_style))
    story.append(Spacer(1, 8))
    
    # Section 1.1
    story.append(Paragraph("Section 1.1: Text Chunking Strategies", h2_style))
    story.append(Paragraph("Chunking is a critical preprocessing step in retrieval-augmented generation (RAG) pipelines. Without proper semantic chunking, relevant context is often lost during the embedding and vector database lookup process.", body_style))
    story.append(Paragraph("Here are three primary chunking methods used in engineering:", body_style))
    story.append(Paragraph("• <b>Fixed-size chunking:</b> Splits text by a strict, predetermined character or token count.", list_style))
    story.append(Paragraph("• <b>Recursive chunking:</b> Uses a strict hierarchy of separators to maintain semantic meaning.", list_style))
    story.append(Paragraph("• <b>Document-based chunking:</b> Respects the native layout and structural elements of the file.", list_style))
    story.append(Spacer(1, 8))
    
    # Section 1.2
    story.append(Paragraph("Section 1.2: Recursive Function Mechanics", h2_style))
    story.append(Paragraph("If a text chunk exceeds the maximum character threshold, the recursive function calls itself on that slice. It then attempts to split the substring using the next logical delimiter in the pre-configured sequence.", body_style))
    story.append(Paragraph("This structural approach ensures that paragraphs stay intact whenever possible. If paragraphs are too large, sentences are preserved, followed by individual words, preventing broken text strings.", body_style))
    
    doc.build(story)
    print(f"File successfully created: {filename}")

if __name__ == "__main__":
    create_pdf()

