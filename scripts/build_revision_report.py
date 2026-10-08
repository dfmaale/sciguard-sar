#!/usr/bin/env python3
"""Build the review response and audit PDF from maintained Markdown sources."""
from pathlib import Path
import re
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
ROOT=Path(__file__).resolve().parents[1]
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
fontroot=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('DejaVu','DejaVuSans.ttf'),('DejaVu-Bold','DejaVuSans-Bold.ttf'),('DejaVuMono','DejaVuSansMono.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(fontroot/file)))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVu-Bold',italic='DejaVu',boldItalic='DejaVu-Bold')
styles=getSampleStyleSheet()
for style in styles.byName.values():style.fontName='DejaVu'
styles['Heading1'].fontName='DejaVu-Bold'
styles['Heading2'].fontName='DejaVu-Bold' 
styles['BodyText'].fontSize=9; styles['BodyText'].leading=12
styles['BodyText'].spaceAfter=6
styles['Heading1'].fontSize=16; styles['Heading1'].leading=20
styles['Heading2'].fontSize=12; styles['Heading2'].leading=15
styles['Heading2'].spaceBefore=12

def markup(s):
 s=escape(s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 return re.sub(r'`([^`]+)`',r'<font name="DejaVuMono">\1</font>',s)

def page(canvas,doc):
 canvas.setFont('DejaVu',8);canvas.setFillColor(colors.HexColor('#555555'))
 canvas.drawString(42,26,'SciGuard | Major revision and reproducibility audit')
 canvas.drawRightString(570,26,str(doc.page))

story=[]
for file_index,name in enumerate(['REVISION_RESPONSE.md','NOTEBOOK_AUDIT.md','VALIDATION_REPORT.md']):
 if file_index:story.append(PageBreak())
 lines=(ROOT/'docs'/name).read_text().splitlines(); i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    vals=[s.strip() for s in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r'[-:]+',v) for v in vals):rows.append([Paragraph(markup(v),styles['BodyText']) for v in vals])
    i+=1
   t=Table(rows,colWidths=[165,160,203],repeatRows=1,hAlign='LEFT')
   t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.grey),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
   story.extend([t,Spacer(1,10)]);continue
  if line.startswith('#'):
   level=len(line)-len(line.lstrip('#'));story.append(Paragraph(markup(line.lstrip('#').strip()),styles['Heading1' if level==1 else 'Heading2']));i+=1;continue
  paragraph=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):
   if re.match(r'^\d+\. ',lines[i]):break
   paragraph.append(lines[i].strip());i+=1
  story.append(Paragraph(markup(' '.join(paragraph)),styles['BodyText']))
out=ROOT/'SciGuard_Major_Revision_Response.pdf'
SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=42,bottomMargin=42).build(story,onFirstPage=page,onLaterPages=page)
print(out)
