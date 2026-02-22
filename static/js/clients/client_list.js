function showDetailsModal(clientId, name, contactPerson, email, phone, address, notes, clientIdCode) {
    document.getElementById('detailsClientName').textContent = name;
    document.getElementById('detailsClientId').textContent = clientIdCode || 'Not assigned';
    document.getElementById('detailsContactPerson').textContent = contactPerson || 'No contact person';
    document.getElementById('detailsEmail').textContent = email || 'No email';
    document.getElementById('detailsPhone').textContent = phone || 'No phone';
    document.getElementById('detailsAddress').textContent = address || 'No address';
    document.getElementById('detailsNotes').textContent = notes || 'No notes';
    
    document.getElementById('detailsModalBackdrop').classList.add('show');
    document.getElementById('clientDetailsModal').classList.add('show');
}

function hideDetailsModal() {
    document.getElementById('detailsModalBackdrop').classList.remove('show');
    document.getElementById('clientDetailsModal').classList.remove('show');
}

// Delete Modal Functions
function showDeleteModal(clientId, name, contactPerson, email, phone) {
    document.getElementById('modalClientName').textContent = name;
    document.getElementById('modalContactPerson').textContent = contactPerson;
    document.getElementById('modalEmail').textContent = email;
    document.getElementById('modalPhone').textContent = phone;
    document.getElementById('deleteForm').action = `/clients/${clientId}/delete/`;
    
    document.getElementById('modalBackdrop').classList.add('show');
    document.getElementById('deleteModal').classList.add('show');
}

function hideDeleteModal() {
    document.getElementById('modalBackdrop').classList.remove('show');
    document.getElementById('deleteModal').classList.remove('show');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Close details modal when clicking outside
    document.getElementById('detailsModalBackdrop').addEventListener('click', hideDetailsModal);
    
    // Close delete modal when clicking outside
    document.getElementById('modalBackdrop').addEventListener('click', hideDeleteModal);
}); 