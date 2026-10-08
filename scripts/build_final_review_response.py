#!/usr/bin/env python3
"""Build the second-round reviewer-response PDF from docs/FINAL_REVIEW_RESPONSE.md."""
from pathlib import Path
import re
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

ROOT = Path(__file__).resolve().parents[1]
fontroot = Path('/usr/share/fonts/truetype/dejavu')
for name, file in [
    ('DejaVu','DejaVuSans.ttf'),
    ('DejaVu-Bold','DejaVuSans-Bold.ttf'),
    ('DejaVuMono','DejaVuSansMono.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, str(fontroot/file)))
pdfmetrics.registerFontFamily(
    'DejaVu', normal='DejaVu', bold='DejaVu-Bold', italic='DejaVu', boldItalic='DejaVu-Bold'
)

styles = getSampleStyleSheet()
for st in styles.byName.values():
    st.fontName = 'DejaVu'
styles['Title'].fontName = 'DejaVu-Bold'
styles['Title'].fontSize = 18
styles['Title'].leading = 22
styles['Title'].alignment = TA_CENTER
styles['Title'].spaceAfter = 14
styles['Heading1'].fontName = 'DejaVu-Bold'
styles['Heading1'].fontSize = 14
styles['Heading1'].leading = 17
styles['Heading1'].spaceBefore = 10
styles['Heading1'].spaceAfter = 6
styles['Heading2'].fontName = 'DejaVu-Bold'
styles['Heading2'].fontSize = 11.5
styles['Heading2'].leading = 14
styles['Heading2'].spaceBefore = 10
styles['Heading2'].spaceAfter = 4
styles['BodyText'].fontSize = 9.2
styles['BodyText'].leading = 12.3
styles['BodyText'].spaceAfter = 6


def markup(s):
    s = escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return re.sub(r'`([^`]+)`', r'<font name="DejaVuMono">\1</font>', s)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('DejaVu', 7.5)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(42, 24, 'SciGuard | Response to second-round review')
    canvas.drawRightString(570, 24, f'Page {doc.page}')
    canvas.restoreState()


def build():
    lines = (ROOT/'docs/FINAL_REVIEW_RESPONSE.md').read_text().splitlines()
    story, first, i = [], True, 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            if first:
                story.append(Paragraph(markup(text), styles['Title']))
                first = False
            else:
                story.append(Paragraph(markup(text), styles['Heading1' if level == 1 else 'Heading2']))
            i += 1
            continue
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith('#'):
            para.append(lines[i].strip())
            i += 1
        story.append(Paragraph(markup(' '.join(para)), styles['BodyText']))

    out = ROOT/'SciGuard_Final_Review_Response.pdf'
    SimpleDocTemplate(
        str(out), pagesize=(612,792), leftMargin=42, rightMargin=42, topMargin=42, bottomMargin=42,
        title='SciGuard Response to Second-Round Review', author='Faustus Domebale Maale and Hui Yi'
    ).build(story, onFirstPage=footer, onLaterPages=footer)
    print(out)


if __name__ == '__main__':
    build()
