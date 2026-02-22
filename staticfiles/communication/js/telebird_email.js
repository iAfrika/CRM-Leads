// Telebird Email Client Interactions
document.addEventListener('DOMContentLoaded', function() {
    const emailContainer = document.querySelector('.telebird-email-container');
    const emailItems = document.querySelectorAll('.telebird-email-item');
    const emailPreviewPane = document.querySelector('.telebird-email-preview-pane');
    const composeButton = document.querySelector('#telebird-compose-btn');
    const sidebarFolders = document.querySelectorAll('.telebird-folder-list li');

    // Email Item Selection
    emailItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active state from all email items
            emailItems.forEach(el => el.classList.remove('active'));
            
            // Add active state to clicked item
            this.classList.add('active');
            
            // Load email preview
            const emailId = this.dataset.emailId;
            loadEmailPreview(emailId);
        });
    });

    // Compose Email
    if (composeButton) {
        composeButton.addEventListener('click', function() {
            window.location.href = this.dataset.composeUrl;
        });
    }

    // Folder Navigation
    sidebarFolders.forEach(folder => {
        folder.addEventListener('click', function() {
            const folderType = this.dataset.folderType;
            navigateToFolder(folderType);
        });
    });

    // Load Email Preview via AJAX
    function loadEmailPreview(emailId) {
        fetch(`/email/view/${emailId}/`)
            .then(response => response.json())
            .then(data => {
                if (emailPreviewPane) {
                    emailPreviewPane.innerHTML = `
                        <div class="email-preview-header">
                            <h4>${data.subject}</h4>
                            <div class="email-meta">
                                <span class="sender">${data.sender}</span>
                                <span class="date">${data.sent_at}</span>
                            </div>
                        </div>
                        <div class="email-preview-body">
                            ${data.body}
                        </div>
                        ${data.attachments ? renderAttachments(data.attachments) : ''}
                    `;
                }
            })
            .catch(error => {
                console.error('Error loading email preview:', error);
                if (emailPreviewPane) {
                    emailPreviewPane.innerHTML = '<p>Unable to load email preview.</p>';
                }
            });
    }

    // Render Email Attachments
    function renderAttachments(attachments) {
        return `
            <div class="email-attachments">
                <h5>Attachments</h5>
                <ul>
                    ${attachments.map(attachment => `
                        <li>
                            <a href="${attachment.url}" download>
                                <i class="fas fa-file"></i> ${attachment.filename}
                            </a>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    // Navigate to Specific Folder
    function navigateToFolder(folderType) {
        switch(folderType) {
            case 'inbox':
                window.location.href = '/email/inbox/';
                break;
            case 'sent':
                window.location.href = '/email/sent/';
                break;
            case 'drafts':
                window.location.href = '/email/drafts/';
                break;
            case 'trash':
                window.location.href = '/email/trash/';
                break;
            default:
                console.warn('Unknown folder type:', folderType);
        }
    }

    // Responsive Design Adjustments
    function adjustLayout() {
        const screenWidth = window.innerWidth;
        if (screenWidth <= 768) {
            emailContainer.classList.add('mobile-view');
        } else {
            emailContainer.classList.remove('mobile-view');
        }
    }

    // Initial layout adjustment and event listener
    adjustLayout();
    window.addEventListener('resize', adjustLayout);

    // Email Action Buttons
    const replyButton = document.querySelector('.btn[title="Reply"]');
    const replyAllButton = document.querySelector('.btn[title="Reply All"]');
    const forwardButton = document.querySelector('.btn[title="Forward"]');

    if (replyButton) {
        replyButton.addEventListener('click', function() {
            const currentEmailId = getCurrentEmailId();
            if (currentEmailId) {
                window.location.href = `/email/reply/${currentEmailId}/`;
            } else {
                console.warn('No email selected to reply to');
            }
        });
    }

    if (replyAllButton) {
        replyAllButton.addEventListener('click', function() {
            const currentEmailId = getCurrentEmailId();
            if (currentEmailId) {
                window.location.href = `/email/reply-all/${currentEmailId}/`;
            } else {
                console.warn('No email selected to reply all');
            }
        });
    }

    if (forwardButton) {
        forwardButton.addEventListener('click', function() {
            const currentEmailId = getCurrentEmailId();
            if (currentEmailId) {
                window.location.href = `/email/forward/${currentEmailId}/`;
            } else {
                console.warn('No email selected to forward');
            }
        });
    }

    // Helper function to get current email ID
    function getCurrentEmailId() {
        const activeEmailItem = document.querySelector('.telebird-email-item.active');
        return activeEmailItem ? activeEmailItem.dataset.emailId : null;
    }
});
