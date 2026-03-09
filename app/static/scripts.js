 document.addEventListener('DOMContentLoaded', () => {
            /* 1. GESTIONE MENU MOBILE */
            const menuToggle = document.querySelector('.menu-toggle');
            const mainNav = document.getElementById('main-nav');
            const navLinks = document.querySelectorAll('#main-nav a');

            menuToggle.addEventListener('click', () => {
                menuToggle.classList.toggle('active');
                mainNav.classList.toggle('active');
            });

            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    menuToggle.classList.remove('active');
                    mainNav.classList.remove('active');
                });
            });

            /* 2. TEMA GIORNO/NOTTE INTELLIGENTE */
            const themeToggleBtn = document.getElementById('theme-toggle');
            const htmlElement = document.documentElement;
            const savedTheme = localStorage.getItem('site-theme');
            const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
            const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

            // Applica il tema al caricamento
            if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme)) {
                htmlElement.setAttribute('data-theme', 'dark');
                themeToggleBtn.innerHTML = sunIcon;
            } else {
                htmlElement.setAttribute('data-theme', 'light');
                themeToggleBtn.innerHTML = moonIcon;
            }

            // Cambia tema manualmente
            themeToggleBtn.addEventListener('click', () => {
                const currentTheme = htmlElement.getAttribute('data-theme');
                if (currentTheme === 'light') {
                    htmlElement.setAttribute('data-theme', 'dark');
                    localStorage.setItem('site-theme', 'dark');
                    themeToggleBtn.innerHTML = sunIcon;
                } else {
                    htmlElement.setAttribute('data-theme', 'light');
                    localStorage.setItem('site-theme', 'light');
                    themeToggleBtn.innerHTML = moonIcon;
                }
            });

            /* 3. ANIMAZIONI DI SCORRIMENTO (Scroll Reveal) 
               Usa IntersectionObserver, metodo "green" e performante 
               per non sovraccaricare la CPU con eventi di scroll continui. */
            const observerOptions = {
                root: null,
                rootMargin: '0px',
                threshold: 0.15 // Inizia l'animazione quando il 15% della sezione è visibile
            };

            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        // Smette di osservare l'elemento una volta apparso per risparmiare risorse
                        observer.unobserve(entry.target); 
                    }
                });
            }, observerOptions);

            document.querySelectorAll('section').forEach(section => {
                observer.observe(section);
            });
        });