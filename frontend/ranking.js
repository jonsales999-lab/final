const podiumEl = document.querySelector('[data-podium]');
const listEl = document.querySelector('[data-list]');
const countEl = document.querySelector('[data-count]');
const statusEl = document.querySelector('[data-status]');
const refreshBtn = document.querySelector('[data-refresh]');
const API_URL = 'http://127.0.0.1:8000/equipes/ranking';

const decodeJwtPayload = (token) => {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const norm = payload.replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(norm);
    return JSON.parse(decoded);
  } catch (_err) {
    return null;
  }
};

const isAdmin = () => {
  try {
    const stored = JSON.parse(localStorage.getItem('user_info'));
    if (stored?.is_admin) return true;
  } catch (_err) {
    /* ignore parse errors */
  }
  const payload = decodeJwtPayload(localStorage.getItem('access_token'));
  return !!payload?.is_admin;
};

const gateRefreshButton = () => {
  if (!refreshBtn) return;
  if (isAdmin()) {
    refreshBtn.hidden = false;
    refreshBtn.style.display = 'inline-flex';
  } else {
    refreshBtn.hidden = true;
    refreshBtn.style.display = 'none';
  }
};

const formatPoints = (value) => {
  const safe = Number.isFinite(Number(value)) ? Number(value) : 0;
  return new Intl.NumberFormat('pt-BR').format(safe);
};

const getInitials = (name) => {
  if (!name) return 'EQ';
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]).join('').toUpperCase();
};

const schoolLabel = (team) => {
  if (team?.escola_nome) return team.escola_nome;
  if (team?.escola_id) return `Escola #${team.escola_id}`;
  return 'Escola não informada';
};

const setStatus = (message, tone = 'muted') => {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.style.color = tone === 'error' ? '#ef4444' : 'var(--muted)';
};

const renderPodium = (teams) => {
  if (!podiumEl) return;
  const top = teams.slice(0, 3);
  if (!top.length) {
    podiumEl.innerHTML = '<div class="empty-msg">Nenhuma equipe cadastrada ainda.</div>';
    return;
  }

  const layout = [
    { team: top[1] || null, rank: top[1] ? 2 : null, className: 'pos-2' },
    { team: top[0] || null, rank: top[0] ? 1 : null, className: 'pos-1' },
    { team: top[2] || null, rank: top[2] ? 3 : null, className: 'pos-3' },
  ];

  podiumEl.innerHTML = layout.map((slot) => {
    if (!slot.team) {
      return `
        <div class="podium-card ${slot.className}">
          <div class="circle" aria-hidden="true">--</div>
          <div class="team-name">Vaga disponível</div>
          <div class="team-sub">Aguardando próxima equipe</div>
        </div>
      `;
    }

    const badgeClass = slot.rank === 1 ? 'badge-gold' : slot.rank === 2 ? 'badge-silver' : 'badge-bronze';
    return `
      <div class="podium-card ${slot.className}" aria-label="${slot.rank}º lugar">
        <div class="rank-badge ${badgeClass}">${slot.rank}</div>
        <div class="circle">${getInitials(slot.team.nome)}</div>
        <div class="team-name">${slot.team.nome || 'Equipe'}</div>
        <div class="team-points">${formatPoints(slot.team.pontuacao)} pts</div>
        <div class="team-sub">${schoolLabel(slot.team)}</div>
      </div>
    `;
  }).join('');
};

const renderList = (teams) => {
  if (!listEl) return;
  const startIndex = teams.length > 3 ? 3 : 0;
  const baseRank = teams.length > 3 ? 4 : 1;
  const remainder = teams.slice(startIndex);

  if (!remainder.length) {
    listEl.innerHTML = '<div class="empty-msg">Todas as equipes já estão no pódio.</div>';
    return;
  }

  listEl.innerHTML = remainder.map((team, idx) => {
    const rank = idx + baseRank;
    const subtitle = schoolLabel(team);
    return `
      <article class="row" aria-label="${rank}º colocado">
        <div class="row-rank">${rank}º</div>
        <div class="row-info">
          <p class="row-team">${team.nome || 'Equipe sem nome'}</p>
          <p class="row-sub">${subtitle}</p>
        </div>
        <div class="row-meta">
          <span class="row-points">${formatPoints(team.pontuacao)} pts</span>
          <span class="status-dot" aria-hidden="true"></span>
        </div>
      </article>
    `;
  }).join('');
};

const renderCount = (teams) => {
  if (!countEl) return;
  const total = teams.length;
  countEl.textContent = total === 1 ? '1 equipe' : `${total} equipes`;
};

const loadRanking = async () => {
  try {
    setStatus('Carregando ranking...', 'muted');
    if (refreshBtn) refreshBtn.disabled = true;

    const res = await fetch(API_URL);
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const data = await res.json();
    const teams = Array.isArray(data) ? data : [];
    const sorted = [...teams].sort((a, b) => (b.pontuacao || 0) - (a.pontuacao || 0));

    renderPodium(sorted);
    renderList(sorted);
    renderCount(sorted);

    const now = new Date();
    setStatus(`Atualizado em ${now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`);
  } catch (err) {
    setStatus(`Falha ao carregar ranking: ${err.message}`, 'error');
    if (listEl) listEl.innerHTML = '<div class="empty-msg">Não foi possível carregar os dados.</div>';
    if (podiumEl) podiumEl.innerHTML = '';
  } finally {
    if (refreshBtn) refreshBtn.disabled = false;
  }
};

if (refreshBtn) {
  refreshBtn.addEventListener('click', loadRanking);
}

gateRefreshButton();
loadRanking();
