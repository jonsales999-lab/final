// Adaptado para tarefas.html
let tarefaSelecionada = null;
let equipeLiderCache = null;
let equipeCache = null;
let papelAtual = null;
const modal = document.getElementById('tarefa-modal');
const modalTexto = document.getElementById('modal-texto');
const modalPontuacao = document.getElementById('modal-pontuacao');
const equipeInput = document.getElementById('equipe-id-input');
const btnIniciar = document.getElementById('btn-iniciar');
const btnCancelar = document.getElementById('btn-cancelar');
const modalNaoFiscal = document.getElementById('modal-nao-fiscal');
const btnNaoFiscalFechar = document.getElementById('btn-nao-fiscal-fechar');

function carregarTarefas() {
  const lista = document.getElementById('lista-tarefas');
  if (!lista) return;
  lista.innerHTML = '';
  fetch('http://127.0.0.1:8000/tarefas')
    .then(res => {
      if (!res.ok) {
        throw new Error(`Erro ${res.status} ao buscar tarefas`);
      }
      return res.json();
    })
    .then(tarefasData => {
      if (!Array.isArray(tarefasData) || tarefasData.length === 0) {
        lista.innerHTML = '<li class="text-center text-slate-500">Nenhuma tarefa encontrada.</li>';
        return;
      }
      const unidadeNome = {
        1: 'KG',
        2: 'Litros',
        3: 'M³',
        4: 'UN',
        5: 'Ação',
      };
      const unidadeSlug = {
        1: 'kg',
        2: 'litros',
        3: 'metro_cubico',
        4: 'unidade',
        5: 'acao',
      };
      // Agrupar tarefas por unidade
      const grupos = {};
      tarefasData.forEach(t => {
        const unidadeId = t.unidade_id ?? t.unidade ?? t.unidade_medida ?? t.medida ?? null;
        const unidadeKey = unidadeSlug[unidadeId] || (t.unidade ? String(t.unidade).toLowerCase() : 'outras');
        if (!grupos[unidadeKey]) grupos[unidadeKey] = [];
        grupos[unidadeKey].push(t);
      });
      const ordem = ['kg', 'litros', 'metro_cubico', 'unidade', 'acao', 'outras'];
      const titulos = {
        kg: 'Tarefas por Quilograma',
        litros: 'Tarefas por Litro',
        metro_cubico: 'Tarefas por Metro Cúbico',
        unidade: 'Tarefas por Unidade',
        acao: 'Tarefas por Ação',
        outras: 'Outras Tarefas'
      };
      ordem.forEach(unidade => {
        if (grupos[unidade] && grupos[unidade].length) {
          // Container para cada grupo
          const container = document.createElement('div');
          container.className = 'bg-white dark:bg-card-dark rounded-2xl shadow-md border border-slate-200 dark:border-slate-800 p-6 mb-8 max-w-xl mx-auto';

          // Título destacado
          const header = document.createElement('h2');
          header.className = 'text-xl font-extrabold mb-4 text-primary tracking-tight text-center';
          header.textContent = titulos[unidade] || unidade.replace('_', ' ').toUpperCase();
          container.appendChild(header);

          // Cards das tarefas já exibidos
          const cardsDiv = document.createElement('div');
          cardsDiv.className = 'tarefas-cards mt-2';
          grupos[unidade].forEach(t => {
            const card = document.createElement('div');
            card.className = "bg-card-light dark:bg-card-dark p-4 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 flex items-center gap-4 active:scale-[0.98] transition-transform mb-3";
            const pontuacao = t.pontuacao ?? t.pontos ?? t.ponto ?? 0;
            const unidadeId = t.unidade_id ?? t.unidade ?? t.unidade_medida ?? t.medida ?? '-';
            const unidadeLabel = unidadeNome[unidadeId] || unidadeId.toString();
            card.innerHTML = `
              <div class=\"w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0\">
                <span class=\"material-icons-round text-primary\">eco</span>
              </div>
              <div class=\"flex-grow\">
                <h3 class=\"font-semibold text-slate-800 dark:text-slate-100\">${t.titulo}</h3>
                <p class=\"text-xs text-slate-500 dark:text-slate-400\">${t.descricao || ''}</p>
              </div>
              <div class=\"flex gap-2\">
                <div class=\"bg-blue-50 dark:bg-primary/20 px-3 py-1 rounded-full flex flex-col items-center justify-center min-w-[56px]\">
                  <span class=\"text-sm font-bold text-primary\">${pontuacao}</span>
                  <span class=\"text-xs font-semibold text-primary\">pontos</span>
                </div>
                <div class=\"bg-blue-50 dark:bg-primary/20 px-3 py-1 rounded-full flex flex-col items-center justify-center min-w-[56px]\">
                  <span class="text-sm font-bold text-primary">${unidadeLabel}<\/span>
                </div>
              </div>
            `;
            card.onclick = async () => {
              const equipeIdAuto = await resolverEquipeId();
              tarefaSelecionada = t;
              if (equipeInput && equipeIdAuto) {
                equipeInput.value = equipeIdAuto;
              }
              const equipeLabel = equipeIdAuto ? `Equipe: ${equipeIdAuto}` : 'Informe o ID da equipe para iniciar/concluir';
              if (modal && modalTexto && modalPontuacao) {
                modalTexto.textContent = `${t.titulo} - ${t.descricao || ''}`;
                modalPontuacao.textContent = `Pontuação: ${t.pontuacao} ${unidadeLabel} | ${equipeLabel}`;
                if (typeof modal.showModal === 'function') {
                  modal.showModal();
                }
              }
            };
            cardsDiv.appendChild(card);
          });
          container.appendChild(cardsDiv);

          lista.appendChild(container);
        }
      });
    })
    .catch((err) => {
      console.error('[tarefas] falha ao carregar:', err);
      lista.innerHTML = '<li class="text-center text-rose-600">Falha ao carregar tarefas do servidor</li>';
    });
}

window.carregarTarefas = carregarTarefas;
carregarTarefas();

function decodeJwtPayload(token) {
  if (!token) return null;
  try {
    const payload = token.split('.')[1];
    const norm = payload.replace(/-/g, '+').replace(/_/g, '/');
    const decoded = atob(norm);
    return JSON.parse(decoded);
  } catch (_err) {
    return null;
  }
}


function isAdminAtual() {
  const token = localStorage.getItem('access_token');
  const payload = decodeJwtPayload(token);
  return !!payload?.is_admin;
}

function isFiscalAtual() {
  const papel = (papelAtual || '').toUpperCase();
  if (papel === 'FISCAL_EQUIPE' || papel === 'FISCAL_EXTERNO') return true;
  if (isAdminAtual()) return true;

  const token = localStorage.getItem('access_token');
  const payload = decodeJwtPayload(token);
  const funcaoToken = (payload?.funcao || payload?.role || '').toUpperCase();
  return funcaoToken.includes('FISCAL');
}

async function obterEquipeLiderId() {
  if (equipeLiderCache) return equipeLiderCache;
  const token = localStorage.getItem('access_token');
  if (!token) return null;
  try {
    const res = await fetch('http://127.0.0.1:8000/auth/lider/equipe', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return null;
    const data = await res.json();
    equipeLiderCache = data.equipe_id;
    return equipeLiderCache;
  } catch (_err) {
    return null;
  }
}

async function resolverEquipeId() {
  // Sempre consulta o backend para garantir que pegamos o vínculo correto
  try {
    const token = localStorage.getItem('access_token');
    if (token) {
      const res = await fetch('http://127.0.0.1:8000/auth/me/equipe', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data?.equipe_id) {
          equipeCache = data.equipe_id.toString();
          localStorage.setItem('equipe_id', equipeCache);
          if (data.meu_papel) {
            papelAtual = data.meu_papel;
          }
          return equipeCache;
        }
      }
    }
  } catch (_err) {
    // ignora e tenta próximo passo
  }

  // Se falhar, tenta cache local mesmo assim
  const local = localStorage.getItem('equipe_id');
  if (local) {
    equipeCache = local;
    return equipeCache;
  }

  // Último recurso: tenta equipe do líder
  const tentativa = await obterEquipeLiderId();
  if (tentativa) {
    equipeCache = tentativa;
    localStorage.setItem('equipe_id', tentativa);
    return equipeCache;
  }

  return null;
}

async function iniciarTarefaFrontend(tarefaId, equipeId) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    alert('É preciso estar logado como fiscal para iniciar.');
    return;
  }
  try {
    const res = await fetch(`http://127.0.0.1:8000/tarefas/${tarefaId}/iniciar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ equipe_id: equipeId }),
    });
    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (_err) { data = null; }
    if (res.ok) {
      alert(data?.mensagem || 'Tarefa iniciada pelo fiscal.');
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail) : text;
      alert(`Erro ao iniciar: ${detail}`);
    }
  } catch (err) {
    alert('Falha na requisição: ' + err.message);
  }
}

if (btnIniciar) {
  btnIniciar.addEventListener('click', async () => {
    if (!tarefaSelecionada) return;
    if (!isFiscalAtual()) {
      if (typeof modalNaoFiscal?.showModal === 'function') {
        // Fecha o modal principal para não ficar visível no fundo.
        modal?.close?.();
        modalNaoFiscal.showModal();
      }
      return;
    }
    const equipeId = (await resolverEquipeId()) || (equipeInput?.value || '').trim();
    if (!equipeId) {
      alert('Não foi possível identificar sua equipe.');
      return;
    }
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://127.0.0.1:8000/tarefas/${tarefaSelecionada.id}/iniciar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ equipe_id: equipeId }),
      });
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch (_err) { data = null; }

      if (res.ok) {
        alert(data?.mensagem || 'Tarefa iniciada pelo fiscal.');
        modal?.close?.();
        tarefaSelecionada = null;
      } else {
        const detail = data?.detail ? JSON.stringify(data.detail) : text;
        alert(`Erro ao iniciar: ${detail}`);
      }
    } catch (err) {
      alert('Falha na requisição: ' + err.message);
    }
  });
}

if (btnCancelar) {
  btnCancelar.addEventListener('click', () => {
    modal?.close?.();
    tarefaSelecionada = null;
  });
}

if (btnNaoFiscalFechar) {
  btnNaoFiscalFechar.addEventListener('click', () => {
    modalNaoFiscal?.close?.();
  });
}

// Carregamento inicial da lista com UI nova
carregarTarefas();
