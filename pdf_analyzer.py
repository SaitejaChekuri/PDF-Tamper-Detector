import os
import re
import logging
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PDFMetadataAnalyzer:
    """
    Class for analyzing PDF metadata to detect potential tampering.
    """
    # List of known legitimate PDF software
    TRUSTED_SOFTWARE = [
        'Adobe', 'Microsoft', 'Apple', 'LibreOffice', 'OpenOffice', 'Acrobat', 
        'Word', 'Google', 'Chrome', 'Safari', 'pdfTeX', 'LaTeX', 'Quartz', 
        'MacOS', 'Windows', 'Foxit', 'ABBYY', 'Nitro', 'Scribus', 'Ghostscript',
        'pdftk', 'PDFCreator', 'pdfFiller', 'pdfforge', 'PDF Architect'
    ]
    
    # List of suspicious PDF editing software
    SUSPICIOUS_SOFTWARE = [
        'PDFEditorX', 'PDFEditPro', 'QuickPDFEdit', 'PDFmodify', 'PDFhack',
        'PDFalter', 'FakePDFTool', 'PDFmodifier', 'EasyPDFEdit', 'PDFTamper'
    ]
    
    # Maximum allowed time difference between creation and modification (in days)
    MAX_REASONABLE_TIME_DIFF = 365 * 5  # 5 years
    
    # Required metadata fields for academic documents
    REQUIRED_METADATA_FIELDS = ['Author', 'Title', 'CreationDate']
    
    def __init__(self, pdf_path: str):
        """
        Initialize the analyzer with the path to a PDF file.
        
        Args:
            pdf_path: Path to the PDF file to analyze
        """
        self.pdf_path = pdf_path
        self.filename = os.path.basename(pdf_path)
        self.metadata = {}
        self.issues = []
        self.extraction_success = False
        
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the PDF file.
        
        Returns:
            Dictionary containing the extracted metadata
        """
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file)
                info = reader.metadata
                
                if info:
                    # Convert PDF metadata to dictionary
                    self.metadata = {
                        'Title': info.get('/Title', ''),
                        'Author': info.get('/Author', ''),
                        'Subject': info.get('/Subject', ''),
                        'Keywords': info.get('/Keywords', ''),
                        'Creator': info.get('/Creator', ''),
                        'Producer': info.get('/Producer', ''),
                        'CreationDate': self._parse_pdf_date(info.get('/CreationDate', '')),
                        'ModificationDate': self._parse_pdf_date(info.get('/ModDate', '')),
                        'PageCount': len(reader.pages)
                    }
                    
                    # Get additional XMP metadata if available
                    xmp_metadata = self._extract_xmp_metadata(reader)
                    if xmp_metadata:
                        self.metadata.update(xmp_metadata)
                        
                    self.extraction_success = True
                    logger.debug(f"Successfully extracted metadata from {self.filename}")
                else:
                    self.issues.append("No metadata found in the document")
                    logger.warning(f"No metadata found in {self.filename}")
            
            return self.metadata
                    
        except Exception as e:
            error_msg = f"Error extracting metadata: {str(e)}"
            self.issues.append(error_msg)
            logger.error(error_msg)
            return {}
    
    def _extract_xmp_metadata(self, reader: PdfReader) -> Dict[str, Any]:
        """
        Extract XMP metadata if available.
        
        Args:
            reader: PdfReader object
            
        Returns:
            Dictionary with XMP metadata
        """
        xmp_metadata = {}
        try:
            if hasattr(reader, 'xmp_metadata') and reader.xmp_metadata:
                # Extract any available XMP metadata
                xmp = reader.xmp_metadata
                if xmp:
                    xmp_metadata['XMP_ModifyDate'] = self._extract_xmp_date(xmp, 'ModifyDate')
                    xmp_metadata['XMP_CreateDate'] = self._extract_xmp_date(xmp, 'CreateDate')
                    xmp_metadata['XMP_MetadataDate'] = self._extract_xmp_date(xmp, 'MetadataDate')
        except Exception as e:
            logger.warning(f"Error extracting XMP metadata: {str(e)}")
        
        return xmp_metadata
    
    def _extract_xmp_date(self, xmp: Any, date_field: str) -> Optional[datetime]:
        """
        Extract a date from XMP metadata.
        
        Args:
            xmp: XMP metadata object
            date_field: Name of the date field to extract
            
        Returns:
            Datetime object or None if extraction fails
        """
        try:
            if hasattr(xmp, date_field):
                date_str = getattr(xmp, date_field)
                return self._parse_iso_date(date_str)
        except Exception:
            pass
        return None
    
    def _parse_pdf_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse PDF date format (D:YYYYMMDDHHmmSSOHH'mm') to datetime object.
        
        Args:
            date_string: PDF date string
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_string:
            return None
            
        try:
            # PDF dates are usually in format: D:YYYYMMDDHHmmSSOHH'mm'
            # Example: D:20200103112201+02'00'
            match = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})([-+Z])(\d{2})'(\d{2})'", date_string)
            
            if match:
                year, month, day, hour, minute, second, tz_sign, tz_hour, tz_minute = match.groups()
                
                dt = datetime(
                    int(year), int(month), int(day),
                    int(hour), int(minute), int(second)
                )
                
                # Apply timezone offset
                if tz_sign in ('+', '-'):
                    offset = timedelta(hours=int(tz_hour), minutes=int(tz_minute))
                    if tz_sign == '-':
                        dt += offset
                    else:
                        dt -= offset
                        
                return dt
            
            # Try alternate format without timezone
            match = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", date_string)
            if match:
                year, month, day, hour, minute, second = match.groups()
                return datetime(
                    int(year), int(month), int(day),
                    int(hour), int(minute), int(second)
                )
                
            # Try ISO format as fallback
            return self._parse_iso_date(date_string)
                
        except Exception as e:
            logger.warning(f"Date parsing error: {str(e)} for string: {date_string}")
            return None
    
    def _parse_iso_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse ISO format date string to datetime object.
        
        Args:
            date_string: ISO date string
            
        Returns:
            Datetime object or None if parsing fails
        """
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            except (ValueError, TypeError):
                return None
    
    def analyze(self) -> Tuple[bool, List[str]]:
        """
        Analyze the PDF metadata for signs of tampering.
        
        Returns:
            Tuple (is_suspicious, issues) where:
              - is_suspicious: Boolean indicating if tampering is suspected
              - issues: List of detected issues
        """
        # Extract metadata if not already done
        if not self.metadata:
            self.extract_metadata()
            
        if not self.extraction_success:
            return True, self.issues
        
        # Analyze the metadata
        self._check_date_consistency()
        self._check_software()
        self._check_missing_fields()
        self._check_date_in_future()
        self._check_file_integrity()
        
        # Determine if the document is suspicious
        is_suspicious = len(self.issues) > 0
        
        return is_suspicious, self.issues
    
    def _check_date_consistency(self) -> None:
        """Check for inconsistencies between creation and modification dates."""
        creation_date = self.metadata.get('CreationDate')
        mod_date = self.metadata.get('ModificationDate')
        
        if creation_date and mod_date:
            # Check if modification date is before creation date
            if mod_date < creation_date:
                self.issues.append(
                    f"Modification date ({mod_date}) is before creation date ({creation_date})"
                )
                
            # Check for unreasonably large time differences
            date_diff = (mod_date - creation_date).days
            if date_diff > self.MAX_REASONABLE_TIME_DIFF:
                self.issues.append(
                    f"Document was modified {date_diff} days after creation, "
                    f"which exceeds the reasonable limit of {self.MAX_REASONABLE_TIME_DIFF} days"
                )
                
        # Check for missing dates
        if creation_date and not mod_date:
            self.issues.append("Modification date is missing while creation date exists")
            
        # Check XMP metadata consistency if available
        xmp_create = self.metadata.get('XMP_CreateDate')
        xmp_modify = self.metadata.get('XMP_ModifyDate')
        
        if creation_date and xmp_create and abs((creation_date - xmp_create).total_seconds()) > 60:
            self.issues.append(
                f"XMP creation date ({xmp_create}) doesn't match PDF creation date ({creation_date})"
            )
            
        if mod_date and xmp_modify and abs((mod_date - xmp_modify).total_seconds()) > 60:
            self.issues.append(
                f"XMP modification date ({xmp_modify}) doesn't match PDF modification date ({mod_date})"
            )
    
    def _check_software(self) -> None:
        """Check for suspicious software in the producer/creator fields."""
        producer = str(self.metadata.get('Producer', '')).strip()
        creator = str(self.metadata.get('Creator', '')).strip()
        
        if producer:
            # Check against list of suspicious software
            for sus_sw in self.SUSPICIOUS_SOFTWARE:
                if sus_sw.lower() in producer.lower():
                    self.issues.append(f"Suspicious editing software detected: {sus_sw}")
                    
            # Check if the producer is not in the trusted list
            if not any(trusted.lower() in producer.lower() for trusted in self.TRUSTED_SOFTWARE):
                self.issues.append(f"Unknown PDF producer software: {producer}")
                
        # Check the creator field too
        if creator:
            for sus_sw in self.SUSPICIOUS_SOFTWARE:
                if sus_sw.lower() in creator.lower():
                    self.issues.append(f"Suspicious creator software detected: {sus_sw}")
    
    def _check_missing_fields(self) -> None:
        """Check for missing metadata fields that are typically required."""
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in self.metadata or not self.metadata[field]:
                self.issues.append(f"Required metadata field '{field}' is missing")
                
        # Check for empty metadata
        if not any(self.metadata.values()):
            self.issues.append("All metadata fields are empty")
    
    def _check_date_in_future(self) -> None:
        """Check if any dates are set in the future."""
        now = datetime.now()
        
        for date_field in ['CreationDate', 'ModificationDate', 'XMP_CreateDate', 'XMP_ModifyDate']:
            date_value = self.metadata.get(date_field)
            if date_value and date_value > now:
                self.issues.append(f"{date_field} is set in the future: {date_value}")
    
    def _check_file_integrity(self) -> None:
        """
        Check for basic file integrity issues that might indicate tampering.
        """
        try:
            # Re-open the file to check for basic integrity
            with open(self.pdf_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Check if we can access all pages
                for i in range(len(reader.pages)):
                    try:
                        _ = reader.pages[i].extract_text(0, 10)  # Just try to extract a small bit
                    except Exception:
                        self.issues.append(f"Page {i+1} appears corrupted or tampered with")
                        break
                
                # Check document information consistency
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        if key.startswith('/'):
                            clean_key = key[1:]
                            metadata_key = clean_key
                            if clean_key == 'ModDate':
                                metadata_key = 'ModificationDate'
                            elif clean_key == 'CreationDate':
                                metadata_key = 'CreationDate'
                                
                            if metadata_key in self.metadata and value != self.metadata[metadata_key]:
                                if isinstance(self.metadata[metadata_key], datetime):
                                    # Skip datetime comparisons as they are handled elsewhere
                                    continue
                                self.issues.append(
                                    f"Inconsistent metadata value for {clean_key}: "
                                    f"{value} vs {self.metadata[metadata_key]}"
                                )
                
        except Exception as e:
            self.issues.append(f"File integrity check failed: {str(e)}")
    
    def get_formatted_report(self) -> str:
        """
        Generate a formatted report of the metadata analysis.
        
        Returns:
            String containing the formatted report
        """
        if not self.metadata:
            self.extract_metadata()
            
        is_suspicious, issues = self.analyze()
        
        report = [f"Analyzing file: {self.filename}"]
        
        # Add metadata information
        for key, value in self.metadata.items():
            if value:  # Only include non-empty values
                report.append(f"{key}: {value}")
        
        # Add analysis results
        if is_suspicious:
            report.append("\n⚠️ Tampering Detected:")
            for issue in issues:
                report.append(f"- {issue}")
        else:
            report.append("\n✅ No tampering detected. Document appears clean.")
            
        return "\n".join(report)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the analysis as a dictionary.
        
        Returns:
            Dictionary containing analysis summary
        """
        if not self.metadata:
            self.extract_metadata()
            
        is_suspicious, issues = self.analyze()
        
        return {
            'filename': self.filename,
            'metadata': self.metadata,
            'is_suspicious': is_suspicious,
            'issues': issues,
            'extraction_success': self.extraction_success
        }
