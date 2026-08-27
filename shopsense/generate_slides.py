import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor
from PyPDF2 import PdfReader, PdfWriter

def draw_background(c):
    c.setFillColor(HexColor('#0f172a')) # Dark background matching modern UI
    c.rect(0, 0, 1280, 720, fill=1, stroke=0)
    # Draw top border accent to match theme
    c.setFillColor(HexColor('#10b981'))
    c.rect(0, 715, 1280, 5, fill=1, stroke=0)

def draw_header(c, title, subtitle=None):
    c.setFillColor(HexColor('#ffffff'))
    c.setFont('Helvetica-Bold', 40)
    c.drawString(60, 630, title)
    
    if subtitle:
        c.setFillColor(HexColor('#10b981')) # Emerald green
        c.setFont('Helvetica', 22)
        c.drawString(60, 580, subtitle)

def draw_bullets(c, x, y, bullets, width=540, line_height=35):
    c.setFillColor(HexColor('#e2e8f0'))
    c.setFont('Helvetica', 20)
    current_y = y
    for bullet in bullets:
        words = bullet.split(' ')
        line = '-  ' if not bullet.startswith(' ') else '   '
        if bullet.startswith('  -'):
            line = '      '
            words = bullet.split(' ')[2:]
        elif bullet == '':
            current_y -= (line_height)
            continue
            
        for word in words:
            if c.stringWidth(line + word, 'Helvetica', 20) < width:
                line += word + ' '
            else:
                c.drawString(x, current_y, line)
                current_y -= line_height
                line = '    ' + word + ' '
        c.drawString(x, current_y, line)
        current_y -= (line_height + 15)

def draw_placeholder(c, text, x, y, width, height):
    c.setFillColor(HexColor('#1e293b'))
    c.setStrokeColor(HexColor('#334155'))
    c.rect(x, y, width, height, fill=1, stroke=1)
    
    c.setFillColor(HexColor('#94a3b8'))
    c.setFont('Helvetica', 18)
    text_width = c.stringWidth(text, 'Helvetica', 18)
    
    # Center text in box
    text_x = x + (width - text_width) / 2
    text_y = y + (height / 2) - 6
    c.drawString(text_x, text_y, text)

def create_milestone2_slides():
    c = canvas.Canvas('m2_slides.pdf', pagesize=(1280, 720))
    
    # SLIDE 11
    draw_background(c)
    draw_header(c, 'Milestone 2: Inventory Intelligence & Customer Analytics')
    
    c.setFillColor(HexColor('#e2e8f0'))
    c.setFont('Helvetica', 22)
    intro_text = "This milestone extends the marketplace by adding real customer transactions and turning transaction data into useful analytics and AI-driven insights."
    current_y = 550
    line = ''
    for word in intro_text.split(' '):
        if c.stringWidth(line + word, 'Helvetica', 22) < 1100:
            line += word + ' '
        else:
            c.drawString(60, current_y, line)
            current_y -= 35
            line = word + ' '
    c.drawString(60, current_y, line)
    
    current_y -= 50
    bullets_11 = [
        "Extended ShopSense with a customer-facing marketplace and real order flow.",
        "Connected customer purchases with transaction and inventory data.",
        "Added customer segmentation and sales-based product recommendations.",
        "Added AI features for demand forecasting and review sentiment analysis."
    ]
    draw_bullets(c, 60, current_y, bullets_11, width=1100, line_height=40)
    c.showPage()
    
    # SLIDE 12
    draw_background(c)
    draw_header(c, 'Customer Portal & Transactions')
    bullets_12 = [
        "Customer enters basic details to start shopping.",
        "Browses the marketplace and places an order.",
        "The system stores the transaction automatically.",
        "Product stock is instantly reduced in the PostgreSQL database."
    ]
    draw_bullets(c, 60, 530, bullets_12, width=540, line_height=40)
    draw_placeholder(c, "Insert Customer Portal / Marketplace Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    # SLIDE 13
    draw_background(c)
    draw_header(c, 'Customer Analytics & Segmentation')
    bullets_13 = [
        "Customer spending is calculated directly from actual transaction records.",
        "Customers are automatically grouped into segments based on total spending:",
        "  - High Value: $500+",
        "  - Regular: $100-$499",
        "  - Low Value: below $100",
        "This helps vendors understand who their top buyers are."
    ]
    draw_bullets(c, 60, 530, bullets_13, width=540, line_height=40)
    draw_placeholder(c, "Insert Customer Analytics Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    # SLIDE 14
    draw_background(c)
    draw_header(c, 'Gemini Review Sentiment Analysis')
    bullets_14 = [
        "The vendor selects a product and enters a customer rating and review text.",
        "Gemini AI analyzes the review text.",
        "The system returns a sentiment score and identifies positive feedback or pros.",
        "This helps the vendor quickly understand customer opinions and product reception."
    ]
    draw_bullets(c, 60, 530, bullets_14, width=540, line_height=40)
    draw_placeholder(c, "Insert Gemini Sentiment Analysis Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    # SLIDE 15
    draw_background(c)
    draw_header(c, 'Rule-Based Recommendations & Historical Validation')
    bullets_15 = [
        "Product sales are calculated strictly from genuine transaction records.",
        "Products are ranked based on the quantity sold.",
        "The highest-selling products are automatically displayed as recommendations.",
        "Historical/test transaction data was used to verify that the analytics produce expected, accurate results."
    ]
    draw_bullets(c, 60, 530, bullets_15, width=540, line_height=40)
    draw_placeholder(c, "Insert Recommendation / Historical Validation Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    # SLIDE 16
    draw_background(c)
    draw_header(c, 'ARIMA Demand Forecasting')
    bullets_16 = [
        "Historical sales data is used to identify demand patterns.",
        "The vendor selects a product.",
        "An ARIMA model generates a 7-day demand forecast.",
        "The forecast is compared directly with current inventory levels.",
        "A restock alert is shown when expected demand is higher than available stock."
    ]
    draw_bullets(c, 60, 530, bullets_16, width=540, line_height=40)
    draw_placeholder(c, "Insert ARIMA Forecast Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    # SLIDE 17
    draw_background(c)
    draw_header(c, 'Milestone 2 Outcome')
    
    c.setFillColor(HexColor('#e2e8f0'))
    c.setFont('Helvetica', 22)
    intro_text = "Customer purchases now generate real transaction data, which feeds the analytics layer. This data is used for customer segmentation, product recommendations, demand forecasting, and review sentiment analysis."
    
    current_y = 550
    line = ''
    for word in intro_text.split(' '):
        if c.stringWidth(line + word, 'Helvetica', 22) < 540:
            line += word + ' '
        else:
            c.drawString(60, current_y, line)
            current_y -= 35
            line = word + ' '
    c.drawString(60, current_y, line)
    
    current_y -= 50
    bullets_17 = [
        "Real customer ordering and transaction tracking",
        "Data-driven customer segmentation and recommendations",
        "7-day inventory demand forecasting with ARIMA",
        "Gemini-powered review sentiment analysis"
    ]
    draw_bullets(c, 60, current_y, bullets_17, width=540, line_height=35)
    
    draw_placeholder(c, "Insert Final Analytics Dashboard Screenshot Here", 640, 100, 580, 450)
    c.showPage()
    
    c.save()

def merge_pdfs():
    original_pdf = r'C:\Users\chimm\.gemini\antigravity\brain\c89b6af1-39be-413b-9129-e3632379a0c3\.user_uploaded\media_1787146833790.pdf'
    new_slides = 'm2_slides.pdf'
    output_pdf = 'ShopSense_Final_Presentation.pdf'
    
    reader_orig = PdfReader(original_pdf)
    reader_new = PdfReader(new_slides)
    writer = PdfWriter()
    
    # Append slides 1 to 10 from original (indices 0 to 9)
    for i in range(min(10, len(reader_orig.pages))):
        writer.add_page(reader_orig.pages[i])
        
    # Append all new slides
    for i in range(len(reader_new.pages)):
        writer.add_page(reader_new.pages[i])
        
    with open(output_pdf, 'wb') as f:
        writer.write(f)
        
    print("Successfully generated", output_pdf)

if __name__ == '__main__':
    create_milestone2_slides()
    merge_pdfs()
