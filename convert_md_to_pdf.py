import markdown
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os

def register_chinese_font():
    """嘗試註冊中文字體"""
    font_paths = [
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/kaiu.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                return 'ChineseFont'
            except:
                continue
    
    return None

def convert_markdown_to_pdf(md_file_path, pdf_file_path):
    """將Markdown轉換為PDF"""
    # 讀取Markdown文件
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 註冊中文字體
    chinese_font = register_chinese_font()
    
    # 創建PDF文檔
    doc = SimpleDocTemplate(pdf_file_path, pagesize=A4)
    
    # 創建樣式
    styles = getSampleStyleSheet()
    
    if chinese_font:
        title_style = ParagraphStyle(
            'ChineseTitle',
            parent=styles['Title'],
            fontName=chinese_font,
            fontSize=18,
            leading=22,
            spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=styles['Heading1'],
            fontName=chinese_font,
            fontSize=14,
            leading=18,
            spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'ChineseNormal',
            parent=styles['Normal'],
            fontName=chinese_font,
            fontSize=10,
            leading=14
        )
    else:
        title_style = styles['Title']
        heading_style = styles['Heading1']
        normal_style = styles['Normal']
    
    elements = []
    
    # 簡單處理：將Markdown轉換為HTML，然後處理
    html = markdown.markdown(md_content, extensions=['tables', 'toc'])
    
    # 按行處理
    lines = html.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 6))
            continue
            
        # 處理標題
        if line.startswith('<h1>'):
            title = re.sub(r'<[^>]+>', '', line)
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))
        elif line.startswith('<h2>'):
            title = re.sub(r'<[^>]+>', '', line)
            elements.append(Paragraph(title, heading_style))
            elements.append(Spacer(1, 12))
        elif line.startswith('<h3>'):
            title = re.sub(r'<[^>]+>', '', line)
            elements.append(Paragraph(title, heading_style))
            elements.append(Spacer(1, 12))
        # 處理表格
        elif line.startswith('<table>'):
            # 簡單跳過表格處理，避免複雜性
            continue
        elif line.startswith('<tr>') or line.startswith('<td>') or line.startswith('<th>'):
            continue
        elif line.startswith('</table>') or line.startswith('</tr>') or line.startswith('</td>') or line.startswith('</th>'):
            continue
        # 處理段落
        elif line.startswith('<p>'):
            para = re.sub(r'<[^>]+>', '', line)
            # 處理粗體和斜體
            para = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', para)
            para = re.sub(r'\*(.*?)\*', r'<i>\1</i>', para)
            elements.append(Paragraph(para, normal_style))
            elements.append(Spacer(1, 6))
        # 處理列表
        elif line.startswith('<ul>') or line.startswith('</ul>') or line.startswith('<li>') or line.startswith('</li>'):
            if line.startswith('<li>'):
                item = re.sub(r'<[^>]+>', '', line)
                elements.append(Paragraph(f"• {item}", normal_style))
                elements.append(Spacer(1, 3))
        # 處理普通文本
        else:
            # 處理HTML標籤
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line:
                # 處理粗體和斜體
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_line)
                clean_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_line)
                elements.append(Paragraph(clean_line, normal_style))
                elements.append(Spacer(1, 6))
    
    # 生成PDF
    doc.build(elements)
    
    print("PDF successfully generated")

if __name__ == "__main__":
    md_file = "程式說明文檔.md"
    pdf_file = "程式說明文檔.pdf"
    
    convert_markdown_to_pdf(md_file, pdf_file)