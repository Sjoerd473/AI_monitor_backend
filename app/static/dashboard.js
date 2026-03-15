async function fetchData(endpoint) {
  const response = await fetch(endpoint);
  return response.json();
}

const chartRegistry = new Map();
const DEFAULT_VISIBLE_CATEGORIES = ['coding', 'creative'];

async function initDashboard() {

  const dataset = await fetchData('/data/dashboard.json');
  window.dashboardData = dataset;

  Object.keys(dataset.prompts).forEach(key => {

    if (!key.endsWith("_current")) return;

    const baseKey = key.replace("_current", "");
    const previousKey = `${baseKey}_previous`;

    if (!dataset.prompts[previousKey]) return;

    const [metric, timeframe] = baseKey.split("_");
    const title = `${metric.toUpperCase()} ${timeframe}`;

    const comparisonId = `${metric}_${timeframe}_chart`;
    const categoryId = `${metric}_${timeframe}_category_chart`;

    createChartContainer(comparisonId, title);
    createChartContainer(categoryId, `${title} by Category`, true);

    const fullLabels = dataset.prompts[previousKey].labels;

    createComparisonChart(
      comparisonId,
      dataset.prompts[key],
      dataset.prompts[previousKey],
      title
    );

    const datasets = buildCategoryDatasets(dataset, key, false);

    createCategoryChart(
      categoryId,
      fullLabels,
      datasets,
      `${title} by Category`
    );

  });

}

initDashboard();



function createChartContainer(id, title, isCategory = false) {

  const dashboard = document.getElementById("dashboard");

  const block = document.createElement("div");
  block.classList.add("chart-block");

  const heading = document.createElement("h3");
  heading.textContent = title;

  const canvas = document.createElement("canvas");
  canvas.id = id;

  block.appendChild(heading);

  if (isCategory) {

    const buttonContainer = document.createElement("div");
    buttonContainer.classList.add("chart-buttons");

    const categories = Object.keys(window.dashboardData.categories);

    categories.forEach(category => {

      const btn = document.createElement("button");
      btn.textContent = category;
      btn.classList.add("category-toggle");

      btn.onclick = () => toggleCategoryDataset(id, category, btn);

      buttonContainer.appendChild(btn);

    });

    block.appendChild(buttonContainer);
  }

  block.appendChild(canvas);
  dashboard.appendChild(block);

}



function createComparisonChart(canvasId, current, previous, title) {

  const ctx = document.getElementById(canvasId);

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: previous.labels,
      datasets: [
        {
          label: `${title} Current`,
          data: current.data,
          borderWidth: 2,
          tension: 0.3,
          borderColor: "#007bff"
        },
        {
          label: `${title} Previous`,
          data: previous.data,
          borderWidth: 2,
          borderDash: [5, 5],
          tension: 0.3,
          borderColor: "#6c757d"
        }
      ]
    },
    options: defaultChartOptions(title)
  });

  chartRegistry.set(canvasId, chart);

}



function createCategoryChart(canvasId, labels, datasets, title) {

  const ctx = document.getElementById(canvasId);

  const chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets
    },
    options: defaultChartOptions(title)
  });

  chartRegistry.set(canvasId, chart);

}



function buildCategoryDatasets(dataset, currentKey, showAll = false) {

  const baseKey = currentKey.replace('_current', '');
  const previousKey = `${baseKey}_previous`;

  const fullLength = dataset.prompts[previousKey].labels.length;

  const categories = showAll
    ? Object.keys(dataset.categories)
    : DEFAULT_VISIBLE_CATEGORIES;

  return categories.flatMap(category => {

    const currentPrompt = dataset.categories[category]?.[currentKey];
    const previousPrompt = dataset.categories[category]?.[previousKey];

    if (!currentPrompt || !previousPrompt) return [];

    return [
      {
        label: `${category} Current`,
        data: padData(currentPrompt.data, fullLength),
        borderWidth: 2,
        tension: 0.3,
        borderColor: getCategoryColor(category, "current")
      },
      {
        label: `${category} Previous`,
        data: padData(previousPrompt.data, fullLength),
        borderWidth: 2,
        borderDash: [5, 5],
        tension: 0.3,
        borderColor: getCategoryColor(category, "previous")
      }
    ];

  });

}



function padData(data, targetLength) {

  const padded = [...data];

  while (padded.length < targetLength) padded.push(null);

  return padded.slice(0, targetLength);

}



function toggleCategoryDataset(chartId, category, btn) {

  const chart = chartRegistry.get(chartId);

  const baseKey = chartId.replace("_category_chart", "_current");
  const dataset = window.dashboardData;

  const base = baseKey.replace('_current', '');
  const previousKey = `${base}_previous`;

  const fullLength = dataset.prompts[previousKey].labels.length;

  const currentPrompt = dataset.categories[category]?.[baseKey];
  const previousPrompt = dataset.categories[category]?.[previousKey];

  if (!currentPrompt || !previousPrompt) return;

  const labelCurrent = `${category} Current`;
  const labelPrevious = `${category} Previous`;

  const existingIndex = chart.data.datasets.findIndex(
    d => d.label === labelCurrent
  );

  if (existingIndex !== -1) {

    chart.data.datasets = chart.data.datasets.filter(
      d => d.label !== labelCurrent && d.label !== labelPrevious
    );

    btn.classList.remove("active");

  } else {

    chart.data.datasets.push({
      label: labelCurrent,
      data: padData(currentPrompt.data, fullLength),
      borderWidth: 2,
      tension: 0.3,
      borderColor: getCategoryColor(category, "current")
    });

    chart.data.datasets.push({
      label: labelPrevious,
      data: padData(previousPrompt.data, fullLength),
      borderWidth: 2,
      borderDash: [5, 5],
      tension: 0.3,
      borderColor: getCategoryColor(category, "previous")
    });

    btn.classList.add("active");

  }

  chart.update();
}



function getCategoryColor(category, period) {

  const colors = {
    coding: ['#3b82f6', '#1e40af'],
    creative: ['#10b981', '#047857'],
    finance: ['#f59e0b', '#b45309'],
    marketing: ['#ef4444', '#b91c1c'],
    productivity: ['#06b6d4', '#0891b2'],
    programming: ['#f97316', '#c2410c'],
    research: ['#ec4899', '#be185d']
  };

  const c = colors[category] || ['#6b7280', '#374151'];

  return period === "current" ? c[0] : c[1];

}



function defaultChartOptions(title) {

  return {
    responsive: true,
    plugins: {
      legend: {
        position: "top"
      },
      title: {
        display: true,
        text: title
      }
    },
    scales: {
      x: {
        ticks: {
          callback: function (value, index) {

            if (title.toLowerCase().includes("week")) {

              const weeks = ["Week 1", "Week 2", "Week 3", "Week 4"];
              return weeks[index] || "";

            }

            return this.getLabelForValue(value);

          }
        }
      }
    }
  };

}