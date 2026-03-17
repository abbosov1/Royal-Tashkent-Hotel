function setTheme(theme) {
  document.body.classList.toggle('light-mode', theme === 'light');
  localStorage.setItem('theme', theme);
}

function togglePwd(button) {
  const input = button.previousElementSibling;
  const icon = button.querySelector('.material-symbols-outlined');

  if (!input || !icon) return;

  if (input.type === 'password') {
    input.type = 'text';
    icon.textContent = 'visibility';
  } else {
    input.type = 'password';
    icon.textContent = 'visibility_off';
  }
}

function renderAuthMessage() {
  const container = document.getElementById('auth-message');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const page = document.body.dataset.authPage;
  let html = '';

  if (page === 'login') {
    if (params.get('error') === '1') {
      html = '<div class="alert error">Invalid credentials</div>';
    } else if (params.get('registered') === '1') {
      html = '<div class="alert success">Successfully registered. Please sign in.</div>';
    }
  }

  if (page === 'register') {
    if (params.get('error') === '2') {
      html = '<div class="alert error">Email already registered</div>';
    }
  }

  container.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);
  renderAuthMessage();
});
