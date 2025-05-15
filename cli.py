#!/usr/bin/env python3
"""
Command-line interface for the PDF Metadata Analyzer.
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

from pdf_analyzer import PDFMetadataAnalyzer
from utils import validate_file_exists, format_metadata_for_display

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Analyze PDF metadata to detect potential tampering."
    )
    
    parser.add_argument(
        'pdf_files', 
        nargs='+', 
        help='Path(s) to the PDF file(s) to analyze'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Write results to the specified file instead of stdout'
    )
    
    parser.add_argument(
        '-s', '--summary',
        action='store_true',
        help='Only show summary results (suspicious/clean)'
    )
    
    return parser.parse_args()

def analyze_pdf_file(file_path: str, verbose: bool = False, summary_only: bool = False) -> str:
    """
    Analyze a single PDF file and return the results.
    
    Args:
        file_path: Path to the PDF file
        verbose: If True, include verbose output
        summary_only: If True, only show the summary result
        
    Returns:
        String with analysis results
    """
    valid, message = validate_file_exists(file_path)
    if not valid:
        return f"Error: {message}"
    
    analyzer = PDFMetadataAnalyzer(file_path)
    
    if verbose and not summary_only:
        # For verbose output, show the full formatted report
        return analyzer.get_formatted_report()
    
    # Extract and analyze metadata
    analyzer.extract_metadata()
    is_suspicious, issues = analyzer.analyze()
    
    if summary_only:
        # Only show if the file is suspicious or not
        if is_suspicious:
            return f"{file_path}: ⚠️ SUSPICIOUS - {len(issues)} issues detected"
        else:
            return f"{file_path}: ✅ CLEAN"
    
    # Regular output shows metadata and issues
    metadata = analyzer.metadata
    formatted_metadata = format_metadata_for_display(metadata)
    
    result = [f"Analyzing file: {os.path.basename(file_path)}"]
    
    # Add key metadata
    for key in ['CreationDate', 'ModificationDate', 'Author', 'Producer']:
        if key in formatted_metadata:
            result.append(f"{key}: {formatted_metadata[key]}")
    
    # Add analysis results
    if is_suspicious:
        result.append("\n⚠️ Tampering Detected:")
        for issue in issues:
            result.append(f"- {issue}")
    else:
        result.append("\n✅ No tampering detected. Document appears clean.")
    
    return "\n".join(result)

def main() -> None:
    """
    Main function for the command-line interface.
    """
    args = parse_arguments()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    results: List[str] = []
    
    # Analyze each PDF file provided
    for pdf_file in args.pdf_files:
        result = analyze_pdf_file(pdf_file, args.verbose, args.summary)
        results.append(result)
        
        # Add a separator if analyzing multiple files
        if len(args.pdf_files) > 1:
            results.append("\n" + "-" * 50 + "\n")
    
    # Remove the last separator if it exists
    if len(results) > 1 and results[-1].strip() == "-" * 50:
        results.pop()
    
    output_text = "\n".join(results)
    
    # Write output to file or stdout
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_text)
            print(f"Results written to {args.output}")
        except Exception as e:
            logger.error(f"Error writing to output file: {str(e)}")
            print(output_text)
    else:
        print(output_text)

if __name__ == "__main__":
    main()
