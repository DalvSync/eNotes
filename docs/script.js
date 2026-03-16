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
});