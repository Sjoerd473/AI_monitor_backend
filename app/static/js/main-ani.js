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