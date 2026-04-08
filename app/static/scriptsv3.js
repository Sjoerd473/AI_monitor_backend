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
// VISTA DETTAGLIO CARDS (Modificato con Layout a Zig-Zag)
// =========================================
let lastOpenedCard = null;

// Nuova struttura dati per popolare le righe e le sezioni finali
const detailsData = {
    co2: {
        title: "Emissioni di CO2",
        img: "https://ai-monitor.madebyshu.net/static/images/co2.svg",
        rows: [
            { img: "https://images.pexels.com/photos/9951823/pexels-photo-9951823.jpeg", text: "L'addestramento dei grandi modelli linguistici produce tonnellate di CO2. Un singolo processo di training può equivalere alle emissioni prodotte da centinaia di voli transatlantici." },
            { img: "https://images.pexels.com/photos/2565400/pexels-photo-2565400.jpeg", text: "Oltre al training, l'inferenza quotidiana contribuisce costantemente all'impronta di carbonio, specialmente quando alimentata da reti elettriche dipendenti dai combustibili fossili." },
            { img: "https://images.pexels.com/photos/5473337/pexels-photo-5473337.jpeg", text: "Adottare soluzioni di calcolo efficienti e monitorare i picchi di emissione è fondamentale per ridurre l'impatto ambientale dell'intelligenza artificiale moderna." }
        ],
        outroTitle: "Agisci per il Clima",
        outroText: "Monitorare le emissioni è il primo passo per compensare l'impatto ambientale dei tuoi modelli IA."
    },
    energy: {
        title: "Consumo Energetico",
        img: "https://ai-monitor.madebyshu.net/static/images/energy.svg",
        rows: [
            { img: "https://images.pexels.com/photos/356036/pexels-photo-356036.jpeg", text: "I data center IA consumano una quantità massiccia di elettricità per alimentare le GPU ad alte prestazioni necessarie per il calcolo parallelo." },
            { img: "https://images.pexels.com/photos/1591448/pexels-photo-1591448.png", text: "La domanda energetica globale è in rapida ascesa. Senza un'ottimizzazione del codice e dell'hardware, i sistemi cognitivi potrebbero pesare eccessivamente sulle reti nazionali." },
            { img: "https://images.pexels.com/photos/7887859/pexels-photo-7887859.jpeg", text: "La transizione verso data center alimentati al 100% da energie rinnovabili è la sfida principale per i giganti tecnologici di domani." }
        ],
        outroTitle: "Energia Consapevole",
        outroText: "Scopri come ottimizzare le tue query per ridurre il carico energetico complessivo del sistema."
    },
    water: {
        title: "Impronta Idrica",
        img: "https://ai-monitor.madebyshu.net/static/images/water.svg",
        rows: [
            { img: "https://images.pexels.com/photos/40784/drops-of-water-water-nature-liquid-40784.jpeg", text: "I sistemi di raffreddamento ad acqua sono essenziali per evitare il surriscaldamento dei server, ma richiedono miliardi di litri di acqua dolce ogni anno." },
            { img: "https://images.pexels.com/photos/11489544/pexels-photo-11489544.jpeg", text: "Gran parte dell'acqua utilizzata evapora durante il processo, sottraendo risorse preziose agli ecosistemi locali, spesso in zone già soggette a stress idrico." },
            { img: "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg", text: "La trasparenza sui dati idrici permette alle comunità locali di valutare meglio l'impatto territoriale delle infrastrutture tecnologiche." }
        ],
        outroTitle: "Preserva l'Acqua",
        outroText: "Unisciti alla nostra missione per rendere l'IA più sostenibile per il pianeta e per le sue risorse vitali."
    }
};

function showDetail(type) {
    lastOpenedCard = type;
    const data = detailsData[type];

    // Header centrato
    let htmlContent = `
        <div class="detail-header">
            <img src="${data.img}" class="detail-image" alt="Icona Metrica">
            <h2>${data.title}</h2>
        </div>
        <div class="detail-body">
    `;

    // Loop per generare le tre righe alternate (zig-zag)
    data.rows.forEach((row, index) => {
        // Aggiunge la classe reverse alle righe dispari (la seconda riga)
        const reverseClass = index % 2 !== 0 ? 'reverse' : '';
        htmlContent += `
            <div class="detail-row ${reverseClass}">
                <div class="detail-row-img">
                    <img src="${row.img}" alt="Immagine descrittiva">
                </div>
                <div class="detail-row-text">
                    <p>${row.text}</p>
                </div>
            </div>
        `;
    });

    // Aggiunta sezione outro finale custom per ogni dettaglio
    htmlContent += `
        </div>
        <section class="intro-outro-section" style="padding: 4rem 0 2rem;">
            <img src="https://ai-monitor.madebyshu.net/static/images/Background.svg" alt="Logo Icona">
            <h3>${data.outroTitle}</h3>
            <p>${data.outroText}</p>
        </section>
    `;

    document.getElementById('detail-content').innerHTML = htmlContent;
    window.scrollTo(0, 0);
    document.getElementById('main-content').style.display = 'none';
    document.getElementById('detail-view').style.display = 'block';

    const header = document.getElementById('main-header');
    if (header) header.classList.add('is-visible');
}

function showMain(scrollToCards = false) {
    document.getElementById('main-content').style.display = 'block';
    document.getElementById('detail-view').style.display = 'none';

    if (scrollToCards && lastOpenedCard) {
        const target = document.getElementById('card-' + lastOpenedCard);
        window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 100, behavior: 'smooth' });
    } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}


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

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}


const paths = Array.from(document.querySelectorAll('#Foreground path'))
const pathsLength = paths.length
const PATHCOLORS = ['hsl(325, 63%, 52%)', 'hsl(192, 78%, 46%)', 'hsl(29, 85%, 53%)']


function animatePath(path) {
    const totalLength = path.getTotalLength();
    const circuitDuration = totalLength * 30 + getRandomInt(10) * 20
    path.classList.add('draw')
    path.style.setProperty('--stroke-color', PATHCOLORS[getRandomInt(3)])
    path.style.setProperty('--total-length', totalLength + 'px');
    path.style.setProperty('--circuit-duration', circuitDuration - (circuitDuration / 10) + 'ms')
    // path.style.setProperty('--circuit-delay', (getRandomInt(500) + 500) + 'ms')
    path.style.setProperty('--wiggle-duration', (2500 + getRandomInt(5000)) + 'ms')

    setTimeout(() => {
        path.classList.remove('draw')
    }, circuitDuration);
}

setInterval(() => {
    let index = getRandomInt(pathsLength);

    // Use Math.max/min or modulo to stay within array bounds
    animatePath(paths[index]);
    animatePath(paths[(index + 2) % pathsLength]);
    animatePath(paths[Math.abs(index - 2)]);
}, 1000);

 document.addEventListener('DOMContentLoaded', () => {
            // Cerca tutte le istanze del divisore (così puoi usarne più di uno)
            const lineDividers = document.querySelectorAll('.line-divider-wrapper');
            if (lineDividers.length === 0) return;

            let currentScrollLines = 0;
            let targetScrollLines = 0;
            const easeLines = 0.03; // Fluidità (più basso = più morbido)

            // Funzione di interpolazione lineare per rendere il movimento fluido
            function lerpLines(start, end, factor) {
                return start + (end - start) * factor;
            }

            function updateLineDividers() {
                targetScrollLines = window.pageYOffset;
                currentScrollLines = lerpLines(currentScrollLines, targetScrollLines, easeLines);

                // Riduce l'intensità del movimento su smartphone
                const isMobile = window.innerWidth < 768;
                const multiplier = isMobile ? 0.6 : 1;

                // Applica il movimento a ciascun divisore trovato nella pagina
                lineDividers.forEach(divider => {
                    const lBordo = divider.querySelector('.line-3');
                    const lArancio = divider.querySelector('.line-2');
                    const lAzzurra = divider.querySelector('.line-1');

                    // Moltiplicatori diversi creano l'effetto parallasse
                    if (lBordo) lBordo.style.transform = `translateX(${currentScrollLines * -0.31 * multiplier}px)`;
                    if (lArancio) lArancio.style.transform = `translateX(${currentScrollLines * 0.19 * multiplier}px)`;
                    if (lAzzurra) lAzzurra.style.transform = `translateX(${currentScrollLines * -0.13 * multiplier}px)`;
                });

                requestAnimationFrame(updateLineDividers);
            }

            updateLineDividers();
        });