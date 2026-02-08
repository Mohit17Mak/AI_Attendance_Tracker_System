// Theme Toggle Functionality
(function() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    if (savedTheme === 'dark') {
        body.classList.add('dark-theme');
        if (themeToggle) themeToggle.textContent = '☀️';
    }
    
    // Toggle theme on button click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-theme');
            
            const isDark = body.classList.contains('dark-theme');
            
            // Update button icon
            themeToggle.textContent = isDark ? '☀️' : '🌙';
            
            // Save preference to localStorage
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
})();
