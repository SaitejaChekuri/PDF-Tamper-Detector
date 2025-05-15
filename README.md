# PDF Metadata Analyzer

A Python-based tool for detecting potential PDF tampering through metadata analysis. This tool can help identify inconsistencies in PDF metadata that might indicate document manipulation.

## Features

- Analyzes PDF metadata to detect signs of tampering
- Identifies suspicious editing software
- Checks for inconsistent creation and modification dates
- Detects missing metadata fields
- Validates document integrity
- Available as both a web application and command-line tool

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pdf-metadata-analyzer.git
cd pdf-metadata-analyzer
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application

Run the web application:

```bash
python main.py
```

Then open your browser and navigate to http://localhost:5000

### Command-Line Interface

Analyze a single PDF file:

```bash
python main.py path/to/your/document.pdf
```

Analyze multiple PDF files:

```bash
python main.py path/to/document1.pdf path/to/document2.pdf
```

Additional CLI options:

```bash
python main.py --help
```

## Example Output

```
Analyzing file: sample_transcript.pdf
CreationDate: 2022-06-15 12:30:00
ModificationDate: 2025-05-09 18:45:00
Author: John Doe
Producer: PDFEditorX

⚠️ Tampering Detected:
- Document was modified 1059 days after creation, which exceeds the reasonable limit of 1825 days
- Suspicious editing software detected: PDFEditorX
```
## Sample output
![image](https://github.com/user-attachments/assets/bca36fb6-3d0d-4509-b51a-af9736d141b5)
![image](https://github.com/user-attachments/assets/1f1b5b32-5738-4388-8639-d1793c80193a)
![image](https://github.com/user-attachments/assets/233b506d-0509-4452-b2db-54dc52e48bcd)

## Project Structure

- `main.py` - Main entry point for both web and CLI
- `app.py` - Flask web application
- `pdf_analyzer.py` - Core PDF analysis functionality
- `cli.py` - Command-line interface
- `utils.py` - Helper utilities
- `config.py` - Configuration settings
- `templates/` - HTML templates for web interface
- `static/` - CSS and JavaScript files for web interface

## How It Works

The PDF Metadata Analyzer examines metadata embedded in PDF files, looking for:

1. **Date Inconsistencies**: Checks if modification dates are before creation dates or far in the future
2. **Suspicious Software**: Identifies PDFs created with known suspicious editing tools
3. **Metadata Completeness**: Verifies required metadata fields are present
4. **Document Integrity**: Examines basic file structure for signs of tampering

## Limitations

- Only detects tampering that affects metadata
- Cannot detect content changes that preserve metadata
- False positives may occur with legitimate documents missing metadata
- Advanced forgeries might clean/fake metadata
