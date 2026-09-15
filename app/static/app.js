const $ = (id) => document.getElementById(id);
const state = {
  token: localStorage.getItem('jobfit_token') || '',
  jobs: [], applications: [], profile: null, remoteJobs: [], showFavorites: false,
  favorites: new Set(JSON.parse(localStorage.getItem('jobfit_favorites') || '[]')),
};
const stages = ['applied','screening','interview','technical','offer','rejected'];

function toast(message, type='good') {
  const el = $('notice');
  el.textContent = message;
  el.className = `notice ${type}`;
  setTimeout(() => { el.className = 'notice hidden'; }, 3200);
}

async function api(path, options={}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map(x => x.msg).join(', ') : (data.detail || 'Request failed');
    if (response.status === 401 && path !== '/auth/login') logout(false);
    throw new Error(detail);
  }
  return data;
}

function setAuthTab(tab) {
  $('loginTab').classList.toggle('active', tab === 'login');
  $('registerTab').classList.toggle('active', tab === 'register');
  $('loginForm').classList.toggle('hidden', tab !== 'login');
  $('registerForm').classList.toggle('hidden', tab !== 'register');
}

async function login(event) {
  event.preventDefault();
  try {
    const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ email: $('loginEmail').value, password: $('loginPassword').value }) });
    state.token = data.access_token;
    localStorage.setItem('jobfit_token', state.token);
    await refreshAll();
    toast('Login realizado. Dashboard sincronizado.');
  } catch (error) { toast(error.message, 'bad'); }
}

async function register(event) {
  event.preventDefault();
  try {
    const payload = { full_name: $('regName').value, email: $('regEmail').value, password: $('regPassword').value };
    await api('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
    $('loginEmail').value = payload.email;
    $('loginPassword').value = payload.password;
    setAuthTab('login');
    toast('Conta criada. Entre para continuar.');
  } catch (error) { toast(error.message, 'bad'); }
}

function logout(show=true) {
  state.token = ''; state.jobs = []; state.applications = []; state.profile = null;
  localStorage.removeItem('jobfit_token');
  updateAuthUI(); renderJobs(); renderPipeline(); updateStats(); renderRemoteJobs();
  if (show) toast('Sessão encerrada.');
}

function updateAuthUI() {
  const logged = Boolean(state.token && state.profile);
  $('authCard').classList.toggle('hidden', logged);
  $('profileCard').classList.toggle('hidden', !logged);
  $('workspace').classList.toggle('hidden', !logged);
  $('logoutBtn').classList.toggle('hidden', !logged);
  $('welcome').textContent = logged ? `Olá, ${state.profile.full_name}` : 'API + dashboard full-stack para encontrar oportunidades e acompanhar candidaturas.';
}

async function saveProfile(event) {
  event.preventDefault();
  try {
    state.profile = await api('/profile', { method: 'PUT', body: JSON.stringify({ skills: $('skills').value, summary: $('summary').value }) });
    await Promise.all(state.jobs.map(job => api(`/jobs/${job.id}/rescore`, { method: 'POST' })));
    await loadJobs(); renderRemoteJobs(); updateStats();
    toast('Perfil atualizado e scores recalculados.');
  } catch (error) { toast(error.message, 'bad'); }
}

async function createJob(event) {
  event.preventDefault();
  try {
    const min = $('salaryMin').value, max = $('salaryMax').value;
    await api('/jobs', { method: 'POST', body: JSON.stringify({
      title: $('jobTitle').value, company: $('jobCompany').value,
      description: $('jobDescription').value, requirements: $('jobRequirements').value,
      location: $('jobLocation').value || 'Remote',
      salary_min: min === '' ? null : Number(min), salary_max: max === '' ? null : Number(max),
    }) });
    $('jobForm').reset(); $('jobLocation').value = 'Remote';
    await loadJobs(); updateStats(); renderRemoteJobs();
    toast('Vaga adicionada e score calculado.');
  } catch (error) { toast(error.message, 'bad'); }
}

function discoveryParams() {
  const p = new URLSearchParams({
    q: $('remoteQuery').value.trim(), source: $('remoteSource').value,
    location: $('remoteLocation').value.trim(), category: $('remoteCategory').value.trim(),
    job_type: $('remoteType').value.trim(), remote_only: $('remoteOnly').checked ? 'true' : 'false',
    sort: $('remoteSort').value === 'match' ? 'recent' : $('remoteSort').value, limit: '30',
  });
  return p.toString();
}

async function searchRemoteJobs(event) {
  event.preventDefault();
  const root = $('remoteJobs');
  root.innerHTML = '<div class="empty">Buscando oportunidades em múltiplas fontes...</div>';
  try {
    const data = await api(`/discover/jobs?${discoveryParams()}`);
    state.remoteJobs = data.jobs || [];
    state.showFavorites = false;
    $('showFavoritesBtn').textContent = '★ Ver favoritas';
    renderRemoteJobs();
    $('remoteCount').textContent = `${state.remoteJobs.length} vaga(s) encontrada(s) · ${data.providers.join(' + ')}`;
  } catch (error) {
    root.innerHTML = `<div class="empty">Não foi possível buscar vagas agora: ${escapeHtml(error.message)}</div>`;
  }
}

function skillSet(text='') {
  return new Set(String(text).toLowerCase().match(/[a-z0-9+#.-]{2,}/g) || []);
}

function quickMatch(job) {
  if (!state.profile?.skills) return null;
  const profile = skillSet(state.profile.skills);
  const target = skillSet(`${job.title} ${job.requirements || ''}`);
  if (!target.size) return 0;
  let hit = 0; target.forEach(x => { if (profile.has(x)) hit++; });
  return Math.round((hit / target.size) * 100);
}

function isDuplicateRemote(job) {
  const t = String(job.title || '').trim().toLowerCase();
  const c = String(job.company || '').trim().toLowerCase();
  return state.jobs.some(x => x.title.trim().toLowerCase() === t && x.company.trim().toLowerCase() === c);
}

function persistFavorites() {
  localStorage.setItem('jobfit_favorites', JSON.stringify([...state.favorites]));
}

function toggleFavorite(index) {
  const job = state.remoteJobs[index]; if (!job) return;
  const id = String(job.external_id || job.url || `${job.company}:${job.title}`);
  state.favorites.has(id) ? state.favorites.delete(id) : state.favorites.add(id);
  persistFavorites(); renderRemoteJobs();
}

function toggleFavoritesView() {
  state.showFavorites = !state.showFavorites;
  $('showFavoritesBtn').textContent = state.showFavorites ? '← Ver resultados' : '★ Ver favoritas';
  renderRemoteJobs();
}

function formatDate(value) {
  if (!value) return '';
  const d = new Date(value); if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleDateString('pt-BR');
}

function renderRemoteJobs() {
  const root = $('remoteJobs'); if (!root) return;
  let jobs = state.remoteJobs.map((job, index) => ({ job, index, match: quickMatch(job) }));
  if (state.showFavorites) jobs = jobs.filter(({job}) => state.favorites.has(String(job.external_id || job.url || `${job.company}:${job.title}`)));
  if ($('remoteSort')?.value === 'match') jobs.sort((a,b) => (b.match ?? -1) - (a.match ?? -1));
  if (!jobs.length) {
    root.innerHTML = `<div class="empty">${state.showFavorites ? 'Nenhuma vaga favorita nesta busca.' : 'Nenhuma vaga encontrada. Tente outro termo ou remova algum filtro.'}</div>`;
    return;
  }
  root.innerHTML = jobs.map(({job,index,match}) => {
    const id = String(job.external_id || job.url || `${job.company}:${job.title}`);
    const fav = state.favorites.has(id), duplicate = isDuplicateRemote(job);
    const meta = [job.company, job.location, job.job_type, job.salary, formatDate(job.published_at)].filter(Boolean).map(escapeHtml).join(' · ');
    const description = escapeHtml(job.description || '').slice(0, 360);
    const sourceUrl = String(job.url || '').startsWith('http') ? job.url : '#';
    const matchBadge = match === null ? '' : `<span class="score small-score">${match}% match</span>`;
    return `<article class="job remote-job"><div class="job-head"><div><h4>${escapeHtml(job.title)}</h4><div class="job-meta">${meta}</div></div><div class="remote-badges">${matchBadge}<span class="chip">${escapeHtml(job.source || 'Fonte')}</span></div></div><p class="muted">${description}${(job.description || '').length > 360 ? '…' : ''}</p><div class="job-actions"><a class="btn small" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">Ver vaga original</a><button class="btn small ${fav?'favorite-on':''}" onclick="toggleFavorite(${index})">${fav?'★ Favorita':'☆ Favoritar'}</button>${duplicate?'<span class="chip good">Já salva</span>':`<button class="btn success small" onclick="saveRemoteJob(${index})">Salvar no JobFit</button>`}</div></article>`;
  }).join('');
}

async function saveRemoteJob(index) {
  if (!state.token) {
    toast('Faça login ou crie uma conta para salvar a vaga no seu workspace.', 'bad');
    $('authCard').scrollIntoView({ behavior: 'smooth', block: 'center' }); return;
  }
  const job = state.remoteJobs[index]; if (!job) return;
  if (isDuplicateRemote(job)) { toast('Essa vaga já está salva no seu workspace.', 'bad'); return; }
  try {
    await api('/jobs', { method: 'POST', body: JSON.stringify({
      title: job.title, company: job.company,
      description: `${job.description}\n\nFonte: ${job.source || 'externa'}\n${job.url || ''}`,
      requirements: job.requirements || '', location: job.location || 'Remote',
      salary_min: null, salary_max: null,
    }) });
    await loadJobs(); updateStats(); renderRemoteJobs();
    toast('Vaga salva no workspace e match calculado.');
  } catch (error) { toast(error.message, 'bad'); }
}

async function applyToJob(jobId) {
  try {
    await api('/applications', { method: 'POST', body: JSON.stringify({ job_id: jobId, stage: 'applied', notes: 'Candidatura registrada no JobFit.' }) });
    await Promise.all([loadJobs(), loadApplications()]); updateStats();
    toast('Candidatura registrada.');
  } catch (error) { toast(error.message, 'bad'); }
}

async function rescoreJob(jobId) { try { await api(`/jobs/${jobId}/rescore`, { method:'POST' }); await loadJobs(); toast('Score recalculado.'); } catch(error){ toast(error.message,'bad'); } }
async function deleteJob(jobId) { if(!confirm('Excluir esta vaga?')) return; try { await api(`/jobs/${jobId}`,{method:'DELETE'}); await Promise.all([loadJobs(),loadApplications()]); updateStats(); renderRemoteJobs(); toast('Vaga excluída.'); } catch(error){ toast(error.message,'bad'); } }
async function showAnalysis(jobId) { try { const data=await api(`/jobs/${jobId}/analysis`); const box=$(`analysis-${jobId}`); box.innerHTML=`<div><strong>Compatíveis</strong><div class="chips">${chips(data.matched_skills,'good')}</div></div><div style="margin-top:8px"><strong>Para desenvolver</strong><div class="chips">${chips(data.missing_skills,'miss')}</div></div>`; box.classList.remove('hidden'); } catch(error){ toast(error.message,'bad'); } }
async function updateStage(applicationId, stage) { try { await api(`/applications/${applicationId}`,{method:'PATCH',body:JSON.stringify({stage})}); await loadApplications(); updateStats(); toast('Etapa atualizada.'); } catch(error){ toast(error.message,'bad'); } }

function chips(items, cls='') { return (!items||!items.length) ? '<span class="muted">Nenhuma</span>' : items.map(x=>`<span class="chip ${cls}">${escapeHtml(x)}</span>`).join(''); }
function escapeHtml(value='') { return String(value).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
function formatMoney(value) { return (value===null||value===undefined) ? '' : new Intl.NumberFormat('pt-BR',{maximumFractionDigits:0}).format(value); }

function renderJobs() {
  const root=$('jobsList'); if(!root) return;
  if(!state.token){root.innerHTML='<div class="empty">Entre para visualizar suas vagas.</div>';return;}
  const query=($('jobSearch')?.value||'').toLowerCase();
  const filtered=state.jobs.filter(job=>`${job.title} ${job.company} ${job.location}`.toLowerCase().includes(query));
  if(!filtered.length){root.innerHTML='<div class="empty">Nenhuma vaga salva encontrada. Use a descoberta acima ou adicione uma manualmente.</div>';return;}
  const appliedJobIds=new Set(state.applications.map(app=>app.job_id));
  root.innerHTML=filtered.map(job=>{const salary=job.salary_min||job.salary_max?` · ${formatMoney(job.salary_min||0)}–${formatMoney(job.salary_max||0)}`:'';return `<article class="job"><div class="job-head"><div><h4>${escapeHtml(job.title)}</h4><div class="job-meta">${escapeHtml(job.company)} · ${escapeHtml(job.location)}${salary}</div></div><div class="score">${job.match_score.toFixed(0)}%</div></div><p class="muted">${escapeHtml(job.description).slice(0,220)}${job.description.length>220?'…':''}</p><div class="job-actions"><button class="btn small" onclick="showAnalysis(${job.id})">Ver análise</button><button class="btn small" onclick="rescoreJob(${job.id})">Recalcular</button>${appliedJobIds.has(job.id)?'<span class="chip good">Candidatura criada</span>':`<button class="btn success small" onclick="applyToJob(${job.id})">Registrar candidatura</button>`}<button class="btn danger small" onclick="deleteJob(${job.id})">Excluir</button></div><div id="analysis-${job.id}" class="analysis hidden"></div></article>`;}).join('');
}

function renderPipeline() {
  const root=$('pipeline'); if(!root) return;
  if(!state.token){root.innerHTML='<div class="empty">Entre para acompanhar seu pipeline.</div>';return;}
  const jobsById=Object.fromEntries(state.jobs.map(job=>[job.id,job]));
  root.innerHTML=stages.map(stage=>{const apps=state.applications.filter(app=>app.stage===stage);return `<section class="stage"><h4>${stage}</h4>${apps.length?apps.map(app=>{const job=jobsById[app.job_id];return `<div class="app-card"><strong>${escapeHtml(job?.title||`Vaga #${app.job_id}`)}</strong><span class="muted">${escapeHtml(job?.company||'')}</span><div class="field" style="margin-top:8px"><select onchange="updateStage(${app.id},this.value)">${stages.map(s=>`<option value="${s}" ${s===app.stage?'selected':''}>${s}</option>`).join('')}</select></div></div>`;}).join(''):'<div class="muted">Sem itens</div>'}</section>`;}).join('');
}

function updateStats(){ $('statJobs').textContent=state.jobs.length; $('statApps').textContent=state.applications.length; $('statInterviews').textContent=state.applications.filter(a=>['interview','technical'].includes(a.stage)).length; const avg=state.jobs.length?state.jobs.reduce((s,j)=>s+j.match_score,0)/state.jobs.length:0; $('statScore').textContent=`${avg.toFixed(0)}%`; }
async function loadProfile(){state.profile=await api('/profile');$('skills').value=state.profile.skills||'';$('summary').value=state.profile.summary||'';}
async function loadJobs(){state.jobs=await api('/jobs');renderJobs();}
async function loadApplications(){state.applications=await api('/applications');renderPipeline();}
async function refreshAll(){if(!state.token){updateAuthUI();return;}try{await loadProfile();await Promise.all([loadJobs(),loadApplications()]);updateAuthUI();updateStats();renderRemoteJobs();}catch(error){logout(false);toast('Sua sessão expirou. Faça login novamente.','bad');}}

document.addEventListener('DOMContentLoaded',()=>{
  $('loginForm').addEventListener('submit',login); $('registerForm').addEventListener('submit',register);
  $('profileForm').addEventListener('submit',saveProfile); $('jobForm').addEventListener('submit',createJob);
  $('remoteSearchForm').addEventListener('submit',searchRemoteJobs); $('showFavoritesBtn').addEventListener('click',toggleFavoritesView);
  $('remoteSort').addEventListener('change',renderRemoteJobs); $('jobSearch').addEventListener('input',renderJobs);
  $('loginTab').addEventListener('click',()=>setAuthTab('login')); $('registerTab').addEventListener('click',()=>setAuthTab('register'));
  $('logoutBtn').addEventListener('click',()=>logout(true)); refreshAll();
});