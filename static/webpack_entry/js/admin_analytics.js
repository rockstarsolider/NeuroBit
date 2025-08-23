/**
 * Admin Analytics (Plotly)
 * NOTE: Add the npm dep once:
 *   npm i --save plotly.js-dist-min
 *
 * Back-end endpoint must be wired to:
 *   {% url 'admin:courses_learnersubscribeplan_analytics_data' %}
 *
 * The view should accept query params:
 *   - chart: "hist" | "lines" | "lines_markers" | "plan_month_counts" | "path_pie" | "age_scatter"
 *   - year: YYYY
 *   - month: 1..12 (optional)
 *   - scope: "active" | "all"
 * and respond with a JSON payload shaped as described per-chart below.
 */

let PlotlyLib = null;
async function loadPlotly() {
  if (PlotlyLib) return PlotlyLib;
  // dynamic import keeps the main bundle small
  const mod = await import(/* webpackChunkName: "plotly" */ 'plotly.js-dist-min');
  PlotlyLib = mod.default || mod;
  return PlotlyLib;
}

function qs(id) { return document.getElementById(id); }

function populateYears(selectEl) {
  const now = new Date();
  const thisYear = now.getFullYear();
  const years = [thisYear - 2, thisYear - 1, thisYear, thisYear + 1];
  selectEl.innerHTML = years.map(y => `<option value="${y}">${y}</option>`).join('');
  selectEl.value = thisYear;
}

function formatMoney(v) {
  try {
    return new Intl.NumberFormat('fa-IR').format(Math.round(v));
  } catch {
    return String(Math.round(v));
  }
}

async function fetchData(params) {
  const root = document.getElementById('analytics-root');
  const baseUrl = root.dataset.url;
  const u = new URL(baseUrl, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') u.searchParams.set(k, v);
  });
  const res = await fetch(u.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function draw() {
  const Plotly = await loadPlotly();

  const chartType = qs('chartType').value;
  const year = qs('year').value;
  const month = qs('month').value;
  const scope = qs('scope').value; // active | all
  const msgEl = qs('msg');

  msgEl.textContent = 'Loading…';

  let data;
  try {
    data = await fetchData({ chart: chartType, year, month, scope });
  } catch (e) {
    msgEl.textContent = `Error: ${e.message}`;
    return;
  }

  const el = qs('chart');

  // Update KPIs if present
  if (typeof data.total_revenue === 'number') qs('kpiRevenue').textContent = formatMoney(data.total_revenue);
  if (typeof data.total_count === 'number') qs('kpiCount').textContent = String(data.total_count);

  let layout = {
    margin: { l: 48, r: 16, t: 28, b: 48 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: { automargin: true },
    yaxis: { automargin: true, tickformat: ',d' },
    showlegend: true,
  };
  let traces = [];

  /**
   * EXPECTED PAYLOADS
   *
   * hist:
   *   { months:[1..12], revenue:[12], count:[12], total_revenue, total_count }
   *
   * lines / lines_markers:
   *   { dates:["YYYY-MM-DD",...], revenue:[...], count:[...], total_revenue, total_count }
   *
   * plan_month_counts:
   *   { months:[1..12], series:[ {name:"Pro", values:[12]}, ... ] }
   *
   * path_pie:
   *   { labels:["Backend","Frontend","AI"], values:[..] }
   *
   * age_scatter:
   *   { ages:[...], dates:["YYYY-MM-DD",...], labels:["Pro",...], note?:string }
   */

  if (chartType === 'hist') {
    const months = (data.months || []).map(m => m.toString().padStart(2, '0'));
    traces = [{
      type: 'bar',
      x: months,
      y: data.revenue || [],
      name: 'Revenue',
      hovertemplate: 'Month %{x}<br>Revenue %{y:,} تومان<extra></extra>',
    }, {
      type: 'bar',
      x: months,
      y: data.count || [],
      name: 'Subscriptions',
      yaxis: 'y2',
      hovertemplate: 'Month %{x}<br>Count %{y}<extra></extra>',
    }];
    layout.barmode = 'group';
    layout.yaxis2 = { overlaying: 'y', side: 'right' };
    layout.xaxis.title = 'Month';
  }

  if (chartType === 'lines' || chartType === 'lines_markers') {
    traces = [{
      type: 'scatter',
      mode: chartType === 'lines_markers' ? 'lines+markers' : 'lines',
      x: data.dates || [],
      y: data.revenue || [],
      name: 'Revenue',
      hovertemplate: '%{x}<br>%{y:,} تومان<extra></extra>',
    }];
    layout.xaxis.type = 'date';
    layout.xaxis.title = 'Date';
    layout.yaxis.title = 'Revenue';
  }

  if (chartType === 'plan_month_counts') {
    const months = (data.months || []).map(m => m.toString().padStart(2, '0'));
    traces = (data.series || []).map(s => ({
      type: 'bar',
      x: months,
      y: s.values,
      name: s.name,
      hovertemplate: '%{x}<br>%{y} learners<extra></extra>',
    }));
    layout.barmode = 'stack';
    layout.xaxis.title = 'Month';
    layout.yaxis.title = 'Learners';
  }

  if (chartType === 'path_pie') {
    traces = [{
      type: 'pie',
      labels: data.labels || [],
      values: data.values || [],
      textinfo: 'label+percent',
      hovertemplate: '%{label}: %{value} learners<extra></extra>',
    }];
    layout.showlegend = false;
  }

  if (chartType === 'age_scatter') {
    if (!data.ages || data.ages.length === 0) {
      msgEl.textContent = data.note || 'No age data available.';
      Plotly.purge(el);
      return;
    }
    traces = [{
      type: 'scatter',
      mode: 'markers',
      x: data.dates || [],
      y: data.ages || [],
      text: data.labels || [],
      name: 'Learners',
      hovertemplate: 'Date %{x}<br>Age %{y}<br>%{text}<extra></extra>',
    }];
    layout.xaxis.type = 'date';
    layout.xaxis.title = 'Date';
    layout.yaxis.title = 'Age';
  }

  await Plotly.react(el, traces, layout, { responsive: true, displaylogo: false });
  msgEl.textContent = scope === 'active' ? 'Filtered: active learners' : 'Filtered: all learners';
}

function attachUI() {
  populateYears(qs('year'));
  qs('refresh').addEventListener('click', draw);
  qs('reset').addEventListener('click', () => {
    populateYears(qs('year'));
    qs('month').value = '';
    qs('scope').value = 'active';
    qs('chartType').value = 'hist';
    draw();
  });
  ['chartType','year','month','scope'].forEach(id => {
    qs(id).addEventListener('change', draw);
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  attachUI();
  draw();
});
