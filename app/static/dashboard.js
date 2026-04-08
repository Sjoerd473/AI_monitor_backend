
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
let currentCostVal = 0;

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

// Default palette for auto-assigning colors to categories derived from data
const categoryPalette = [
    { color: '#ef4444', fill: 'rgba(239, 68, 68, 0.2)' },
    { color: '#f59e0b', fill: 'rgba(245, 158, 11, 0.2)' },
    { color: '#10b981', fill: 'rgba(16, 185, 129, 0.2)' },
    { color: '#8b5cf6', fill: 'rgba(139, 92, 246, 0.2)' },
    { color: '#06b6d4', fill: 'rgba(6, 182, 212, 0.2)' },
    { color: '#f43f5e', fill: 'rgba(244, 63, 94, 0.2)' },
    { color: '#84cc16', fill: 'rgba(132, 204, 22, 0.2)' },
    { color: '#6366f1', fill: 'rgba(99, 102, 241, 0.2)' },
];

// Built at runtime from the data — populated in buildDynamicUI()
let catStyles = {};

// Default palette for auto-assigning colors to models derived from data
const modelPalette = [
    { colorStr: '#3b82f6', fillStr: 'rgba(59, 130, 246, 0.2)' },
    { colorStr: '#f97316', fillStr: 'rgba(249, 115, 22, 0.2)' },
    { colorStr: '#10b981', fillStr: 'rgba(16, 185, 129, 0.2)' },
    { colorStr: '#a8a29e', fillStr: 'rgba(168, 162, 158, 0.2)' },
    { colorStr: '#8b5cf6', fillStr: 'rgba(139, 92, 246, 0.2)' },
    { colorStr: '#f43f5e', fillStr: 'rgba(244, 63, 94, 0.2)' },
    { colorStr: '#06b6d4', fillStr: 'rgba(6, 182, 212, 0.2)' },
    { colorStr: '#84cc16', fillStr: 'rgba(132, 204, 22, 0.2)' },
];

// Built at runtime from the data — populated in buildDynamicUI()
let dynamicModelMap = [];

// Build category buttons and model map dynamically from data
function buildDynamicUI(data) {
    // --- Categories ---
    const categories = data.categories ? Object.keys(data.categories) : [];
    catStyles = {};
    categories.forEach((cat, i) => {
        const palette = categoryPalette[i % categoryPalette.length];
        const display = cat.charAt(0).toUpperCase() + cat.slice(1);
        catStyles[cat] = { color: palette.color, fill: palette.fill, display };
    });

    const container = document.getElementById('category-toggle-container');
    container.innerHTML = '';
    categories.forEach(cat => {
        const style = catStyles[cat];
        const btn = document.createElement('button');
        if (cat === 'general') {
            btn.className = 'filter-btn active-category category-toggle';
        } else {
            btn.className = 'filter-btn category-toggle';
        }
        btn.setAttribute('data-cat', cat);
        btn.textContent = style.display;
        btn.addEventListener('click', () => {
            btn.classList.toggle('active-category');
            renderChart();
        });
        container.appendChild(btn);
    });

    // --- Models ---
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const models = data.models ? Object.keys(data.models) : [];
    dynamicModelMap = models.map((id, i) => {
        const palette = modelPalette[i % modelPalette.length];
        // Special case: first model gets a theme-aware neutral color (like the old "chatgpt" slot)
        if (i === 0 && models.length > 1) {
            return {
                id,
                name: id,
                colorStr: isDark ? '#ffffff' : '#475569',
                fillStr: isDark ? 'rgba(255,255,255,0.2)' : 'rgba(71,85,105,0.2)'
            };
        }
        return { id, name: id, colorStr: palette.colorStr, fillStr: palette.fillStr };
    });
}

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

let dashboardData = null;

// Updated Fetch Function
async function fetchAndRenderData() {
    try {
        // You can change this endpoint to your actual JSON path
        const data = await fetchData('/data/dashboard.json');

        if (data) {
            dashboardData = data;
            buildDynamicUI(data);
            applyFilterClasses();
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
        catFilterBlock.classList.add('visible');
    } else {
        catFilterBlock.classList.remove('visible');
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
                    catFilterBlock.classList.add('visible');
                } else {
                    catFilterBlock.classList.remove('visible');
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
    if (!dashboardData || Object.keys(dashboardData).length === 0) return;

    const config = outputConfig[state.output];
    const timeframe = tempoConfig[state.tempo];
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    // Build the specific keys to lookup in JSON (e.g., 'water_day')
    const baseKey = `${config.key}_${timeframe}`;
    const currentKey = `${baseKey}_current`;
    const previousKey = `${baseKey}_previous`;

    const hasData = dashboardData.prompts && dashboardData.prompts[currentKey] && dashboardData.prompts[previousKey];

    let labels = [];
    if (state.tempo === 'ora') {
        labels = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"];
    } else if (state.tempo === 'giorno') {
        labels = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"];
    } else if (state.tempo === 'settimana') {
        labels = ["Settimana 1", "Settimana 2", "Settimana 3", "Settimana 4"];
    }

    let currentLabel = "Periodo Attuale";
    let previousLabel = "Periodo Precedente";
    if (state.tempo === 'ora') {
        currentLabel = "Oggi";
        previousLabel = "Ieri";
    } else if (state.tempo === 'giorno') {
        currentLabel = "Questa Settimana";
        previousLabel = "Settimana Scorsa";
    } else if (state.tempo === 'settimana') {
        currentLabel = "Questo Mese";
        previousLabel = "Mese Scorso";
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
        // Model map is built dynamically from dashboardData.models keys in buildDynamicUI()
        dynamicModelMap.forEach(model => {
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

    // Calcolo costo simulato
    const costRates = { acqua: 0.0045, co2: 0.00009, energia: 0.00028 }; // Moltiplicatori fittizi per calcolare il costo
    const targetCost = total * costRates[state.output];

    animateValue(document.getElementById('stat-total'), currentTotalVal, total, 1200, (val) => val.toFixed(4) + unitSuffix);
    currentTotalVal = total;

    animateValue(document.getElementById('stat-cost'), currentCostVal, targetCost, 1200, (val) => '€ ' + val.toFixed(4));
    currentCostVal = targetCost;

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
        trendEl.className = 'stat-value stat-value--red';
        trendIconContainer.className = 'stat-icon stat-icon--red';
        trendIconContainer.innerHTML = `<i data-lucide="trending-up"></i>`;
    } else if (diffPercent < 0) {
        trendEl.innerText = `${diffPercent.toFixed(1)}%`;
        trendEl.className = 'stat-value stat-value--green';
        trendIconContainer.className = 'stat-icon stat-icon--green';
        trendIconContainer.innerHTML = `<i data-lucide="trending-down"></i>`;
    } else {
        trendEl.innerText = `--%`;
        trendEl.className = 'stat-value stat-value--gray';
        trendIconContainer.className = 'stat-icon stat-icon--gray';
        trendIconContainer.innerHTML = `<i data-lucide="minus"></i>`;
    }

    const iconContainer = document.getElementById('stat-icon-1');
    iconContainer.innerHTML = `<i data-lucide="${config.icon}"></i>`;
    const outputIconClass = state.output === 'acqua' ? 'stat-icon--blue' :
        state.output === 'co2' ? 'stat-icon--slate' : 'stat-icon--yellow';
    iconContainer.className = `stat-icon ${outputIconClass}`;
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

