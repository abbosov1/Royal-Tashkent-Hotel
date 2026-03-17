function renderBookingSuccessMessage() {
  const target = document.getElementById('booking-success-container');
  if (!target) {
    return;
  }

  const params = new URLSearchParams(window.location.search);
  if (params.get('success') === 'booked') {
    target.innerHTML = '<div class="booking-success-card" data-scroll><strong data-i18n="book_success_t">Booking Confirmed</strong><p data-i18n="book_success_d">Your room has been successfully booked. You can manage dates from Dashboard.</p></div>';

    if (typeof applyI18n === 'function') {
      applyI18n(localStorage.getItem('lang') || 'en');
    }
  }
}

document.addEventListener('DOMContentLoaded', renderBookingSuccessMessage);
