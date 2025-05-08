/**
 * Enhanced Upload Functionality
 */

// Additional DOM Elements
const uploadElements = {
    // Tab navigation
    tabFiles: document.getElementById('tab-files'),
    tabDirectory: document.getElementById('tab-directory'),

    // Inputs
    fileInput: document.getElementById('file-input'),
    directoryInput: document.getElementById('directory-input'),

    // Selected files
    selectedFiles: document.getElementById('selected-files'),
    filesCount: document.getElementById('files-count'),
    filesList: document.getElementById('files-list'),
    removeAllFilesBtn: document.getElementById('remove-all-files-btn'),

    // Upload elements
    uploadArea: document.getElementById('upload-area'),
    uploadProgress: document.getElementById('upload-progress'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    uploadSuccess: document.getElementById('upload-success'),
    uploadError: document.getElementById('upload-error'),
    errorMessage: document.getElementById('error-message'),

    // Buttons
    confirmUploadBtn: document.getElementById('confirm-upload-btn'),
    cancelUploadBtn: document.getElementById('cancel-upload-btn'),
    closeUploadBtn: document.getElementById('close-upload-btn'),
};

// Upload state
const uploadState = {
    files: [],
    activeTab: 'files',
    isUploading: false,
    uploadedCount: 0,
    failedCount: 0,
};

// Initialize upload functionality
function initUpload() {
    // Setup event listeners
    setupUploadEventListeners();
}

// Setup upload event listeners
function setupUploadEventListeners() {
    // Tab switching
    uploadElements.tabFiles.addEventListener('click', () => switchUploadTab('files'));
    uploadElements.tabDirectory.addEventListener('click', () => switchUploadTab('directory'));

    // File selection
    uploadElements.fileInput.addEventListener('change', handleFilesSelect);
    uploadElements.directoryInput.addEventListener('change', handleFilesSelect);

    // Upload area click
    uploadElements.uploadArea.addEventListener('click', () => {
        if (uploadState.activeTab === 'files') {
            uploadElements.fileInput.click();
        } else {
            uploadElements.directoryInput.click();
        }
    });

    // Drag and drop
    uploadElements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadElements.uploadArea.classList.add('dragover');
    });

    uploadElements.uploadArea.addEventListener('dragleave', () => {
        uploadElements.uploadArea.classList.remove('dragover');
    });

    uploadElements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadElements.uploadArea.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFilesSelect({ target: { files: e.dataTransfer.files } });
        }
    });

    // Remove all files
    uploadElements.removeAllFilesBtn.addEventListener('click', removeAllFiles);

    // Upload button
    uploadElements.confirmUploadBtn.addEventListener('click', uploadFiles);
}

// Switch between file and directory upload tabs
function switchUploadTab(tab) {
    uploadState.activeTab = tab;

    // Update tab UI
    if (tab === 'files') {
        uploadElements.tabFiles.classList.add('active');
        uploadElements.tabDirectory.classList.remove('active');
        uploadElements.uploadArea.querySelector('p').textContent = 'Drag & drop files here or click to select';

        // Hide directory info if it exists
        const dirInfo = document.querySelector('.directory-info');
        if (dirInfo) dirInfo.remove();

    } else {
        uploadElements.tabFiles.classList.remove('active');
        uploadElements.tabDirectory.classList.add('active');
        uploadElements.uploadArea.querySelector('p').textContent = 'Click to select a directory for upload';

        // Add directory upload explanation
        const modalBody = document.querySelector('.modal-body');
        if (!document.querySelector('.directory-info')) {
            const dirInfo = document.createElement('div');
            dirInfo.className = 'directory-info';
            dirInfo.innerHTML = '<i class="fas fa-info-circle"></i> Directory upload will process all supported files in the selected folder. Supported formats: PDF, DOCX, HTML, TXT, CSV, JSON.';
            uploadElements.uploadArea.insertAdjacentElement('afterend', dirInfo);
        }
    }
}

// Handle file selection
function handleFilesSelect(e) {
    if (!e.target.files || e.target.files.length === 0) {
        return;
    }

    // Clear previous upload progress and errors
    uploadElements.uploadProgress.classList.add('hidden');
    uploadElements.uploadSuccess.classList.add('hidden');
    uploadElements.uploadError.classList.add('hidden');

    // Add files to state
    const newFiles = Array.from(e.target.files);
    uploadState.files = [...uploadState.files, ...newFiles];

    // Update UI
    updateFilesListUI();
}

// Update the files list UI
function updateFilesListUI() {
    const { files } = uploadState;

    if (files.length === 0) {
        uploadElements.selectedFiles.classList.add('hidden');
        uploadElements.confirmUploadBtn.disabled = true;
        return;
    }

    // Show files panel and enable upload button
    uploadElements.selectedFiles.classList.remove('hidden');
    uploadElements.confirmUploadBtn.disabled = false;

    // Update files count
    uploadElements.filesCount.textContent = files.length === 1
        ? '1 file selected'
        : `${files.length} files selected`;

    // Generate list HTML
    const filesListHTML = files.map((file, index) => {
        // Get file icon based on type
        let fileIcon = 'fa-file';
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (['pdf'].includes(fileExtension)) {
            fileIcon = 'fa-file-pdf';
        } else if (['doc', 'docx'].includes(fileExtension)) {
            fileIcon = 'fa-file-word';
        } else if (['html', 'htm'].includes(fileExtension)) {
            fileIcon = 'fa-file-code';
        } else if (['txt', 'md', 'rtf'].includes(fileExtension)) {
            fileIcon = 'fa-file-alt';
        } else if (['csv'].includes(fileExtension)) {
            fileIcon = 'fa-file-csv';
        } else if (['json'].includes(fileExtension)) {
            fileIcon = 'fa-file-code';
        }

        // Format file size
        const formattedSize = formatFileSize(file.size);

        return `
            <div class="file-item" data-index="${index}">
                <i class="fas ${fileIcon}"></i>
                <span class="file-name" title="${file.name}">${file.name}</span>
                <span class="file-size">${formattedSize}</span>
                <button class="remove-file-btn" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }).join('');

    uploadElements.filesList.innerHTML = filesListHTML;

    // Add event listeners for remove buttons
    document.querySelectorAll('.remove-file-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            removeFile(index);
        });
    });
}

// Remove a file from the list
function removeFile(index) {
    uploadState.files.splice(index, 1);
    updateFilesListUI();
}

// Remove all files
function removeAllFiles() {
    uploadState.files = [];
    updateFilesListUI();
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Upload files
async function uploadFiles() {
    if (uploadState.files.length === 0 || uploadState.isUploading) {
        return;
    }

    // Update state
    uploadState.isUploading = true;
    uploadState.uploadedCount = 0;
    uploadState.failedCount = 0;

    // Update UI
    uploadElements.uploadProgress.classList.remove('hidden');
    uploadElements.uploadSuccess.classList.add('hidden');
    uploadElements.uploadError.classList.add('hidden');
    uploadElements.confirmUploadBtn.disabled = true;
    uploadElements.progressFill.style.width = '0%';
    uploadElements.progressText.textContent = 'Preparing upload...';

    // Determine if we're doing individual uploads or batch upload
    const totalFiles = uploadState.files.length;
    const API_URL = 'http://localhost:8000';

    // For small number of files, upload individually
    // For large number of files or directory upload, use batch endpoint
    const useBatchUpload = totalFiles > 5 || uploadState.activeTab === 'directory';

    if (useBatchUpload) {
        // Batch upload - use multi-file endpoint
        try {
            // Create form data with all files
            const formData = new FormData();
            uploadState.files.forEach(file => {
                // Preserve directory structure for directory uploads
                formData.append('files', file);
            });

            // Determine the correct endpoint based on the active tab
            const endpoint = uploadState.activeTab === 'directory'
                ? `${API_URL}/documents/ingest-directory`
                : `${API_URL}/documents/ingest-multi`;

            // Send request with progress tracking
            const xhr = new XMLHttpRequest();

            // Set up progress event
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 100);
                    uploadElements.progressFill.style.width = `${percentComplete}%`;
                    uploadElements.progressText.textContent = `Uploading... ${percentComplete}%`;
                }
            });

            // Set up completion handler
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);

                        // Process results for each file
                        if (response.results) {
                            response.results.forEach(result => {
                                // Find the file item by name
                                const filename = result.filename;
                                const fileItem = Array.from(document.querySelectorAll('.file-item')).find(
                                    item => item.querySelector('.file-name').textContent === filename
                                );

                                if (fileItem) {
                                    // Remove previous status indicators
                                    fileItem.querySelectorAll('.file-uploaded, .file-error').forEach(el => el.remove());
                                    fileItem.classList.remove('uploading');

                                    if (result.status === 'success') {
                                        // Add success indicator
                                        uploadState.uploadedCount++;
                                        const successEl = document.createElement('span');
                                        successEl.className = 'file-uploaded';
                                        successEl.innerHTML = '<i class="fas fa-check"></i>';
                                        fileItem.appendChild(successEl);
                                    } else {
                                        // Add error indicator
                                        uploadState.failedCount++;
                                        const errorEl = document.createElement('span');
                                        errorEl.className = 'file-error';
                                        errorEl.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                                        errorEl.title = result.error || 'Upload failed';
                                        fileItem.appendChild(errorEl);
                                    }
                                }
                            });
                        }

                        // Update final UI
                        finalizeUpload();

                    } catch (e) {
                        console.error('Error parsing response:', e);
                        uploadElements.uploadError.classList.remove('hidden');
                        uploadElements.errorMessage.textContent = 'Error processing server response';
                        uploadState.isUploading = false;
                    }
                } else {
                    // Error response
                    let errorMsg = 'Batch upload failed';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.error) {
                            errorMsg = response.error;
                        }
                    } catch (e) {
                        // Ignore parse errors
                    }

                    uploadElements.uploadError.classList.remove('hidden');
                    uploadElements.errorMessage.textContent = errorMsg;
                    uploadState.isUploading = false;
                }
            });

            // Set up error handler
            xhr.addEventListener('error', () => {
                uploadElements.uploadError.classList.remove('hidden');
                uploadElements.errorMessage.textContent = 'Network error occurred during batch upload';
                uploadState.isUploading = false;
            });

            // Send the request
            xhr.open('POST', endpoint);
            xhr.send(formData);

        } catch (error) {
            console.error('Error in batch upload:', error);
            uploadElements.uploadError.classList.remove('hidden');
            uploadElements.errorMessage.textContent = 'Error preparing batch upload: ' + error.message;
            uploadState.isUploading = false;
        }
    } else {
        // Individual file upload
        for (let i = 0; i < totalFiles; i++) {
            const file = uploadState.files[i];

            try {
                // Highlight current file in the list
                const fileItem = document.querySelector(`.file-item[data-index="${i}"]`);
                if (fileItem) {
                    // Remove previous upload status
                    fileItem.querySelectorAll('.file-uploaded, .file-error').forEach(el => el.remove());

                    // Add "uploading" class
                    fileItem.classList.add('uploading');
                }

                // Update progress
                const progress = Math.round((i / totalFiles) * 100);
                uploadElements.progressFill.style.width = `${progress}%`;
                uploadElements.progressText.textContent = `Uploading file ${i + 1} of ${totalFiles}...`;

                // Create form data for this file
                const formData = new FormData();
                formData.append('files', file);

                // Send request
                const response = await fetch(`${API_URL}/documents/ingest`, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    // File uploaded successfully
                    uploadState.uploadedCount++;

                    // Add success indicator to file item
                    if (fileItem) {
                        fileItem.classList.remove('uploading');
                        const successEl = document.createElement('span');
                        successEl.className = 'file-uploaded';
                        successEl.innerHTML = '<i class="fas fa-check"></i>';
                        fileItem.appendChild(successEl);
                    }
                } else {
                    // Upload failed
                    uploadState.failedCount++;

                    // Get error message
                    let errorMsg = 'Upload failed';
                    try {
                        const errorData = await response.json();
                        if (errorData.detail) {
                            errorMsg = errorData.detail;
                        }
                    } catch (e) {
                        // Ignore parse errors
                    }

                    // Add error indicator to file item
                    if (fileItem) {
                        fileItem.classList.remove('uploading');
                        const errorEl = document.createElement('span');
                        errorEl.className = 'file-error';
                        errorEl.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                        errorEl.title = errorMsg;
                        fileItem.appendChild(errorEl);
                    }
                }
            } catch (error) {
                // Handle network errors
                uploadState.failedCount++;

                // Add error indicator to file item
                const fileItem = document.querySelector(`.file-item[data-index="${i}"]`);
                if (fileItem) {
                    fileItem.classList.remove('uploading');
                    const errorEl = document.createElement('span');
                    errorEl.className = 'file-error';
                    errorEl.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                    errorEl.title = 'Network error';
                    fileItem.appendChild(errorEl);
                }
            }
        }

        // Finalize the upload process
        finalizeUpload();
    }
}

// Finalize the upload process
function finalizeUpload() {
    // Update final progress
    uploadElements.progressFill.style.width = '100%';
    uploadElements.progressText.textContent = `Upload complete: ${uploadState.uploadedCount} succeeded, ${uploadState.failedCount} failed`;

    // Show success or error message
    if (uploadState.failedCount === 0) {
        uploadElements.uploadSuccess.classList.remove('hidden');

        // Reset state after delay
        setTimeout(() => {
            // Reload documents if on documents page
            if (state.currentPage === 'documents') {
                loadDocuments();
            }

            // Close the upload modal
            closeUploadModal();

            // Reset the upload form
            uploadState.files = [];
            updateFilesListUI();
            uploadElements.uploadProgress.classList.add('hidden');
            uploadElements.uploadSuccess.classList.add('hidden');

            // Open query interface to allow user to query the uploaded documents
            if (uploadState.successCount > 0) {
                setTimeout(() => {
                    // Use the global openQueryInterface function from main.js
                    if (typeof window.openQueryInterface === 'function') {
                        window.openQueryInterface();
                    } else {
                        console.error('openQueryInterface function not found');
                    }
                }, 500);
            }
        }, 1500);
    } else {
        uploadElements.uploadError.classList.remove('hidden');
        uploadElements.errorMessage.textContent = `${uploadState.failedCount} files failed to upload. Check the file list for details.`;
    }

    // Reset upload state
    uploadState.isUploading = false;
}

// Close upload modal - using the function from main.js
function closeUploadModal() {
    const uploadModal = document.getElementById('upload-modal');
    const overlay = document.getElementById('overlay');

    if (uploadModal) {
        uploadModal.classList.remove('active');
    }

    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Initialize on main script load
document.addEventListener('DOMContentLoaded', initUpload);
