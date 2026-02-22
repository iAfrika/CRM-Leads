// project_management_minimal.js
document.addEventListener('DOMContentLoaded', function() {
    // Animation for projects loading
    const projects = document.querySelectorAll('.project');
    projects.forEach((project, index) => {
      project.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Make entire project card clickable
    projects.forEach(project => {
      const viewLink = project.querySelector('footer a:first-child').getAttribute('href');
      project.addEventListener('click', function(e) {
        // Don't redirect if clicking on a button
        if (e.target.closest('a')) return;
        window.location.href = viewLink;
      });
      project.style.cursor = 'pointer';
    });
  
    // Add subtle hover effect to buttons
    const buttons = document.querySelectorAll('.button');
    buttons.forEach(button => {
      button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
      });
      button.addEventListener('mouseleave', function() {
        this.style.transform = '';
      });
    });
  
    // Smooth details expansion
    const details = document.querySelector('details');
    if (details) {
      details.addEventListener('toggle', function() {
        if (this.open) {
          const content = this.querySelector('form');
          content.style.maxHeight = '0';
          content.style.opacity = '0';
          content.style.overflow = 'hidden';
          content.style.transition = 'max-height 0.3s ease, opacity 0.3s ease';
          
          // Force reflow
          content.offsetHeight;
          
          content.style.maxHeight = content.scrollHeight + 'px';
          content.style.opacity = '1';
        }
      });
    }
  });