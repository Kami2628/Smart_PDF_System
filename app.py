import os
import base64
import fitz
import streamlit as st

from core.pdf_engine import (
    get_pdf_info,
    merge_pdfs,
    generate_page_thumbnails,
    modify_pdf_pages,
    extract_pdf_pages,
    split_pdf_pages,
    compress_pdf,
    images_to_pdf,
    pdf_to_images,
    ocr_pdf
)

from core.ai_engine import analyze_document

from core.rag_engine import (
    build_rag_data,
    ask_pdf
)
from core.security_engine import (
    get_security_status,
    protect_pdf,
    remove_pdf_password
)
from core.auth import (
    register_user,
    login_user
)

from core.database import (
    add_pdf_history,
    get_pdf_history
)

st.set_page_config(
    page_title="Smart PDF System",
    page_icon="📄",
    layout="wide"
)


st.title("📄 Smart PDF System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None
if not st.session_state.logged_in:

    st.subheader("🔐 Login / Signup")

    auth_mode = st.radio(
        "Select",
        ["Login", "Signup"],
        horizontal=True
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if auth_mode == "Signup":

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if password != confirm_password:

                st.error("Passwords do not match.")

            else:

                success, message = register_user(
                    username,
                    password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    else:

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            user = login_user(
                username,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.username = user["username"]

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.stop()

st.sidebar.title("🛠️ PDF Tools")

st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

    st.rerun()


if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "Dashboard"

tools_list = [
    "Dashboard",
    "PDF Merger",
    "PDF Page Manager",
    "PDF Splitter",
    "PDF Compressor",
    "PDF Converter",
    "OCR",
    "AI Document Analysis",
    "Chat with PDF",
    "PDF Security",
    "PDF History"
]

if st.session_state.selected_tool not in tools_list:
    st.session_state.selected_tool = "Dashboard"

tool = st.sidebar.selectbox(
    "Select Tool",
    tools_list,
    index=tools_list.index(
        st.session_state.selected_tool
    )
)


def create_download_link(
    data,
    filename,
    text="⬇️ Download PDF"
):

    b64 = base64.b64encode(
        data
    ).decode()

    href = (
        f'<a href="data:application/pdf;base64,{b64}" '
        f'download="{filename}">'
        f'{text}'
        f'</a>'
    )

    st.markdown(
        href,
        unsafe_allow_html=True
    )

# ============================================================
# PDF HISTORY
# ============================================================

if tool == "PDF History":

    st.header("📜 PDF History")

    history = get_pdf_history(
        st.session_state.user_id
    )

    if history:

        search_text = st.text_input(
            "🔎 Search PDF",
            placeholder="Search by PDF filename..."
        )

        operations = [
            "All Operations",
            "PDF Merger",
            "PDF Page Manager",
            "Page Extraction",
            "PDF Splitter",
            "PDF Compressor",
            "Images → PDF",
            "PDF → Images",
            "OCR",
            "AI Document Analysis",
            "Chat with PDF",
            "PDF Security"
        ]

        selected_operation = st.selectbox(
            "🛠️ Filter by Operation",
            operations
        )

        filtered_history = history

        if search_text.strip():

            filtered_history = [
                item
                for item in filtered_history
                if search_text.lower()
                in item["file_name"].lower()
            ]

        if selected_operation != "All Operations":

            filtered_history = [
                item
                for item in filtered_history
                if item["operation"]
                == selected_operation
            ]

        st.divider()

        st.write(
            f"Showing **{len(filtered_history)}** "
            f"of **{len(history)}** operations."
        )

        if filtered_history:

            for index, item in enumerate(
                filtered_history,
                start=1
            ):

                st.info(
                    f"#{index} | "
                    f"📄 {item['file_name']} | "
                    f"🛠️ {item['operation']} | "
                    f"🕒 {item['created_at']}"
                )

        else:

            st.warning(
                "No matching history found."
            )

    else:

        st.info(
            "No PDF history found yet."
        )


# ============================================================
# PDF MERGER
# ============================================================

elif tool == "PDF Merger":
    st.header("📎 PDF Merger")

    st.write(
        "Merge multiple PDF files into one PDF document."
    )

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_pdfs"
    )

    if uploaded_files:

        st.subheader("📋 Selected Files")

        total_pages = 0

        for index, pdf_file in enumerate(
            uploaded_files,
            start=1
        ):

            try:

                info = get_pdf_info(
                    pdf_file
                )

                total_pages += info["pages"]

                status = (
                    "🔒 Password Protected"
                    if info["encrypted"]
                    else "✅ Ready"
                )

                st.write(
                    f"{index}. {pdf_file.name} — "
                    f"{info['pages']} pages — {status}"
                )

            except Exception as e:

                st.error(
                    f"Could not read {pdf_file.name}: {e}"
                )

        st.info(
            f"Total selected pages: {total_pages}"
        )

        if st.button(
            "🔗 Merge PDFs",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Merging PDFs..."
                ):

                    merged_pdf = merge_pdfs(
                        uploaded_files
                    )

                output_dir = "output"

                os.makedirs(
                    output_dir,
                    exist_ok=True
                )

                output_path = os.path.join(
                    output_dir,
                    "merged_document.pdf"
                )

                with open(
                    output_path,
                    "wb"
                ) as file:

                    file.write(
                        merged_pdf
                    )

                add_pdf_history(
                    st.session_state.user_id,
                    "merged_document.pdf",
                    "PDF Merger"
                )

                st.success(
                    "PDFs merged successfully."
                )

                st.write(
                    f"Saved to: `{output_path}`"
                )

                create_download_link(
                    merged_pdf,
                    "merged_document.pdf"
                )

            except Exception as e:

                st.error(
                    f"Merge failed: {e}"
                )
# ============================================================
# PDF PAGE MANAGER
# ============================================================

elif tool == "PDF Page Manager":

    st.header("🗂️ PDF Page Manager")

    st.write(
        "Preview, reorder, delete, rotate "
        "and extract PDF pages."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="page_manager_file"
    )

    if uploaded_pdf:

        try:

            thumbnails = generate_page_thumbnails(
                uploaded_pdf
            )

            total_pages = len(
                thumbnails
            )

            if (
                "page_manager_file_name"
                not in st.session_state
                or st.session_state.page_manager_file_name
                != uploaded_pdf.name
            ):

                st.session_state.page_manager_file_name = (
                    uploaded_pdf.name
                )

                st.session_state.page_order = list(
                    range(total_pages)
                )

                st.session_state.deleted_pages = set()

                st.session_state.rotations = {
                    page_number: 0
                    for page_number in range(total_pages)
                }

            current_pages = [
                page_number
                for page_number in st.session_state.page_order
                if page_number
                not in st.session_state.deleted_pages
            ]

            st.info(
                f"Total pages: {total_pages} | "
                f"Current pages: {len(current_pages)}"
            )

            st.subheader("📄 Page Preview")

            for display_index, page_number in enumerate(
                current_pages
            ):

                col1, col2, col3 = st.columns(
                    [1, 4, 1]
                )

                with col1:

                    st.write(
                        f"Page {display_index + 1}"
                    )

                    st.image(
                        thumbnails[page_number],
                        width=140
                    )

                with col2:

                    rotation = st.session_state.rotations.get(
                        page_number,
                        0
                    )

                    st.write(
                        f"Original page: "
                        f"{page_number + 1}"
                    )

                    st.write(
                        f"Rotation: {rotation}°"
                    )

                with col3:

                    if st.button(
                        "↩️",
                        key=f"left_{page_number}"
                    ):

                        st.session_state.rotations[
                            page_number
                        ] = (
                            rotation - 90
                        ) % 360

                        st.rerun()

                    if st.button(
                        "↪️",
                        key=f"right_{page_number}"
                    ):

                        st.session_state.rotations[
                            page_number
                        ] = (
                            rotation + 90
                        ) % 360

                        st.rerun()

                    if st.button(
                        "🗑️",
                        key=f"delete_{page_number}"
                    ):

                        st.session_state.deleted_pages.add(
                            page_number
                        )

                        st.rerun()

            st.divider()

            st.subheader("🔀 Reorder Pages")

            order_text = st.text_input(
                "Enter page order",
                value=", ".join(
                    str(page + 1)
                    for page in current_pages
                )
            )

            if st.button(
                "Apply Page Order",
                use_container_width=True
            ):

                try:

                    requested_order = [
                        int(value.strip()) - 1
                        for value in order_text.split(",")
                        if value.strip()
                    ]

                    if sorted(requested_order) != sorted(
                        current_pages
                    ):

                        raise ValueError(
                            "Order must contain every "
                            "remaining page exactly once."
                        )

                    st.session_state.page_order = (
                        requested_order
                    )

                    st.success(
                        "Page order updated."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        str(e)
                    )

            st.divider()

            st.subheader("📤 Extract Selected Pages")

            selected_pages = st.multiselect(
                "Select pages",
                options=[
                    page_number + 1
                    for page_number in current_pages
                ]
            )

            if st.button(
                "Extract Selected Pages",
                use_container_width=True
            ):

                try:

                    if not selected_pages:

                        st.warning(
                            "Please select at least one page."
                        )

                    else:

                        selected_zero_based = [
                            page - 1
                            for page in selected_pages
                        ]

                        uploaded_pdf.seek(0)

                        extracted_pdf = extract_pdf_pages(
                            uploaded_pdf,
                            selected_zero_based
                        )

                        output_path = os.path.join(
                            "output",
                            "extracted_pages.pdf"
                        )

                        os.makedirs(
                            "output",
                            exist_ok=True
                        )

                        with open(
                            output_path,
                            "wb"
                        ) as file:

                            file.write(
                                extracted_pdf
                            )

                        add_pdf_history(
                            st.session_state.user_id,
                            "extracted_pages.pdf",
                            "Page Extraction"
                        )

                        st.success(
                            "Selected pages extracted successfully."
                        )

                        create_download_link(
                            extracted_pdf,
                            "extracted_pages.pdf"
                        )

                except Exception as e:

                    st.error(
                        f"Extraction failed: {e}"
                    )

            st.divider()

            if st.button(
                "💾 Generate Modified PDF",
                type="primary",
                use_container_width=True
            ):

                try:

                    uploaded_pdf.seek(0)

                    modified_pdf = modify_pdf_pages(
                        uploaded_pdf,
                        st.session_state.page_order,
                        st.session_state.deleted_pages,
                        st.session_state.rotations
                    )

                    os.makedirs(
                        "output",
                        exist_ok=True
                    )

                    output_path = os.path.join(
                        "output",
                        "modified_document.pdf"
                    )

                    with open(
                        output_path,
                        "wb"
                    ) as file:

                        file.write(
                            modified_pdf
                        )

                    add_pdf_history(
                        st.session_state.user_id,
                        "modified_document.pdf",
                        "PDF Page Manager"
                    )

                    st.success(
                        "Modified PDF generated successfully."
                    )

                    create_download_link(
                        modified_pdf,
                        "modified_document.pdf"
                    )

                except Exception as e:

                    st.error(
                        f"Could not generate PDF: {e}"
                    )

        except Exception as e:

            st.error(
                f"Page Manager error: {e}"
            )


# ============================================================
# PDF SPLITTER
# ============================================================

elif tool == "PDF Splitter":

    st.header("✂️ PDF Splitter")

    st.write(
        "Extract a specific page range from a PDF."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="split_pdf"
    )

    if uploaded_pdf:

        try:

            info = get_pdf_info(
                uploaded_pdf
            )

            total_pages = info["pages"]

            st.info(
                f"Total pages: {total_pages}"
            )

            col1, col2 = st.columns(2)

            with col1:

                start_page = st.number_input(
                    "Start Page",
                    min_value=1,
                    max_value=total_pages,
                    value=1
                )

            with col2:

                end_page = st.number_input(
                    "End Page",
                    min_value=1,
                    max_value=total_pages,
                    value=total_pages
                )

            if st.button(
                "✂️ Split PDF",
                type="primary",
                use_container_width=True
            ):

                try:

                    if start_page > end_page:

                        st.error(
                            "Start Page cannot be greater than End Page."
                        )

                    else:

                        uploaded_pdf.seek(0)

                        split_pdf = split_pdf_pages(
                            uploaded_pdf,
                            start_page - 1,
                            end_page - 1
                        )

                        os.makedirs(
                            "output",
                            exist_ok=True
                        )

                        output_path = os.path.join(
                            "output",
                            "split_document.pdf"
                        )

                        with open(
                            output_path,
                            "wb"
                        ) as file:

                            file.write(
                                split_pdf
                            )

                        add_pdf_history(
                            st.session_state.user_id,
                            "split_document.pdf",
                            "PDF Splitter"
                        )

                        st.success(
                            "PDF split successfully."
                        )

                        create_download_link(
                            split_pdf,
                            "split_document.pdf"
                        )

                except Exception as e:

                    st.error(
                        f"Split failed: {e}"
                    )

        except Exception as e:

            st.error(
                f"Could not read PDF: {e}"
            )

# ============================================================
# PDF COMPRESSOR
# ============================================================

elif tool == "PDF Compressor":

    st.header("🗜️ PDF Compressor")

    st.write(
        "Reduce PDF file size while keeping the document usable."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="compress_pdf"
    )

    if uploaded_pdf:

        original_size = len(
            uploaded_pdf.getvalue()
        )

        st.info(
            f"Original size: "
            f"{original_size / 1024:.2f} KB"
        )

        compression_level = st.selectbox(
            "Compression Level",
            [
                "low",
                "medium",
                "high"
            ],
            index=1
        )

        if st.button(
            "🗜️ Compress PDF",
            type="primary",
            use_container_width=True
        ):

            try:

                uploaded_pdf.seek(0)

                compressed_pdf = compress_pdf(
                    uploaded_pdf,
                    compression_level
                )

                compressed_size = len(
                    compressed_pdf
                )

                os.makedirs(
                    "output",
                    exist_ok=True
                )

                output_path = os.path.join(
                    "output",
                    "compressed_document.pdf"
                )

                with open(
                    output_path,
                    "wb"
                ) as file:

                    file.write(
                        compressed_pdf
                    )

                add_pdf_history(
                    st.session_state.user_id,
                    "compressed_document.pdf",
                    "PDF Compressor"
                )

                st.success(
                    "PDF compression completed."
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Original",
                        f"{original_size / 1024:.2f} KB"
                    )

                with col2:

                    st.metric(
                        "Compressed",
                        f"{compressed_size / 1024:.2f} KB"
                    )

                with col3:

                    if original_size > 0:

                        reduction = (
                            (
                                original_size
                                - compressed_size
                            )
                            / original_size
                            * 100
                        )

                    else:

                        reduction = 0

                    st.metric(
                        "Reduction",
                        f"{reduction:.2f}%"
                    )

                create_download_link(
                    compressed_pdf,
                    "compressed_document.pdf"
                )

            except Exception as e:

                st.error(
                    f"Compression failed: {e}"
                )

# ============================================================
# PDF CONVERTER
# ============================================================

elif tool == "PDF Converter":

    st.header("🔄 PDF Converter")

    conversion_type = st.radio(
        "Select Conversion",
        [
            "Images → PDF",
            "PDF → Images"
        ],
        horizontal=True
    )

    if conversion_type == "Images → PDF":

        st.subheader("🖼️ Images → PDF")

        image_files = st.file_uploader(
            "Upload Images",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            accept_multiple_files=True,
            key="images_to_pdf"
        )

        if image_files:

            st.info(
                f"{len(image_files)} image(s) selected."
            )

            if st.button(
                "📄 Convert to PDF",
                type="primary",
                use_container_width=True
            ):

                try:

                    pdf_data = images_to_pdf(
                        image_files
                    )

                    output_dir = "output"

                    os.makedirs(
                        output_dir,
                        exist_ok=True
                    )

                    output_path = os.path.join(
                        output_dir,
                        "images_document.pdf"
                    )

                    with open(
                        output_path,
                        "wb"
                    ) as file:

                        file.write(
                            pdf_data
                        )

                    add_pdf_history(
                        st.session_state.user_id,
                        "images_document.pdf",
                        "Images → PDF"
                    )

                    st.success(
                        "Images converted to PDF successfully."
                    )

                    create_download_link(
                        pdf_data,
                        "images_document.pdf"
                    )

                except Exception as e:

                    st.error(
                        f"Conversion failed: {e}"
                    )

    else:

        st.subheader("📄 PDF → Images")

        uploaded_pdf = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="pdf_to_images"
        )

        if uploaded_pdf:

            image_format = st.selectbox(
                "Image Format",
                [
                    "PNG",
                    "JPEG"
                ]
            )

            if st.button(
                "🖼️ Convert PDF",
                type="primary",
                use_container_width=True
            ):

                try:

                    uploaded_pdf.seek(0)

                    images = pdf_to_images(
                        uploaded_pdf,
                        image_format
                    )

                    add_pdf_history(
                        st.session_state.user_id,
                        uploaded_pdf.name,
                        "PDF → Images"
                    )

                    st.success(
                        f"{len(images)} image(s) generated."
                    )

                    for index, image_data in enumerate(
                        images,
                        start=1
                    ):

                        st.image(
                            image_data,
                            caption=f"Page {index}",
                            use_container_width=True
                        )

                        extension = (
                            "png"
                            if image_format == "PNG"
                            else "jpg"
                        )

                        st.download_button(
                            f"⬇️ Download Page {index}",
                            data=image_data,
                            file_name=(
                                f"page_{index}.{extension}"
                            ),
                            mime=(
                                "image/png"
                                if image_format == "PNG"
                                else "image/jpeg"
                            ),
                            use_container_width=True
                        )

                except Exception as e:

                    st.error(
                        f"Conversion failed: {e}"
                    )


# ============================================================
# OCR
# ============================================================

elif tool == "OCR":

    st.header("🔍 OCR - Optical Character Recognition")

    st.write(
        "Extract text from scanned or image-based PDF documents."
    )

    uploaded_pdf = st.file_uploader(
        "Upload scanned PDF",
        type=["pdf"],
        key="ocr_pdf"
    )

    language = st.selectbox(
        "OCR Language",
        [
            "eng"
        ]
    )

    if uploaded_pdf:

        if st.button(
            "🔍 Run OCR",
            type="primary",
            use_container_width=True
        ):

            try:

                uploaded_pdf.seek(0)

                extracted_text = ocr_pdf(
                    uploaded_pdf,
                    language
                )

                add_pdf_history(
                    st.session_state.user_id,
                    uploaded_pdf.name,
                    "OCR"
                )

                st.success(
                    "OCR completed successfully."
                )

                st.subheader(
                    "📝 Extracted Text"
                )

                st.text_area(
                    "OCR Result",
                    extracted_text,
                    height=500
                )

                st.download_button(
                    "⬇️ Download Extracted Text",
                    data=extracted_text.encode(
                        "utf-8"
                    ),
                    file_name="ocr_extracted_text.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"OCR failed: {e}"
                )


# ============================================================
# AI DOCUMENT ANALYSIS
# ============================================================

elif tool == "AI Document Analysis":

    st.header("🤖 AI Document Analysis")

    st.write(
        "Upload a PDF and generate a professional AI-powered "
        "document analysis."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="ai_analysis_pdf"
    )

    if uploaded_pdf:

        st.info(
            f"File: {uploaded_pdf.name}"
        )

        if st.button(
            "🤖 Analyze Document",
            type="primary",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Extracting document text..."
                ):

                    uploaded_pdf.seek(0)

                    pdf_bytes = uploaded_pdf.read()

                    document = fitz.open(
                        stream=pdf_bytes,
                        filetype="pdf"
                    )

                    document_text = ""

                    for page in document:

                        document_text += (
                            page.get_text()
                            + "\n"
                        )

                    total_pages = len(
                        document
                    )

                    document.close()

                if not document_text.strip():

                    st.warning(
                        "No selectable text found. "
                        "Run OCR on this scanned PDF first."
                    )

                else:

                    with st.spinner(
                        "AI is analyzing the document..."
                    ):

                        analysis = analyze_document(
                            document_text
                        )

                    add_pdf_history(
                        st.session_state.user_id,
                        uploaded_pdf.name,
                        "AI Document Analysis"
                    )

                    st.success(
                        "AI analysis completed successfully."
                    )

                    st.subheader(
                        "📄 Document Information"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Document Type",
                            analysis["document_type"]
                        )

                    with col2:

                        st.metric(
                            "Pages",
                            total_pages
                        )

                    with col3:

                        st.metric(
                            "Words",
                            analysis["word_count"]
                        )

                    st.divider()

                    st.subheader(
                        "📌 AI Generated Summary"
                    )

                    st.write(
                        analysis["summary"]
                    )

                    st.divider()

                    st.subheader(
                        "🔑 Key Points"
                    )

                    if analysis["key_points"]:

                        for point in analysis["key_points"]:

                            st.markdown(
                                f"- {point}"
                            )

                    else:

                        st.info(
                            "No key points could be extracted."
                        )

                    complete_analysis = (
                        "SMART PDF SYSTEM\n"
                        "AI DOCUMENT ANALYSIS\n\n"
                        f"Document Type: "
                        f"{analysis['document_type']}\n"
                        f"Pages: {total_pages}\n"
                        f"Words: "
                        f"{analysis['word_count']}\n"
                        f"Characters: "
                        f"{analysis['character_count']}\n\n"
                        "AI SUMMARY\n"
                        "------------\n"
                        f"{analysis['summary']}\n\n"
                        "KEY POINTS\n"
                        "----------\n"
                    )

                    for point in analysis["key_points"]:

                        complete_analysis += (
                            f"- {point}\n"
                        )

                    st.download_button(
                        "⬇️ Download AI Analysis",
                        data=complete_analysis.encode(
                            "utf-8"
                        ),
                        file_name="AI_Document_Analysis.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            except Exception as e:

                st.error(
                    f"AI analysis failed: {e}"
                )


# ============================================================
# CHAT WITH PDF
# ============================================================

elif tool == "Chat with PDF":

    st.header("💬 Chat with PDF")

    st.write(
        "Upload a PDF and ask questions about its content."
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="chat_pdf"
    )

    if uploaded_pdf:

        if (
            "rag_file_name"
            not in st.session_state
            or st.session_state.rag_file_name
            != uploaded_pdf.name
        ):

            try:

                with st.spinner(
                    "Processing PDF..."
                ):

                    uploaded_pdf.seek(0)

                    rag_data = build_rag_data(
                        uploaded_pdf
                    )

                st.session_state.rag_data = rag_data

                st.session_state.rag_file_name = (
                    uploaded_pdf.name
                )

                st.session_state.chat_history = []

                st.success(
                    "PDF processed successfully."
                )

            except Exception as e:

                st.error(
                    f"Could not process PDF: {e}"
                )

        if (
            "rag_data"
            in st.session_state
        ):

            rag_data = st.session_state.rag_data

            st.info(
                f"PDF ready. "
                f"{len(rag_data['pages'])} pages and "
                f"{len(rag_data['chunks'])} searchable sections."
            )

            question = st.text_input(
                "Ask a question about your PDF",
                placeholder=(
                    "Example: What is this document about?"
                )
            )

            if st.button(
                "💬 Ask Question",
                type="primary",
                use_container_width=True
            ):

                if not question.strip():

                    st.warning(
                        "Please enter a question."
                    )

                else:

                    try:

                        with st.spinner(
                            "Searching PDF..."
                        ):

                            response = ask_pdf(
                                rag_data,
                                question,
                                top_k=5
                            )

                        st.session_state.chat_history.append(
                            {
                                "question": question,
                                "answer": response["answer"]
                            }
                        )

                        add_pdf_history(
                            st.session_state.user_id,
                            uploaded_pdf.name,
                            "Chat with PDF"
                        )

                    except Exception as e:

                        st.error(
                            f"Question processing failed: {e}"
                        )

            if (
                "chat_history"
                in st.session_state
                and st.session_state.chat_history
            ):

                st.divider()

                st.subheader(
                    "💬 Conversation"
                )

                for chat in reversed(
                    st.session_state.chat_history
                ):

                    st.markdown(
                        f"**You:** {chat['question']}"
                    )

                    st.markdown(
                        f"**PDF Assistant:** {chat['answer']}"
                    )

                    st.divider()
# ============================================================
# PDF SECURITY
# ============================================================

elif tool == "PDF Security":

    st.header("🔐 PDF Security")

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="security_pdf"
    )

    if uploaded_pdf:

        action = st.radio(
            "Select Action",
            [
                "Check Security",
                "Password Protect",
                "Remove Password"
            ],
            horizontal=True
        )

        os.makedirs(
            "temp",
            exist_ok=True
        )

        os.makedirs(
            "output",
            exist_ok=True
        )

        input_path = os.path.join(
            "temp",
            "security_input.pdf"
        )

        with open(
            input_path,
            "wb"
        ) as file:

            file.write(
                uploaded_pdf.getbuffer()
            )

        if action == "Check Security":

            try:

                status = get_security_status(
                    input_path
                )

                if status["encrypted"]:

                    st.error(
                        "🔒 This PDF is password protected."
                    )

                else:

                    st.success(
                        "🔓 This PDF is not password protected."
                    )

                st.info(
                    f"Total Pages: {status['pages']}"
                )

            except Exception as e:

                st.error(
                    f"Security check failed: {e}"
                )

        elif action == "Password Protect":

            password = st.text_input(
                "Enter Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button(
                "🔐 Protect PDF",
                type="primary",
                use_container_width=True
            ):

                if not password:

                    st.warning(
                        "Please enter a password."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    output_path = os.path.join(
                        "output",
                        "protected_pdf.pdf"
                    )

                    try:

                        protect_pdf(
                            input_path,
                            output_path,
                            password
                        )

                        add_pdf_history(
                            st.session_state.user_id,
                            "protected_pdf.pdf",
                            "PDF Security"
                        )

                        st.success(
                            "PDF protected successfully."
                        )

                        with open(
                            output_path,
                            "rb"
                        ) as file:

                            pdf_data = file.read()

                        st.download_button(
                            "⬇️ Download Protected PDF",
                            data=pdf_data,
                            file_name="protected_pdf.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                    except Exception as e:

                        st.error(
                            f"Protection failed: {e}"
                        )

        elif action == "Remove Password":

            password = st.text_input(
                "Enter Current Password",
                type="password"
            )

            if st.button(
                "🔓 Remove Password",
                type="primary",
                use_container_width=True
            ):

                if not password:

                    st.warning(
                        "Please enter the current password."
                    )

                else:

                    output_path = os.path.join(
                        "output",
                        "unlocked_pdf.pdf"
                    )

                    try:

                        remove_pdf_password(
                            input_path,
                            output_path,
                            password
                        )

                        add_pdf_history(
                            st.session_state.user_id,
                            "unlocked_pdf.pdf",
                            "PDF Security"
                        )

                        st.success(
                            "PDF password removed successfully."
                        )

                        with open(
                            output_path,
                            "rb"
                        ) as file:

                            pdf_data = file.read()

                        st.download_button(
                            "⬇️ Download Unlocked PDF",
                            data=pdf_data,
                            file_name="unlocked_pdf.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                    except Exception as e:

                        st.error(
                            f"Password removal failed: {e}"
                        )

# ============================================================
# DASHBOARD
# ============================================================

elif tool == "Dashboard":

    st.header("🏠 Dashboard")

    st.write(
        f"Welcome back, **{st.session_state.username}** 👋"
    )

    history = get_pdf_history(
        st.session_state.user_id
    )

    total_operations = len(history)

    merger_count = sum(
        1
        for item in history
        if item["operation"] == "PDF Merger"
    )

    security_count = sum(
        1
        for item in history
        if item["operation"] == "PDF Security"
    )

    chat_count = sum(
        1
        for item in history
        if item["operation"] == "Chat with PDF"
    )

    ocr_count = sum(
        1
        for item in history
        if item["operation"] == "OCR"
    )

    splitter_count = sum(
        1
        for item in history
        if item["operation"] == "PDF Splitter"
    )

    compressor_count = sum(
        1
        for item in history
        if item["operation"] == "PDF Compressor"
    )

    converter_count = sum(
        1
        for item in history
        if item["operation"] in [
            "Images → PDF",
            "PDF → Images"
        ]
    )

    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    st.divider()

    st.subheader("📊 System Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📄 Total Operations",
            total_operations
        )

    with col2:
        st.metric(
            "🔗 PDFs Merged",
            merger_count
        )

    with col3:
        st.metric(
            "🔐 Security Operations",
            security_count
        )

    with col4:
        st.metric(
            "💬 PDF Chats",
            chat_count
        )

    # ========================================================
    # QUICK ACTIONS
    # ========================================================

    st.divider()

    st.subheader("⚡ Quick Actions")

    st.write(
        "Quickly access your most-used PDF tools."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "📎 Merge PDF",
            use_container_width=True
        ):
            st.session_state.selected_tool = "PDF Merger"
            st.rerun()

        if st.button(
            "✂️ Split PDF",
            use_container_width=True
        ):
            st.session_state.selected_tool = "PDF Splitter"
            st.rerun()

    with col2:

        if st.button(
            "📦 Compress PDF",
            use_container_width=True
        ):
            st.session_state.selected_tool = "PDF Compressor"
            st.rerun()

        if st.button(
            "🔍 OCR",
            use_container_width=True
        ):
            st.session_state.selected_tool = "OCR"
            st.rerun()

    with col3:

        if st.button(
            "🤖 AI Analysis",
            use_container_width=True
        ):
            st.session_state.selected_tool = "AI Document Analysis"
            st.rerun()

        if st.button(
            "💬 Chat with PDF",
            use_container_width=True
        ):
            st.session_state.selected_tool = "Chat with PDF"
            st.rerun()

    # ========================================================
    # TOOL ACTIVITY
    # ========================================================

    st.divider()

    st.subheader("🛠️ Tool Activity")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🔍 OCR",
            ocr_count
        )

    with col2:
        st.metric(
            "✂️ PDF Splitter",
            splitter_count
        )

    with col3:
        st.metric(
            "📦 Compressor",
            compressor_count
        )

    with col4:
        st.metric(
            "🔄 Converter",
            converter_count
        )

    # ========================================================
    # TOOL USAGE
    # ========================================================

    st.divider()

    st.subheader("📈 Tool Usage")

    tool_usage = {
        "PDF Merger": merger_count,
        "PDF Splitter": splitter_count,
        "Compressor": compressor_count,
        "Converter": converter_count,
        "OCR": ocr_count,
        "Chat with PDF": chat_count,
        "PDF Security": security_count
    }

    st.bar_chart(
        tool_usage,
        horizontal=True
    )

    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    st.divider()

    st.subheader("📜 Recent Activity")

    if history:

        for index, item in enumerate(
            history[:8],
            start=1
        ):

            col1, col2, col3 = st.columns(
                [1, 4, 2]
            )

            with col1:
                st.write(
                    f"**#{index}**"
                )

            with col2:

                st.write(
                    f"📄 **{item['file_name']}**"
                )

                st.caption(
                    f"Operation: {item['operation']}"
                )

            with col3:

                st.caption(
                    f"🕒 {item['created_at']}"
                )

    else:

        st.info(
            "No PDF operations yet. "
            "Start using the tools to see activity here."
        )

    # ========================================================
    # AVAILABLE TOOLS
    # ========================================================

    st.divider()

    st.subheader("🧰 Available Tools")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "📎 **PDF Merger**\n\n"
            "Combine multiple PDF documents "
            "into a single file."
        )

        st.info(
            "✂️ **PDF Splitter**\n\n"
            "Split PDF documents into separate files."
        )

        st.info(
            "🔍 **OCR**\n\n"
            "Extract text from scanned PDF documents."
        )

    with col2:

        st.info(
            "📑 **Page Manager**\n\n"
            "Reorder, rotate, delete and extract pages."
        )

        st.info(
            "📦 **PDF Compressor**\n\n"
            "Reduce PDF file size."
        )

        st.info(
            "🤖 **AI Document Analysis**\n\n"
            "Analyze documents and generate summaries."
        )

    with col3:

        st.info(
            "🔄 **PDF Converter**\n\n"
            "Convert images and PDF pages."
        )

        st.info(
            "💬 **Chat with PDF**\n\n"
            "Ask questions about your PDF documents."
        )

        st.info(
            "🔐 **PDF Security**\n\n"
            "Protect or unlock password-protected PDFs."
        )
    