document.addEventListener('DOMContentLoaded', function() {
  // Modal handling
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modalClosers = document.querySelectorAll('[data-modal-close]');
  const backdrop = document.querySelector('.modal-backdrop');
  
  // Open modal function
  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    const backdrop = document.querySelector('.modal-backdrop');
    backdrop.style.display = 'block';
    
    setTimeout(() => {
      backdrop.classList.add('show');
      modal.style.display = 'flex';
      
      setTimeout(() => {
        modal.classList.add('show');
      }, 50);
    }, 50);
    
    // Focus first input in modal
    setTimeout(() => {
      const firstInput = modal.querySelector('input, textarea');
      if (firstInput) {
        firstInput.focus();
      }
    }, 300);
  }
  
  // Close modal function
  function closeModal(modal) {
    if (!modal) return;
    
    modal.classList.remove('show');
    
    setTimeout(() => {
      modal.style.display = 'none';
      const backdrop = document.querySelector('.modal-backdrop');
      backdrop.classList.remove('show');
      
      setTimeout(() => {
        backdrop.style.display = 'none';
      }, 300);
    }, 300);
  }
  
  // Close all modals
  function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => closeModal(modal));
  }
  
  // Setup modal triggers
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = trigger.getAttribute('data-modal-target');
      openModal(modalId);
    });
  });
  
  // Setup modal closers
  modalClosers.forEach(closer => {
    closer.addEventListener('click', (e) => {
      e.preventDefault();
      const modal = closer.closest('.modal');
      closeModal(modal);
    });
  });
  
  // Close modal when clicking on backdrop
  if (backdrop) {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        closeAllModals();
      }
    });
  }
  
  // Close modal on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });
  
  // Form validations
  const noteForm = document.querySelector('#addNoteModal form');
  if (noteForm) {
    noteForm.addEventListener('submit', function(e) {
      const content = document.getElementById('id_content').value.trim();
      if (!content) {
        e.preventDefault();
        alert('Please enter a note content');
      }
    });
  }
  
  const documentForm = document.querySelector('#addDocumentModal form');
  if (documentForm) {
    documentForm.addEventListener('submit', function(e) {
      const file = document.getElementById('id_file').value;
      if (!file) {
        e.preventDefault();
        alert('Please select a file to upload');
      }
    });
  }
  
  // File input enhancement
  const fileInputs = document.querySelectorAll('input[type="file"]');
  fileInputs.forEach(input => {
    input.addEventListener('change', function() {
      const fileName = this.value.split('\\').pop();
      const fileLabel = this.nextElementSibling;
      if (fileLabel && fileLabel.classList.contains('file-label')) {
        fileLabel.textContent = fileName || 'Choose file';
      }
    });
  });
}); 