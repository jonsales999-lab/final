function log(msg) {
  const out = document.getElementById('log');
  out.textContent = msg + "\n" + out.textContent;
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
    // ignore
  }
  const token = localStorage.getItem('access_token');
  return decodeJwtPayload(token);
}

let minhaEquipe = null;
let tarefas = [];
let opcoesEquipes = [];
let convitesPendentes = [];
let acessoNegado = false;

function isFiscal(info) {
  if (!info) return false;
  const funcao = String(info.funcao || info.role || '').toUpperCase();
  return funcao.includes('FISCAL');
}

function papelUsuarioAtual() {
  const info = obterUserInfo();
  if (info?.is_admin) return 'ADMIN';
  const funcao = String(info?.funcao || info?.role || '').toUpperCase();
  if (funcao.includes('EXTERNO')) return 'FISCAL_EXTERNO';
  if (funcao.includes('FISCAL')) return 'FISCAL_EQUIPE';
  return null;
}

function exigirFiscal() {
  const info = obterUserInfo();
  const token = localStorage.getItem('access_token');
  if (info?.is_admin) return token;
  const autorizado = !!token && isFiscal(info);
  if (!autorizado) {
    alert('Acesso restrito: apenas fiscais (ou admin) podem acessar esta área.');
    acessoNegado = true;
    return null;
  }
  return token;
}

// Bloqueia imediatamente a página se não for fiscal/admin, sem redirecionar.
function bloquearSeNaoFiscal() {
  const info = obterUserInfo();
  const token = localStorage.getItem('access_token');
  if (info?.is_admin) return true;
  const autorizado = !!token && isFiscal(info);
  if (!autorizado) {
    acessoNegado = true;
    alert('Acesso restrito: apenas fiscais (ou admin) podem acessar esta área.');
    window.location.replace('home.html');
    return false;
  }
  return true;
}

const autorizadoInicial = bloquearSeNaoFiscal();

function renderEquipes() {
  const container = document.getElementById('equipesContainer');
  if (!container) return;
  container.innerHTML = '';

  if (!opcoesEquipes.length) {
    container.textContent = 'Nenhuma equipe atribuída. Peça para um líder escolher você como fiscal externo ou verifique seu vínculo.';
    return;
  }

  opcoesEquipes.forEach((op) => {
    const card = document.createElement('div');
    card.className = 'equipe-card';

    const header = document.createElement('div');
    header.className = 'equipe-header';

    const titleBox = document.createElement('div');
    const title = document.createElement('p');
    title.className = 'equipe-name';
    title.textContent = op.equipe_nome || 'Equipe';
    const sub = document.createElement('p');
    sub.className = 'subinfo';
    sub.textContent = `ID: ${op.equipe_id} · ${op.origem || ''}`;
    titleBox.appendChild(title);
    titleBox.appendChild(sub);

    const badge = document.createElement('span');
    badge.className = 'badge badge-success';
    badge.textContent = 'ATIVA';

    header.appendChild(titleBox);
    header.appendChild(badge);

    const btn = document.createElement('button');
    btn.textContent = 'Atualizar';
    btn.className = 'btn btn-sm btn-primary';
    btn.addEventListener('click', () => carregarTarefasPara(op));

    const ul = document.createElement('ul');
    ul.id = `tarefas-${op.equipe_id}`;
    ul.className = 'task-list';
    ul.innerHTML = '<li class="task-item"><span class="task-title">Carregando...</span></li>';

    card.appendChild(header);
    card.appendChild(btn);
    card.appendChild(ul);
    container.appendChild(card);

    carregarTarefasPara(op, ul);
  });
}

async function carregarContextoFiscal() {
  const token = exigirFiscal();
  if (!token || acessoNegado) return null;
  const novasOpcoes = [];

  try {
    const res = await fetch('http://127.0.0.1:8000/equipes/minha', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      novasOpcoes.push({
        equipe_id: data.equipe_id,
        equipe_nome: data.equipe_nome,
        origem: `papel ${data.papel}`,
      });
    }
  } catch (err) {
    log('Falha ao obter equipe interna: ' + err.message);
  }

  try {
    const resExt = await fetch('http://127.0.0.1:8000/equipes/fiscal-externo/minhas', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (resExt.ok) {
      const lista = await resExt.json();
      if (Array.isArray(lista)) {
        lista.forEach((e) => {
          novasOpcoes.push({
            equipe_id: e.equipe_id,
            equipe_nome: e.equipe_nome,
            origem: 'fiscal externo',
          });
        });
      }
    }
  } catch (err) {
    log('Falha ao obter equipes como fiscal externo: ' + err.message);
  }

  opcoesEquipes = novasOpcoes;
  renderEquipes();

  await carregarConvites();

  if (!opcoesEquipes.length) {
    document.getElementById('info').textContent = 'Nenhuma equipe atribuída. Peça para um líder escolher você como fiscal externo ou verifique seu vínculo.';
    return null;
  }

  const alvo = document.getElementById('info');
  alvo.textContent = `Você tem ${opcoesEquipes.length} equipe(s) atribuída(s). Veja abaixo e atualize as tarefas em cada bloco.`;
  return opcoesEquipes;
}

async function carregarConvites() {
  const token = exigirFiscal();
  if (!token || acessoNegado) return;
  const ul = document.getElementById('listaConvites');
  if (ul) ul.innerHTML = 'Carregando convites...';
  try {
    const res = await fetch('http://127.0.0.1:8000/equipes/convites/pendentes', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Erro ' + res.status);
    convitesPendentes = await res.json();
    renderConvites();
  } catch (err) {
    if (ul) ul.innerHTML = '<li>Erro ao carregar convites</li>';
    log('Falha convites: ' + err.message);
  }
}

function renderConvites() {
  const ul = document.getElementById('listaConvites');
  if (!ul) return;
  ul.innerHTML = '';
  if (!convitesPendentes.length) {
    ul.innerHTML = '<li class="convites-card">Nenhum convite pendente.</li>';
    return;
  }
  convitesPendentes.forEach((c) => {
    const li = document.createElement('li');
    li.className = 'task-item';
    const left = document.createElement('div');
    left.className = 'task-left';
    const t = document.createElement('p');
    t.className = 'task-title';
    t.textContent = `Convite: ${c.equipe_nome || c.equipe_id}`;
    const d = document.createElement('p');
    d.className = 'task-desc';
    d.textContent = 'Aceite para atuar como fiscal externo';
    left.appendChild(t);
    left.appendChild(d);
    const btn = document.createElement('button');
    btn.className = 'btn-validate';
    btn.textContent = 'Aceitar';
    btn.addEventListener('click', () => aceitarConvite(c.id));
    li.appendChild(left);
    li.appendChild(btn);
    ul.appendChild(li);
  });
}

async function aceitarConvite(id) {
  const token = exigirFiscal();
  if (!token || acessoNegado) return;
  try {
    const res = await fetch(`http://127.0.0.1:8000/equipes/convites/${id}/aceitar`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }
    if (res.ok) {
      alert('Convite aceito e pareamento realizado.');
      await carregarContextoFiscal();
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail) : text;
      alert(`Erro ${res.status}: ${detail}`);
    }
  } catch (err) {
    alert('Falha na requisição: ' + err.message);
  }
}

async function carregarTarefasPara(equipe, ulOverride) {
  const token = exigirFiscal();
  if (!token || acessoNegado || !equipe) return;
  const papelAtual = papelUsuarioAtual();

  const ul = ulOverride || document.getElementById(`tarefas-${equipe.equipe_id}`);
  if (!ul) return;
  ul.innerHTML = '<li>Carregando...</li>';

  try {
    const res = await fetch('http://127.0.0.1:8000/tarefas');
    if (!res.ok) throw new Error('Erro ' + res.status);
    tarefas = await res.json();
  } catch (err) {
    ul.innerHTML = '<li>Falha ao carregar tarefas</li>';
    log(err.message);
    return;
  }

  try {
    const tarefasComStatus = await Promise.all(tarefas.map(async (tarefa) => {
      const respStatus = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/status?equipe_id=${equipe.equipe_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (respStatus.status === 204) return null; // aguardando validação interna
      if (!respStatus.ok) return null;
      const statusData = await respStatus.json();
      return { tarefa, statusData };
    }));

    const iniciadas = tarefasComStatus
      // Mostra apenas iniciadas (com alguma aprovação) que ainda não foram concluídas (one-shot).
      .filter((item) => item && (item.statusData.aprovacoes || []).length && !item.statusData.executada)
      .filter((item) => {
        if (papelAtual === 'FISCAL_EXTERNO') {
          const aprovacoes = item.statusData.aprovacoes || [];
          // Externo só enxerga se já houve aprovação do fiscal interno.
          return aprovacoes.some((a) => String(a.papel || '').toUpperCase() === 'FISCAL_EQUIPE');
        }
        return true;
      });

    ul.innerHTML = '';
    if (!iniciadas.length) {
      ul.innerHTML = '<li>Nenhuma tarefa iniciada para esta equipe.</li>';
      return;
    }

    for (const { tarefa, statusData } of iniciadas) {
      const li = document.createElement('li');
      li.className = 'task-item';

      const left = document.createElement('div');
      left.className = 'task-left';
      const title = document.createElement('p');
      title.className = 'task-title';
      title.textContent = tarefa.titulo;
      const desc = document.createElement('p');
      desc.className = 'task-desc';
      desc.textContent = `Recompensa: ${tarefa.pontuacao} pts`;
      const statusEl = document.createElement('p');
      statusEl.className = 'task-meta';
      statusEl.textContent = formatarStatus(tarefa, statusData);
      left.appendChild(title);
      left.appendChild(desc);
      left.appendChild(statusEl);

      const btn = document.createElement('button');
      btn.className = 'btn-validate';
      btn.textContent = 'Validar';
      btn.addEventListener('click', () => validarTarefaPara(tarefa, equipe, statusEl, li, btn));

      li.appendChild(left);
      li.appendChild(btn);

      ul.appendChild(li);
    }
  } catch (err) {
    ul.innerHTML = '<li>Falha ao verificar status das tarefas</li>';
    log(err.message);
  }
}

async function atualizarStatusPara(tarefa, equipe, statusEl) {
  const token = exigirFiscal();
  if (!token || !equipe || acessoNegado) return null;
  try {
    const res = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/status?equipe_id=${equipe.equipe_id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Erro ' + res.status);
    const data = await res.json();
    statusEl.textContent = formatarStatus(tarefa, data);
    return data;
  } catch (err) {
    statusEl.textContent = 'Erro ao verificar';
    log(err.message);
    return null;
  }
}

function formatarStatus(tarefa, data) {
  if (!data) return 'Status indisponível';
  const aprovacoes = data.aprovacoes || [];
  if (!data.executada && !aprovacoes.length) return 'Aguardando iniciar';
  if (data.executada) {
    const pontos = data.pontos || tarefa.pontuacao;
    return `Concluída (+${pontos} pts)`;
  }
  // Já há uma aprovação registrada: aguarda o fiscal externo concluir o pareamento.
  return 'Aguardando sua aprovacao';
}

async function validarTarefaPara(tarefa, equipe, statusEl, liEl, btnEl) {
  const token = exigirFiscal();
  if (!token || !equipe || acessoNegado) return;
  // Se for fiscal externo, só pode validar após o fiscal da própria equipe ter aprovado.
  const papelAtual = papelUsuarioAtual();
  if (papelAtual === 'FISCAL_EXTERNO') {
    try {
      const resStatus = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/status?equipe_id=${equipe.equipe_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (resStatus.ok) {
        const dataStatus = await resStatus.json();
        const aprovacoes = dataStatus.aprovacoes || [];
        const temInterno = aprovacoes.some((a) => String(a.papel || '').toUpperCase() === 'FISCAL_EQUIPE');
        if (!temInterno) {
          alert('Aguardando validação do fiscal da própria equipe antes do fiscal externo.');
          await atualizarStatusPara(tarefa, equipe, statusEl);
          return;
        }
      }
    } catch (_err) {
      // Se falhar ao consultar, continua fluxo normal.
    }
  }
  try {
    // Consulta status atual para decidir se precisa reiniciar (limpando execução) antes de validar novamente.
    const statusAntes = await (async () => {
      const resStatus = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/status?equipe_id=${equipe.equipe_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!resStatus.ok) return null;
      return resStatus.json();
    })();

    // Se já estava executada, precisamos reiniciar o fluxo para permitir nova execução.
    if (statusAntes?.executada) {
      const resReiniciar = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/iniciar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ equipe_id: equipe.equipe_id }),
      });
      if (!resReiniciar.ok) {
        const msg = await resReiniciar.text();
        alert('Não foi possível reiniciar a tarefa: ' + msg);
        return;
      }
    }

    const res = await fetch(`http://127.0.0.1:8000/tarefas/${tarefa.id}/executar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ equipe_id: equipe.equipe_id }),
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }

    if (res.ok) {
      if (data?.pontos_adicionados) {
        alert(`Tarefa concluída com sucesso (+${data.pontos_adicionados} pts).`);
      } else {
        alert(data?.mensagem || 'Aguardando o outro fiscal.');
      }
      const statusData = await atualizarStatusPara(tarefa, equipe, statusEl);
      if (btnEl && statusData) {
        btnEl.textContent = 'Validar';
      }
      // Se concluiu, remove o card da lista (one-shot).
      if (statusData?.executada && liEl?.remove) {
        liEl.remove();
      }
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail) : text;
      alert('Erro ao validar: ' + detail);
      await atualizarStatusPara(tarefa, equipe, statusEl);
    }
  } catch (err) {
    alert('Falha na requisição: ' + err.message);
  }
}

(async function init() {
  if (acessoNegado || !autorizadoInicial) {
    const alvo = document.getElementById('info');
    if (alvo) alvo.textContent = 'Acesso restrito a fiscais (ou admin).';
    return;
  }
  await carregarContextoFiscal();
  if (acessoNegado) {
    const alvo = document.getElementById('info');
    if (alvo) alvo.textContent = 'Acesso restrito a fiscais (ou admin).';
    return;
  }
})();

