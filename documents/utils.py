from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os

def generate_quote_pdf(quote):
    # Create filename
    filename = f"quote_{quote.quote_number}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, 'quotes', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Add company header
    elements.append(Paragraph(settings.COMPANY_NAME, title_style))
    elements.append(Paragraph(settings.COMPANY_ADDRESS, normal_style))
    elements.append(Spacer(1, 20))
    
    # Add quote details
    elements.append(Paragraph(f"Quote #{quote.quote_number}", styles['Heading2']))
    elements.append(Paragraph(f"Date: {quote.created_at.strftime('%B %d, %Y')}", normal_style))
    elements.append(Paragraph(f"Client: {quote.client.name}", normal_style))
    elements.append(Paragraph(f"Valid Until: {quote.valid_until.strftime('%B %d, %Y')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Create table data
    data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in quote.items.all():
        data.append([
            item.description,
            str(item.quantity),
            f"${item.unit_price}",
            f"${item.total}"
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    # Add totals
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Subtotal: ${quote.subtotal}", normal_style))
    elements.append(Paragraph(f"Tax ({quote.tax_rate}%): ${quote.tax_amount}", normal_style))
    elements.append(Paragraph(f"Total: ${quote.total_amount}", styles['Heading3']))
    
    # Build PDF
    doc.build(elements)
    
    return f'quotes/{filename}' 