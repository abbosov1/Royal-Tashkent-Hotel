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
      html = '<div class="alert error" data-i18n="auth_invalid">Invalid credentials</div>';
    } else if (params.get('error') === 'unverified') {
      html = '<div class="alert error" data-i18n="auth_unverified">Please verify your email first.</div>';
    } else if (params.get('registered') === '1') {
      html = '<div class="alert success" data-i18n="auth_registered">Successfully registered. Please sign in.</div>';
    } else if (params.get('verified') === '1') {
      html = '<div class="alert success" data-i18n="auth_verified">Email verified. You can sign in now.</div>';
    } else if (params.get('password_reset') === '1') {
      html = '<div class="alert success" data-i18n="reset_success">Password reset successful. Please sign in.</div>';
    }
  }

  if (page === 'register') {
    if (params.get('error') === '2') {
      html = '<div class="alert error" data-i18n="auth_email_exists">Email already registered</div>';
    }
  }

  if (page === 'verify-email') {
    if (params.get('sent') === '1') {
      html = '<div class="alert success" data-i18n="verify_sent">Verification code sent to your email.</div>';
    }
    if (params.get('error') === 'invalid_code') {
      html = '<div class="alert error" data-i18n="verify_invalid">Invalid verification code.</div>';
    }
    if (params.get('error') === 'code_required') {
      html = '<div class="alert error" data-i18n="verify_required">Please enter full 6-digit code.</div>';
    }
    if (params.get('error') === 'expired') {
      html = '<div class="alert error" data-i18n="verify_expired">Code expired. New code was sent.</div>';
    }
    if (params.get('error') === 'attempt_limit') {
      html = '<div class="alert error" data-i18n="verify_attempt_limit">Attempt limit reached. New code was sent.</div>';
    }
    if (params.get('error') === 'unverified') {
      html = '<div class="alert error" data-i18n="auth_unverified">Please verify your email first.</div>';
    }
  }

  if (page === 'forgot-password') {
    if (params.get('sent') === '1') {
      html = '<div class="alert success" data-i18n="forgot_sent">If account exists, reset code was sent.</div>';
    }
  }

  if (page === 'reset-password') {
    if (params.get('sent') === '1') {
      html = '<div class="alert success" data-i18n="verify_sent">Verification code sent to your email.</div>';
    }
    if (params.get('error') === 'invalid_code') {
      html = '<div class="alert error" data-i18n="verify_invalid">Invalid verification code.</div>';
    }
    if (params.get('error') === 'code_required') {
      html = '<div class="alert error" data-i18n="verify_required">Please enter full 6-digit code.</div>';
    }
    if (params.get('error') === 'expired') {
      html = '<div class="alert error" data-i18n="verify_expired">Code expired. New code was sent.</div>';
    }
    if (params.get('error') === 'attempt_limit') {
      html = '<div class="alert error" data-i18n="verify_attempt_limit">Attempt limit reached. New code was sent.</div>';
    }
    if (params.get('error') === 'password_mismatch') {
      html = '<div class="alert error" data-i18n="reset_mismatch">Passwords do not match.</div>';
    }
    if (params.get('error') === 'password_short') {
      html = '<div class="alert error" data-i18n="reset_short">Password must be at least 6 characters.</div>';
    }
  }

  container.innerHTML = html;

  // Re-apply language after injecting new translatable nodes.
  if (typeof applyI18n === 'function') {
    applyI18n(localStorage.getItem('lang') || 'en');
  }
}

function initCodeInputs() {
  const wrapper = document.querySelector('[data-code-inputs]');
  if (!wrapper) return;

  const inputs = Array.from(wrapper.querySelectorAll('[data-code-cell]'));
  const hidden = document.querySelector('#verify-code-hidden, #reset-code-hidden');
  const submitButton = document.querySelector('[data-code-submit]');
  const form = submitButton ? submitButton.closest('form') : null;

  const syncCode = () => {
    const value = inputs.map((input) => input.value.trim()).join('');
    if (hidden) hidden.value = value;
    if (submitButton) submitButton.disabled = value.length !== 6;
  };

  inputs.forEach((input, index) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/\D/g, '').slice(0, 1);
      if (input.value && index < inputs.length - 1) {
        inputs[index + 1].focus();
      }
      syncCode();
    });

    input.addEventListener('keydown', (event) => {
      if (event.key === 'Backspace' && !input.value && index > 0) {
        inputs[index - 1].focus();
      }
    });
  });

  if (form) {
    form.addEventListener('submit', (event) => {
      syncCode();
      if (!hidden || hidden.value.length !== 6) {
        event.preventDefault();
      }
    });
  }

  syncCode();
  inputs[0]?.focus();
}

function initResendCooldown() {
  const form = document.querySelector('[data-resend-form]');
  const button = document.querySelector('[data-resend-button]');
  if (!form || !button) return;

  const seconds = Number(form.dataset.resendSeconds || 60);
  const key = form.dataset.resendKey || 'resend';
  const storageKey = `resendCooldown:${key}`;
  const baseLabel = button.textContent;
  const params = new URLSearchParams(window.location.search);

  if (params.get('sent') === '1') {
    localStorage.setItem(storageKey, String(Date.now() + seconds * 1000));
  }

  const updateState = () => {
    const until = Number(localStorage.getItem(storageKey) || 0);
    const left = Math.ceil((until - Date.now()) / 1000);
    if (left > 0) {
      button.disabled = true;
      button.textContent = `${baseLabel} (${left}s)`;
      return;
    }

    button.disabled = false;
    button.textContent = baseLabel;
  };

  updateState();
  setInterval(updateState, 1000);
}

function initGlobalLoader() {
  const loader = document.createElement('div');
  loader.className = 'global-loader active';
  loader.innerHTML = '<div class="global-loader-spinner"></div>';
  document.body.appendChild(loader);

  const showLoader = () => loader.classList.add('active');
  const hideLoader = () => loader.classList.remove('active');

  window.addEventListener('load', hideLoader);
  document.querySelectorAll('a[href]').forEach((anchor) => {
    anchor.addEventListener('click', () => {
      const href = anchor.getAttribute('href') || '';
      if (href.startsWith('#') || href.startsWith('javascript:')) return;
      showLoader();
    });
  });
  document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', showLoader);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initGlobalLoader();
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);

  document.querySelectorAll('[data-password-toggle]').forEach((button) => {
    button.addEventListener('click', () => togglePwd(button));
  });

  renderAuthMessage();
  initCodeInputs();
  initResendCooldown();
});
