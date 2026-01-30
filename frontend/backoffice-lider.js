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
    // fallback silencioso
  }
  const token = localStorage.getItem('access_token');
  return decodeJwtPayload(token);
}

function garantirAutenticado() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = 'login.html';
    return null;
  }
  // Permite admin acessar tudo
  const info = obterUserInfo();
  if (info?.is_admin) {
    return token;
  }
  return token;
}

async function carregarEquipe() {
  const token = garantirAutenticado();
  if (!token) return null;

  log('Carregando equipe...');
  try {
    // Primeiro, garante que a equipe do líder seja criada automaticamente
    await fetch('http://127.0.0.1:8000/auth/lider/equipe', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    // Agora busca os detalhes da equipe normalmente
    const res = await fetch('http://127.0.0.1:8000/equipes/minha/detalhes', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!res.ok) {
      const text = await res.text();
      log(`Erro ${res.status}: ${text}`);
      return null;
    }

    const data = await res.json();
    window.__equipeCache = data;
    renderResumo(data);
    renderMembros(data?.membros || []);
    await carregarFiscaisExternosOptions();
    return data;
  } catch (err) {
    log('Falha ao carregar equipe: ' + err.message);
    return null;
  }
}

async function carregarFiscaisExternosOptions() {
  const select = document.getElementById('selectFiscalExterno');
  if (!select) return;
  const equipe = window.__equipeCache;
  select.innerHTML = '<option value="">carregando...</option>';
  try {
    const equipeId = equipe?.equipe_id;
    if (!equipeId) {
      select.innerHTML = '<option value="">carregue a equipe antes</option>';
      return;
    }

    const res = await fetch(`http://127.0.0.1:8000/equipes/fiscais/elegiveis?equipe_id=${equipeId}`, {
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
      }
    });
    const data = await res.json();
    select.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = equipe?.escola_id
      ? '-- selecione um fiscal externo --'
      : '-- selecione (listando todas as escolas) --';
    select.appendChild(placeholder);

    const membrosIds = new Set((equipe?.membros || []).map((m) => m.usuario_id));
    let adicionou = false;

    if (Array.isArray(data)) {
      data
        .filter((u) => !membrosIds.has(u.id)) // evita listar alguém já da própria equipe
        .forEach((u) => {
          const opt = document.createElement('option');
          opt.value = u.id;
          const escolaLabel = u.escola_nome || (u.escola_id ? `Escola ${u.escola_id}` : 'Sem escola');
          const origemLabel = u.equipe_origem_nome ? `Equipe ${u.equipe_origem_nome}` : `Equipe ${u.equipe_origem_id || '-'}`;
          opt.textContent = `${u.nome_completo || 'Usuário'} - ${escolaLabel} · ${origemLabel}`;
          if (equipe.fiscal_externo_id && Number(equipe.fiscal_externo_id) === Number(u.id)) {
            opt.selected = true;
          }
          select.appendChild(opt);
          adicionou = true;
        });
    }

    if (select.value === '' && equipe.fiscal_externo_id) {
      const opt = document.createElement('option');
      opt.value = equipe.fiscal_externo_id;
      opt.textContent = `Selecionado (ID ${equipe.fiscal_externo_id})`;
      opt.selected = true;
      select.appendChild(opt);
      adicionou = true;
    }

    if (!adicionou) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'Nenhum fiscal elegível encontrado';
      select.appendChild(opt);
    }
  } catch (err) {
    select.innerHTML = '<option value="">erro ao carregar</option>';
    log('Erro ao carregar usuários para fiscal externo: ' + err.message);
  }
}

function renderResumo(data) {
  const alvo = document.getElementById('resumoDados');
  if (!data) {
    alvo.textContent = 'Sem dados';
    return;
  }
  window.__equipeCache = data;
  const totals = data.totais_por_papel || {};
  const resumoEquipeId = document.getElementById('resumoEquipeId');
  const resumoPontuacao = document.getElementById('resumoPontuacao');
  if (resumoEquipeId) resumoEquipeId.textContent = data.equipe_id || '-';
  if (resumoPontuacao) resumoPontuacao.textContent = `${data.pontuacao ?? 0} Pts`;
  alvo.innerHTML = `
    <div>Equipe: ${data.equipe_nome || '-'} (ID ${data.equipe_id || '-'})</div>
    <div>Pontuação: ${data.pontuacao ?? 0}</div>
    <div>Integrantes: ${data.total_integrantes || 0}</div>
    <div>Fiscais: ${totals.FISCAL_EQUIPE || 0}</div>
    <div>Fiscal externo: ${data.fiscal_externo_id || 'não definido'}</div>
    <div>Participantes: ${totals.PARTICIPANTE || 0}</div>
  `;
}

function preencherRemoverSelect(lista) {
  const select = document.getElementById('selectRemoverMembro');
  if (!select) return;
  select.innerHTML = '';
  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = '-- selecione --';
  select.appendChild(placeholder);

  (lista || []).forEach((m) => {
    if (m.papel === 'LIDER') return; // não permitir remover líder
    const opt = document.createElement('option');
    opt.value = m.usuario_id;
    opt.textContent = `${m.nome || 'Usuário'} (${m.papel || m.funcao || ''})`;
    select.appendChild(opt);
  });
}

function renderMembros(lista) {
  const tbody = document.getElementById('membrosBody');
  if (!tbody) return;
  tbody.innerHTML = '';
  if (!lista.length) {
    const row = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 4;
    td.textContent = 'Nenhum membro cadastrado ainda.';
    row.appendChild(td);
    tbody.appendChild(row);
    return;
  }

  const formatPapel = (p) => {
    if (!p) return '-';
    const upper = String(p).toUpperCase();
    if (upper === 'FISCAL_EXTERNO') return 'Fiscal externo';
    if (upper === 'FISCAL_EQUIPE') return 'Fiscal interno';
    if (upper === 'LIDER') return 'Líder';
    return p;
  };

  lista.forEach((m) => {
    const row = document.createElement('tr');
    const cols = [m.nome || '-', m.funcao || '-', m.email || '-'];
    cols.forEach((c) => {
      const td = document.createElement('td');
      td.textContent = c;
      row.appendChild(td);
    });
    tbody.appendChild(row);
  });

  preencherRemoverSelect(lista);
}

document.getElementById('btnRefresh')?.addEventListener('click', carregarEquipe);

document.getElementById('btnCadastro')?.addEventListener('click', async () => {
  // Sempre refaz a leitura para não usar cache desatualizado
  const info = await carregarEquipe();
  if (!info) return;

  const limite = 8;
  const membros = Array.isArray(info.membros) ? info.membros : [];
  const totalMembros = membros.length; // inclui líder

  if (totalMembros >= limite) {
    alert('Equipe completa: já possui 8 membros.');
    return;
  }

  window.location.href = 'form.html';
});

document.getElementById('btnEscolherFiscal')?.addEventListener('click', async () => {
  const token = garantirAutenticado();
  if (!token) return;
  const equipe = window.__equipeCache;
  if (!equipe?.equipe_id) {
    alert('Carregue a equipe primeiro.');
    return;
  }
  const select = document.getElementById('selectFiscalExterno');
  if (!select) return;
  const val = select.value;
  if (!val) {
    alert('Selecione um usuário.');
    return;
  }
  const usuarioId = Number(val);
  try {
    const res = await fetch(`http://127.0.0.1:8000/equipes/${equipe.equipe_id}/fiscal-externo/convite`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ usuario_id: usuarioId })
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }
    if (res.ok) {
      alert('Convite enviado para o fiscal externo. Aguarde ele aceitar para vigorar.');
      await carregarEquipe();
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail) : text;
      alert(`Erro ${res.status}: ${detail}`);
    }
  } catch (err) {
    alert('Falha na requisição: ' + err.message);
  }
});

document.getElementById('btnSair')?.addEventListener('click', () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_info');
  window.location.href = 'login.html';
});

document.getElementById('btnRemoverMembro')?.addEventListener('click', async () => {
  const token = garantirAutenticado();
  if (!token) return;
  const equipe = window.__equipeCache;
  const select = document.getElementById('selectRemoverMembro');
  if (!equipe?.equipe_id) {
    alert('Carregue a equipe primeiro.');
    return;
  }
  if (!select || !select.value) {
    alert('Selecione um membro para remover.');
    return;
  }
  const usuarioId = Number(select.value);
  try {
    const res = await fetch(`http://127.0.0.1:8000/equipes/${equipe.equipe_id}/membros/${usuarioId}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }
    if (res.ok) {
      alert('Membro removido com sucesso.');
      await carregarEquipe();
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail) : text;
      alert(`Erro ${res.status}: ${detail}`);
    }
  } catch (err) {
    alert('Falha na requisição: ' + err.message);
  }
});

carregarEquipe();

// Atualiza membros se outro cadastro for feito em outra aba/janela
window.addEventListener('storage', (event) => {
  if (event.key === 'ecoplay_membro_cadastrado') {
    carregarEquipe();
  }
});
