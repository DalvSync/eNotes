document.addEventListener("DOMContentLoaded", () => {
    const observerElements = document.querySelectorAll('.animate-on-scroll');
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    observerElements.forEach(el => observer.observe(el));

    const langToggle = document.getElementById('lang-toggle');
    const body = document.body;

    const savedLang = localStorage.getItem('dalvid-lang') || 'uk';
    
    if (savedLang === 'en') {
        body.classList.replace('lang-uk', 'lang-en');
        langToggle.checked = true;
    }

    langToggle.addEventListener('change', () => {
        if (langToggle.checked) {
            body.classList.replace('lang-uk', 'lang-en');
            localStorage.setItem('dalvid-lang', 'en');
        } else {
            body.classList.replace('lang-en', 'lang-uk');
            localStorage.setItem('dalvid-lang', 'uk');
        }
    });

const menuBtn = document.getElementById('menu-btn');
    const navMenu = document.getElementById('nav-menu');

    menuBtn.addEventListener('click', () => {
        menuBtn.classList.toggle('active');
        navMenu.classList.toggle('active');
        
        // Блокуємо скрол сторінки при відкритому меню
        if (navMenu.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });

    // Закриваємо меню при кліку на посилання
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            menuBtn.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
});