"""
Main entry point for the PDF Metadata Analyzer.
"""
import os
import sys
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Check if running in command line mode
    if len(sys.argv) > 1:
        # Import and run the CLI
        from cli import main
        main()
    else:
        # Run the web application
        app.run(host='0.0.0.0', port=5000, debug=True)
