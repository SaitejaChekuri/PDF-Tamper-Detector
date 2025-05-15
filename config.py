"""
Configuration settings for the PDF Metadata Analyzer application.
"""

import os
from datetime import timedelta

# Flask application settings
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "development-key-change-in-production")
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'temp_uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
ALLOWED_EXTENSIONS = {'pdf'}

# Create the upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Temporary file cleanup settings
TEMP_FILE_MAX_AGE = timedelta(minutes=30)
CLEANUP_INTERVAL = timedelta(hours=1)

# PDF Analysis settings
PDF_ANALYSIS_SETTINGS = {
    'max_reasonable_time_diff': 365 * 5,  # 5 years in days
    'required_metadata_fields': ['Author', 'Title', 'CreationDate'],
    'trusted_software': [
        'Adobe', 'Microsoft', 'Apple', 'LibreOffice', 'OpenOffice', 'Acrobat', 
        'Word', 'Google', 'Chrome', 'Safari', 'pdfTeX', 'LaTeX', 'Quartz', 
        'MacOS', 'Windows', 'Foxit', 'ABBYY', 'Nitro', 'Scribus', 'Ghostscript',
        'pdftk', 'PDFCreator', 'pdfFiller', 'pdfforge', 'PDF Architect'
    ],
    'suspicious_software': [
        'PDFEditorX', 'PDFEditPro', 'QuickPDFEdit', 'PDFmodify', 'PDFhack',
        'PDFalter', 'FakePDFTool', 'PDFmodifier', 'EasyPDFEdit', 'PDFTamper'
    ]
}

# Web interface settings
WEB_SETTINGS = {
    'items_per_page': 10,
    'session_lifetime': timedelta(hours=1)
}
