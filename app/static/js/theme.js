function setTheme(theme) {
  document.body.classList.toggle('light-mode', theme === 'light');
  localStorage.setItem('theme', theme);

  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.textContent = theme === 'light' ? '🌙' : '☀️';
  }
}

function toggleTheme() {
  const currentTheme = localStorage.getItem('theme') || 'dark';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
}

function initThemeControls() {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);

  const themeToggle = document.getElementById('theme-icon');
  if (themeToggle) {
    themeToggle.addEventListener('click', (event) => {
      event.preventDefault();
      toggleTheme();
    });
  }
}

function initMobileMenu() {
  const menuToggle = document.getElementById('mobile-menu');
  const navLinks = document.querySelector('.nav-links');
  if (!menuToggle || !navLinks) {
    return;
  }

  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });

  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('active');
    });
  });
}

function refreshNavbarLayout() {
  const nav = document.querySelector('nav');
  const links = document.querySelector('.nav-links');
  const logo = document.querySelector('.logo');
  if (!nav || !links || !logo) {
    return;
  }

  nav.classList.remove('nav-compact');

  if (window.innerWidth <= 768) {
    return;
  }

  const navStyles = getComputedStyle(nav);
  const horizontalPadding =
    parseFloat(navStyles.paddingLeft || '0') + parseFloat(navStyles.paddingRight || '0');
  const available = nav.clientWidth - logo.clientWidth - horizontalPadding - 36;
  const needed = links.scrollWidth;

  if (needed > available) {
    nav.classList.add('nav-compact');
  }
}

function initNavbarLayoutWatcher() {
  refreshNavbarLayout();
  window.addEventListener('resize', refreshNavbarLayout);
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
  initThemeControls();
  initMobileMenu();
  initNavbarLayoutWatcher();
});

window.toggleTheme = toggleTheme;
window.refreshNavbarLayout = refreshNavbarLayout;
