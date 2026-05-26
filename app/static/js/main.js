/**
 * ARM System - Main JavaScript
 * Association Rule Mining and Market Basket Analysis System
 */

// Sidebar Toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            if (sidebar.style.marginLeft === '0px' || sidebar.style.marginLeft === '') {
                sidebar.style.marginLeft = '-260px';
                mainContent.style.marginLeft = '0';
                mainContent.style.width = '100%';
            } else {
                sidebar.style.marginLeft = '0px';
                mainContent.style.marginLeft = '260px';
                mainContent.style.width = 'calc(100% - 260px)';
            }
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // File input label update
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (label && this.files.length > 0) {
                label.textContent = this.files[0].name;
            }
        });
    });
});

// Confirm delete
function confirmDelete(formId) {
    if (confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) {
        document.getElementById(formId).submit();
    }
}
