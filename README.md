# Smart PDF Document Management & AI Processing System

A professional Python-based application for managing, processing, securing, and analyzing PDF documents using Artificial Intelligence.

## Project Overview

The Smart PDF System is designed to simplify PDF document management through a user-friendly web interface. It combines essential PDF tools with AI-powered document summarization, OCR, and document question-answering capabilities.

## Features

- **PDF Merger:** Merge multiple PDF files into one document.
- **PDF Page Manager:** Preview, reorder, rotate, delete, and extract pages.
- **PDF Splitter:** Split PDF documents into separate files.
- **PDF Compressor:** Reduce PDF file size.
- **PDF Converter:** Convert images to PDF and PDF pages to images.
- **OCR:** Extract text from scanned PDF documents.
- **AI Document Analysis:** Generate summaries of document content.
- **Chat with PDF:** Ask questions about uploaded PDF documents.
- **PDF Security:** Add or remove PDF passwords and check document protection.
- **User Authentication:** Login and signup functionality.
- **Dashboard:** Access tools and view application activity.
- **PDF History:** Search and review recorded document operations.

## Technologies Used

- Python
- Streamlit
- PyPDF
- PyMuPDF
- Pillow
- Hugging Face Transformers
- PyTorch
- Tesseract OCR
- SQLite

## Project Structure

    Smart_PDF_System/
    ├── app.py
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    ├── core/
    │   ├── pdf_engine.py
    │   ├── ai_engine.py
    │   ├── rag_engine.py
    │   ├── security_engine.py
    │   ├── database.py
    │   └── auth.py
    ├── utils/
    │   └── file_utils.py
    ├── assets/
    ├── output/
    └── temp/

## Installation and Setup

### 1. Clone the Repository

    git clone https://github.com/YOUR_USERNAME/Smart_PDF_System.git
    cd Smart_PDF_System

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

    py -3.11 -m venv venv

### 3. Activate the Environment on Windows

    .\venv\Scripts\Activate.ps1

If PowerShell blocks activation, run:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

Then activate the environment again.

### 4. Install Dependencies

    python -m pip install -r requirements.txt

### 5. Install Tesseract OCR

Install Tesseract OCR for Windows and ensure its executable is accessible to the application.

Official project: https://github.com/tesseract-ocr/tesseract

### 6. Run the Application

    streamlit run app.py

The application will open in your browser.

## AI Functionality

The AI document analysis feature uses a Hugging Face Transformers summarization model. The chat-with-PDF feature retrieves relevant document content to help answer questions about uploaded files.

The first model download may take time and requires an internet connection.

## Database and Data

SQLite is used to store application records. Local database files, generated PDFs, temporary files, and virtual environments should not be committed to the public repository.

## Future Improvements

- Improved document search and retrieval.
- More file conversion options.
- Enhanced authentication and access control.
- Cloud storage integration.
- Automated testing and deployment.

## Academic Project

Developed as a Final Year Project (FYP) focused on PDF document management, automation, and AI-assisted document processing.

## License

This project is available for educational and academic use. Add a suitable open-source license before redistributing it under specific license terms.