/**
 * Progress Analytics (Plotly) — Learning Path
 * Endpoints are injected as data-* on #pa-root
 */
let PlotlyLib = null;
async function loadPlotly() {
  if (PlotlyLib) return PlotlyLib;
  const mod = await import(/* webpackChunkName: "plotly" */ 'plotly.js-dist-min');
  PlotlyLib = mod.default || mod;
  return PlotlyLib;
}

const el = (id) => document.getElementById(id);
const debounce = (fn, ms=250) => { let t=null; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),ms); }; };

function showMsg(text) { el('pa-msg').textContent = text; }

function getUrls() {
  const root = el('pa-root');
  return {
    dataUrl: root.dataset.dataUrl,
    choicesUrl: root.dataset.choicesUrl,
    searchMentorsUrl: root.dataset.searchMentorsUrl,
    searchLearnersUrl: root.dataset.searchLearnersUrl,
  };
}

async function fetchJSON(url, params = {}) {
  const u = new URL(url, window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') u.searchParams.set(k, v);
  });
  const res = await fetch(u.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function setupYears() {
  const s = el('pa-year');
  const now = new Date();
  const y = now.getFullYear();
  const years = ['', y - 2, y - 1, y, y + 1]; // '' = All years (default)
  s.innerHTML = years.map(v => {
    const label = v === '' ? 'All years' : String(v);
    return `<option value="${v}">${label}</option>`;
  }).join('');
  s.value = '';
}

async function loadInitialChoices() {
  const { choicesUrl } = getUrls();
  const data = await fetchJSON(choicesUrl, {});
  // LPs
  const lpSel = el('pa-lp');
  lpSel.innerHTML = (data.learning_paths || [])
    .map(x => `<option value="${x.id}">${x.name}</option>`).join('');
  if (data.learning_paths && data.learning_paths.length) lpSel.value = data.learning_paths[0].id;

  // seed suggestions
  await refreshMentors('');
  await refreshLearners('');
}

function getSelectedId(raw) {
  const s = String(raw || '');
  if (!s) return '';
  const m = s.match(/^\s*(\d+)/); // "12" or "12 — Full Name"
  return m ? m[1] : '';
}

async function refreshMentors(q='') {
  const { searchMentorsUrl } = getUrls();
  const lp = el('pa-lp').value;
  const learnerId = getSelectedId(el('pa-learner-id').value);
  const data = await fetchJSON(searchMentorsUrl, { lp, learner: learnerId, q });
  const list = el('pa-mentor-list');
  list.innerHTML = (data.results || [])
    .map(x => `<option value="${x.id} — ${x.name}"></option>`)
    .join('');
}

async function refreshLearners(q='') {
  const { searchLearnersUrl } = getUrls();
  const lp = el('pa-lp').value;
  const mentorId = getSelectedId(el('pa-mentor-id').value);
  const data = await fetchJSON(searchLearnersUrl, { lp, mentor: mentorId, q });
  const list = el('pa-learner-list');
  list.innerHTML = (data.results || [])
    .map(x => `<option value="${x.id} — ${x.name}"></option>`)
    .join('');
}

function paramsFromUI() {
  return {
    chart: el('pa-chart-type').value,
    lp: el('pa-lp').value,
    mentor: getSelectedId(el('pa-mentor-id').value),
    learner: getSelectedId(el('pa-learner-id').value),
    year: el('pa-year').value,
    month: el('pa-month').value,
  };
}

function monthName(m) {
  const names = ['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const i = parseInt(m,10); return isNaN(i) ? '' : names[i];
}

async function draw() {
  const Plotly = await loadPlotly();
  const { dataUrl } = getUrls();
  const p = paramsFromUI();

  if (!p.lp) {
    showMsg('Select a learning path to load charts.');
    Plotly.purge('pa-plot');
    return;
  }
  if (p.chart === 'learner_progress' && !p.learner) {
    showMsg('Select a learner for the "Learner progress" chart.');
    Plotly.purge('pa-plot');
    return;
  }

  showMsg('Loading…');
  let data;
  try {
    data = await fetchJSON(dataUrl, p);
  } catch (e) {
    showMsg(`Error: ${e.message}`);
    return;
  }

  const layout = {
    margin: { l: 48, r: 16, t: 32, b: 64 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    xaxis: { automargin: true },
    yaxis: { automargin: true, tickformat: ',d' },
    showlegend: true,
  };
  let traces = [];

  if (p.chart === 'step_funnel') {
    const labels = data.labels || [];
    const completed = data.completed || [];
    const total = data.total || [];
    const remaining = total.map((t, i) => Math.max(0, (t || 0) - (completed[i] || 0)));
    traces = [
      { type: 'bar', x: labels, y: completed, name: 'Completed',
        hovertemplate: '%{x}<br>%{y} learners<extra></extra>' },
      { type: 'bar', x: labels, y: remaining, name: 'Remaining',
        hovertemplate: '%{x}<br>%{y} learners<extra></extra>' },
    ];
    layout.barmode = 'stack';
    layout.xaxis.title = 'Step';
    layout.yaxis.title = 'Learners';
  }

  if (p.chart === 'avg_score') {
    traces = [{
      type: 'bar',
      x: data.labels || [],
      y: data.scores || [],
      hovertemplate: '%{x}<br>%{y:.2f} avg<extra></extra>',
      name: 'Average score',
    }];
    layout.xaxis.title = 'Step';
    layout.yaxis.title = 'Average score';
  }

  if (p.chart === 'completions_over_time') {
    traces = [{
      type: 'bar',
      x: data.labels || [],
      y: data.daily || [],
      name: 'Daily completions',
      hovertemplate: '%{x}<br>%{y} completions<extra></extra>',
    }, {
      type: 'scatter',
      mode: 'lines+markers',
      x: data.labels || [],
      y: data.cumulative || [],
      name: 'Cumulative',
      hovertemplate: '%{x}<br>%{y} total<extra></extra>',
      yaxis: 'y2',
    }];
    layout.yaxis2 = { overlaying: 'y', side: 'right' };
    layout.xaxis.title = 'Date';
    layout.yaxis.title = 'Completions';
  }

  if (p.chart === 'learner_progress') {
    traces = [{
      type: 'bar',
      x: data.labels || [],
      y: data.promised_days || [],
      name: 'Promised (days)',
      hovertemplate: '%{x}<br>%{y} promised<extra></extra>',
    }, {
      type: 'bar',
      x: data.labels || [],
      y: data.actual_days || [],
      name: 'Actual (days)',
      hovertemplate: '%{x}<br>%{y} actual<extra></extra>',
    }];
    layout.barmode = 'group';
    layout.xaxis.title = 'Step';
    layout.yaxis.title = 'Days';
  }

  await Plotly.react('pa-plot', traces, layout, { responsive: true, displaylogo: false });

  const scopeBits = [
    p.mentor ? `Mentor #${p.mentor}` : 'All mentors',
    p.learner ? `Learner #${p.learner}` : 'All learners',
    p.month ? `Month: ${monthName(p.month)}` : null,
    p.year ? `Year: ${p.year}` : null,
  ].filter(Boolean);
  showMsg(scopeBits.join(' • '));
}

async function refreshAfterLPChange() {
  el('pa-mentor-input').value = ''; el('pa-mentor-id').value = '';
  el('pa-learner-input').value = ''; el('pa-learner-id').value = '';
  await refreshMentors('');
  await refreshLearners('');
  await draw();
}

function setupInstantSearch() {
  const mentorInput = el('pa-mentor-input');
  const mentorId = el('pa-mentor-id');
  const learnerInput = el('pa-learner-input');
  const learnerId = el('pa-learner-id');

  // typing → search suggestions
  mentorInput.addEventListener('input', debounce(async () => {
    mentorId.value = '';
    await refreshMentors(mentorInput.value);
    // when typing a mentor, reset learner suggestions to “no mentor filter”
    await refreshLearners('');
  }, 200));

  learnerInput.addEventListener('input', debounce(async () => {
    learnerId.value = '';
    await refreshLearners(learnerInput.value);
    // when typing a learner, give the UI a chance to pick & then filter mentors on change event
  }, 200));

  // choosing a mentor value (from datalist)
  mentorInput.addEventListener('change', async () => {
    const id = getSelectedId(mentorInput.value);
    mentorId.value = id || '';
    await refreshLearners(''); // cascade: learners constrained by mentor
    await draw();
  });

  // choosing a learner value (from datalist)
  learnerInput.addEventListener('change', async () => {
    const id = getSelectedId(learnerInput.value);
    learnerId.value = id || '';
    await refreshMentors(''); // cascade: mentors constrained by learner
    await draw();
  });
}

function setupEvents() {
  el('pa-refresh').addEventListener('click', draw);
  el('pa-reset').addEventListener('click', async () => {
    el('pa-chart-type').value = 'step_funnel';
    el('pa-year').value = '';
    el('pa-month').value = '';
    el('pa-mentor-input').value = '';
    el('pa-mentor-id').value = '';
    el('pa-learner-input').value = '';
    el('pa-learner-id').value = '';
    await refreshMentors('');
    await refreshLearners('');
    await draw();
  });

  el('pa-lp').addEventListener('change', refreshAfterLPChange);

  // simple changes that don’t affect options
  el('pa-chart-type').addEventListener('change', draw);
  el('pa-year').addEventListener('change', draw);
  el('pa-month').addEventListener('change', draw);
}

async function init() {
  setupYears();
  await loadInitialChoices();
  setupInstantSearch();
  setupEvents();
  await draw();
}
document.addEventListener('DOMContentLoaded', init);
