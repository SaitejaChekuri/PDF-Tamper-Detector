/**
 * Main JavaScript file for PDF Metadata Analyzer
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // Setup file input validation and UI feedback
    const fileInput = document.getElementById('pdf_file');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            validateFileInput(event.target);
        });
    }

    // Setup form submission feedback
    const uploadForm = document.querySelector('.upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            const fileInput = this.querySelector('input[type="file"]');
            if (fileInput && fileInput.files.length > 0) {
                // Show loading state
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
                }
            }
        });
    }

    // Initialize collapsible elements
    const accordionElements = document.querySelectorAll('.accordion-button');
    if (accordionElements.length > 0) {
        accordionElements.forEach(button => {
            button.addEventListener('click', function() {
                this.classList.toggle('collapsed');
                const target = document.querySelector(this.getAttribute('data-bs-target'));
                if (target) {
                    target.classList.toggle('show');
                }
            });
        });
    }

    // Initialize tooltips if Bootstrap JS is loaded
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Validate the file input to ensure it's a PDF
 * @param {HTMLInputElement} fileInput - The file input element
 */
function validateFileInput(fileInput) {
    const feedbackElement = fileInput.nextElementSibling;
    const submitButton = fileInput.form.querySelector('button[type="submit"]');

    if (fileInput.files.length === 0) {
        // No file selected
        fileInput.classList.remove('is-valid');
        fileInput.classList.remove('is-invalid');
        if (feedbackElement) {
            feedbackElement.textContent = 'Maximum file size: 16MB';
        }
        if (submitButton) {
            submitButton.disabled = false;
        }
        return;
    }

    const file = fileInput.files[0];
    const fileSize = file.size / 1024 / 1024; // Size in MB
    const fileType = file.type;
    const fileName = file.name;

    // Check if it's a PDF file
    if (fileType !== 'application/pdf' && !fileName.toLowerCase().endsWith('.pdf')) {
        fileInput.classList.remove('is-valid');
        fileInput.classList.add('is-invalid');
        if (feedbackElement) {
            feedbackElement.textContent = 'Please select a PDF file';
            feedbackElement.className = 'invalid-feedback d-block';
        }
        if (submitButton) {
            submitButton.disabled = true;
        }
        return;
    }

    // Check file size
    if (fileSize > 16) {
        fileInput.classList.remove('is-valid');
        fileInput.classList.add('is-invalid');
        if (feedbackElement) {
            feedbackElement.textContent = 'File is too large. Maximum size is 16MB';
            feedbackElement.className = 'invalid-feedback d-block';
        }
        if (submitButton) {
            submitButton.disabled = true;
        }
        return;
    }

    // File is valid
    fileInput.classList.remove('is-invalid');
    fileInput.classList.add('is-valid');
    if (feedbackElement) {
        feedbackElement.textContent = `Selected: ${fileName} (${fileSize.toFixed(2)} MB)`;
        feedbackElement.className = 'form-text';
    }
    if (submitButton) {
        submitButton.disabled = false;
    }
}
