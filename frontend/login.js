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

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);

  const payload = {
    email: f.get('email') || null,
    senha: f.get('senha') || null
  };

  log('Enviando login...');
  const submitBtn = e.target.querySelector('button[type="submit"]');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const res = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const text = await res.text();
    let data = null;
    try { data = JSON.parse(text); } catch (err) { data = null; }

    if (res.ok) {
      log('Login realizado com sucesso. Tokens recebidos:\n' + JSON.stringify(data, null, 2));
      if (data?.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      if (data?.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      // Guarda metadados do usuário para controle de acesso no front
      const userInfo = data?.user || decodeJwtPayload(data?.access_token);
      if (userInfo) {
        localStorage.setItem('user_info', JSON.stringify(userInfo));
      }

      // Redireciona sempre para a página inicial
      window.location.href = 'home.html';
    } else {
      const detail = data?.detail ? JSON.stringify(data.detail, null, 2) : text;
      log(`Erro ${res.status}: ` + detail);
    }
  } catch (err) {
    log('Falha na requisição (CORS ou servidor offline): ' + err.message);
    console.error('Erro detalhado:', err);
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
});
