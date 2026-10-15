import os
from pypdf import PdfReader, PdfWriter


def get_security_status(pdf_path):
    reader = PdfReader(pdf_path)

    return {
        "encrypted": reader.is_encrypted,
        "pages": len(reader.pages)
    }


def protect_pdf(pdf_path, output_path, password):
    reader = PdfReader(pdf_path)

    if reader.is_encrypted:
        raise ValueError("PDF is already password protected.")

    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(password)

    with open(output_path, "wb") as file:
        writer.write(file)

    return output_path


def remove_pdf_password(pdf_path, output_path, password):
    reader = PdfReader(pdf_path)

    if not reader.is_encrypted:
        raise ValueError("PDF is not password protected.")

    if not reader.decrypt(password):
        raise ValueError("Incorrect PDF password.")

    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, "wb") as file:
        writer.write(file)

    return output_path