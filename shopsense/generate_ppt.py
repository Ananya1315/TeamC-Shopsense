from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import os

# ── Palette ────────────────────────────────────────────────────────────────────
DARK_NAVY   = RGBColor(0x0D, 0x1B, 0x2A)
MID_BLUE    = RGBColor(0x16, 0x3A, 0x5C)
TEAL        = RGBColor(0x10, 0xB9, 0x81)
TEAL_LIGHT  = RGBColor(0x6E, 0xE7, 0xC0)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
SLATE       = RGBColor(0xCB, 0xD5, 0xE1)
YELLOW      = RGBColor(0xFB, 0xBF, 0x24)
CARD_DARK   = RGBColor(0x0F, 0x2C, 0x47)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

# Safe content area constants — used on every content slide
TITLE_TOP   = Inches(0.30)   # Where title starts
CONTENT_TOP = Inches(1.75)   # Where body content starts (below title+subtitle)
LEFT_MARGIN = Inches(0.55)
LEFT_COL_W  = Inches(5.75)   # left column width on split slides
RIGHT_COL_L = Inches(6.75)   # right column left edge on split slides
RIGHT_COL_W = Inches(6.30)   # right column width on split slides
SLIDE_BASE  = Inches(7.10)   # safe bottom boundary for content

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


# ── Helpers ───────────────────────────────────────────────────────────────────

def rect(slide, l, t, w, h, fill=None, line=None, line_w=Pt(0)):
    s = slide.shapes.add_shape(1, l, t, w, h)
    s.line.width = line_w
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = line
    else:
        s.line.fill.background()
    return s


def tb(slide, text, l, t, w, h,
       size=Pt(22), bold=False, color=WHITE,
       align=PP_ALIGN.LEFT, italic=False, font="Calibri"):
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name   = font
    r.font.size   = size
    r.font.bold   = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return txb


def bullets(slide, items, l, t, w, h,
            size=Pt(22), color=SLATE, dot_color=TEAL, line_gap=Pt(9)):
    """Render a bullet list with consistent spacing. line_gap controls space_after each item."""
    txb = slide.shapes.add_textbox(l, t, w, h)
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after  = line_gap
        p.space_before = Pt(3)
        is_sub = item.startswith("  ")
        stripped = item.strip()
        dot = p.add_run()
        dot.text = "  ›  " if is_sub else "●  "
        dot.font.name  = "Calibri"
        dot.font.size  = size
        dot.font.color.rgb = dot_color
        dot.font.bold  = False
        txt = p.add_run()
        txt.text = stripped
        txt.font.name  = "Calibri"
        txt.font.size  = size
        txt.font.color.rgb = color
        txt.font.bold  = False
    return txb


def screenshot_box(slide, l, t, w, h, label="Screenshot Placeholder"):
    rect(slide, l, t, w, h,
         fill=RGBColor(0x0A, 0x20, 0x35), line=TEAL, line_w=Pt(1.5))
    rect(slide, l + Inches(0.12), t + Inches(0.12),
         w - Inches(0.24), h - Inches(0.24),
         fill=None, line=RGBColor(0x1E, 0x4A, 0x6E), line_w=Pt(0.75))
    tb(slide, "[ Screenshot ]",
       l, t + (h / 2) - Inches(0.48), w, Inches(0.44),
       size=Pt(18), color=RGBColor(0x33, 0x6A, 0x90), align=PP_ALIGN.CENTER)
    tb(slide, label,
       l, t + (h / 2) + Inches(0.04), w, Inches(0.42),
       size=Pt(15), color=RGBColor(0x3B, 0x82, 0xF6),
       align=PP_ALIGN.CENTER, italic=True)


def slide_bg(slide):
    rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill=DARK_NAVY)


def title_block(slide, main_title, subtitle=None, left=None):
    """
    Renders the slide title and optional subtitle.
    NO divider line is drawn.
    Returns the vertical coordinate where body content should begin.
    """
    l = left if left is not None else LEFT_MARGIN
    tb(slide, main_title,
       l, TITLE_TOP, Inches(12.5), Inches(0.88),
       size=Pt(36), bold=True, color=WHITE)
    if subtitle:
        tb(slide, subtitle,
           l, TITLE_TOP + Inches(0.90), Inches(12.5), Inches(0.42),
           size=Pt(20), color=TEAL_LIGHT)
    # Return safe content start — a bit below the title block
    return TITLE_TOP + Inches(0.90 + (0.50 if subtitle else 0.10)) + Inches(0.35)


def section_heading(slide, text, l, t, w, color=TEAL):
    """Small section heading above a bullet list. Returns bottom of heading."""
    tb(slide, text, l, t, w, Inches(0.44),
       size=Pt(23), bold=True, color=color)
    return t + Inches(0.50)   # gap below heading before bullets


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)

rect(s, 0, 0, Inches(0.22), SLIDE_H, fill=TEAL)
rect(s, 0, 0, SLIDE_W, Inches(0.08), fill=TEAL)

# Watermark (behind)
tb(s, "ShopSense", Inches(5.5), Inches(1.9), Inches(8), Inches(3.3),
   size=Pt(110), bold=True, color=RGBColor(0x13, 0x2D, 0x45))

# Infosys badge
rect(s, Inches(0.5), Inches(0.20), Inches(3.6), Inches(0.52),
     fill=RGBColor(0x00, 0x3E, 0x7E), line=WHITE, line_w=Pt(0.5))
tb(s, "Infosys Springboard Project",
   Inches(0.52), Inches(0.22), Inches(3.56), Inches(0.46),
   size=Pt(13), bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Main title
tb(s, "ShopSense",
   Inches(0.5), Inches(1.20), Inches(12), Inches(1.15),
   size=Pt(64), bold=True, color=TEAL)

tb(s, "AI-Powered Multi-Vendor Inventory Analytics Platform",
   Inches(0.5), Inches(2.38), Inches(11), Inches(0.70),
   size=Pt(26), color=WHITE)

# Divider (title slide only — intentional design element)
rect(s, Inches(0.5), Inches(3.18), Inches(7.5), Inches(0.055), fill=TEAL)

tb(s, "Milestone 1 Presentation",
   Inches(0.5), Inches(3.34), Inches(8), Inches(0.55),
   size=Pt(22), bold=True, color=YELLOW)

details = [
    "Backend :  FastAPI  +  PostgreSQL",
    "Frontend :  HTML5  +  CSS3  +  JavaScript",
    "Date :  August 2026",
]
for i, d in enumerate(details):
    tb(s, d, Inches(0.5), Inches(4.04) + Inches(i * 0.52), Inches(9), Inches(0.48),
       size=Pt(19), color=SLATE)

notes(s,
    "Good morning/afternoon. My name is [Name]. This is my Infosys Springboard Milestone 1 presentation "
    "for ShopSense — an AI-Powered Multi-Vendor Inventory Analytics Platform. "
    "It is built using FastAPI, PostgreSQL, and a modern HTML/CSS/JavaScript frontend. "
    "I will walk you through the problem, the architecture, and what we have delivered in Milestone 1.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 2 — PROBLEM STATEMENT & PROJECT OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Problem Statement & Overview",
                 "Why ShopSense was built and what it does")
# ct ≈ 1.75"

# Left column
lh = section_heading(s, "The Problem", LEFT_MARGIN, ct, LEFT_COL_W)
# lh ≈ 2.25"

prob = [
    "No centralized inventory system for vendors",
    "No data isolation — vendors see each other's stock",
    "No admin visibility over the marketplace",
    "Zero demand forecasting — stock-outs happen",
]
bullets(s, prob, LEFT_MARGIN, lh, LEFT_COL_W, Inches(3.0), size=Pt(22))

# Vertical divider
rect(s, Inches(6.52), ct, Inches(0.05), SLIDE_BASE - ct,
     fill=RGBColor(0x1E, 0x4A, 0x6E))

# Right column
rh = section_heading(s, "ShopSense Solution", RIGHT_COL_L, ct, RIGHT_COL_W)

sol = [
    "Role-based portals — Vendor & Admin",
    "Strict per-vendor data isolation (PostgreSQL)",
    "Admin control console with live metrics",
    "ARIMA demand forecasting + AI analytics",
    "Full REST API with Swagger documentation",
]
bullets(s, sol, RIGHT_COL_L, rh, RIGHT_COL_W, Inches(3.5), size=Pt(22))

notes(s,
    "The core problem is that multi-vendor marketplaces have no centralized inventory system, "
    "no vendor data isolation, no admin oversight, and no demand intelligence. "
    "ShopSense addresses all four problems with role-based portals backed by PostgreSQL, "
    "a dedicated admin console, and an AI analytics layer using ARIMA and Gemini.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 3 — MILESTONE 1 OBJECTIVES
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Milestone 1 Objectives",
                 "Six core deliverables targeted for this phase")
# ct ≈ 1.75"

objectives = [
    ("01", "Secure Multi-Vendor Authentication",
     "Vendor registration + login with SHA-256 password hashing in PostgreSQL"),
    ("02", "Vendor Data Isolation",
     "Every vendor sees and manages only their own products via vendor_id filtering"),
    ("03", "Product & Inventory Management",
     "Full CRUD — Add, Edit, Delete products with live stock status tracking"),
    ("04", "Admin Marketplace Dashboard",
     "Admin views all vendors, all products, and revenue metrics from PostgreSQL"),
    ("05", "REST API Development",
     "16 endpoints across Vendors, Admin, Products, Analytics — documented in Swagger"),
    ("06", "AI Analytics Foundation",
     "ARIMA demand forecasting + Gemini LLM sentiment analysis integrated"),
]

card_h  = Inches(1.55)
card_gap = Inches(0.10)
num_w   = Inches(0.65)
card_w  = Inches(5.95)

for i, (num, title, desc) in enumerate(objectives):
    col = i % 2
    row = i // 2
    l = LEFT_MARGIN + col * Inches(6.50)
    t = ct + row * (card_h + card_gap)

    rect(s, l, t + Inches(0.05), num_w, num_w, fill=TEAL)
    tb(s, num, l, t + Inches(0.05), num_w, num_w,
       size=Pt(17), bold=True, color=DARK_NAVY, align=PP_ALIGN.CENTER)

    rect(s, l + num_w + Inches(0.08), t, card_w, card_h,
         fill=CARD_DARK, line=TEAL, line_w=Pt(0.75))
    tb(s, title,
       l + num_w + Inches(0.20), t + Inches(0.10),
       card_w - Inches(0.25), Inches(0.44),
       size=Pt(20), bold=True, color=WHITE)
    tb(s, desc,
       l + num_w + Inches(0.20), t + Inches(0.62),
       card_w - Inches(0.25), Inches(0.85),
       size=Pt(17), color=SLATE)

notes(s,
    "The six objectives for Milestone 1 are: "
    "Secure authentication, vendor data isolation, full product management, "
    "an admin dashboard, 16 REST APIs, and the AI analytics foundation. "
    "All six have been delivered and are live.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 4 — TECHNOLOGY STACK
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Technology Stack",
                 "Technologies powering the complete ShopSense platform")

layers = [
    ("FRONTEND",  MID_BLUE,
     "HTML5  |  Vanilla CSS  |  JavaScript ES6+  |  Fetch API"),
    ("BACKEND",   CARD_DARK,
     "Python 3.11  |  FastAPI  |  Uvicorn (ASGI)  |  Pydantic v2"),
    ("DATABASE",  MID_BLUE,
     "PostgreSQL  |  SQLAlchemy ORM  |  psycopg2  |  SHA-256 Hashing"),
    ("AI / ML",   CARD_DARK,
     "ARIMA (statsmodels)  |  Google Gemini LLM  |  REST Analytics APIs"),
]

layer_h   = Inches(1.22)
layer_gap = Inches(0.10)
label_w   = Inches(1.75)

for i, (label, fill_col, tech) in enumerate(layers):
    t = ct + i * (layer_h + layer_gap)
    # Full row card
    rect(s, LEFT_MARGIN, t, Inches(12.23), layer_h,
         fill=fill_col, line=TEAL, line_w=Pt(0.75))
    # Label pill
    rect(s, LEFT_MARGIN, t, label_w, layer_h, fill=TEAL)
    tb(s, label, LEFT_MARGIN, t, label_w, layer_h,
       size=Pt(13), bold=True, color=DARK_NAVY, align=PP_ALIGN.CENTER)
    # Layer name — matches label text conceptually
    layer_names = {"FRONTEND": "Frontend Layer", "BACKEND": "Backend Layer",
                   "DATABASE": "Database Layer", "AI / ML": "AI & Analytics Layer"}
    tb(s, layer_names[label],
       LEFT_MARGIN + label_w + Inches(0.20), t + Inches(0.10),
       Inches(3.2), Inches(0.42),
       size=Pt(20), bold=True, color=TEAL)
    tb(s, tech,
       LEFT_MARGIN + label_w + Inches(0.20), t + Inches(0.60),
       Inches(10.1), Inches(0.52),
       size=Pt(20), color=WHITE)

notes(s,
    "The technology stack has four layers. "
    "Frontend uses HTML5, CSS3, and JavaScript. "
    "Backend uses Python with FastAPI and Uvicorn. "
    "The database is PostgreSQL with SQLAlchemy ORM and SHA-256 password hashing. "
    "The AI layer uses ARIMA for demand forecasting and Google Gemini for sentiment analysis.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 5 — BACKEND ARCHITECTURE + VS CODE SCREENSHOT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Backend Architecture",
                 "FastAPI project structure and module responsibilities")

# Left column
lh = section_heading(s, "Project Structure", LEFT_MARGIN, ct, LEFT_COL_W)

mods = [
    "main.py — App entry, startup, static file serving",
    "database.py — PostgreSQL connection & sessions",
    "models.py — SQLAlchemy ORM table definitions",
    "routers/ — API endpoint handlers",
    "schemas/ — Pydantic request/response models",
    "crud/ — Database operation functions",
]
bullets(s, mods, LEFT_MARGIN, lh, LEFT_COL_W, Inches(4.20), size=Pt(21))

# Right: screenshot placeholder
ph_top = ct
ph_h   = SLIDE_BASE - ph_top
screenshot_box(s, RIGHT_COL_L, ph_top, RIGHT_COL_W, ph_h,
               "VS Code — Backend File Structure")

notes(s,
    "The backend is structured into clearly separated modules. "
    "main.py bootstraps the app and serves static files. database.py manages the connection. "
    "models.py defines ORM tables. routers handle API endpoints. "
    "schemas validate data. crud performs database operations.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 6 — DATABASE DESIGN + pgAdmin SCREENSHOT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Database Design",
                 "PostgreSQL schema — tables, columns and relationships")

# Left column
lh = section_heading(s, "PostgreSQL Tables (5)", LEFT_MARGIN, ct, LEFT_COL_W)

db_items = [
    "vendors — Store name, owner, email, hashed password",
    "products — Name, price, stock, category, vendor_id (FK)",
    "transactions — Sale records linked to product & vendor",
    "reviews — Customer reviews with rating and sentiment",
    "admins — Admin credentials (separate from vendors)",
]
bullets(s, db_items, LEFT_MARGIN, lh, LEFT_COL_W, Inches(3.30), size=Pt(21))

# Key relationship box — positioned with a safe gap after bullets
# bullets end ≈ lh + 3.30 = ~5.35"; leave 0.22" gap
rel_top = lh + Inches(3.40)
rect(s, LEFT_MARGIN, rel_top, LEFT_COL_W, Inches(1.20),
     fill=CARD_DARK, line=TEAL, line_w=Pt(1))
tb(s, "Key Relationship",
   LEFT_MARGIN + Inches(0.16), rel_top + Inches(0.10), LEFT_COL_W - Inches(0.22), Inches(0.40),
   size=Pt(19), bold=True, color=TEAL)
tb(s, "vendors (1) ──── products (many)\nvendor_id foreign key enforces data isolation",
   LEFT_MARGIN + Inches(0.16), rel_top + Inches(0.54), LEFT_COL_W - Inches(0.22), Inches(0.58),
   size=Pt(18), color=SLATE)

# Right: screenshot placeholder
ph_top = ct
ph_h   = SLIDE_BASE - ph_top
screenshot_box(s, RIGHT_COL_L, ph_top, RIGHT_COL_W, ph_h,
               "pgAdmin — Tables: vendors, products, reviews, transactions")

notes(s,
    "The PostgreSQL database has five tables. "
    "The vendors table stores store name, owner name, hashed password, and account status. "
    "The products table has a vendor_id foreign key that links every product to its vendor — this enforces data isolation. "
    "Transactions and reviews are linked to products. The admins table is separate from vendors.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 7 — REST APIs + SWAGGER SCREENSHOT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "REST API Development",
                 "16 endpoints built with FastAPI, documented in Swagger UI")

# Left column — two sub-sections
lh = section_heading(s, "API Modules", LEFT_MARGIN, ct, LEFT_COL_W)

api_groups = [
    "Vendors — Register, Login, Get All",
    "Admin — Dashboard metrics, Vendor management",
    "Products — Full CRUD (filtered by vendor_id)",
    "Analytics — ARIMA Forecast, Gemini Sentiment",
]
bullets(s, api_groups, LEFT_MARGIN, lh, LEFT_COL_W, Inches(2.10), size=Pt(21))

# Second section — key endpoints
# API groups bullets end ≈ lh + 2.10; leave 0.28" gap
ep_head_top = lh + Inches(2.20)
eh = section_heading(s, "Key Endpoints", LEFT_MARGIN, ep_head_top, LEFT_COL_W)

endpoints = [
    "POST /vendors/register — New vendor signup",
    "POST /vendors/login — Auth (404 / 401 errors)",
    "GET  /admin/dashboard — Marketplace metrics",
    "GET  /admin/products — All products + vendor name",
    "GET  /analytics/forecast/{id} — ARIMA forecast",
]
bullets(s, endpoints, LEFT_MARGIN, eh, LEFT_COL_W, Inches(2.30), size=Pt(19))

# Right: screenshot placeholder
ph_top = ct
ph_h   = SLIDE_BASE - ph_top
screenshot_box(s, RIGHT_COL_L, ph_top, RIGHT_COL_W, ph_h,
               "Swagger UI at http://127.0.0.1:8000/docs")

notes(s,
    "ShopSense has 16 REST API endpoints across four modules. "
    "The Vendor module handles registration and login. "
    "The Admin module provides dashboard metrics and vendor management. "
    "The Products module has full CRUD filtered by vendor_id. "
    "The Analytics module provides ARIMA forecasting and Gemini sentiment analysis.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 8 — VENDOR DASHBOARD + SCREENSHOT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Vendor Dashboard",
                 "Isolated workspace — each vendor manages their own store")

# Left column
lh = section_heading(s, "Vendor Workspace Features", LEFT_MARGIN, ct, LEFT_COL_W)

vendor_f = [
    "Inventory Health Summary — Available / Low / Out of Stock",
    "Add, Edit, Delete products with image support",
    "Search, Category filter, and Price/Stock sorting",
    "Analytics — ARIMA Forecast + Gemini AI Sentiment",
    "Media Library and Settings panel",
]
bullets(s, vendor_f, LEFT_MARGIN, lh, LEFT_COL_W, Inches(3.00), size=Pt(21))

# Auth box — positioned with gap after bullets
auth_top = lh + Inches(3.10)
rect(s, LEFT_MARGIN, auth_top, LEFT_COL_W, Inches(1.20),
     fill=CARD_DARK, line=TEAL, line_w=Pt(1))
tb(s, "Authentication & Isolation",
   LEFT_MARGIN + Inches(0.16), auth_top + Inches(0.10),
   LEFT_COL_W - Inches(0.22), Inches(0.40),
   size=Pt(19), bold=True, color=TEAL)
tb(s, "Vendor A NEVER sees Vendor B's products.\nAll data filtered by vendor_id in PostgreSQL.",
   LEFT_MARGIN + Inches(0.16), auth_top + Inches(0.54),
   LEFT_COL_W - Inches(0.22), Inches(0.58),
   size=Pt(18), color=SLATE)

# Right: screenshot placeholder
ph_top = ct
ph_h   = SLIDE_BASE - ph_top
screenshot_box(s, RIGHT_COL_L, ph_top, RIGHT_COL_W, ph_h,
               "Vendor Dashboard — Inventory Health + Product Table")

notes(s,
    "The Vendor Dashboard is a role-based workspace. "
    "After login, each vendor sees only their own products fetched from PostgreSQL using their vendor_id. "
    "The Inventory Health Summary shows available stock, low stock warnings, and out-of-stock alerts. "
    "Vendors can add, edit, delete products, search the catalog, filter by category, and sort by price or stock.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 9 — ADMIN DASHBOARD + SCREENSHOT
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Admin Control Console",
                 "Marketplace oversight — all vendors, products and revenue in one view")

# Left column
lh = section_heading(s, "Admin Dashboard Features", LEFT_MARGIN, ct, LEFT_COL_W)

admin_f = [
    "Live metrics — Total Vendors, Products, Revenue",
    "Registered Vendors table — Enable / Disable / Delete",
    "Global Marketplace Catalog — all products with Vendor Name",
    "Stock Value and Low Stock alerts across all vendors",
    "Admin cannot add products — read & manage only",
]
bullets(s, admin_f, LEFT_MARGIN, lh, LEFT_COL_W, Inches(3.00), size=Pt(21))

# Key note box
note_top = lh + Inches(3.10)
rect(s, LEFT_MARGIN, note_top, LEFT_COL_W, Inches(1.20),
     fill=CARD_DARK, line=YELLOW, line_w=Pt(1))
tb(s, "Completely Separate from Vendor Portal",
   LEFT_MARGIN + Inches(0.16), note_top + Inches(0.10),
   LEFT_COL_W - Inches(0.22), Inches(0.40),
   size=Pt(19), bold=True, color=YELLOW)
tb(s, "Admin login uses predefined credentials.\nDifferent UI, different data, different role.",
   LEFT_MARGIN + Inches(0.16), note_top + Inches(0.54),
   LEFT_COL_W - Inches(0.22), Inches(0.58),
   size=Pt(18), color=SLATE)

# Right: screenshot placeholder
ph_top = ct
ph_h   = SLIDE_BASE - ph_top
screenshot_box(s, RIGHT_COL_L, ph_top, RIGHT_COL_W, ph_h,
               "Admin Control Console — Vendor Management + Products Table")

notes(s,
    "The Admin Control Console is completely separate from the Vendor workspace. "
    "Admin logs in with predefined admin credentials. "
    "The dashboard shows live metrics — total vendors, total products, total revenue, and stock value — all from PostgreSQL. "
    "The vendor management table allows admin to enable, disable, or delete any vendor account. "
    "Deleting a vendor automatically removes all their products, reviews, and transactions.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 10 — KEY ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Milestone 1 Key Achievements",
                 "Everything delivered and verified in this milestone")

achievements = [
    ("01", "Authentication",
     "SHA-256 hashed passwords, 404 / 401 error responses, immediate login after registration"),
    ("02", "Data Isolation",
     "vendor_id filtered queries — Vendor A never sees Vendor B's data"),
    ("03", "Inventory Management",
     "Full CRUD with stock status: Available / Low Stock / Out of Stock Warning"),
    ("04", "Admin Console",
     "Live vendor, product and revenue data from PostgreSQL. Cascade delete supported."),
    ("05", "16 REST APIs",
     "Swagger-documented endpoints across Vendors, Admin, Products, Analytics modules"),
    ("06", "Unified Launch",
     "uvicorn main:app --reload  →  http://127.0.0.1:8000/  serves full application"),
]

card_h  = Inches(1.52)
card_gap = Inches(0.10)
num_w   = Inches(0.65)
card_w  = Inches(5.95)

for i, (num, title, desc) in enumerate(achievements):
    col = i % 2
    row = i // 2
    l = LEFT_MARGIN + col * Inches(6.50)
    t = ct + row * (card_h + card_gap)

    rect(s, l, t + Inches(0.05), num_w, num_w, fill=TEAL)
    tb(s, num, l, t + Inches(0.05), num_w, num_w,
       size=Pt(16), bold=True, color=DARK_NAVY, align=PP_ALIGN.CENTER)

    rect(s, l + num_w + Inches(0.08), t, card_w, card_h,
         fill=CARD_DARK, line=TEAL, line_w=Pt(0.75))
    tb(s, title,
       l + num_w + Inches(0.20), t + Inches(0.10),
       card_w - Inches(0.25), Inches(0.42),
       size=Pt(20), bold=True, color=WHITE)
    tb(s, desc,
       l + num_w + Inches(0.20), t + Inches(0.60),
       card_w - Inches(0.25), Inches(0.85),
       size=Pt(17), color=SLATE)

notes(s,
    "In Milestone 1 we delivered six things: "
    "secure authentication, strict vendor data isolation, full inventory management, "
    "an admin console with live PostgreSQL data, 16 documented REST APIs, "
    "and unified launch via a single uvicorn command.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 11 — FUTURE ENHANCEMENTS
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
ct = title_block(s, "Future Enhancements",
                 "Planned additions for Milestone 2 and beyond")

future = [
    ("Advanced AI Analytics",
     "Full ARIMA model trained on real transaction data.\nGemini LLM integration for actual customer review analysis."),
    ("Automated Notifications",
     "Email alerts to vendors when stock falls below threshold.\nOrder confirmation and shipping notifications."),
    ("Payment Gateway",
     "Razorpay / Stripe integration for vendor transactions and order payments."),
    ("Mobile-Responsive UI",
     "Fully responsive design optimized for mobile and tablet screen sizes."),
    ("Downloadable Reports",
     "PDF and Excel exports for vendor inventory reports and admin analytics."),
]

card_h  = Inches(1.52)
card_gap = Inches(0.10)

# 4 cards in 2×2, then 1 full-width card below
for i in range(4):
    col = i % 2
    row = i // 2
    title_txt, desc_txt = future[i]
    l = LEFT_MARGIN + col * Inches(6.50)
    t = ct + row * (card_h + card_gap)
    w = Inches(6.10)
    rect(s, l, t, w, card_h, fill=CARD_DARK, line=TEAL, line_w=Pt(0.75))
    tb(s, title_txt, l + Inches(0.18), t + Inches(0.10), w - Inches(0.28), Inches(0.42),
       size=Pt(21), bold=True, color=TEAL)
    tb(s, desc_txt, l + Inches(0.18), t + Inches(0.60), w - Inches(0.28), Inches(0.84),
       size=Pt(18), color=SLATE)

# Full-width bottom card
last_t = ct + 2 * (card_h + card_gap)
title_txt, desc_txt = future[4]
rect(s, LEFT_MARGIN, last_t, Inches(12.23), card_h,
     fill=CARD_DARK, line=TEAL, line_w=Pt(0.75))
tb(s, title_txt, LEFT_MARGIN + Inches(0.18), last_t + Inches(0.10),
   Inches(12.0), Inches(0.42),
   size=Pt(21), bold=True, color=TEAL)
tb(s, desc_txt, LEFT_MARGIN + Inches(0.18), last_t + Inches(0.60),
   Inches(12.0), Inches(0.84),
   size=Pt(18), color=SLATE)

notes(s,
    "For Milestone 2, we plan five major enhancements: "
    "fully trained ARIMA model and live Gemini LLM integration, "
    "automated email notifications for low stock and orders, "
    "a payment gateway integration, a fully responsive mobile UI, "
    "and downloadable PDF and Excel reports.")


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 12 — THANK YOU
# ══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)

rect(s, 0, 0, SLIDE_W, Inches(0.1), fill=TEAL)
rect(s, 0, SLIDE_H - Inches(0.1), SLIDE_W, Inches(0.1), fill=TEAL)

# Watermark
tb(s, "ShopSense", Inches(1.5), Inches(1.5), Inches(10), Inches(3.5),
   size=Pt(110), bold=True, color=RGBColor(0x13, 0x2D, 0x45))

tb(s, "Thank You",
   Inches(0.5), Inches(1.55), Inches(12.3), Inches(1.25),
   size=Pt(62), bold=True, color=TEAL, align=PP_ALIGN.CENTER)

# Horizontal accent — this is an intentional design element on the closing slide
rect(s, Inches(4.0), Inches(2.92), Inches(5.3), Inches(0.06), fill=TEAL)

tb(s, "Open for Questions & Feedback",
   Inches(0.5), Inches(3.08), Inches(12.3), Inches(0.62),
   size=Pt(26), color=WHITE, align=PP_ALIGN.CENTER)

rect(s, Inches(2.5), Inches(3.90), Inches(8.3), Inches(2.40),
     fill=CARD_DARK, line=TEAL, line_w=Pt(1))
tb(s, "Milestone 1 Summary",
   Inches(2.65), Inches(4.02), Inches(8.0), Inches(0.44),
   size=Pt(22), bold=True, color=TEAL, align=PP_ALIGN.CENTER)

summary_lines = [
    "Backend: FastAPI + PostgreSQL   |   Frontend: HTML + CSS + JS",
    "16 REST APIs   |   2 Portals (Vendor + Admin)   |   AI Analytics",
    "Run: uvicorn main:app --reload      Open: http://127.0.0.1:8000/",
]
for i, line in enumerate(summary_lines):
    tb(s, line,
       Inches(2.65), Inches(4.58) + Inches(i * 0.52), Inches(8.0), Inches(0.48),
       size=Pt(18), color=SLATE, align=PP_ALIGN.CENTER)

tb(s, "Infosys Springboard  |  ShopSense – AI-Powered Multi-Vendor Inventory Analytics Platform",
   Inches(0.5), Inches(6.82), Inches(12.3), Inches(0.44),
   size=Pt(14), color=RGBColor(0x4A, 0x6F, 0x8A), align=PP_ALIGN.CENTER)

notes(s,
    "That concludes my Milestone 1 presentation for ShopSense. "
    "We have built a fully operational multi-vendor marketplace with FastAPI, PostgreSQL, and a modern frontend. "
    "The application launches with a single command and includes 16 REST APIs, role-based portals, "
    "secure authentication, vendor data isolation, an admin console, and an AI analytics foundation. "
    "Thank you, and I am happy to take any questions.")


# ── Save ───────────────────────────────────────────────────────────────────────
output_path = os.path.join(os.path.dirname(__file__), "ShopSense_Milestone1_Final.pptx")
prs.save(output_path)
print("Saved: " + output_path)
print("Total slides: 12")
