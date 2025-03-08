document.addEventListener('DOMContentLoaded', function() {
    document.documentElement.dataset.appliedMode = localStorage.getItem('theme') || 'dark';
});