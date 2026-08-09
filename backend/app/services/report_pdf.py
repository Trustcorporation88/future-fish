"""
报告 PDF 导出

把报告的 Markdown 渲染成 PDF。用 PyMuPDF 的 Story 引擎（已是本项目依赖，
见 requirements.txt 的 PyMuPDF），不额外引入 weasyprint/wkhtmltopdf 这类
需要系统级依赖的组件 —— Railway 上装那些要改构建镜像。

Story 只认 HTML/CSS 的一个子集，所以这里自己做一遍 Markdown→HTML，
只覆盖报告实际会产出的语法：标题、段落、引用、列表、粗斜体、分隔线、
行内代码。报告由 LLM 按固定模板生成，不会出现表格和图片。
"""

import html
import io
import re
from typing import List

import pymupdf

from ..utils.logger import get_logger

logger = get_logger('mirofish.services.report_pdf')

# A4 + 2cm 页边距。报告是给人读的长文，正文行宽控制在 ~90 字符。
_PAGE = 'a4'
_MARGIN = 57  # ≈2cm at 72dpi

_INLINE_CODE_RE = re.compile(r'`([^`]+)`')
_BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')
_ITALIC_RE = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')
_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_HR_RE = re.compile(r'^\s*([-*_])\s*(\1\s*){2,}$')
_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
_UL_RE = re.compile(r'^\s*[-*+]\s+(.*)$')
_OL_RE = re.compile(r'^\s*(\d+)[.)]\s+(.*)$')


def _inline(text: str) -> str:
    """行内标记 → HTML。先转义，再放回标签，避免正文里的 < > 破坏结构。"""
    out = html.escape(text, quote=False)
    # 链接在报告里通常是新闻来源，PDF 里保留文字并把 URL 跟在后面，
    # 因为打印出来点不动，光有锚文本会丢失出处。
    out = _LINK_RE.sub(lambda m: f'{m.group(1)} &lt;{m.group(2)}&gt;', out)
    out = _INLINE_CODE_RE.sub(r'<code>\1</code>', out)
    out = _BOLD_RE.sub(r'<b>\1</b>', out)
    out = _ITALIC_RE.sub(r'<i>\1</i>', out)
    return out


_BOLD_ONLY_RE = re.compile(r'^\*\*([^*]+)\*\*$')


def markdown_to_html(md: str, title: str = '') -> str:
    """报告 Markdown → Story 能吃的 HTML 片段。"""
    body: List[str] = []
    list_stack: List[str] = []  # 'ul' / 'ol'
    para: List[str] = []
    last_heading = ''  # 用来去掉 LLM 重复输出的标题行，见下面 _BOLD_ONLY_RE 处

    def flush_para():
        if para:
            body.append(f'<p>{" ".join(para)}</p>')
            para.clear()

    def close_lists():
        while list_stack:
            body.append(f'</{list_stack.pop()}>')

    for raw in md.splitlines():
        line = raw.rstrip()

        if not line.strip():
            flush_para()
            close_lists()
            continue

        if _HR_RE.match(line):
            flush_para()
            close_lists()
            body.append('<div class="rule"></div>')
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            flush_para()
            close_lists()
            level = min(len(heading.group(1)), 4)
            last_heading = heading.group(2).strip()
            body.append(f'<h{level}>{_inline(heading.group(2))}</h{level}>')
            continue

        # 生成器写章节时常把标题再用粗体重复一遍（"## X" 后面紧跟 "**X**"）。
        # 屏幕上章节标题是单独的 UI 组件所以看不出来，导出成连续正文就是重复行。
        bold_only = _BOLD_ONLY_RE.match(line.strip())
        if bold_only and bold_only.group(1).strip() == last_heading:
            continue

        if line.lstrip().startswith('>'):
            flush_para()
            close_lists()
            quote = line.lstrip()[1:].lstrip()
            body.append(f'<div class="quote">{_inline(quote)}</div>')
            continue

        ul = _UL_RE.match(line)
        if ul:
            flush_para()
            if list_stack[-1:] != ['ul']:
                close_lists()
                list_stack.append('ul')
                body.append('<ul>')
            body.append(f'<li>{_inline(ul.group(1))}</li>')
            continue

        ol = _OL_RE.match(line)
        if ol:
            flush_para()
            if list_stack[-1:] != ['ol']:
                close_lists()
                list_stack.append('ol')
                body.append('<ol>')
            body.append(f'<li>{_inline(ol.group(2))}</li>')
            continue

        close_lists()
        para.append(_inline(line))

    flush_para()
    close_lists()

    heading_text = f'<h1>{html.escape(title)}</h1>' if title else ''
    return f'<html><head><style>{_CSS}</style></head><body>{heading_text}{"".join(body)}</body></html>'


_CSS = """
body { font-family: sans-serif; font-size: 10.5pt; line-height: 1.55; color: #1b2430; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 14pt 0; color: #0f2338; }
h2 { font-size: 14pt; margin: 20pt 0 7pt 0; color: #123a63; }
h3 { font-size: 11.5pt; margin: 14pt 0 5pt 0; color: #123a63; }
h4 { font-size: 10.5pt; margin: 12pt 0 4pt 0; color: #35506d; }
p { margin: 0 0 8pt 0; text-align: justify; }
/* 报告里的引用是 agent 的原话，是核心证据，给一条左边线让它在长文里跳出来 */
.quote { margin: 8pt 0 10pt 0; padding: 2pt 0 2pt 10pt;
         border-left: 2.5pt solid #3b8ff3; color: #3d4a5c; font-style: italic; }
.rule { margin: 12pt 0; border-top: 0.7pt solid #c9d4e2; }
ul, ol { margin: 0 0 8pt 0; padding-left: 16pt; }
li { margin: 0 0 3pt 0; }
code { font-family: monospace; font-size: 9.5pt; color: #123a63; }
b { color: #0f2338; }
"""


def render_markdown_pdf(md: str, title: str = '', footer_label: str = '') -> bytes:
    """Markdown → PDF 字节流。footer_label 打在每页页脚（报告 ID / 日期）。"""
    story = pymupdf.Story(html=markdown_to_html(md, title))

    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    mediabox = pymupdf.paper_rect(_PAGE)
    where = mediabox + (_MARGIN, _MARGIN, -_MARGIN, -_MARGIN)

    page_no = 0
    more = True
    while more:
        page_no += 1
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()
    writer.close()

    doc = pymupdf.open('pdf', buf.getvalue())
    try:
        _stamp_footer(doc, footer_label)
        if title:
            doc.set_metadata({'title': title, 'producer': 'MiroFish'})
        return doc.tobytes(deflate=True, garbage=3)
    finally:
        doc.close()


def _stamp_footer(doc, label: str):
    """页脚：左边是报告标识，右边是页码。Story 自己不排页脚。"""
    total = doc.page_count
    for index, page in enumerate(doc, start=1):
        baseline = page.rect.height - _MARGIN + 26
        if label:
            page.insert_text(
                (_MARGIN, baseline), label,
                fontname='helv', fontsize=7.5, color=(0.55, 0.6, 0.66),
            )
        counter = f'{index} / {total}'
        page.insert_text(
            (page.rect.width - _MARGIN - pymupdf.get_text_length(counter, 'helv', 7.5), baseline),
            counter, fontname='helv', fontsize=7.5, color=(0.55, 0.6, 0.66),
        )
