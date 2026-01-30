function log(msg, variant = 'info') {
  const out = document.getElementById('output');
  if (out) out.textContent = msg + "\n\n" + out.textContent;

  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'pointer-events-auto flex items-start gap-3 rounded-2xl px-4 py-3 shadow-lg shadow-slate-400/30 bg-white border border-slate-200';

  const badge = document.createElement('span');
  badge.className = 'mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white';
  if (variant === 'success') {
    badge.classList.add('bg-[var(--primary-green)]');
    badge.textContent = '✓';
  } else if (variant === 'error') {
    badge.classList.add('bg-[var(--danger-red)]');
    badge.textContent = '!';
  } else {
    badge.classList.add('bg-[var(--accent-yellow)]');
    badge.textContent = 'i';
  }

  const text = document.createElement('div');
  text.className = 'text-sm text-slate-700 leading-snug';
  text.textContent = msg;

  toast.appendChild(badge);
  toast.appendChild(text);
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2', 'transition', 'duration-300');
    setTimeout(() => toast.remove(), 300);
  }, 5000);
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


function garantirPermissaoOuSair() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = 'login.html';
    return false;
  }

  const info = obterUserInfo();
  if (info?.is_admin || info?.pode_criar_equipe) {
    return true;
  }

  log('Acesso bloqueado: aguarde o administrador liberar seu perfil de lider.');
  window.location.href = 'aguardando.html';
  return false;
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    if (!file || !(file instanceof File)) return resolve(null);
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function formatValidationErrors(detail) {
  if (!Array.isArray(detail)) return null;
  return detail
    .map((err) => {
      const loc = Array.isArray(err.loc) ? err.loc : [];
      const field = loc.length ? loc[loc.length - 1] : 'campo';
      const msg = err.msg || err.detail || 'Valor inválido';
      return `${field}: ${msg}`;
    })
    .join('; ');
}

const acessoLiberado = garantirPermissaoOuSair();

const cadastroForm = document.getElementById('cadastroForm');

cadastroForm?.addEventListener('submit', async (e) => {
  if (!acessoLiberado) return;
  e.preventDefault();
  const f = new FormData(e.target);

  const info = obterUserInfo();
  const escolaId = info?.escola_id;
  if (!escolaId) {
    log('Não foi possível identificar a escola do líder.', 'error');
    return;
  }

  // Validação mínima no front para evitar payload inválido
  // Os nomes dos campos devem bater com os IDs do HTML
  const requiredTextFields = ['nome', 'sexo', 'nascimento', 'funcao', 'telefone', 'cpf', 'email', 'cursando', 'manequim', 'sanguineo'];
  for (const field of requiredTextFields) {
    const value = (f.get(field) || '').toString().trim();
    if (!value) {
      log(`Preencha o campo obrigatório: ${field}`, 'error');
      return;
    }
  }

  const rgFile = f.get('rg');
  const cpf = (f.get('cpf') || '').toString().replace(/\D/g, '');
  const email = (f.get('email') || '').toString().trim().toLowerCase();
  if (!cpf) {
    log('Preencha o CPF para continuar.', 'error');
    return;
  }
  f.set('cpf', cpf);
  f.set('email', email);

  const rgBase64 = (rgFile && rgFile.name) ? await fileToBase64(rgFile) : null;
  if (!rgBase64) {
    log('O arquivo de RG é obrigatório.', 'error');
    return;
  }

  const medicamentoControlado = f.get('medicamento_controlado') === 'on';
  const nomeMedicamento = (f.get('nome_medicamento_1') || '').toString().trim();
  if (medicamentoControlado && !nomeMedicamento) {
    log('Informe o nome do medicamento controlado.', 'error');
    return;
  }

  const declaracaoLida = f.get('declaracao_lida') === 'on';
  if (!declaracaoLida) {
    log('É necessário marcar que leu a declaração.', 'error');
    return;
  }

  const payload = {
    escola_id: escolaId,
    nome_completo: f.get('nome') || null,
    sexo: f.get('sexo') || null,
    data_nascimento: f.get('nascimento') || null,
    funcao: f.get('funcao') || null,
    telefone_pessoal: f.get('telefone') || null,
    rg_path: rgBase64,
    cpf: cpf,
    email: email || null,
    senha: cpf, // senha padrão = CPF
    cursando: f.get('cursando') || null,
    manequim: f.get('manequim') || null,
    tipo_sanguineo: f.get('sanguineo') || null,
    medicamento_controlado: medicamentoControlado,
    nome_medicamento_1: nomeMedicamento || null,
    declaracao_lida: declaracaoLida
  };

  // Pré-checagem para evitar 409 por duplicidade
  try {
    const checkRes = await fetch(`http://127.0.0.1:8000/auth/verificar-duplicidade?email=${encodeURIComponent(email)}&cpf=${encodeURIComponent(cpf)}`);
    const checkData = await checkRes.json();
    if (!checkData.ok) {
      const campos = (checkData.duplicados || []).join(', ');
      log(`Já existe cadastro com: ${campos}. Altere antes de continuar.`, 'error');
      return;
    }
  } catch (err) {
    log('Não foi possível validar duplicidade antes do envio: ' + err.message, 'error');
  }

  log('Enviando cadastro para o backend...');
  const submitBtn = e.target.querySelector('button[type="submit"]');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      log('Precisa estar logado como lider.', 'error');
      return;
    }

    const res = await fetch('http://127.0.0.1:8000/auth/lider/cadastrar', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch(e) { data = null; }

    if (res.ok) {
      log('Sucesso: ' + (data ? JSON.stringify(data, null, 2) : text), 'success');
      // Sinaliza para outras abas que houve cadastro
      localStorage.setItem('ecoplay_membro_cadastrado', Date.now().toString());
      // Redireciona para o backoffice do líder para atualizar a lista de membros
      setTimeout(() => {
        window.location.replace('backoffice-lider.html');
      }, 1000);
    } else {
      if (res.status === 409 && data?.detail?.fields?.length) {
        const campos = data.detail.fields.join(', ');
        const mensagem = data.detail.message || 'Dados ja cadastrados';
        log(`${mensagem}: ${campos}.`, 'error');
      } else if (res.status === 409 && data?.detail) {
        log(`Conflito: ${JSON.stringify(data.detail)}`, 'error');
      } else if (res.status === 422 && data?.detail) {
        const formatted = formatValidationErrors(data.detail);
        log(`Falha na validação: ${formatted || JSON.stringify(data.detail)}`, 'error');
      } else {
        log(`Erro ${res.status}: ` + (data?.detail ? JSON.stringify(data.detail, null, 2) : text), 'error');
      }
    }
  } catch (err) {
    log('Falha na requisição (CORS ou Servidor Offline): ' + err.message, 'error');
    console.error('Erro detalhado:', err);
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
});
