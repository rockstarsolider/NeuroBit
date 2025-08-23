/**
 * Admin Analytics (Plotly)
 * Works with the existing Django admin endpoint:
 *   {% url 'admin:courses_learnersubscribeplan_analytics_data' %}
 *
 * Frontend <-> Backend mapping:
 *   hist, lines, lines_markers   -> monthly_revenue
 *   plan_month_counts            -> plan_counts  (fallback: single-series bar)
 *   path_pie                     -> paths_pie
 *   age_scatter                  -> age_scatter
 *
 * Payloads supported (back-compat):
 *   monthly_revenue -> {labels:["YYYY-MM",...], revenues:[...], counts:[...]}
 *                  or {months:[1..12], revenue:[...], count:[...]}
 *   plan_counts     -> {labels:[plan,...], counts:[...]}  // (we draw a bar)
 *                  or {months:[1..12], series:[{name,values:[]},...]} // (stacked)
 *   paths_pie       -> {labels:[...], values:[...]}
 *   age_scatter     -> {x:[...], y:[...]}  // fallback style
 *                  or {dates:[...], ages:[...], labels:[...]}
 */

let PlotlyLib = null;
async function loadPlotly() {
  if (PlotlyLib) return PlotlyLib;
  const mod = await import(/* webpackChunkName: "plotly" */ 'plotly.js-dist-min');
  PlotlyLib = mod.default || mod;
  return PlotlyLib;
}

function qs(id) { return document.getElementById(id); }

function populateYears(selectEl, preferYear) {
  const now = new Date();
  const thisYear = now.getFullYear();
  const years = [thisYear - 2, thisYear - 1, thisYear, thisYear + 1];
  selectEl.innerHTML = years.map(y => `<option value="${y}">${y}</option>`).join('');
  selectEl.value = preferYear || thisYear;
}

function formatMoney(v) {
  try {
    return new Intl.NumberFormat('fa-IR').format(Math.round(v));
  } catch {
    return String(Math.round(v));
  }
}

function mapChartParam(uiValue) {
  switch (uiValue) {
    case 'hist':
    case 'lines':
    case 'lines_markers':
      return 'monthly_revenue';
    case 'plan_month_counts':
      return 'plan_counts';
    case 'path_pie':
      return 'paths_pie';
    case 'age_scatter':
      return 'age_scatter';
    default:
      return uiValue;
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

function sum(arr) { return (arr || []).reduce((a, b) => a + (Number(b) || 0), 0); }

async function draw() {
  const Plotly = await loadPlotly();

  const chartType = qs('chartType').value;   // UI type
  const serverChart = mapChartParam(chartType); // backend param
  const year  = qs('year').value;
  const month = qs('month').value;
  const scope = qs('scope').value; // active | all
  const msgEl = qs('msg');

  msgEl.textContent = 'Loading…';

  let data;
  try {
    data = await fetchData({ chart: serverChart, year, month, scope });
  } catch (e) {
    msgEl.textContent = `Error: ${e.message}`;
    return;
  }

  const el = qs('chart');

  // KPIs — we compute if backend didn’t send explicit totals
  let totalRevenue = typeof data.total_revenue === 'number' ? data.total_revenue : null;
  let totalCount   = typeof data.total_count   === 'number' ? data.total_count   : null;

  let layout = {
    margin: { l: 48, r: 16, t: 28, b: 48 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: { automargin: true },
    yaxis: { automargin: true, tickformat: ',d' },
    showlegend: true,
  };
  let traces = [];

  // ─────────────────────────────────────────────────────────────
  // monthly_revenue -> used by hist, lines, lines_markers
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'monthly_revenue') {
    // normalize shapes
    // Backend (current): labels:["YYYY-MM"], revenues:[], counts:[]
    // Alt shape (future): months:[1..12], revenue:[], count:[]
    const labels = Array.isArray(data.labels) ? data.labels : null;
    let months = Array.isArray(data.months) ? data.months.map(Number) : null;

    const revenues = Array.isArray(data.revenues) ? data.revenues
                    : Array.isArray(data.revenue) ? data.revenue : [];
    const counts   = Array.isArray(data.counts)   ? data.counts
                    : Array.isArray(data.count)   ? data.count   : [];

    if (!months && labels) {
      // derive month 1..12 from "YYYY-MM"
      months = labels.map(s => {
        const m = String(s).slice(5, 7);
        return parseInt(m, 10);
      });
    }
    // If still nothing, ensure arrays are aligned and not undefined
    months = months || [];

    if (totalRevenue == null) totalRevenue = sum(revenues);
    if (totalCount   == null) totalCount   = sum(counts);

    if (chartType === 'hist') {
      const x = (months.length ? months : (labels || [])).map(v => String(v).padStart(2, '0'));
      traces = [{
        type: 'bar',
        x, y: revenues,
        name: 'Revenue',
        hovertemplate: 'Month %{x}<br>Revenue %{y:,} تومان<extra></extra>',
      }, {
        type: 'bar',
        x, y: counts,
        name: 'Subscriptions',
        yaxis: 'y2',
        hovertemplate: 'Month %{x}<br>Count %{y}<extra></extra>',
      }];
      layout.barmode = 'group';
      layout.yaxis2 = { overlaying: 'y', side: 'right' };
      layout.xaxis.title = 'Month';
      layout.yaxis.title = 'Value';
    } else {
      // lines / lines_markers — draw revenue trend (use labels or YYYY-MM)
      const x = labels && labels.length ? labels
                : months.map(m => String(m).padStart(2, '0'));
      traces = [{
        type: 'scatter',
        mode: chartType === 'lines_markers' ? 'lines+markers' : 'lines',
        x, y: revenues,
        name: 'Revenue',
        hovertemplate: '%{x}<br>%{y:,} تومان<extra></extra>',
      }];
      layout.xaxis.title = 'Period';
      layout.yaxis.title = 'Revenue';
    }
  }

  // ─────────────────────────────────────────────────────────────
  // plan_counts -> map UI "plan_month_counts" to either stacked series
  //               or (current backend) a single bar by plan
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'plan_counts') {
    if (Array.isArray(data.series) && Array.isArray(data.months)) {
      // stacked monthly per plan — if you ever add this server-side
      const months = data.months.map(m => String(m).padStart(2, '0'));
      traces = (data.series || []).map(s => ({
        type: 'bar',
        x: months,
        y: s.values || [],
        name: s.name || 'Plan',
        hovertemplate: '%{x}<br>%{y} learners<extra></extra>',
      }));
      layout.barmode = 'stack';
      layout.xaxis.title = 'Month';
      layout.yaxis.title = 'Learners';
      totalCount = sum((data.series || []).flatMap(s => s.values || []));
    } else {
      // current backend shape: labels=[plan], counts=[n]
      const labels = data.labels || [];
      const counts = data.counts || [];
      traces = [{
        type: 'bar',
        x: labels,
        y: counts,
        name: 'Subscriptions',
        hovertemplate: '%{x}<br>%{y} learners<extra></extra>',
      }];
      layout.barmode = 'group';
      layout.xaxis.title = 'Plan';
      layout.yaxis.title = 'Learners';
      totalCount = totalCount == null ? sum(counts) : totalCount;
    }
  }

  // ─────────────────────────────────────────────────────────────
  // paths_pie
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'paths_pie') {
    traces = [{
      type: 'pie',
      labels: data.labels || [],
      values: data.values || [],
      textinfo: 'label+percent',
      hovertemplate: '%{label}: %{value} learners<extra></extra>',
    }];
    layout.showlegend = false;
  }

  // ─────────────────────────────────────────────────────────────
  // age_scatter
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'age_scatter') {
    // Accept both {x,y} and {dates,ages,labels}
    const x = Array.isArray(data.x) ? data.x : (data.dates || []);
    const y = Array.isArray(data.y) ? data.y : (data.ages  || []);
    const text = data.labels || [];
    if (!y.length) {
      msgEl.textContent = data.note || 'No age data available.';
      Plotly.purge(el);
      // Update KPIs area but keep it quiet for this chart type
      if (totalRevenue != null) qs('kpiRevenue').textContent = formatMoney(totalRevenue);
      if (totalCount   != null) qs('kpiCount').textContent = String(totalCount);
      return;
    }
    traces = [{
      type: 'scatter',
      mode: 'markers',
      x, y, text,
      name: 'Learners',
      hovertemplate: (Array.isArray(data.x) ? 'X %{x}' : 'Date %{x}') +
                     '<br>Age %{y}<br>%{text}<extra></extra>',
    }];
    layout.xaxis.title = Array.isArray(data.x) ? 'Value' : 'Date';
    layout.yaxis.title = 'Age';
  }

  // Write KPIs (if we could compute)
  if (totalRevenue != null) qs('kpiRevenue').textContent = formatMoney(totalRevenue);
  if (totalCount   != null) qs('kpiCount').textContent   = String(totalCount);

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
