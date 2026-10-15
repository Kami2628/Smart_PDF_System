from io import BytesIO

from pypdf import PdfReader, PdfWriter
import fitz


def get_pdf_info(pdf_file):
    pdf_file.seek(0)

    reader = PdfReader(pdf_file)

    return {
        "pages": len(reader.pages),
        "encrypted": reader.is_encrypted
    }


def merge_pdfs(pdf_files):
    writer = PdfWriter()

    for pdf_file in pdf_files:
        pdf_file.seek(0)

        reader = PdfReader(pdf_file)

        if reader.is_encrypted:
            raise ValueError(
                f"Password-protected PDF cannot be merged: {pdf_file.name}"
            )

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)

    data = output.getvalue()

    if not data:
        raise ValueError("Merged PDF is empty.")

    test_reader = PdfReader(BytesIO(data))

    if len(test_reader.pages) == 0:
        raise ValueError(
            "Generated PDF contains no pages."
        )

    return data


def generate_page_thumbnails(pdf_file):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    thumbnails = []

    for page_number in range(len(document)):

        page = document[page_number]

        matrix = fitz.Matrix(
            0.7,
            0.7
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        thumbnails.append(
            pixmap.tobytes("png")
        )

    document.close()

    return thumbnails


def modify_pdf_pages(
    pdf_file,
    page_order,
    deleted_pages,
    rotations
):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    deleted_pages = set(deleted_pages)

    valid_order = [
        page_number
        for page_number in page_order
        if page_number not in deleted_pages
        and 0 <= page_number < len(document)
    ]

    if not valid_order:
        document.close()

        raise ValueError(
            "At least one page must remain."
        )

    new_document = fitz.open()

    for page_number in valid_order:

        source_page = document[page_number]

        rotation = rotations.get(
            page_number,
            0
        )

        new_page = new_document.new_page(
            width=source_page.rect.width,
            height=source_page.rect.height
        )

        new_page.show_pdf_page(
            new_page.rect,
            document,
            page_number
        )

        if rotation != 0:
            new_page.set_rotation(rotation)

    output = BytesIO()

    new_document.save(
        output,
        garbage=4,
        deflate=True
    )

    new_document.close()
    document.close()

    data = output.getvalue()

    if not data:
        raise ValueError(
            "Modified PDF is empty."
        )

    return data


def extract_pdf_pages(
    pdf_file,
    selected_pages
):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if not selected_pages:
        document.close()

        raise ValueError(
            "Please select at least one page."
        )

    new_document = fitz.open()

    for page_number in selected_pages:

        if page_number < 0 or page_number >= len(document):
            continue

        source_page = document[page_number]

        new_page = new_document.new_page(
            width=source_page.rect.width,
            height=source_page.rect.height
        )

        new_page.show_pdf_page(
            new_page.rect,
            document,
            page_number
        )

    output = BytesIO()

    new_document.save(
        output,
        garbage=4,
        deflate=True
    )

    new_document.close()
    document.close()

    data = output.getvalue()

    if not data:
        raise ValueError(
            "Extracted PDF is empty."
        )

    return data


def split_pdf_pages(
    pdf_file,
    start_page,
    end_page
):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    total_pages = len(document)

    if start_page < 0 or end_page >= total_pages:
        document.close()

        raise ValueError(
            "Invalid page range."
        )

    if start_page > end_page:
        document.close()

        raise ValueError(
            "Start page cannot be greater than end page."
        )

    new_document = fitz.open()

    for page_number in range(
        start_page,
        end_page + 1
    ):

        source_page = document[page_number]

        new_page = new_document.new_page(
            width=source_page.rect.width,
            height=source_page.rect.height
        )

        new_page.show_pdf_page(
            new_page.rect,
            document,
            page_number
        )

    output = BytesIO()

    new_document.save(
        output,
        garbage=4,
        deflate=True
    )

    new_document.close()
    document.close()

    data = output.getvalue()

    if not data:
        raise ValueError(
            "Split PDF is empty."
        )

    return data


def compress_pdf(
    pdf_file,
    compression_level="medium"
):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if len(document) == 0:
        document.close()

        raise ValueError(
            "PDF contains no pages."
        )

    output = BytesIO()

    if compression_level == "low":
        garbage_level = 2

    elif compression_level == "medium":
        garbage_level = 4

    elif compression_level == "high":
        garbage_level = 4

    else:
        document.close()

        raise ValueError(
            "Invalid compression level."
        )

    document.save(
        output,
        garbage=garbage_level,
        deflate=True,
        clean=True
    )

    document.close()

    compressed_data = output.getvalue()

    if not compressed_data:
        raise ValueError(
            "Compressed PDF is empty."
        )

    return compressed_data


def images_to_pdf(image_files):
    if not image_files:
        raise ValueError(
            "No images selected."
        )

    from PIL import Image

    images = []

    for image_file in image_files:

        image_file.seek(0)

        image = Image.open(
            image_file
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        images.append(image)

    output = BytesIO()

    images[0].save(
        output,
        format="PDF",
        save_all=True,
        append_images=images[1:],
        resolution=100.0
    )

    for image in images:
        image.close()

    data = output.getvalue()

    if not data:
        raise ValueError(
            "Generated PDF is empty."
        )

    return data


def pdf_to_images(
    pdf_file,
    image_format="PNG"
):
    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if len(document) == 0:
        document.close()

        raise ValueError(
            "PDF contains no pages."
        )

    images = []

    for page_number in range(len(document)):

        page = document[page_number]

        matrix = fitz.Matrix(
            2.0,
            2.0
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        if image_format == "PNG":
            image_bytes = pixmap.tobytes("png")
        else:
            image_bytes = pixmap.tobytes("jpeg")

        images.append(
            image_bytes
        )

    document.close()

    return images


def ocr_pdf(
    pdf_file,
    language="eng"
):
    import os
    import subprocess
    import tempfile

    from PIL import Image

    tesseract_path = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if not os.path.exists(tesseract_path):
        raise ValueError(
            "Tesseract OCR engine was not found."
        )

    pdf_file.seek(0)

    pdf_bytes = pdf_file.read()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    if len(document) == 0:
        document.close()

        raise ValueError(
            "PDF contains no pages."
        )

    extracted_text = []

    try:

        for page_number in range(
            len(document)
        ):

            page = document[page_number]

            existing_text = page.get_text().strip()

            if existing_text:

                extracted_text.append(
                    existing_text
                )

                continue

            matrix = fitz.Matrix(
                2.0,
                2.0
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            with tempfile.TemporaryDirectory() as temp_dir:

                image_path = os.path.join(
                    temp_dir,
                    f"page_{page_number + 1}.png"
                )

                output_base = os.path.join(
                    temp_dir,
                    f"ocr_page_{page_number + 1}"
                )

                with open(
                    image_path,
                    "wb"
                ) as image_file:

                    image_file.write(
                        image_bytes
                    )

                command = [
                    tesseract_path,
                    image_path,
                    output_base,
                    "-l",
                    language
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:

                    error_message = (
                        result.stderr.strip()
                        or "Tesseract OCR failed."
                    )

                    raise ValueError(
                        error_message
                    )

                text_file = (
                    output_base + ".txt"
                )

                if os.path.exists(
                    text_file
                ):

                    with open(
                        text_file,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as text_reader:

                        page_text = (
                            text_reader.read().strip()
                        )

                    extracted_text.append(
                        page_text
                    )

                else:

                    extracted_text.append(
                        ""
                    )

    finally:

        document.close()

    final_text = "\n\n".join(
        extracted_text
    ).strip()

    if not final_text:
        raise ValueError(
            "OCR could not detect any text."
        )

    return final_text