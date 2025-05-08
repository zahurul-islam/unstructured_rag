/**
 * Unstructured RAG Web UI
 * Main JavaScript file
 */

// API URL - Not used directly as we go through the Flask proxy
const API_URL = window.location.origin;

// DOM Elements
let elements = {};

// Function to initialize DOM elements
function initElements() {
    elements = {
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
        queryContainer: document.querySelector('.query-container'),
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

    return elements;
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
    console.log("Initializing application...");

    // Initialize DOM elements
    initElements();

    // Setup event listeners
    setupEventListeners();

    // Setup query form - we'll now do this only when the query interface is opened
    // to avoid issues with the form not being fully loaded yet
    // setupQueryForm();

    // Add additional event listeners directly
    const closeQueryBtn = document.getElementById('close-query-btn');
    if (closeQueryBtn) {
        closeQueryBtn.addEventListener('click', handleCloseButtonClick);
        console.log("Added event listener to close query button");
    }

    // Setup query input key event handler
    const queryForm = document.getElementById('query-form');
    if (queryForm) {
        queryForm.addEventListener('submit', handleQueryFormSubmit);
        console.log("Added submit event to query form");
    }

    // Check if URL has hash for navigation
    const hash = window.location.hash.substring(1);
    if (hash && ['home', 'documents', 'about'].includes(hash)) {
        navigateTo(hash);
    }

    console.log("Application initialized successfully");
}

// Setup query form
function setupQueryForm() {
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const sendQueryBtn = document.getElementById('send-query-btn');
    const closeQueryBtn = document.getElementById('close-query-btn');

    if (queryForm && queryInput && sendQueryBtn) {
        // Remove any existing event listeners (use try-catch to avoid errors if listeners weren't added)
        try {
            queryForm.removeEventListener('submit', handleQueryFormSubmit);
            queryInput.removeEventListener('keydown', handleQueryInputKeydown);
            sendQueryBtn.removeEventListener('click', handleSendButtonClick);
            if (closeQueryBtn) {
                closeQueryBtn.removeEventListener('click', handleCloseButtonClick);
            }
        } catch (e) {
            console.log("No previous event listeners to remove");
        }

        // Add event listeners
        queryForm.addEventListener('submit', handleQueryFormSubmit);
        queryInput.addEventListener('keydown', handleQueryInputKeydown);
        sendQueryBtn.addEventListener('click', handleSendButtonClick);
        if (closeQueryBtn) {
            closeQueryBtn.addEventListener('click', handleCloseButtonClick);
        }

        // Clear any existing conversation content except welcome message
        const conversationContainer = document.getElementById('conversation-container');
        if (conversationContainer) {
            // Keep only the welcome message
            const welcomeMessage = conversationContainer.querySelector('.welcome-message');
            if (welcomeMessage) {
                conversationContainer.innerHTML = '';
                conversationContainer.appendChild(welcomeMessage);
            }
        }

        console.log("Query form setup complete");
    } else {
        console.error("Could not find query form elements");
    }
}

// Handle query form submit
function handleQueryFormSubmit(e) {
    console.log("Query form submit event");
    if (e) {
        e.preventDefault();
        e.stopPropagation();
    }
    sendQuery();
    return false;
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

    // Query interface - add direct event listener to the close button
    const closeQueryBtn = document.getElementById('close-query-btn');
    if (closeQueryBtn) {
        closeQueryBtn.addEventListener('click', (e) => {
            console.log("Close query button clicked");
            e.preventDefault();
            e.stopPropagation();
            closeQueryInterface();
        });
    }

    // Make sure query input and send button are properly wired
    const queryInput = document.getElementById('query-input');
    const sendQueryBtn = document.getElementById('send-query-btn');

    if (queryInput) {
        queryInput.addEventListener('keydown', handleQueryInputKeydown);
    }

    if (sendQueryBtn) {
        sendQueryBtn.addEventListener('click', handleSendButtonClick);
    }

    // Upload modal basic navigation (the detailed functionality is in upload.js)
    elements.closeUploadBtn.addEventListener('click', closeUploadModal);
    elements.cancelUploadBtn.addEventListener('click', closeUploadModal);

    // Overlay
    elements.overlay.addEventListener('click', (e) => {
        // Only close if the overlay itself was clicked, not its children
        if (e.target === elements.overlay) {
            closeUploadModal();
            closeQueryInterface();
        }
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
// Making this function available globally for use in upload.js
window.openQueryInterface = function() {
    console.log("Opening query interface");

    // Show the query interface and overlay first
    const queryInterface = document.getElementById('query-interface');
    const overlay = document.getElementById('overlay');

    if (queryInterface) {
        queryInterface.classList.add('active');
    }

    if (overlay) {
        overlay.classList.add('active');
    }

    // Refresh the conversation display (welcome message or existing conversation)
    refreshConversation();

    // Setup the query form and event listeners
    setupQueryForm();

    // Make sure close button has an event listener
    const closeQueryBtn = document.getElementById('close-query-btn');
    if (closeQueryBtn) {
        closeQueryBtn.removeEventListener('click', handleCloseButtonClick);
        closeQueryBtn.addEventListener('click', handleCloseButtonClick);
        console.log("Close button event listener attached");
    }

    // Focus the input field
    const queryInput = document.getElementById('query-input');
    if (queryInput) {
        setTimeout(() => {
            queryInput.focus();
            console.log("Focused query input");
        }, 300);
    }

    console.log("Query interface opened and initialized");
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
    console.log("Closing query interface");
    const queryInterface = document.getElementById('query-interface');
    const overlay = document.getElementById('overlay');

    if (queryInterface) {
        queryInterface.classList.remove('active');
    }

    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Send query
async function sendQuery() {
    console.log("sendQuery function called");

    // Get the query input element directly from the DOM
    const queryInput = document.getElementById('query-input');
    if (!queryInput) {
        console.error("Query input element not found");
        return;
    }

    // Get the query text
    const query = queryInput.value.trim();
    console.log("Query text:", query);

    if (!query) {
        console.log("Empty query, not sending");
        return;
    }

    // Get the conversation container
    const conversationContainer = document.getElementById('conversation-container');
    if (!conversationContainer) {
        console.error("Conversation container not found");
        return;
    }

    // First, remove the welcome message if it exists
    const welcomeMessage = conversationContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Add user message to conversation
    const userMessageEl = document.createElement('div');
    userMessageEl.className = 'message user';
    userMessageEl.innerHTML = `
        <div class="message-content">${escapeHTML(query)}</div>
        <div class="message-meta">
            <span class="time">${formatTime(new Date())}</span>
        </div>
    `;
    conversationContainer.appendChild(userMessageEl);

    // Scroll to bottom
    conversationContainer.scrollTop = conversationContainer.scrollHeight;

    // Update the conversation state first so we don't lose this message
    state.conversation.push({
        type: 'user',
        message: query,
        timestamp: new Date()
    });

    // Save the message count before sending query
    const messageCountBefore = conversationContainer.childElementCount;
    console.log(`Message count before sending query: ${messageCountBefore}`);

    // Clear input
    queryInput.value = '';

    // Create query payload
    const payload = {
        query: query
    };

    // Add document ID if we're querying a specific document
    if (state.currentDocumentId) {
        payload.document_ids = [state.currentDocumentId];
    }

    try {
        // Show loading message
        const loadingMessageEl = document.createElement('div');
        loadingMessageEl.className = 'message system loading-indicator';
        loadingMessageEl.innerHTML = `
            <div class="message-content loading-message">
                <i class="fas fa-spinner fa-spin"></i> Thinking...
            </div>
            <div class="message-meta">
                <span class="time">${formatTime(new Date())}</span>
            </div>
        `;
        conversationContainer.appendChild(loadingMessageEl);

        // Scroll to bottom
        conversationContainer.scrollTop = conversationContainer.scrollHeight;

        // Disable input and button while processing
        queryInput.disabled = true;

        const sendQueryBtn = document.getElementById('send-query-btn');
        if (sendQueryBtn) {
            sendQueryBtn.disabled = true;
        }

        console.log("Sending query to API:", payload);

        // Send query to our proxy endpoint on the Flask server, not directly to the API
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Failed to query: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Received response:", data);

        // Store the message count after receiving response (before removing loading)
        const messageCountAfterResponse = conversationContainer.childElementCount;
        console.log(`Message count after response: ${messageCountAfterResponse}`);

        // Remove loading message - use a class selector to make sure we get the right one
        const loadingMessages = document.querySelectorAll('.loading-indicator');
        loadingMessages.forEach(msg => {
            if (msg) {
                msg.remove();
            }
        });

        // Verify message count after removing loading message
        const messageCountAfterLoading = conversationContainer.childElementCount;
        console.log(`Message count after removing loading: ${messageCountAfterLoading}`);

        // Add system message with response
        const responseMessageEl = document.createElement('div');
        responseMessageEl.className = 'message system';

        let messageContent = `
            <div class="message-content">
                ${escapeHTML(data.answer)}
                ${data.sources && data.sources.length > 0 ? `
                    <div class="sources">
                        <strong>📚 Sources Referenced (${data.sources.length}):</strong>
                        ${data.sources.map((source, index) => {
                            // Clean up document name
                            let docName = source.document_name;

                            // Remove file extension if present
                            if (docName.includes('.')) {
                                docName = docName.split('.').slice(0, -1).join('.');
                            }

                            // Handle different document types
                            let icon = '📄';
                            if (docName.toLowerCase().includes('pdf')) icon = '📕';
                            else if (docName.toLowerCase().includes('doc')) icon = '📘';
                            else if (docName.toLowerCase().includes('txt')) icon = '📃';

                            // Make document names more readable
                            if (docName.toLowerCase().includes('llm')) {
                                docName = 'LLM Guide';
                            } else if (docName.length > 8 && docName.includes('-')) {
                                // Try to extract a meaningful name or use a generic one
                                docName = `Document ${index + 1}`;
                            }

                            return `<span class="source" title="${escapeHTML(source.document_name)}">${icon} ${escapeHTML(docName)}</span>`;
                        }).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        responseMessageEl.innerHTML = `
            ${messageContent}
            <div class="message-meta">
                <span class="time">${formatTime(new Date())}</span>
            </div>
        `;

        conversationContainer.appendChild(responseMessageEl);

        // Add to conversation state
        state.conversation.push({
            type: 'system',
            message: data.answer,
            sources: data.sources || [],
            timestamp: new Date()
        });

        // Double-check message count after adding response
        const finalMessageCount = conversationContainer.childElementCount;
        console.log(`Final message count: ${finalMessageCount}`);

        // Scroll to bottom
        conversationContainer.scrollTop = conversationContainer.scrollHeight;

    } catch (error) {
        console.error('Error querying:', error);

        // Remove loading message
        const loadingMessages = document.querySelectorAll('.loading-indicator');
        loadingMessages.forEach(msg => {
            if (msg) {
                msg.remove();
            }
        });

        // Add error message
        const errorMessageEl = document.createElement('div');
        errorMessageEl.className = 'message system';
        errorMessageEl.innerHTML = `
            <div class="message-content error-message">
                <i class="fas fa-exclamation-circle"></i> Failed to get a response: ${error.message}
            </div>
            <div class="message-meta">
                <span class="time">${formatTime(new Date())}</span>
            </div>
        `;

        conversationContainer.appendChild(errorMessageEl);

        // Scroll to bottom
        conversationContainer.scrollTop = conversationContainer.scrollHeight;
    } finally {
        // Re-enable input and button
        queryInput.disabled = false;

        const sendQueryBtn = document.getElementById('send-query-btn');
        if (sendQueryBtn) {
            sendQueryBtn.disabled = false;
        }

        // Focus the input field again
        queryInput.focus();

        // Log the conversation state
        console.log("Current conversation state:", state.conversation);
    }
}

// Add user message to conversation
function addUserMessage(message) {
    // Get conversation container directly from DOM
    const conversationContainer = document.getElementById('conversation-container');
    if (!conversationContainer) {
        console.error("Conversation container not found");
        return;
    }

    // First, remove the welcome message if it exists
    const welcomeMessage = conversationContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageEl = document.createElement('div');
    messageEl.className = 'message user';
    messageEl.innerHTML = `
        <div class="message-content">${escapeHTML(message)}</div>
        <div class="message-meta">
            <span class="time">${formatTime(new Date())}</span>
        </div>
    `;

    conversationContainer.appendChild(messageEl);

    // Scroll to bottom
    conversationContainer.scrollTop = conversationContainer.scrollHeight;

    // Add to state
    state.conversation.push({
        type: 'user',
        message,
        timestamp: new Date()
    });

    console.log("Added user message to conversation:", message);
    console.log("Current conversation state length:", state.conversation.length);
}

// Add system message to conversation
function addSystemMessage(message, type = 'normal', sources = []) {
    // Get conversation container directly from DOM to avoid any issues with elements object
    const conversationContainer = document.getElementById('conversation-container');
    if (!conversationContainer) {
        console.error("Conversation container not found");
        return;
    }

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
                        <strong>📚 Sources Referenced (${sources.length}):</strong>
                        ${sources.map((source, index) => {
                            // Clean up document name
                            let docName = source.document_name;

                            // Remove file extension if present
                            if (docName.includes('.')) {
                                docName = docName.split('.').slice(0, -1).join('.');
                            }

                            // Handle different document types
                            let icon = '📄';
                            if (docName.toLowerCase().includes('pdf')) icon = '📕';
                            else if (docName.toLowerCase().includes('doc')) icon = '📘';
                            else if (docName.toLowerCase().includes('txt')) icon = '📃';

                            // Make document names more readable
                            if (docName.toLowerCase().includes('llm')) {
                                docName = 'LLM Guide';
                            } else if (docName.length > 8 && docName.includes('-')) {
                                // Try to extract a meaningful name or use a generic one
                                docName = `Document ${index + 1}`;
                            }

                            return `<span class="source" title="${escapeHTML(source.document_name)}">${icon} ${escapeHTML(docName)}</span>`;
                        }).join('')}
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

    conversationContainer.appendChild(messageEl);

    // Scroll to bottom
    conversationContainer.scrollTop = conversationContainer.scrollHeight;

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

    console.log("Added system message:", message);
    console.log("Current conversation state length:", state.conversation.length);
}

// Function to refresh the conversation display
function refreshConversation() {
    const conversationContainer = document.getElementById('conversation-container');
    if (!conversationContainer) {
        console.error("Conversation container not found");
        return;
    }

    // Clear the container
    conversationContainer.innerHTML = '';

    // If no conversation, add welcome message
    if (!state.conversation || state.conversation.length === 0) {
        conversationContainer.innerHTML = `
            <div class="welcome-message">
                <h4>Welcome to the RAG Query Interface</h4>
                <p>Ask any questions about your uploaded documents!</p>
            </div>
        `;
        return;
    }

    // Rebuild from state
    state.conversation.forEach(msg => {
        if (msg.type === 'user') {
            const userMessageEl = document.createElement('div');
            userMessageEl.className = 'message user';
            userMessageEl.innerHTML = `
                <div class="message-content">${escapeHTML(msg.message)}</div>
                <div class="message-meta">
                    <span class="time">${formatTime(msg.timestamp)}</span>
                </div>
            `;
            conversationContainer.appendChild(userMessageEl);
        } else if (msg.type === 'system') {
            const responseMessageEl = document.createElement('div');
            responseMessageEl.className = 'message system';

            let messageContent = `
                <div class="message-content">
                    ${escapeHTML(msg.message)}
                    ${msg.sources && msg.sources.length > 0 ? `
                        <div class="sources">
                            <strong>📚 Sources Referenced (${msg.sources.length}):</strong>
                            ${msg.sources.map((source, index) => {
                                // Clean up document name
                                let docName = source.document_name;

                                // Remove file extension if present
                                if (docName.includes('.')) {
                                    docName = docName.split('.').slice(0, -1).join('.');
                                }

                                // Handle different document types
                                let icon = '📄';
                                if (docName.toLowerCase().includes('pdf')) icon = '📕';
                                else if (docName.toLowerCase().includes('doc')) icon = '📘';
                                else if (docName.toLowerCase().includes('txt')) icon = '📃';

                                // Make document names more readable
                                if (docName.toLowerCase().includes('llm')) {
                                    docName = 'LLM Guide';
                                } else if (docName.length > 8 && docName.includes('-')) {
                                    // Try to extract a meaningful name or use a generic one
                                    docName = `Document ${index + 1}`;
                                }

                                return `<span class="source" title="${escapeHTML(source.document_name)}">${icon} ${escapeHTML(docName)}</span>`;
                            }).join('')}
                        </div>
                    ` : ''}
                </div>
            `;

            responseMessageEl.innerHTML = `
                ${messageContent}
                <div class="message-meta">
                    <span class="time">${formatTime(msg.timestamp)}</span>
                </div>
            `;
            conversationContainer.appendChild(responseMessageEl);
        }
    });

    // Scroll to bottom
    conversationContainer.scrollTop = conversationContainer.scrollHeight;
    console.log("Refreshed conversation display with", state.conversation.length, "messages");
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

// Reset modal state (actual upload reset is handled in upload.js)
function resetUploadState() {
    // This basic version just resets the UI elements
    // The detailed functionality is in upload.js
    elements.uploadProgress.classList.add('hidden');
    elements.uploadSuccess.classList.add('hidden');
    elements.uploadError.classList.add('hidden');
}

// These functions have been replaced by improved versions in upload.js
// Keeping empty function definitions for backward compatibility
function handleFileSelect(e) {}
function removeSelectedFile() {}
function uploadFile() {}

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

// Handle Enter key in query input
function handleQueryInputKeydown(e) {
    console.log("Query input keydown event:", e.key);
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        e.stopPropagation(); // Prevent event from bubbling up
        console.log("Enter key pressed, sending query");
        sendQuery();
        return false;
    }
}

// Handle send button click
function handleSendButtonClick(e) {
    console.log("Send button clicked");
    if (e) {
        e.preventDefault();
        e.stopPropagation(); // Prevent event from bubbling up
    }
    sendQuery();
    return false;
}

// Handle close button click
function handleCloseButtonClick(e) {
    console.log("Close button clicked");
    if (e) {
        e.preventDefault();
        e.stopPropagation(); // Prevent event from bubbling up
    }
    closeQueryInterface();
    return false;
}

// Stop event propagation
function stopPropagation(e) {
    e.stopPropagation();
}

// Initialize on DOM loaded
document.addEventListener('DOMContentLoaded', init);
