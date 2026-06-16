"""
generate_doc.py
Compiles all project documentation markdown files into a single,
professionally formatted .docx file that can be directly uploaded to Google Docs.
"""

import os
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Face_Recognition_Attendance_System_Blueprint.docx')

# Ordered sequence of documents as they appear in the prompt
DOC_SEQUENCE = [
    ("README.md",                          "Documentation Index"),
    ("project-overview.md",               "Project Overview"),
    ("problem-statement.md",              "Problem Statement"),
    ("objectives-and-goals.md",           "Objectives and Goals"),
    ("stakeholder-analysis.md",           "Stakeholder Analysis"),
    ("user-personas.md",                  "User Personas"),
    ("functional-requirements.md",        "Functional Requirements"),
    ("non-functional-requirements.md",    "Non-Functional Requirements"),
    ("system-specifications.md",          "System Specifications"),
    ("feasibility-study.md",              "Feasibility Study"),
    ("prototype-and-design-specification.md", "Prototype and Design Specification"),
    ("architecture.md",                   "Architecture"),
    ("workflow.md",                       "Workflow"),
    ("features.md",                       "Features"),
    ("user-journeys.md",                  "User Journeys"),
    ("database-design.md",               "Database Design"),
    ("api-documentation.md",             "API Documentation"),
    ("sequence-diagrams.md",             "Sequence Diagrams"),
    ("security-design.md",               "Security Design"),
    ("testing-strategy.md",              "Testing Strategy"),
    ("deployment-guide.md",              "Deployment Guide"),
    ("configuration-guide.md",           "Configuration Guide"),
    ("maintenance-guide.md",             "Maintenance Guide"),
    ("troubleshooting.md",               "Troubleshooting"),
    ("scalability-roadmap.md",           "Scalability Roadmap"),
    ("future-enhancements.md",           "Future Enhancements"),
    ("repository-cleanup-report.md",     "Repository Cleanup Report"),
    ("glossary.md",                      "Glossary"),
]


def set_heading_style(para, level, text):
    """Apply heading colours and fonts."""
    run = para.runs[0] if para.runs else para.add_run(text)
    run.font.name = 'Calibri'
    if level == 0:  # Document title
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif level == 1:
        run.font.size = Pt(20)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    elif level == 2:
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x20, 0x53, 0x8F)
    elif level == 3:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)


def add_separator(doc):
    """Add a horizontal rule."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("─" * 80)
    run.font.size = Pt(7)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)


def parse_and_add_markdown(doc, content):
    """Parse markdown content and add it to the document."""
    in_code_block = False
    code_lines = []

    for line in content.split('\n'):
        stripped = line.rstrip()

        # Code block handling
        if stripped.startswith('```'):
            if in_code_block:
                # End of code block — write accumulated lines
                code_para = doc.add_paragraph()
                code_para.style = 'No Spacing'
                for cl in code_lines:
                    run = code_para.add_run(cl + '\n')
                    run.font.name = 'Courier New'
                    run.font.size = Pt(8)
                    run.font.color.rgb = RGBColor(0x24, 0x29, 0x2e)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Skip mermaid diagram lines (not renderable in .docx easily)
        if stripped.startswith('graph ') or stripped.startswith('sequenceDiagram') or stripped.startswith('erDiagram') or stripped == 'mermaid':
            continue

        # Headings
        if stripped.startswith('#### '):
            p = doc.add_heading(stripped[5:], level=4)
        elif stripped.startswith('### '):
            p = doc.add_heading(stripped[4:], level=3)
            set_heading_style(p, 3, stripped[4:])
        elif stripped.startswith('## '):
            p = doc.add_heading(stripped[3:], level=2)
            set_heading_style(p, 2, stripped[3:])
        elif stripped.startswith('# '):
            p = doc.add_heading(stripped[2:], level=1)
            set_heading_style(p, 1, stripped[2:])
        # Tables (basic)
        elif stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            # Skip separator rows like |---|---|
            if all(re.fullmatch(r':?-+:?', c) for c in cells if c):
                continue
            # Create a single-row table style paragraph
            p = doc.add_paragraph()
            p.style = 'No Spacing'
            run = p.add_run('  '.join(cells))
            run.font.name = 'Courier New'
            run.font.size = Pt(9)
        # Bullet points
        elif stripped.startswith('* ') or stripped.startswith('- '):
            p = doc.add_paragraph(stripped[2:], style='List Bullet')
            p.runs[0].font.size = Pt(10)
        elif re.match(r'^\d+\. ', stripped):
            p = doc.add_paragraph(re.sub(r'^\d+\. ', '', stripped), style='List Number')
            p.runs[0].font.size = Pt(10)
        # Horizontal rules
        elif stripped in ('---', '___', '***'):
            add_separator(doc)
        # Blank lines
        elif stripped == '':
            doc.add_paragraph()
        # Normal paragraph — strip basic markdown bold/italic
        else:
            cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
            cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
            cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
            p = doc.add_paragraph(cleaned)
            p.runs[0].font.size = Pt(10) if p.runs else None


def main():
    doc = Document()

    # ── Cover Page ─────────────────────────────────────────────────────────────
    doc.add_paragraph()
    doc.add_paragraph()
    title = doc.add_heading('Face Recognition-Based\nAttendance System', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.name = 'Calibri'
        run.font.size = Pt(32)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    sub = doc.add_paragraph('Complete Project Blueprint & Documentation Suite')
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(16)
    sub.runs[0].font.color.rgb = RGBColor(0x70, 0x70, 0x70)

    doc.add_paragraph()
    version = doc.add_paragraph('Version 1.0  |  June 2026  |  NIELIT')
    version.alignment = WD_ALIGN_PARAGRAPH.CENTER
    version.runs[0].font.size = Pt(11)
    version.runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.add_page_break()

    # ── Table of Contents (manual) ─────────────────────────────────────────────
    toc_heading = doc.add_heading('Table of Contents', level=1)
    set_heading_style(toc_heading, 1, 'Table of Contents')

    for i, (filename, title_label) in enumerate(DOC_SEQUENCE, start=1):
        p = doc.add_paragraph(f'{i:02d}.  {title_label}')
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.name = 'Calibri'

    doc.add_page_break()

    # ── Each Document ──────────────────────────────────────────────────────────
    for filename, section_title in DOC_SEQUENCE:
        filepath = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(filepath):
            print(f'  [SKIP] Not found: {filename}')
            continue

        print(f'  [ADD] {filename}')

        # Section divider banner
        banner = doc.add_paragraph()
        banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
        br = banner.add_run(f'  {section_title.upper()}  ')
        br.font.name = 'Calibri'
        br.font.size = Pt(12)
        br.font.bold = True
        br.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        # Shade the paragraph background blue
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '2E74B5')
        banner._p.get_or_add_pPr().append(shd)

        doc.add_paragraph()

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parse_and_add_markdown(doc, content)
        doc.add_page_break()

    doc.save(OUTPUT_FILE)
    print(f'\n✅ Document saved to:\n   {OUTPUT_FILE}')
    print('\n📌 To open in Google Docs:')
    print('   1. Go to https://drive.google.com')
    print('   2. Click "+ New" → "File Upload"')
    print('   3. Select: Face_Recognition_Attendance_System_Blueprint.docx')
    print('   4. Right-click the uploaded file → "Open with Google Docs"')


if __name__ == '__main__':
    main()
