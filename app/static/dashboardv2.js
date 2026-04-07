
lucide.createIcons();

/* TEMA GIORNO/NOTTE INTELLIGENTE */
const themeToggleBtn = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;
const savedTheme = localStorage.getItem('site-theme');
const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;

const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`;
const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;

if (savedTheme === 'dark' || (!savedTheme && prefersDarkScheme)) {
    htmlElement.setAttribute('data-theme', 'dark');
    themeToggleBtn.innerHTML = sunIcon;
} else {
    htmlElement.setAttribute('data-theme', 'light');
    themeToggleBtn.innerHTML = moonIcon;
}

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
    if (chartInstance) renderChart();
});



// Stato dei filtri
const savedFilters = JSON.parse(localStorage.getItem('dashboard-filters')) || {};
const state = {
    output: savedFilters.output || 'acqua',
    tempo: savedFilters.tempo || 'giorno',
    tipo: savedFilters.tipo || 'prompt'
};

let chartInstance = null;

let currentTotalVal = 0;
let currentAvgVal = 0;

function animateValue(obj, start, end, duration, formatter) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const easeOut = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        const currentVal = start + easeOut * (end - start);

        if (obj) obj.innerText = formatter(currentVal);

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            if (obj) obj.innerText = formatter(end);
        }
    };
    window.requestAnimationFrame(step);
}

const outputConfig = {
    acqua: { label: 'Consumo Acqua', key: 'water', unit: 'Litri', color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.2)', icon: 'droplet' },
    co2: { label: 'Emissioni CO2', key: 'co2', unit: 'g', color: '#64748b', bgColor: 'rgba(100, 116, 139, 0.2)', icon: 'cloud' },
    energia: { label: 'Consumo Energia', key: 'energy', unit: 'Wh', color: '#eab308', bgColor: 'rgba(234, 179, 8, 0.2)', icon: 'zap' }
};

const tempoConfig = {
    ora: 'hour',
    giorno: 'day',
    settimana: 'week'
};

const catStyles = {
    'culture': { color: '#ef4444', fill: 'rgba(239, 68, 68, 0.2)', display: 'Culture' },
    'finance': { color: '#f59e0b', fill: 'rgba(245, 158, 11, 0.2)', display: 'Finance' },
    'general': { color: '#10b981', fill: 'rgba(16, 185, 129, 0.2)', display: 'General' }
};

const getLabelsFallback = () => {
    switch (state.tempo) {
        case 'ora': return Array.from({ length: 24 }, (_, i) => `${i}:00`);
        case 'giorno': return ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];
        case 'settimana': return ['Sett 1', 'Sett 2', 'Sett 3', 'Sett 4'];
        default: return [];
    }
};

function padData(data, targetLength) {
    if (!data) return Array(targetLength).fill(0);
    const padded = [...data];
    while (padded.length < targetLength) padded.push(null);
    return padded.slice(0, targetLength);
}

// GESTIONE DEI DATI REALI (Lettura da file JSON)
// Per funzionare senza un server locale, il JSON è stato incorporato direttamente qui.
// NEW: Global data variable
let dashboardData = null;

// Updated Fetch Function
async function fetchAndRenderData() {
    try {
        // You can change this endpoint to your actual JSON path
        const data = await fetchData('/data/dashboard.json');

        if (data) {
            dashboardData = data;
            renderChart();
        } else {
            console.error("Data received is empty or invalid");
        }
    } catch (error) {
        console.error("Error loading dashboard data:", error);
        // Optional: Show a "Data failed to load" message in the UI
        document.getElementById('chart-title').innerText = "Errore nel caricamento dei dati";
    }
}

// Helper fetch function
async function fetchData(endpoint) {
    const response = await fetch(endpoint);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

// UPDATED: Start the app when window loads
window.addEventListener('load', () => {
    fetchAndRenderData();
});

function applyFilterClasses() {
    ['output', 'tempo', 'tipo'].forEach(key => {
        const container = document.getElementById(`filter-${key}`);
        const activeClass = `active-${key}`;
        container.querySelectorAll('button').forEach(btn => {
            if (btn.getAttribute('data-val') === state[key]) {
                btn.classList.add(activeClass);
            } else {
                btn.classList.remove(activeClass);
            }
        });
    });
    const catFilterBlock = document.getElementById('category-filters');
    if (state.tipo === 'categorie') {
        catFilterBlock.classList.remove('hidden');
        catFilterBlock.classList.add('flex');
    } else {
        catFilterBlock.classList.add('hidden');
        catFilterBlock.classList.remove('flex');
    }
}

// Listener dei filtri standard (Output, Tempo, Tipo)
function setupFilters(containerId, stateKey, activeClass) {
    const container = document.getElementById(containerId);
    const buttons = container.querySelectorAll('button');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove(activeClass));
            btn.classList.add(activeClass);
            state[stateKey] = btn.getAttribute('data-val');
            localStorage.setItem('dashboard-filters', JSON.stringify(state));

            if (stateKey === 'tipo') {
                const catFilterBlock = document.getElementById('category-filters');
                if (state.tipo === 'categorie') {
                    catFilterBlock.classList.remove('hidden');
                    catFilterBlock.classList.add('flex');
                } else {
                    catFilterBlock.classList.add('hidden');
                    catFilterBlock.classList.remove('flex');
                }
            }

            renderChart();
        });
    });
}

setupFilters('filter-output', 'output', 'active-output');
setupFilters('filter-tempo', 'tempo', 'active-tempo');
setupFilters('filter-tipo', 'tipo', 'active-tipo');
applyFilterClasses();

// Listener Sottocategorie
document.querySelectorAll('.category-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.classList.toggle('active-category');
        renderChart();
    });
});

// CREAZIONE E RENDERING DEL GRAFICO CON I DATI PREDISPOSTI DAL JSON
function renderChart() {
    if (!dashboardData || Object.keys(dashboardData).length === 0) {
        console.log("Waiting for data...");
        return;
    }

    const config = outputConfig[state.output];
    const timeframe = tempoConfig[state.tempo];
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    // Build the specific keys to lookup in JSON (e.g., 'water_day')
    const baseKey = `${config.key}_${timeframe}`;
    const currentKey = `${baseKey}_current`;
    const previousKey = `${baseKey}_previous`;

    const hasData = dashboardData.prompts && dashboardData.prompts[currentKey] && dashboardData.prompts[previousKey];

    let labels = hasData ? dashboardData.prompts[previousKey].labels : getLabelsFallback();

    const now = new Date();

    // Genera etichette dinamiche basate sull'ora/data attuale dell'utente per l'asse X
    const dynLabels = [];
    const len = labels.length;
    const mesi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
    const giorniSett = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];

    if (state.tempo === 'ora' && len > 0) {
        for (let i = len - 1; i >= 0; i--) {
            const d = new Date(now.getTime() - i * 60 * 60 * 1000);
            dynLabels.push(`${d.getHours()}:00`);
        }
        labels = dynLabels;
    } else if (state.tempo === 'giorno' && len > 0) {
        for (let i = len - 1; i >= 0; i--) {
            const d = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
            dynLabels.push(`${giorniSett[d.getDay()]} ${d.getDate()}`);
        }
        labels = dynLabels;
    } else if (state.tempo === 'settimana' && len > 0) {
        const settLabels = ["3 sett. fa", "2 sett. fa", "Settimana scorsa", "Questa settimana"];
        // Se abbiamo meno o più punti, prendiamo gli ultimi N
        for (let i = 0; i < len; i++) {
            const labelIdx = settLabels.length - len + i;
            dynLabels.push(settLabels[labelIdx] || `Sett. -${len - 1 - i}`);
        }
        labels = dynLabels;
    }

    // Etichette dinamiche per i tooltip/legenda
    const formatDateFull = (d) => `${giorniSett[d.getDay()]} ${d.getDate()} ${mesi[d.getMonth()]}`;

    let currentLabel = "Periodo Attuale";
    let previousLabel = "Periodo Precedente";
    if (state.tempo === 'ora') {
        currentLabel = `Oggi (${formatDateFull(now)})`;
        const prev = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        previousLabel = `Ieri (${formatDateFull(prev)})`;
    } else if (state.tempo === 'giorno') {
        currentLabel = `Questa Settimana`;
        previousLabel = `Settimana Scorsa`;
    } else if (state.tempo === 'settimana') {
        currentLabel = `Questo Mese`;
        previousLabel = `Mese Scorso`;
    }

    const datasets = [];
    let chartType = state.tipo === 'prompt' ? 'line' : 'bar';

    let total = 0;
    let currentDataPoints = 0;
    let prevTotal = 0;

    if (state.tipo === 'prompt') {
        if (hasData) {
            const currentPrompt = dashboardData.prompts[currentKey];
            const previousPrompt = dashboardData.prompts[previousKey];

            const paddedCurrentData = padData(currentPrompt.data, labels.length);
            // Calculate totals
            paddedCurrentData.forEach(v => {
                if (v !== null && v !== undefined) {
                    total += Number(v);
                    if (v > 0) currentDataPoints++;
                }
            });

            const paddedPrevData = padData(previousPrompt.data, labels.length);
            paddedPrevData.forEach(v => {
                if (v !== null && v !== undefined) prevTotal += Number(v);
            });

            datasets.push({
                label: `${config.label} - ${currentLabel} (${config.unit})`,
                data: paddedCurrentData,
                borderColor: config.color,
                backgroundColor: config.color + '40', // 25% opacity
                pointBackgroundColor: config.color,
                pointRadius: 5,
                borderWidth: 2,
                borderRadius: 6,
                fill: true,
                tension: 0.3
            });

            datasets.push({
                label: `${config.label} - ${previousLabel} (${config.unit})`,
                data: paddedPrevData,
                borderColor: '#94a3b8',
                borderDash: [5, 5],
                backgroundColor: 'transparent',
                pointBackgroundColor: '#94a3b8',
                pointRadius: 5,
                borderWidth: 2,
                fill: false,
                tension: 0.3
            });
        }
    } else if (state.tipo === 'categorie') {
        const activeCategories = Array.from(document.querySelectorAll('.category-toggle.active-category'))
            .map(btn => btn.getAttribute('data-cat'));

        activeCategories.forEach(cat => {
            const currentCategoryPrompt = dashboardData.categories[cat]?.[currentKey];
            if (currentCategoryPrompt) {
                const style = catStyles[cat] || { color: '#8b5cf6', fill: 'rgba(139, 92, 246, 0.2)', display: cat };

                const paddedData = padData(currentCategoryPrompt.data, labels.length);
                paddedData.forEach(v => {
                    if (v !== null && v !== undefined) {
                        total += Number(v);
                        if (v > 0) currentDataPoints++; // Appoximate average
                    }
                });

                datasets.push({
                    label: `${style.display} - ${currentLabel} (${config.unit})`,
                    data: paddedData,
                    borderColor: style.color,
                    backgroundColor: chartType === 'bar' ? style.color : style.fill,
                    pointBackgroundColor: style.color,
                    pointRadius: 5,
                    borderWidth: 2,
                    borderRadius: 4,
                    fill: chartType === 'line',
                    tension: 0.3
                });

                // Optionally add previous for category as well with dashed line:
                const previousCategoryPrompt = dashboardData.categories[cat]?.[previousKey];
                if (previousCategoryPrompt) {
                    const prevPaddedData = padData(previousCategoryPrompt.data, labels.length);
                    prevPaddedData.forEach(v => {
                        if (v !== null && v !== undefined) prevTotal += Number(v);
                    });
                }
            }
        });
    } else if (state.tipo === 'modelli') {
        // Mappa dei modelli da includere
        const modelMap = [
            { id: 'chatgpt', name: 'ChatGPT', colorStr: isDark ? '#ffffff' : '#475569', fillStr: isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(71, 85, 105, 0.2)' },
            { id: 'gemini-flash', name: 'Gemini', colorStr: '#3b82f6', fillStr: 'rgba(59, 130, 246, 0.2)' },
            { id: 'claude-sonnet', name: 'Claude', colorStr: '#f97316', fillStr: 'rgba(249, 115, 22, 0.2)' }
        ];

        modelMap.forEach(model => {
            const modelDataObj = dashboardData.models?.[model.id];
            if (modelDataObj) {
                const currentModelData = modelDataObj[currentKey];
                const previousModelData = modelDataObj[previousKey];

                if (currentModelData) {
                    const paddedCurrentData = padData(currentModelData.data, labels.length);
                    paddedCurrentData.forEach(v => {
                        if (v !== null && v !== undefined) {
                            total += Number(v);
                            if (v > 0) currentDataPoints++;
                        }
                    });

                    datasets.push({
                        label: `${model.name} - ${currentLabel} (${config.unit})`,
                        data: paddedCurrentData,
                        borderColor: model.colorStr,
                        backgroundColor: chartType === 'bar' ? model.colorStr : model.fillStr,
                        pointBackgroundColor: model.colorStr,
                        pointBorderColor: model.colorStr,
                        pointRadius: 5,
                        borderWidth: 2,
                        borderRadius: 4,
                        fill: chartType === 'line'
                    });
                }

                if (previousModelData) {
                    const paddedPrevData = padData(previousModelData.data, labels.length);
                    paddedPrevData.forEach(v => {
                        if (v !== null && v !== undefined) prevTotal += Number(v);
                    });
                }
            }
        });
    }

    // UI updates
    const tipoCap = state.tipo.charAt(0).toUpperCase() + state.tipo.slice(1);
    const tempoCap = state.tempo.charAt(0).toUpperCase() + state.tempo.slice(1);
    document.getElementById('chart-title').innerText = `${config.label} per ${tipoCap} (${tempoCap})`;

    const unitSuffix = config.unit === 'Litri' ? ' L' : ` ${config.unit}`;
    const targetAvg = currentDataPoints > 0 ? (total / currentDataPoints) : 0;

    animateValue(document.getElementById('stat-total'), currentTotalVal, total, 1200, (val) => val.toFixed(2) + unitSuffix);
    currentTotalVal = total;

    animateValue(document.getElementById('stat-avg'), currentAvgVal, targetAvg, 1200, (val) => val.toFixed(3) + unitSuffix);
    currentAvgVal = targetAvg;

    // Percentage difference vs previous
    const trendEl = document.getElementById('stat-trend');
    const trendIconContainer = trendEl.parentElement.previousElementSibling;

    let diffPercent = 0;
    if (prevTotal > 0) {
        diffPercent = ((total - prevTotal) / prevTotal) * 100;
    } else if (total > 0 && prevTotal === 0) {
        diffPercent = 100; // From 0 to something
    }

    if (diffPercent > 0) {
        trendEl.innerText = `+${diffPercent.toFixed(1)}%`;
        trendEl.className = 'text-2xl font-bold text-red-500';
        trendIconContainer.className = 'w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600 transition-colors';
        trendIconContainer.innerHTML = `<i data-lucide="trending-up"></i>`;
    } else if (diffPercent < 0) {
        trendEl.innerText = `${diffPercent.toFixed(1)}%`;
        trendEl.className = 'text-2xl font-bold text-green-500';
        trendIconContainer.className = 'w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-green-600 transition-colors';
        trendIconContainer.innerHTML = `<i data-lucide="trending-down"></i>`;
    } else {
        trendEl.innerText = `--%`;
        trendEl.className = 'text-2xl font-bold text-gray-500';
        trendIconContainer.className = 'w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 transition-colors';
        trendIconContainer.innerHTML = `<i data-lucide="minus"></i>`;
    }

    const iconContainer = document.getElementById('stat-icon-1');
    iconContainer.innerHTML = `<i data-lucide="${config.icon}"></i>`;
    iconContainer.className = `w-12 h-12 rounded-full flex items-center justify-center transition-colors ${state.output === 'acqua' ? (isDark ? 'bg-blue-900/40 text-blue-400' : 'bg-blue-100 text-blue-600') :
        state.output === 'co2' ? (isDark ? 'bg-slate-700/50 text-slate-300' : 'bg-slate-200 text-slate-700') :
            (isDark ? 'bg-yellow-900/40 text-yellow-400' : 'bg-yellow-100 text-yellow-600')
        }`;
    lucide.createIcons();

    // Render Chart.js
    const rootStyle = getComputedStyle(document.documentElement);
    const gridColor = rootStyle.getPropertyValue('--border-color').trim() || 'rgba(226, 232, 240, 0.6)';
    const textColor = rootStyle.getPropertyValue('--text-muted').trim() || '#64748b';
    const tooltipBg = rootStyle.getPropertyValue('--card-bg').trim() || 'rgba(15, 23, 42, 0.9)';
    const tooltipText = rootStyle.getPropertyValue('--text-color').trim() || '#fff';

    const ctx = document.getElementById('mainChart').getContext('2d');

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: textColor,
                        font: { family: "'Inter', sans-serif" },
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: tooltipBg,
                    titleColor: tooltipText,
                    bodyColor: tooltipText,
                    borderColor: gridColor,
                    borderWidth: 1,
                    titleFont: { family: "'Inter', sans-serif", size: 13 },
                    bodyFont: { family: "'Inter', sans-serif", size: 13 },
                    padding: 12,
                    cornerRadius: 8,
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) label += context.parsed.y.toFixed(3);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor, drawBorder: false },
                    ticks: {
                        font: { family: "'Inter', sans-serif" },
                        color: textColor,
                        callback: function (value) {
                            return value.toString();
                        }
                    }
                },
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: { font: { family: "'Inter', sans-serif" }, color: textColor }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false,
            },
        }
    });
}

window.addEventListener('load', () => {
    fetchAndRenderData();
});
