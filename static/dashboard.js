// all of this is just to show us how to create a graph, they are non-functional examples.
// I will add explanation once there is some real content

// Reusable function to fetch JSON
async function fetchData(endpoint) {
  const response = await fetch(endpoint);
  return response.json();
}

// Fetch all datasets in parallel
Promise.all([
  fetchData('/api/prompts/summary'),
  fetchData('/api/prompts/by-date'),
  fetchData('/api/prompts/top')
]).then(([summary, byDate, top]) => {
    // write an api for every prompt that fetches a specific dataset
    // modify the data from the DB into the desired json format
// every fetch has its variable in then, which is then passed into a ctx for a specific graph


  // 1️⃣ Total Prompts Bar Chart
  const ctx1 = document.getElementById('totalPromptsChart').getContext('2d');
  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: Object.keys(summary.top_categories),
      datasets: [{
        label: 'Prompt count',
        data: Object.values(summary.top_categories),
        backgroundColor: 'rgba(75, 192, 192, 0.6)'
      }]
    }
  });

  // 2️⃣ Prompts Over Time Line Chart
  const ctx2 = document.getElementById('promptsOverTimeChart').getContext('2d');
  new Chart(ctx2, {
    type: 'line',
    data: {
      labels: byDate.map(d => d.date),
      datasets: [{
        label: 'Prompts per day',
        data: byDate.map(d => d.count),
        borderColor: 'rgba(153, 102, 255, 0.8)',
        fill: false
      }]
    }
  });

  // 3️⃣ Top Categories Pie Chart
  const ctx3 = document.getElementById('topCategoriesChart').getContext('2d');
  new Chart(ctx3, {
    type: 'pie',
    data: {
      labels: top.categories,
      datasets: [{
        label: 'Top categories',
        data: top.values,
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)'
        ]
      }]
    }
  });

});

fetch('/api/prompts/summary')
  .then(res => res.json())
  .then(apiData => {

    // 1️⃣ Prepare data
    const data = {
      labels: Object.keys(apiData.top_categories),
      datasets: [{
        label: 'Prompt count',
        data: Object.values(apiData.top_categories),
        backgroundColor: ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)'],
        borderColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)'],
        borderWidth: 1
      }]
    };

    // 2️⃣ Prepare config
    const config = {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    };

    // 3️⃣ Render chart
    const ctx = document.getElementById('totalPromptsChart').getContext('2d');
    new Chart(ctx, config);

  });


  // this is the best example to follow I think
  Promise.all([
    fetchData('summary'),
    fetchData('date'),
    fetchData('top')
  ]).then(([summary,date,tops]) =>{

    const summaryData = {
        labels: Object.keys(summary.some_data), //keys or categories on X-axis
        datasets :[{
            label : 'Prompt count', // Object.keys(summary.something) //these are the labels below the bars
            data: Object.values(summary.data), //numeric value for each label
            backgroundColor: '...', // a list of background colours
            borderColor:  '...' // a single or an array of colours
        }]
    }

    const summaryConfig = {
        // the stuff for configuring the graph
        type: 'bar',
      data: summaryData,
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true }
        }
      }
    }

    const ctx1 = document.getElementById('some ID of a canvas').getContext('2d');
    new Chart(ctx1, summaryConfig)
  })