function renderDashboardBookingSuccess() {
  const target = document.getElementById('dashboard-success-container');
  if (!target) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  if (params.get('success') === 'booked') {
    target.innerHTML = '<div class="alert success">Booking confirmed.</div>';
  }
}

function bindDashboardConfirmForms() {
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const message = form.dataset.confirm || 'Are you sure?';
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  renderDashboardBookingSuccess();
  bindDashboardConfirmForms();
});
