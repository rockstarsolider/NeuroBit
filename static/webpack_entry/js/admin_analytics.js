// static/webpack_entry/js/admin_analytics.js
function qs(id){ return document.getElementById(id); }


async function getPlotly() {
  const mod = await import(/* webpackChunkName:"plotly" */ 'plotly.js-cartesian-dist-min');
  const Plotly = mod.default || mod;
  if (Plotly.setPlotConfig) Plotly.setPlotConfig({ locale: 'fa' });
  return Plotly;
}



async function loadData(endpoint, year){
  const url = new URL(endpoint, window.location.origin);
  url.searchParams.set('year', year);
  const res = await fetch(url.toString(), { credentials: 'same-origin' });
  if(!res.ok) throw new Error(`Analytics fetch failed: ${res.status}`);
  return await res.json();
}

function renderKpis(d){
  const revTotal = (d.revenue_total || 0);
  const activeNow = (d.active_now || 0);
  const kpiRev = qs('kpi-rev'); const kpiActive = qs('kpi-active');
  if (kpiRev) kpiRev.textContent = revTotal.toLocaleString('fa-IR');
  if (kpiActive) kpiActive.textContent = activeNow;
}

async function renderChart(d){
  const Plotly = await getPlotly();
  const chartEl = qs('chart'); if (!chartEl) return;
  const data = [{ x: d.labels || [], y: d.revenues || [], type: 'bar', name: 'Revenue (T)' }];
  const layout = { title: `Monthly Revenue – ${d.year}`, margin: { t: 48 }, yaxis: { tickformat: ',d' } };
  if (chartEl.__plotted) Plotly.react(chartEl, data, layout, { displayModeBar: false });
  else { Plotly.newPlot(chartEl, data, layout, { displayModeBar: false }); chartEl.__plotted = true; }
}

async function refresh(root){
  const endpoint = root.dataset.endpoint;
  const yearSel = qs('year');
  const year = yearSel ? yearSel.value : new Date().getFullYear();
  const d = await loadData(endpoint, year);
  renderKpis(d);
  await renderChart(d);
}

function boot(){
  const root = qs('analytics-root'); if (!root) return;
  const yearSel = qs('year'); const refreshBtn = qs('refresh');
  const doRefresh = () => refresh(root).catch(console.error);
  yearSel && yearSel.addEventListener('change', doRefresh);
  refreshBtn && refreshBtn.addEventListener('click', doRefresh);
  doRefresh();
}

document.addEventListener('DOMContentLoaded', boot);
