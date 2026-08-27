import os
import copy
import pymupdf
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def style_text(tf, is_title=False):
    for p in tf.paragraphs:
        for run in p.runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            if is_title:
                run.font.bold = True

def add_bullet(tf, text, level=0):
    p = tf.add_paragraph()
    p.text = text
    p.level = level
    if p.runs:
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

def set_intro(tf, text):
    tf.text = text
    if tf.paragraphs and tf.paragraphs[0].runs:
        tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

def run():
    prs = Presentation('ShopSense_Milestone1_Final.pptx')
    
    # Store the dark background shape from Slide 1
    bg_element = copy.deepcopy(prs.slides[1].shapes[0].element)
    
    # Delete all slides
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    for slide in slides:
        prs.part.drop_rel(slide.rId)
        xml_slides.remove(slide)
        
    layout_blank = prs.slide_layouts[6]
    layout_1 = prs.slide_layouts[1]
    layout_3 = prs.slide_layouts[3]
    
    # 1. Restore Slides 1-10 from PDF
    pdf_path = r"C:\Users\chimm\.gemini\antigravity\brain\c89b6af1-39be-413b-9129-e3632379a0c3\.user_uploaded\media_1787146833790.pdf"
    doc = pymupdf.open(pdf_path)
    
    for i in range(10): # pages 0 to 9
        page = doc[i]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)) # high res
        img_path = f"temp_slide_{i}.png"
        pix.save(img_path)
        
        slide = prs.slides.add_slide(layout_blank)
        slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
        os.remove(img_path)
        
    doc.close()
    
    # 2. Re-create Milestone 2 slides exactly as they were (without vertical line)
    
    # PAGE 11
    slide11 = prs.slides.add_slide(layout_1)
    slide11.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide11.shapes.title.text = "Milestone 2: Inventory Intelligence & Customer Analytics"
    style_text(slide11.shapes.title.text_frame, is_title=True)
    
    tf11 = slide11.placeholders[1].text_frame
    set_intro(tf11, "Milestone 2 extends the marketplace with real customer transactions and data-driven analytics.")
    bullets_11 = [
        "Extended ShopSense with a customer-facing marketplace and real order flow.",
        "Connected customer purchases with transaction and inventory data.",
        "Added customer segmentation and sales-based product recommendations.",
        "Added AI features for demand forecasting and review sentiment analysis."
    ]
    for b in bullets_11:
        add_bullet(tf11, b, level=0)
        
    # PAGE 12
    slide12 = prs.slides.add_slide(layout_3)
    slide12.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide12.shapes.title.text = "Customer Portal & Transactions"
    style_text(slide12.shapes.title.text_frame, is_title=True)
    
    tf12 = slide12.placeholders[1].text_frame
    set_intro(tf12, "Customer enters basic details to start shopping.")
    bullets_12 = [
        "Browses the marketplace and places an order.",
        "The system stores the transaction automatically.",
        "Product stock is instantly reduced in the PostgreSQL database."
    ]
    for b in bullets_12:
        add_bullet(tf12, b, level=0)

    # PAGE 13
    slide13 = prs.slides.add_slide(layout_3)
    slide13.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide13.shapes.title.text = "Customer Analytics & Segmentation"
    style_text(slide13.shapes.title.text_frame, is_title=True)
    
    tf13 = slide13.placeholders[1].text_frame
    set_intro(tf13, "Customer spending is calculated from transaction history and customers are grouped into:")
    bullets_13 = [
        "High Value: $500+",
        "Regular: $100–$499",
        "Low Value: below $100",
        "Analytics are calculated directly from actual transaction records."
    ]
    for b in bullets_13:
        level = 0 if "Value:" not in b and "Regular:" not in b else 1
        add_bullet(tf13, b, level=level)

    # PAGE 14
    slide14 = prs.slides.add_slide(layout_3)
    slide14.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide14.shapes.title.text = "Gemini Review Sentiment Analysis"
    style_text(slide14.shapes.title.text_frame, is_title=True)
    
    tf14 = slide14.placeholders[1].text_frame
    set_intro(tf14, "Vendor selects a product.")
    bullets_14 = [
        "Enters rating and customer review text.",
        "Gemini AI analyzes the review.",
        "The system returns a sentiment score and identifies positive feedback and pros.",
        "This helps the vendor quickly understand customer opinions."
    ]
    for b in bullets_14:
        add_bullet(tf14, b, level=0)

    # PAGE 15
    slide15 = prs.slides.add_slide(layout_3)
    slide15.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide15.shapes.title.text = "Rule-Based Recommendations & Historical Validation"
    style_text(slide15.shapes.title.text_frame, is_title=True)
    
    tf15 = slide15.placeholders[1].text_frame
    set_intro(tf15, "Product sales are calculated from recorded transaction data.")
    bullets_15 = [
        "Products are ranked based on the quantity sold.",
        "The highest-selling products are shown as recommendations.",
        "Historical/test transaction data was used to verify that the analytics produce the expected results."
    ]
    for b in bullets_15:
        add_bullet(tf15, b, level=0)

    # PAGE 16
    slide16 = prs.slides.add_slide(layout_3)
    slide16.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide16.shapes.title.text = "ARIMA Demand Forecasting"
    style_text(slide16.shapes.title.text_frame, is_title=True)
    
    tf16 = slide16.placeholders[1].text_frame
    set_intro(tf16, "Historical sales data is used to identify demand patterns.")
    bullets_16 = [
        "The vendor selects a product.",
        "ARIMA generates a 7-day demand forecast.",
        "The forecast is compared with current inventory.",
        "A restock alert is shown when expected demand is higher than available stock."
    ]
    for b in bullets_16:
        add_bullet(tf16, b, level=0)

    # PAGE 17
    slide17 = prs.slides.add_slide(layout_3)
    slide17.shapes._spTree.insert(2, copy.deepcopy(bg_element))
    slide17.shapes.title.text = "Milestone 2 Outcome"
    style_text(slide17.shapes.title.text_frame, is_title=True)
    
    tf17 = slide17.placeholders[1].text_frame
    set_intro(tf17, "Customer purchases now generate real transaction data, which feeds the analytics layer. This data is used for customer segmentation, product recommendations, demand forecasting, and review sentiment analysis.")
    bullets_17 = [
        "Real customer ordering and transaction tracking",
        "Data-driven customer segmentation and recommendations",
        "7-day inventory demand forecasting with ARIMA",
        "Gemini-powered review sentiment analysis"
    ]
    for b in bullets_17:
        add_bullet(tf17, b, level=0)
    
    output_path = 'ShopSense_Final_Presentation.pptx'
    prs.save(output_path)
    print(f"Saved {output_path}")

if __name__ == '__main__':
    run()
