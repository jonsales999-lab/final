// Painel "Minha Equipe" (backoffice.html) conectado ao backend.
// Reaproveita as mesmas rotas usadas pelo painel do líder.

function decodeJwtPayload(token) {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const norm = payload.replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(norm);
    return JSON.parse(decoded);
  } catch (err) {
    return null;
  }
}

function obterUserInfo() {
  try {
    const raw = localStorage.getItem('user_info');
    if (raw) return JSON.parse(raw);
  } catch (_err) {
    // ignore parse issues
  }
  const token = localStorage.getItem('access_token');
  return decodeJwtPayload(token);
}

function ehLider(info) {
  if (!info) return false;
  const funcao = String(info.funcao || info.role || '').toUpperCase();
  return funcao.includes('LIDER');
}

function exigirAutenticado() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.replace('login.html');
    return null;
  }
  return token;
}

async function garantirEquipeDoLider(token) {
  // Garante que o backend crie/retorne a equipe do líder.
  await fetch('http://127.0.0.1:8000/auth/lider/equipe', {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  }).catch(() => {});
}

async function carregarEquipeDetalhes(token) {
  const res = await fetch('http://127.0.0.1:8000/equipes/minha/detalhes', {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Erro ${res.status}: ${txt}`);
  }
  return res.json();
}

async function carregarRankingPosicao(equipeId) {
  if (!equipeId) return '-';
  try {
    const res = await fetch('http://127.0.0.1:8000/equipes/ranking');
    if (!res.ok) return '-';
    const data = await res.json();
    const idx = Array.isArray(data)
      ? data.findIndex((e) => Number(e.id) === Number(equipeId) || Number(e.equipe_id) === Number(equipeId))
      : -1;
    return idx >= 0 ? idx + 1 : '-';
  } catch (_err) {
    return '-';
  }
}

function renderResumo(equipe, posicao) {
  const resumoEquipeId = document.getElementById('resumoEquipeId');
  const resumoPontuacao = document.getElementById('resumoPontuacao');
  const resumoPosicao = document.getElementById('resumoPosicao');
  if (resumoEquipeId) resumoEquipeId.textContent = equipe?.equipe_id ?? '-';
  if (resumoPontuacao) resumoPontuacao.textContent = `${equipe?.pontuacao ?? 0} Pts`;
  if (resumoPosicao) resumoPosicao.textContent = posicao ?? '-';
  const resumoDados = document.getElementById('resumoDados');
  if (resumoDados) {
    const totals = equipe?.totais_por_papel || {};
    resumoDados.innerHTML = `
      <div>Equipe: ${equipe?.equipe_nome || '-'} (ID ${equipe?.equipe_id || '-'})</div>
      <div>Pontuação: ${equipe?.pontuacao ?? 0}</div>
      <div>Integrantes: ${equipe?.total_integrantes || 0}</div>
      <div>Fiscais internos: ${totals.FISCAL_EQUIPE || 0}</div>
      <div>Fiscal externo: ${equipe?.fiscal_externo_id || 'não definido'}</div>
      <div>Participantes: ${totals.PARTICIPANTE || 0}</div>
    `;
  }
}

function renderMembros(membros) {
  const tbody = document.getElementById('membrosBody');
  const count = document.getElementById('membrosCount');
  if (count) count.textContent = `${membros?.length || 0} membros`;
  if (!tbody) return;
  tbody.innerHTML = '';
  if (!membros || !membros.length) {
    const row = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 4;
    td.textContent = 'Nenhum membro cadastrado ainda.';
    row.appendChild(td);
    tbody.appendChild(row);
    return;
  }
  membros.forEach((m) => {
    const row = document.createElement('tr');
    const cols = [m.nome || '-', m.funcao || '-', m.papel || '-', m.email || '-'];
    cols.forEach((c) => {
      const td = document.createElement('td');
      td.className = 'px-6 py-4 text-sm text-slate-700';
      td.textContent = c;
      row.appendChild(td);
    });
    tbody.appendChild(row);
  });
}

async function carregarPainel() {
  const token = exigirAutenticado();
  if (!token) return;
  const info = obterUserInfo();
  const podeCriarOuGarantirEquipe = ehLider(info) || info?.is_admin;
  try {
    if (podeCriarOuGarantirEquipe) {
      await garantirEquipeDoLider(token);
    }
    const equipe = await carregarEquipeDetalhes(token);
    const posicao = await carregarRankingPosicao(equipe?.equipe_id);
    renderResumo(equipe, posicao);
    renderMembros(equipe?.membros || []);
  } catch (err) {
    const out = document.getElementById('resumoDados');
    if (out) {
      out.textContent = err.message.includes('404')
        ? 'Você ainda não está vinculado a nenhuma equipe. Procure o líder da sua escola.'
        : err.message;
    }
  }
}

function wireNav() {
  document.getElementById('goBackoffice')?.addEventListener('click', () => window.location.href = 'backoffice.html');
  document.getElementById('goFiscal')?.addEventListener('click', () => window.location.href = 'backoffice-fiscal.html');
  document.getElementById('goAdmin')?.addEventListener('click', () => window.location.href = 'admin.html');
  document.getElementById('goTarefas')?.addEventListener('click', () => window.location.href = 'tarefas.html');

  // Tenta ligar o botão de sair pelo texto/ícone se existir.
  const logoutBtn = Array.from(document.querySelectorAll('button'))
    .find((b) => (b.textContent || '').toLowerCase().includes('sair'));
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_info');
      window.location.href = 'login.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  wireNav();
  carregarPainel();
});
