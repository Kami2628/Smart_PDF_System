# Smart PDF Document Management & AI Processing System
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![PDF](https://img.shields.io/badge/PDF-Management-green)

A professional Python-based application for managing, processing, securing, and analyzing PDF documents using Artificial Intelligence.

## Project Overview

The Smart PDF System is designed to simplify PDF document management through a user-friendly web interface. It combines essential PDF tools with AI-powered document summarization, OCR, and document question-answering capabilities.

## Features

## How to Use

1. Install Python 3.11 or a compatible Python version.
2. Clone or download this repository.
3. Create and activate a Python virtual environment.
4. Install the required dependencies using `python -m pip install -r requirements.txt`.
5. Install and configure Tesseract OCR for OCR functionality.
6. Start the application using `streamlit run app.py`.
7. Open the application in your browser.
8. Sign up or log in, select a PDF tool, upload a document, and follow the on-screen instructions.

## Future Enhancements

- Improved document search and retrieval.
- Additional document conversion formats.
- Enhanced authentication and access control.
- Cloud storage integration.
- Automated testing and deployment.
- Improved AI response accuracy and performance.

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
