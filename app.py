"""
Flask web application for PDF metadata analysis.
"""
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename

from pdf_analyzer import PDFMetadataAnalyzer
from utils import (
    validate_file_exists, format_metadata_for_display, get_temp_upload_path, 
    clean_temp_files, get_severity_class, filter_issues_by_category
)
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask application
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page."""
    clean_temp_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and start analysis.
    """
    # Check if the post request has the file part
    if 'pdf_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['pdf_file']
    
    # If user does not select file, browser may submit an empty file without a filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent conflicts
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # Save the file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        # Store original filename in session for display purposes
        session['original_filename'] = original_filename
        
        # Redirect to the analysis page
        return redirect(url_for('analyze', filename=unique_filename))
    
    flash('Invalid file type. Please upload a PDF file.', 'danger')
    return redirect(url_for('index'))

@app.route('/analyze/<filename>')
def analyze(filename):
    """
    Analyze an uploaded PDF file and display the results.
    """
    # Get the original filename from session
    original_filename = session.get('original_filename', filename)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    valid, message = validate_file_exists(file_path)
    
    if not valid:
        flash(f"Error: {message}", "danger")
        return redirect(url_for('index'))
    
    try:
        # Analyze the PDF
        analyzer = PDFMetadataAnalyzer(file_path)
        analyzer.extract_metadata()
        is_suspicious, issues = analyzer.analyze()
        
        # Format metadata for display
        metadata = format_metadata_for_display(analyzer.metadata)
        
        # Format issues by category for better display
        categorized_issues = filter_issues_by_category(issues)
        
        # Get severity class for UI
        severity_class = get_severity_class(is_suspicious)
        
        # Prepare analysis timestamp
        analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template(
            'result.html',
            filename=original_filename,
            metadata=metadata,
            is_suspicious=is_suspicious,
            issues=issues,
            categorized_issues=categorized_issues,
            severity_class=severity_class,
            analysis_time=analysis_time
        )
    
    except Exception as e:
        logger.error(f"Error analyzing file {filename}: {str(e)}")
        flash(f"Error analyzing file: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """
    API endpoint for analyzing PDFs.
    """
    # Check if the post request has the file part
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdf_file']
    
    # If user does not select file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        # Save the file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        try:
            # Analyze the PDF
            analyzer = PDFMetadataAnalyzer(upload_path)
            analyzer.extract_metadata()
            is_suspicious, issues = analyzer.analyze()
            
            # Format metadata
            metadata = format_metadata_for_display(analyzer.metadata)
            
            # Prepare response
            response = {
                'filename': original_filename,
                'metadata': metadata,
                'is_suspicious': is_suspicious,
                'issues': issues,
                'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"API error analyzing file {original_filename}: {str(e)}")
            return jsonify({'error': f"Analysis error: {str(e)}"}), 500
        
        finally:
            # Clean up the file
            try:
                os.remove(upload_path)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size too large error."""
    flash('File too large. Maximum file size is 16MB.', 'danger')
    return redirect(url_for('index')), 413

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 error."""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 error."""
    return render_template('index.html', error="Internal server error. Please try again later."), 500

if __name__ == '__main__':
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Clean any temporary files
    clean_temp_files()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
