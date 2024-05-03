import fitz


def read_all_pdf_pages(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_doc:
        for page_num in range(pdf_doc.page_count):
            page = pdf_doc.load_page(page_num)
            text += page.get_text()
    return text
