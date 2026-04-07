// =========================================
// GESTIONE HEADER DINAMICO (Intersection Observer)
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('main-header');
    const heroSection = document.getElementById('hero-section');

    const headerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                header.classList.add('is-visible');
            } else {
                header.classList.remove('is-visible');
            }
        });
    }, {
        threshold: 0.1
    });

    if (heroSection && header) {
        headerObserver.observe(heroSection);
    }
});

// =========================================
// LOGICA COMPONENTI CAROSELLO
// =========================================
function initCarousel(carouselId) {
    const container = document.getElementById(carouselId);
    if (!container) return;

    const slides = container.querySelectorAll('.carousel-slide');
    const prevBtn = container.querySelector('.carousel-btn.prev');
    const nextBtn = container.querySelector('.carousel-btn.next');
    const dotsContainer = container.querySelector('.carousel-dots');
    let currentIdx = 0;

    slides.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.classList.add('carousel-dot');
        if (i === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(i));
        dotsContainer.appendChild(dot);
    });
    const dots = dotsContainer.querySelectorAll('.carousel-dot');

    function goToSlide(idx) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        currentIdx = idx;
        slides[currentIdx].classList.add('active');
        dots[currentIdx].classList.add('active');
    }

    nextBtn.addEventListener('click', () => {
        let nextIdx = (currentIdx + 1) % slides.length;
        goToSlide(nextIdx);
    });

    prevBtn.addEventListener('click', () => {
        let prevIdx = (currentIdx - 1 + slides.length) % slides.length;
        goToSlide(prevIdx);
    });

    let autoplayInterval = setInterval(() => {
        nextBtn.click();
    }, 6000);

    container.addEventListener('mouseenter', () => clearInterval(autoplayInterval));
    container.addEventListener('mouseleave', () => {
        autoplayInterval = setInterval(() => { nextBtn.click(); }, 6000);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initCarousel('carousel-1');
    initCarousel('carousel-2');
});





// =========================================
// FUNZIONI UI DI BASE
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
    const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

    const setInitialTheme = () => {
        const saved = localStorage.getItem('site-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        htmlElement.setAttribute('data-theme', saved);
        themeToggleBtn.innerHTML = saved === 'dark' ? sunIcon : moonIcon;
    };
    setInitialTheme();

    themeToggleBtn.addEventListener('click', () => {
        const isDark = htmlElement.getAttribute('data-theme') === 'dark';
        const next = isDark ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', next);
        localStorage.setItem('site-theme', next);
        themeToggleBtn.innerHTML = next === 'dark' ? sunIcon : moonIcon;
    });

    const mobileBtn = document.getElementById('mobile-menu-btn');
    const nav = document.getElementById('main-nav');

    nav.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 1150) {
                nav.classList.remove('active');
                mobileBtn.classList.remove('open');
            }
        });
    });

    mobileBtn.addEventListener('click', () => {
        nav.classList.toggle('active');
        mobileBtn.classList.toggle('open');
    });

    // =========================================
    // LOGICA MICRO-BANNER
    // =========================================
    const banner = document.getElementById('micro-banner');
    const closeBannerBtn = document.getElementById('close-banner');
    const targetSection = document.getElementById('dati');

    if (!localStorage.getItem('ai-monitor-banner-closed')) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    banner.classList.add('visible');
                    observer.disconnect();
                }
            });
        }, { threshold: 0.2 });

        if (targetSection) observer.observe(targetSection);

        closeBannerBtn.addEventListener('click', () => {
            banner.classList.remove('visible');
            localStorage.setItem('ai-monitor-banner-closed', 'true');
            setTimeout(() => { banner.style.display = 'none'; }, 600);
        });
    }
});