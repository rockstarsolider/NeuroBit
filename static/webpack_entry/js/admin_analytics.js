/**
 * Admin Analytics (Plotly)
 * Works with the existing Django admin endpoint:
 *   {% url 'admin:courses_learnersubscribeplan_analytics_data' %}
 *
 * Frontend <-> Backend mapping:
 *   hist, lines, lines_markers   -> monthly_revenue
 *   plan_month_counts            -> plan_counts
 *   path_pie                     -> paths_pie
 *   age_scatter                  -> age_scatter
 *
 * Payloads supported:
 *   monthly_revenue
 *     - by year:   {labels:["YYYY-MM",...], revenues:[...], counts:[...]}
 *     - by month:  {labels:["YYYY-MM-DD",...], revenues:[...], counts:[...]}
 *     - (alt)      {months:[1..12], revenue:[...], count:[...]}
 *   plan_counts     -> {labels:[plan,...], counts:[...]}
 *   paths_pie       -> {labels:[...], values:[...]}
 *   age_scatter     -> {x:[...], y:[...]}  (or {dates:[...], ages:[...], labels:[...]})
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

function monthName(m) {
  const names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const i = Math.max(1, Math.min(12, parseInt(m || 0, 10))) - 1;
  return names[i] || '';
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

  const chartType = qs('chartType').value;           // UI type
  const serverChart = mapChartParam(chartType);      // backend param
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

  // KPIs — compute if not provided
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
    const labels = Array.isArray(data.labels) ? data.labels : null; // YYYY-MM or YYYY-MM-DD
    let months = Array.isArray(data.months) ? data.months.map(Number) : null;

    const revenues = Array.isArray(data.revenues) ? data.revenues
                    : Array.isArray(data.revenue) ? data.revenue : [];
    const counts   = Array.isArray(data.counts)   ? data.counts
                    : Array.isArray(data.count)   ? data.count   : [];

    if (!months && labels) {
      // if labels are YYYY-MM, derive month; if YYYY-MM-DD, do not derive
      const looksLikeMonth = labels.every(s => String(s).length === 7);
      months = looksLikeMonth ? labels.map(s => parseInt(String(s).slice(5, 7), 10)) : null;
    }

    if (totalRevenue == null) totalRevenue = sum(revenues);
    if (totalCount   == null) totalCount   = sum(counts);

    const useMonthsAxis = Array.isArray(months) && months.length > 0;
    const xForBars = useMonthsAxis ? months.map(m => String(m).padStart(2, '0')) : (labels || []);
    const xTitle = useMonthsAxis ? 'Month' : 'Date';
    const hoverMonth = useMonthsAxis ? 'Month %{x}' : 'Date %{x}';

    if (chartType === 'hist') {
      traces = [{
        type: 'bar',
        x: xForBars, y: revenues,
        name: 'Revenue',
        hovertemplate: `${hoverMonth}<br>Revenue %{y:,} تومان<extra></extra>`,
      }, {
        type: 'bar',
        x: xForBars, y: counts,
        name: 'Subscriptions',
        yaxis: 'y2',
        hovertemplate: `${hoverMonth}<br>Count %{y}<extra></extra>`,
      }];
      layout.barmode = 'group';
      layout.yaxis2 = { overlaying: 'y', side: 'right' };
      layout.xaxis.title = xTitle;
      layout.yaxis.title = 'Value';
    } else {
      const x = labels && labels.length ? labels
                : (months || []).map(m => String(m).padStart(2, '0'));
      traces = [{
        type: 'scatter',
        mode: chartType === 'lines_markers' ? 'lines+markers' : 'lines',
        x, y: revenues,
        name: 'Revenue',
        hovertemplate: '%{x}<br>%{y:,} تومان<extra></extra>',
      }];
      layout.xaxis.title = labels && labels.length && labels[0].length === 10 ? 'Date' : 'Period';
      layout.yaxis.title = 'Revenue';
    }
  }

  // ─────────────────────────────────────────────────────────────
  // plan_counts -> "Plan count (bar)" — respects month
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'plan_counts') {
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

  // ─────────────────────────────────────────────────────────────
  // paths_pie — respects month
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
  // age_scatter — NOW respects month (server filters it)
  // ─────────────────────────────────────────────────────────────
  if (serverChart === 'age_scatter') {
    const x = Array.isArray(data.x) ? data.x : (data.dates || []);
    const y = Array.isArray(data.y) ? data.y : (data.ages  || []);
    const text = data.labels || [];
    if (!y.length) {
      msgEl.textContent = data.note || 'No age data available for this filter.';
      Plotly.purge(el);
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

  // Write KPIs
  if (totalRevenue != null) qs('kpiRevenue').textContent = formatMoney(totalRevenue);
  if (totalCount   != null) qs('kpiCount').textContent   = String(totalCount);

  await Plotly.react(el, traces, layout, { responsive: true, displaylogo: false });

  const monthNote = month ? ` • Month: ${monthName(month)}` : '';
  msgEl.textContent =
    (scope === 'active' ? 'Filtered: active learners' : 'Filtered: all learners') + monthNote;
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

  // Each control just redraws with current chart type (no auto-switching)
  ['chartType','year','month','scope'].forEach(id => {
    qs(id).addEventListener('change', draw);
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  attachUI();
  draw();
});
