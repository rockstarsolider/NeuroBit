// static/webpack_entry/js/admin_analytics.js

function qs(id){ return document.getElementById(id); }

async function getPlotly() {
  // Modular Plotly: core + traces we need + fa locale
  const [coreMod, barMod, histMod, scatterMod, pieMod, faMod] = await Promise.all([
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/core'),
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/bar'),
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/histogram'),
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/scatter'),
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/pie'),
    import(/* webpackChunkName:"plotly" */ 'plotly.js/lib/locales/fa'),
  ]);
  const Plotly  = coreMod.default || coreMod;
  const bar     = barMod.default || barMod;
  const hist    = histMod.default || histMod;
  const scatter = scatterMod.default || scatterMod;
  const pie     = pieMod.default || pieMod;
  Plotly.register([bar, hist, scatter, pie, (faMod.default || faMod)]);
  if (Plotly.setPlotConfig) Plotly.setPlotConfig({ locale: 'fa' });
  return Plotly;
}

async function loadData(endpoint, chart, year){
  const url = new URL(endpoint, window.location.origin);
  url.searchParams.set('chart', chart);
  if (year) url.searchParams.set('year', year);
  const res = await fetch(url.toString(), { credentials: 'same-origin' });
  if(!res.ok) throw new Error(`Analytics fetch failed: ${res.status}`);
  return await res.json();
}

function setKpis(d){
  const rev = d.revenue_total ?? (Array.isArray(d.revenues) ? d.revenues.reduce((a,b)=>a+(b||0),0) : 0);
  qs('kpi-rev').textContent = (rev||0).toLocaleString('fa-IR');
  qs('kpi-active').textContent = d.active_now ?? 0;
}

async function draw(chart, d){
  const Plotly = await getPlotly();
  const el = qs('chart');
  let data = [], layout = { margin:{t:48} };

  if (chart === 'monthly_bar') {
    data = [{ x: d.labels||[], y: d.revenues||[], type: 'bar', name: 'Revenue (T)' }];
    layout.title = `Monthly Revenue – ${d.year}`;
    layout.yaxis = { tickformat: ',d' };
  }
  else if (chart === 'revenue_line') {
    data = [{ x: d.x||[], y: d.y||[], type: 'scatter', mode: 'lines+markers', name: 'Revenue (T)' }];
    layout.title = `Daily Revenue – ${d.year}`;
    layout.yaxis = { tickformat: ',d' };
    layout.xaxis = { type: 'date' };
  }
  else if (chart === 'paths_pie') {
    data = [{ labels: d.labels||[], values: d.values||[], type: 'pie', hole: 0 }];
    layout.title = `Learners by Learning-Path`;
  }
  else if (chart === 'age_scatter') {
    data = [{ x: d.x||[], y: d.y||[], type: 'scatter', mode: 'markers', name: 'Learners' }];
    layout.title = `Learner Age vs Revenue`;
    layout.xaxis = { title: d.x_title || 'Age' };
    layout.yaxis = { title: d.y_title || 'Revenue (T)', tickformat: ',d' };
  }

  if (el.__plotted) Plotly.react(el, data, layout, { displayModeBar: false });
  else { Plotly.newPlot(el, data, layout, { displayModeBar: false }); el.__plotted = true; }
}

function toggleYearVisibility(){
  const chart = qs('chart-type').value;
  const yearWrap = qs('year-wrap');
  // Year relevant for time-based charts
  yearWrap.style.display = (chart === 'monthly_bar' || chart === 'revenue_line') ? '' : 'none';
}

async function refresh(){
  const root = qs('analytics-root');
  const chart = qs('chart-type').value;
  const year = qs('year') ? qs('year').value : undefined;
  const d = await loadData(root.dataset.endpoint, chart, year);
  setKpis(d);
  await draw(chart, d);
}

function boot(){
  const root = qs('analytics-root'); if (!root) return;
  toggleYearVisibility();
  qs('chart-type').addEventListener('change', () => { toggleYearVisibility(); refresh(); });
  const yr = qs('year'); if (yr) yr.addEventListener('change', refresh);
  const btn = qs('refresh'); if (btn) btn.addEventListener('click', refresh);
  refresh().catch(console.error);
}
document.addEventListener('DOMContentLoaded', boot);
