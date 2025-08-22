(function () {
  const node = document.getElementById("subdata");
  if (!node) return;
  const data = JSON.parse(node.textContent || "{}");
  const k = data.kpis || {active: 0, expired: 0, revenue: 0};

  // KPI cards (Unfold’s Tailwind utility classes)
  const kpis = [
    {title: "Active", value: k.active},
    {title: "Expired", value: k.expired},
    {title: "Revenue (T)", value: (k.revenue || 0).toLocaleString()},
  ];
  document.getElementById("kpis").innerHTML = kpis.map(
    x => `<div class="box"><div class="box__body"><h3 class="text-sm opacity-70">${x.title}</h3><p class="text-2xl font-bold">${x.value}</p></div></div>`
  ).join("");

  // Chart
  const labels = data.labels || [];
  const counts = data.counts || [];
  if (window.Plotly) {
    Plotly.newPlot("chart", [{x: labels, y: counts, type: "bar"}],
      {title: "Subscriptions started per day", margin: {t: 40}});
  }
})();
