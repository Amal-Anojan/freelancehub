document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        themeToggle.innerHTML = newTheme === 'dark' 
            ? '<i class="fas fa-sun"></i> Light Mode' 
            : '<i class="fas fa-moon"></i> Dark Mode';
    });

    // Remove transition class after animation
    setTimeout(() => {
        document.body.classList.remove('theme-transition');
    }, 300);

    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    if (savedTheme === 'dark') {
        document.querySelectorAll('.nav-link, .dropdown-item').forEach(el => {
             el.style.color = 'white';
        });
}

});


// Add smooth theme transition class
// document.addEventListener('DOMContentLoaded', function() {
//     const themeToggle = document.getElementById('theme-toggle');
    
//     themeToggle.addEventListener('click', function() {
        // Add transition class to body
        // document.body.classList.add('theme-transition');
        
        // Your existing theme toggle logic here
        
        
//     });
// });