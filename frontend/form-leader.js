const outEl = document.getElementById('output');
const selectEscola = document.getElementById('escolaSelect');
const form = document.getElementById('leaderForm');

function log(msg) {
  outEl.textContent = msg + "\n\n" + outEl.textContent;
}

async function carregarEscolas() {
  if (!selectEscola) return;
  try {
    const res = await fetch('http://127.0.0.1:8000/catalog/escolas');
    if (!res.ok) throw new Error(`Erro ao carregar escolas (${res.status})`);
    const data = await res.json();
    selectEscola.innerHTML = '<option value="">-- selecione --</option>';
    (data || []).forEach((escola) => {
      const opt = document.createElement('option');
      opt.value = escola.id;
      opt.textContent = escola.nome;
      selectEscola.appendChild(opt);
    });
  } catch (err) {
    selectEscola.innerHTML = '<option value="">Erro ao carregar escolas</option>';
    log(`Falha ao carregar escolas: ${err.message}`);
  }
}

carregarEscolas();

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    if (!file || !(file instanceof File)) return resolve(null);
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);

  const requiredTextFields = ['escola_id', 'nome_completo', 'sexo', 'data_nascimento', 'telefone_pessoal', 'cpf', 'email', 'senha', 'cursando', 'manequim', 'tipo_sanguineo'];
  for (const field of requiredTextFields) {
    const value = (f.get(field) || '').toString().trim();
    if (!value) {
      log(`Preencha o campo obrigatorio: ${field}`);
      return;
    }
  }

  const rgFile = f.get('rg_path_file');
  const cpf = f.get('cpf');

  const rgBase64 = (rgFile && rgFile.name) ? await fileToBase64(rgFile) : null;
  if (!rgBase64) {
    log('O arquivo de RG e obrigatorio.');
    return;
  }

  const medicamentoControlado = f.get('medicamento_controlado') === 'on';
  const nomeMedicamento = (f.get('nome_medicamento_1') || '').toString().trim();
  if (medicamentoControlado && !nomeMedicamento) {
    log('Informe o nome do medicamento controlado.');
    return;
  }

  const declaracaoLida = f.get('declaracao_lida') === 'on';
  if (!declaracaoLida) {
    log('E necessario marcar que leu a declaracao.');
    return;
  }

  const payload = {
    escola_id: parseInt(f.get('escola_id'), 10),
    nome_completo: f.get('nome_completo') || null,
    sexo: f.get('sexo') || null,
    data_nascimento: f.get('data_nascimento') || null,
    funcao: 'Lider',
    telefone_pessoal: f.get('telefone_pessoal') || null,
    rg_path: rgBase64,
    cpf: cpf,
    email: f.get('email') || null,
    senha: f.get('senha') || null,
    cursando: f.get('cursando') || null,
    manequim: f.get('manequim') || null,
    tipo_sanguineo: f.get('tipo_sanguineo') || null,
    medicamento_controlado: medicamentoControlado,
    nome_medicamento_1: nomeMedicamento || null,
    declaracao_lida: declaracaoLida
  };

  log('Enviando cadastro de lider para o backend. Aguarde a aprovacao do administrador.');
  const submitBtn = e.target.querySelector('button[type="submit"]');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const res = await fetch('http://127.0.0.1:8000/auth/', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const text = await res.text();
    let data = null;
    try {
      data = JSON.parse(text);
    } catch (err) {
      data = null;
    }

    if (res.ok) {
      log('Cadastro enviado. Aguarde a liberacao do administrador para acessar os formularios de equipe e participantes.');
      setTimeout(() => {
        window.location.href = 'aguardando.html';
      }, 1000);
    } else {
      if (res.status === 409 && data?.detail?.fields?.length) {
        const campos = data.detail.fields.join(', ');
        const mensagem = data.detail.message || 'Dados ja cadastrados';
        log(`${mensagem}: ${campos}.`);
      } else {
        log(`Erro ${res.status}: ` + (data?.detail ? JSON.stringify(data.detail, null, 2) : text));
      }
    }
  } catch (err) {
    log('Falha na requisicao (CORS ou Servidor Offline): ' + err.message);
    console.error('Erro detalhado:', err);
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
});
