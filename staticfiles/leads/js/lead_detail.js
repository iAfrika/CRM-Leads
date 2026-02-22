document.addEventListener('DOMContentLoaded', function() {
    // Add Note Modal
    const addNoteBtn = document.getElementById('addNoteBtn');
    const addNoteModal = document.getElementById('addNoteModal');
    
    if (addNoteBtn) {
        addNoteBtn.addEventListener('click', function() {
            // Create modal if it doesn't exist
            if (!addNoteModal) {
                const modalHtml = `
                <div class="modal fade" id="addNoteModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Add Note</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form method="POST">
                                {% csrf_token %}
                                <input type="hidden" name="action" value="add_note">
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label for="noteContent" class="form-label">Note Content</label>
                                        <textarea class="form-control" id="noteContent" name="content" rows="4" required></textarea>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="submit" class="btn btn-primary">Save Note</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>`;
                
                document.body.insertAdjacentHTML('beforeend', modalHtml);
            }
            
            // Show the modal
            const modalInstance = new bootstrap.Modal(document.getElementById('addNoteModal'));
            modalInstance.show();
        });
    }

    // Add Document Modal
    const addDocumentBtn = document.getElementById('addDocumentBtn');
    const addDocumentModal = document.getElementById('addDocumentModal');
    
    if (addDocumentBtn) {
        addDocumentBtn.addEventListener('click', function() {
            // Create modal if it doesn't exist
            if (!addDocumentModal) {
                const modalHtml = `
                <div class="modal fade" id="addDocumentModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Add Document</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <form method="POST" enctype="multipart/form-data">
                                {% csrf_token %}
                                <input type="hidden" name="action" value="add_document">
                                <div class="modal-body">
                                    <div class="mb-3">
                                        <label for="documentFile" class="form-label">File</label>
                                        <input type="file" class="form-control" id="documentFile" name="file" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="documentDescription" class="form-label">Description (Optional)</label>
                                        <textarea class="form-control" id="documentDescription" name="description" rows="3"></textarea>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    <button type="submit" class="btn btn-primary">Upload Document</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>`;
                
                document.body.insertAdjacentHTML('beforeend', modalHtml);
            }
            
            // Show the modal
            const modalInstance = new bootstrap.Modal(document.getElementById('addDocumentModal'));
            modalInstance.show();
        });
    }
});
