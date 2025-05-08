/**
 * Unstructured RAG Web UI
 * Main JavaScript file
 */

// API URL
const API_URL = 'http://localhost:8000';

// DOM Elements
const elements = {
    // Navigation
    navLinks: document.querySelectorAll('nav a'),
    pages: document.querySelectorAll('.page'),
    
    // Home page
    uploadBtn: document.getElementById('upload-btn'),
    queryBtn: document.getElementById('query-btn'),
    
    // Documents page
    documentLoading: document.getElementById('document-loading'),
    documentError: document.getElementById('document-error'),
    documentTable: document.getElementById('document-table'),
    documentEmpty: document.getElementById('document-empty'),
    documentList: document.getElementById('document-list'),
    uploadDocumentBtn: document.getElementById('upload-document-btn'),
    retryDocumentsBtn: document.getElementById('retry-documents-btn'),
    emptyUploadBtn: document.getElementById('empty-upload-btn'),
    
    // Query interface
    queryInterface: document.getElementById('query-interface'),
    closeQueryBtn: document.getElementById('close-query-btn'),
    conversationContainer: document.getElementById('conversation-container'),
    queryInput: document.getElementById('query-input'),
    sendQueryBtn: document.getElementById('send-query-btn'),
    
    // Upload modal
    uploadModal: document.getElementById('upload-modal'),
    closeUploadBtn: document.getElementById('close-upload-btn'),
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    selectedFile: document.getElementById('selected-file'),
    fileName: document.getElementById('file-name'),
    removeFileBtn: document.getElementById('remove-file-btn'),
    uploadProgress: document.getElementById('upload-progress'),
    progressFill: document.getElementById('progress-fill'),
    progressText: document.getElementById('progress-text'),
    uploadSuccess: document.getElementById('upload-success'),
    uploadError: document.getElementById('upload-error'),
    errorMessage: document.getElementById('error-message'),
    cancelUploadBtn: document.getElementById('cancel-upload-btn'),
    confirmUploadBtn: document.getElementById('confirm-upload-btn'),
    
    // Overlay
    overlay: document.getElementById('overlay')
};

// State
const state = {
    currentPage: 'home',
    documents: [],
    selectedFile: null,
    isUploading: false,
    conversation: []
};

// Initialize
function init() {
    // Setup event listeners
    setupEventListeners();
    
    // Check if URL has hash for navigation
    const hash = window.location.hash.substring(1);
    if (hash && ['home', 'documents', 'about'].includes(hash)) {
        navigateTo(hash);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    elements.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.target.dataset.page;
            navigateTo(page);
        });
    });
    
    // Hash change
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.substring(1);
        if (hash && ['home', 'documents', 'about'].includes(hash)) {
            navigateTo(hash);
        }
    });
    
    // Home page buttons
    elements.uploadBtn.addEventListener('click', openUploadModal);
    elements.queryBtn.addEventListener('click', openQueryInterface);
    
    // Documents page
    elements.uploadDocumentBtn.addEventListener('click', openUploadModal);
    elements.retryDocumentsBtn.addEventListener('click', loadDocuments);
    elements.emptyUploadBtn.addEventListener('click', openUploadModal);
    
    // Query interface
    elements.closeQueryBtn.addEventListener('click', closeQueryInterface);
    elements.queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    });
    elements.sendQueryBtn.addEventListener('click', sendQuery);
    
    // Upload modal
    elements.closeUploadBtn.addEventListener('click', closeUploadModal);
    elements.cancelUploadBtn.addEventListener('click', closeUploadModal);
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.removeFileBtn.addEventListener('click', removeSelectedFile);
    elements.confirmUploadBtn.addEventListener('click', uploadFile);
    
    // Drag and drop
    elements.uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.add('dragover');
    });
    
    elements.uploadArea.addEventListener('dragleave', () => {
        elements.uploadArea.classList.remove('dragover');
    });
    
    elements.uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect({ target: { files: e.dataTransfer.files } });
        }
    });
    
    // Overlay
    elements.overlay.addEventListener('click', () => {
        closeUploadModal();
        closeQueryInterface();
    });
}

// Navigation
function navigateTo(page) {
    // Update state
    state.currentPage = page;
    
    // Update hash
    window.location.hash = page;
    
    // Update navigation
    elements.navLinks.forEach(link => {
        if (link.dataset.page === page) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Update pages
    elements.pages.forEach(pageEl => {
        if (pageEl.id === page) {
            pageEl.classList.add('active');
            
            // Load data if needed
            if (page === 'documents' && state.documents.length === 0) {
                loadDocuments();
            }
        } else {
            pageEl.classList.remove('active');
        }
    });
}

// Load documents
async function loadDocuments() {
    // Show loading
    elements.documentLoading.classList.remove('hidden');
    elements.documentError.classList.add('hidden');
    elements.documentTable.classList.add('hidden');
    elements.documentEmpty.classList.add('hidden');
    
    try {
        // Fetch documents
        const response = await fetch(`${API_URL}/documents`);
        
        if (!response.ok) {
            throw new Error('Failed to load documents');
        }
        
        const data = await response.json();
        state.documents = data.documents || [];
        
        // Update UI
        elements.documentLoading.classList.add('hidden');
        
        if (state.documents.length === 0) {
            elements.documentEmpty.classList.remove('hidden');
        } else {
            elements.documentTable.classList.remove('hidden');
            renderDocumentList();
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        
        // Show error
        elements.documentLoading.classList.add('hidden');
        elements.documentError.classList.remove('hidden');
    }
}

// Render document list
function renderDocumentList() {
    const documentListHTML = state.documents.map(doc => {
        // Format the date
        const uploadDate = new Date(doc.upload_time);
        const formattedDate = uploadDate.toLocaleDateString() + ' ' + uploadDate.toLocaleTimeString();
        
        // Get file extension
        const fileExtension = doc.filename.split('.').pop().toLowerCase();
        
        // Determine icon based on file type
        let fileIcon = 'fa-file';
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
        
        // Determine status badge
        let statusBadgeClass = 'uploaded';
        if (doc.status === 'processing') {
            statusBadgeClass = 'processing';
        } else if (doc.status === 'processed') {
            statusBadgeClass = 'processed';
        } else if (doc.status === 'error') {
            statusBadgeClass = 'error';
        }
        
        return `
            <tr data-id="${doc.id}">
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas ${fileIcon}"></i>
                        ${doc.filename}
                    </div>
                </td>
                <td>${fileExtension.toUpperCase()}</td>
                <td>${formattedDate}</td>
                <td><span class="status-badge ${statusBadgeClass}">${doc.status}</span></td>
                <td>
                    <div class="actions">
                        <button class="action-btn query" title="Query this document" data-id="${doc.id}">
                            <i class="fas fa-search"></i>
                        </button>
                        <button class="action-btn delete" title="Delete document" data-id="${doc.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    elements.documentList.innerHTML = documentListHTML;
    
    // Add event listeners for action buttons
    document.querySelectorAll('.action-btn.query').forEach(btn => {
        btn.addEventListener('click', () => {
            const docId = btn.dataset.id;
            openQueryInterfaceForDocument(docId);
        });
    });
    
    document.querySelectorAll('.action-btn.delete').forEach(btn => {
        btn.addEventListener('click', () => {
            const docId = btn.dataset.id;
            deleteDocument(docId);
        });
    });
}

// Delete document
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/documents/${docId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete document');
        }
        
        // Remove from state
        state.documents = state.documents.filter(doc => doc.id !== docId);
        
        // Update UI
        if (state.documents.length === 0) {
            elements.documentTable.classList.add('hidden');
            elements.documentEmpty.classList.remove('hidden');
        } else {
            renderDocumentList();
        }
    } catch (error) {
        console.error('Error deleting document:', error);
        alert('Failed to delete document. Please try again.');
    }
}

// Open query interface
function openQueryInterface() {
    elements.queryInterface.classList.add('active');
    elements.overlay.classList.add('active');
    elements.queryInput.focus();
}

// Open query interface for specific document
function openQueryInterfaceForDocument(docId) {
    // Set the current document ID to state or similar
    state.currentDocumentId = docId;
    
    // Open the query interface
    openQueryInterface();
    
    // Maybe add a message to the conversation
    const doc = state.documents.find(d => d.id === docId);
    if (doc) {
        addSystemMessage(`Now querying document: ${doc.filename}`);
    }
}

// Close query interface
function closeQueryInterface() {
    elements.queryInterface.classList.remove('active');
    elements.overlay.classList.remove('active');
}

// Send query
async function sendQuery() {
    const query = elements.queryInput.value.trim();
    
    if (!query) {
        return;
    }
    
    // Add user message to conversation
    addUserMessage(query);
    
    // Clear input
    elements.queryInput.value = '';
    
    // Create query payload
    const payload = {
        query: query
    };
    
    // Add document ID if we're querying a specific document
    if (state.currentDocumentId) {
        payload.document_ids = [state.currentDocumentId];
    }
    
    try {
        // Show loading
        addSystemMessage('Thinking...', 'loading');
        
        // Send query
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error('Failed to query');
        }
        
        const data = await response.json();
        
        // Remove loading message
        removeLoadingMessage();
        
        // Add system message
        addSystemMessage(data.answer, 'response', data.sources);
        
    } catch (error) {
        console.error('Error querying:', error);
        
        // Remove loading message
        removeLoadingMessage();
        
        // Add error message
        addSystemMessage('Failed to get a response. Please try again.', 'error');
    }
}

// Add user message to conversation
function addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message user';
    messageEl.innerHTML = `
        <div class="message-content">${escapeHTML(message)}</div>
        <div class="message-meta">
            <span class="time">${formatTime(new Date())}</span>
        </div>
    `;
    
    elements.conversationContainer.appendChild(messageEl);
    
    // Scroll to bottom
    elements.conversationContainer.scrollTop = elements.conversationContainer.scrollHeight;
    
    // Add to state
    state.conversation.push({
        type: 'user',
        message,
        timestamp: new Date()
    });
}

// Add system message to conversation
function addSystemMessage(message, type = 'normal', sources = []) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message system';
    
    let messageContent = '';
    
    if (type === 'loading') {
        messageContent = `
            <div class="message-content loading-message">
                <i class="fas fa-spinner fa-spin"></i> ${message}
            </div>
        `;
    } else if (type === 'error') {
        messageContent = `
            <div class="message-content error-message">
                <i class="fas fa-exclamation-circle"></i> ${message}
            </div>
        `;
    } else if (type === 'response') {
        messageContent = `
            <div class="message-content">
                ${escapeHTML(message)}
                ${sources && sources.length > 0 ? `
                    <div class="sources">
                        <strong>Sources:</strong>
                        ${sources.map(source => `
                            <span class="source">${escapeHTML(source.document_name)}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    } else {
        messageContent = `
            <div class="message-content">
                ${escapeHTML(message)}
            </div>
        `;
    }
    
    messageEl.innerHTML = `
        ${messageContent}
        <div class="message-meta">
            <span class="time">${formatTime(new Date())}</span>
        </div>
    `;
    
    elements.conversationContainer.appendChild(messageEl);
    
    // Scroll to bottom
    elements.conversationContainer.scrollTop = elements.conversationContainer.scrollHeight;
    
    // Add to state (except loading messages)
    if (type !== 'loading') {
        state.conversation.push({
            type: 'system',
            message,
            messageType: type,
            sources,
            timestamp: new Date()
        });
    }
}

// Remove loading message
function removeLoadingMessage() {
    const loadingMessage = document.querySelector('.loading-message');
    if (loadingMessage) {
        loadingMessage.parentElement.parentElement.remove();
    }
}

// Open upload modal
function openUploadModal() {
    elements.uploadModal.classList.add('active');
    elements.overlay.classList.add('active');
    
    // Reset state
    resetUploadState();
}

// Close upload modal
function closeUploadModal() {
    elements.uploadModal.classList.remove('active');
    elements.overlay.classList.remove('active');
    
    // Reset state
    resetUploadState();
}

// Reset upload state
function resetUploadState() {
    state.selectedFile = null;
    state.isUploading = false;
    
    elements.selectedFile.classList.add('hidden');
    elements.uploadProgress.classList.add('hidden');
    elements.uploadSuccess.classList.add('hidden');
    elements.uploadError.classList.add('hidden');
    elements.confirmUploadBtn.disabled = true;
    elements.fileInput.value = '';
}

// Handle file select
function handleFileSelect(e) {
    if (e.target.files.length === 0) {
        return;
    }
    
    const file = e.target.files[0];
    
    // Update state
    state.selectedFile = file;
    
    // Update UI
    elements.fileName.textContent = file.name;
    elements.selectedFile.classList.remove('hidden');
    elements.confirmUploadBtn.disabled = false;
}

// Remove selected file
function removeSelectedFile() {
    // Update state
    state.selectedFile = null;
    
    // Update UI
    elements.selectedFile.classList.add('hidden');
    elements.confirmUploadBtn.disabled = true;
    elements.fileInput.value = '';
}

// Upload file
async function uploadFile() {
    if (!state.selectedFile || state.isUploading) {
        return;
    }
    
    // Update state
    state.isUploading = true;
    
    // Update UI
    elements.uploadProgress.classList.remove('hidden');
    elements.confirmUploadBtn.disabled = true;
    elements.progressFill.style.width = '0%';
    elements.progressText.textContent = 'Uploading... 0%';
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', state.selectedFile);
        
        // Create request
        const xhr = new XMLHttpRequest();
        
        // Setup progress event
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                elements.progressFill.style.width = `${percentComplete}%`;
                elements.progressText.textContent = `Uploading... ${percentComplete}%`;
            }
        });
        
        // Setup load event
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                // Success
                elements.uploadProgress.classList.add('hidden');
                elements.uploadSuccess.classList.remove('hidden');
                
                // Reset state after delay
                setTimeout(() => {
                    closeUploadModal();
                    
                    // Reload documents if on documents page
                    if (state.currentPage === 'documents') {
                        loadDocuments();
                    }
                }, 1500);
            } else {
                // Error
                let errorMsg = 'Upload failed. Please try again.';
                
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.detail) {
                        errorMsg = response.detail;
                    }
                } catch (e) {
                    // Ignore parse errors
                }
                
                elements.errorMessage.textContent = errorMsg;
                elements.uploadProgress.classList.add('hidden');
                elements.uploadError.classList.remove('hidden');
                
                // Reset upload state
                state.isUploading = false;
            }
        });
        
        // Setup error event
        xhr.addEventListener('error', () => {
            elements.errorMessage.textContent = 'Network error. Please try again.';
            elements.uploadProgress.classList.add('hidden');
            elements.uploadError.classList.remove('hidden');
            
            // Reset upload state
            state.isUploading = false;
        });
        
        // Send request
        xhr.open('POST', `${API_URL}/documents/ingest`);
        xhr.send(formData);
        
    } catch (error) {
        console.error('Error uploading file:', error);
        
        elements.errorMessage.textContent = 'Upload failed. Please try again.';
        elements.uploadProgress.classList.add('hidden');
        elements.uploadError.classList.remove('hidden');
        
        // Reset upload state
        state.isUploading = false;
    }
}

// Utility functions
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\n/g, '<br>');
}

// Initialize on DOM loaded
document.addEventListener('DOMContentLoaded', init);
