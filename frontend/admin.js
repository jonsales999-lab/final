function log(msg) {
  const out = document.getElementById('output');
  out.textContent = msg + "\n\n" + out.textContent;
}

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
  } catch (err) {
    // ignore parse errors
  }
  return decodeJwtPayload(localStorage.getItem('access_token'));
}

function exigirAdmin() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = 'login.html';
    return null;
  }
  const info = obterUserInfo();
  if (!info?.is_admin) {
    log('Apenas administradores podem acessar esta página.');
    window.location.href = 'home.html';
    return null;
  }
  return { token, info };
}

async function acaoPermissao(usuarioId, acao) {
  const ctx = exigirAdmin();
  if (!ctx) return;
  const { token } = ctx;

  if (!usuarioId || Number(usuarioId) <= 0) {
    log('Selecione um usuário.');
    return;
  }

  const endpoint = acao === 'liberar'
    ? `http://127.0.0.1:8000/auth/admin/liberar-criacao/${usuarioId}`
    : `http://127.0.0.1:8000/auth/admin/revogar-criacao/${usuarioId}`;

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }

    if (res.ok) {
      log(`Sucesso (${acao}):\n` + JSON.stringify(data || text, null, 2));
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail, null, 2) : text;
      log(`Erro ${res.status}: ${detail}`);
    }
  } catch (err) {
    log('Falha na requisição: ' + err.message);
  }
}

async function carregarPendentes() {
  const ctx = exigirAdmin();
  if (!ctx) return;
  const { token } = ctx;
  const sel = document.getElementById('userSelect');
  if (!sel) return;
  sel.innerHTML = '<option value="">Carregando...</option>';

  try {
    const res = await fetch('http://127.0.0.1:8000/auth/admin/pendentes', {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    const data = await res.json();
    sel.innerHTML = '';

    if (Array.isArray(data) && data.length) {
      sel.appendChild(new Option('-- selecione --', ''));
      data.forEach((u) => {
        const label = `${u.nome_completo || 'Sem nome'} (${u.email || 'sem email'})`;
        sel.appendChild(new Option(label, u.id));
      });
    } else {
      sel.appendChild(new Option('Nenhum pendente', ''));
    }
  } catch (err) {
    sel.innerHTML = '';
    sel.appendChild(new Option('Erro ao carregar', ''));
    log('Falha ao carregar pendentes: ' + err.message);
  }
}

function setup() {
  if (!exigirAdmin()) return;

  document.getElementById('btnLiberar')?.addEventListener('click', () => {
    const id = document.getElementById('userSelect').value;
    acaoPermissao(id, 'liberar').then(() => {
      carregarPendentes();
      carregarResumoAdmin();
    });
  });

  document.getElementById('btnAtualizar')?.addEventListener('click', () => {
    carregarPendentes();
    carregarResumoAdmin();
  });

  carregarPendentes();
  carregarResumoAdmin();
}

async function carregarResumoAdmin() {
  const ctx = exigirAdmin();
  if (!ctx) return;
  const { token } = ctx;
  try {
    const res = await fetch('http://127.0.0.1:8000/auth/admin/resumo', {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    if (!res.ok) throw new Error('Erro ao buscar resumo');
    const data = await res.json();
    if (typeof data.pendentes === 'number') {
      document.getElementById('resumoPendentes').textContent = data.pendentes;
    }
    if (typeof data.lideres_ativos === 'number') {
      document.getElementById('resumoLideres').textContent = data.lideres_ativos;
    }
    if (typeof data.escolas === 'number') {
      document.getElementById('resumoEscolas').textContent = data.escolas;
    }
  } catch (err) {
    log('Falha ao carregar resumo: ' + err.message);
  }
}

setup();
