// Custom Cursor
const cursor = document.querySelector('.cursor');

document.addEventListener('mousemove', (e) => {
    if(cursor) cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
});

const interactiveElements = document.querySelectorAll('a, button, input, textarea, .logo, .room-card, .service-item');

interactiveElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
        if(cursor) cursor.style.width = '50px';
        if(cursor) cursor.style.height = '50px';
        if(cursor) cursor.style.background = 'rgba(203, 168, 124, 0.2)';
    });
    
    el.addEventListener('mouseleave', () => {
        if(cursor) cursor.style.width = '20px';
        if(cursor) cursor.style.height = '20px';
        if(cursor) cursor.style.background = 'transparent';
    });
});

// Scroll Effects
const nav = document.querySelector('nav');
const scrollElements = document.querySelectorAll('[data-scroll]');
const heroBg = document.querySelector('.hero-bg');

window.addEventListener('scroll', () => {
    // Navbar background
    if (window.scrollY > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }

    // Parallax hero image
    let offset = window.scrollY;
    if (heroBg && offset < window.innerHeight) {
        heroBg.style.transform = `translateY(${offset * 0.4}px) scale(${1 + offset * 0.0005})`;
    }
});

// Intersection Observer for scroll reveal mapping
const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            scrollObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px"
});

scrollElements.forEach((el) => {
    scrollObserver.observe(el);
});

// Initial load animation for hero text
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        document.querySelectorAll('.hero [data-scroll]').forEach(el => {
            el.classList.add('is-visible');
        });
    }, 100);
});

// Room filters
const filterPrice = document.getElementById('filterPrice');
const filterType = document.getElementById('filterType');
const filterAmenity = document.getElementById('filterAmenity');

function applyRoomFilters() {
    const cards = document.querySelectorAll('.room-card');
    if (!cards.length) return;

    const priceVal = filterPrice ? filterPrice.value : 'all';
    const typeVal = filterType ? filterType.value : 'all';
    const amenityVal = filterAmenity ? filterAmenity.value : 'all';

    cards.forEach((card) => {
        const price = Number(card.dataset.price || 0);
        const name = (card.dataset.name || '').toLowerCase();
        const amenities = (card.dataset.amenities || '').toLowerCase();

        let matchPrice = true;
        if (priceVal === 'low') matchPrice = price <= 200;
        if (priceVal === 'mid') matchPrice = price > 200 && price <= 500;
        if (priceVal === 'high') matchPrice = price > 500;

        let matchType = true;
        if (typeVal !== 'all') matchType = name.includes(typeVal);

        let matchAmenity = true;
        if (amenityVal !== 'all') matchAmenity = amenities.includes(amenityVal);

        card.style.display = (matchPrice && matchType && matchAmenity) ? '' : 'none';
    });
}

[filterPrice, filterType, filterAmenity].forEach((el) => {
    if (el) el.addEventListener('change', applyRoomFilters);
});

// Room mini-gallery
document.querySelectorAll('.room-gallery-thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
        const card = thumb.closest('.room-card');
        if (!card) return;
        const mainImg = card.querySelector('.room-main-img');
        const src = thumb.dataset.src;
        if (mainImg && src) {
            mainImg.classList.add('is-switching');
            setTimeout(() => {
                mainImg.src = src;
                mainImg.classList.remove('is-switching');
            }, 320);
        }

        card.querySelectorAll('.room-gallery-thumb').forEach((t) => t.classList.remove('active'));
        thumb.classList.add('active');
    });
});

const contactForm = document.getElementById('contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', (event) => {
        event.preventDefault();
    });
}

function getPromoDiscountMap() {
    const config = document.getElementById('promo-config');
    if (!config) return {};
    try {
        return JSON.parse(config.textContent || '{}');
    } catch {
        return {};
    }
}

const PROMO_DISCOUNTS = getPromoDiscountMap();

function calculateNights(checkIn, checkOut) {
    if (!checkIn || !checkOut) return 0;
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
}

function updateLiveQuote(form) {
    const pricePerNight = Number(form.dataset.roomPrice || 0);
    const checkIn = form.querySelector('input[name="check_in"]')?.value;
    const checkOut = form.querySelector('input[name="check_out"]')?.value;
    const promoInput = form.querySelector('input[name="promo_code"]');
    const quoteBox = form.querySelector('[data-live-quote]');
    if (!quoteBox) return;

    const nights = calculateNights(checkIn, checkOut);
    const subtotal = nights * pricePerNight;
    const promoCode = (promoInput?.value || '').trim().toUpperCase();
    const discountPercent = PROMO_DISCOUNTS[promoCode] || 0;
    const discountValue = subtotal * discountPercent / 100;
    const total = Math.max(0, subtotal - discountValue);

    const nightsEl = quoteBox.querySelector('[data-quote-nights]');
    const discountEl = quoteBox.querySelector('[data-quote-discount]');
    const totalEl = quoteBox.querySelector('[data-quote-total]');

    if (nightsEl) nightsEl.textContent = String(nights);
    if (discountEl) discountEl.textContent = `-$${discountValue.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
}

function initBookingEnhancements() {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('.room-booking-form').forEach((form) => {
        const checkIn = form.querySelector('input[name="check_in"]');
        const checkOut = form.querySelector('input[name="check_out"]');
        if (checkIn) checkIn.min = today;
        if (checkOut) checkOut.min = today;

        [
            'input[name="check_in"]',
            'input[name="check_out"]',
            'input[name="promo_code"]',
        ].forEach((selector) => {
            const field = form.querySelector(selector);
            if (field) {
                field.addEventListener('input', () => updateLiveQuote(form));
                field.addEventListener('change', () => updateLiveQuote(form));
            }
        });

        updateLiveQuote(form);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    applyRoomFilters();
    initBookingEnhancements();
});
