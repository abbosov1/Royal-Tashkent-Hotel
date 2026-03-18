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

function initRoomImageLightbox() {
    const lightbox = document.getElementById('image-lightbox');
    const lightboxImage = document.getElementById('lightbox-image');
    const closeBtn = document.getElementById('lightbox-close');
    const prevBtn = document.getElementById('lightbox-prev');
    const nextBtn = document.getElementById('lightbox-next');
    if (!lightbox || !lightboxImage || !closeBtn || !prevBtn || !nextBtn) return;

    let gallery = [];
    let currentIndex = 0;
    let touchStartX = 0;
    let touchEndX = 0;

    const setImage = (index) => {
        if (!gallery.length) return;
        currentIndex = (index + gallery.length) % gallery.length;
        lightboxImage.src = gallery[currentIndex];
    };

    const openLightbox = (images, startIndex = 0) => {
        gallery = images.filter(Boolean);
        if (!gallery.length) return;
        lightbox.classList.add('active');
        lightbox.setAttribute('aria-hidden', 'false');
        setImage(startIndex);
        document.body.classList.add('lightbox-open');
    };

    const closeLightbox = () => {
        lightbox.classList.remove('active');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('lightbox-open');
        lightboxImage.src = '';
    };

    const showPrev = () => setImage(currentIndex - 1);
    const showNext = () => setImage(currentIndex + 1);

    document.querySelectorAll('.room-card').forEach((card) => {
        const mainImage = card.querySelector('.room-main-img');
        if (!mainImage) return;

        mainImage.style.cursor = 'zoom-in';
        mainImage.addEventListener('click', () => {
            const thumbs = Array.from(card.querySelectorAll('.room-gallery-thumb'));
            const images = thumbs.map((thumb) => thumb.dataset.src).filter(Boolean);
            const currentSrc = mainImage.getAttribute('src') || '';
            let startIndex = images.indexOf(currentSrc);
            if (startIndex < 0) startIndex = 0;
            openLightbox(images, startIndex);
        });
    });

    closeBtn.addEventListener('click', closeLightbox);
    prevBtn.addEventListener('click', showPrev);
    nextBtn.addEventListener('click', showNext);

    lightbox.addEventListener('click', (event) => {
        if (event.target === lightbox) closeLightbox();
    });

    document.addEventListener('keydown', (event) => {
        if (!lightbox.classList.contains('active')) return;
        if (event.key === 'Escape') closeLightbox();
        if (event.key === 'ArrowLeft') showPrev();
        if (event.key === 'ArrowRight') showNext();
    });

    lightbox.addEventListener('touchstart', (event) => {
        touchStartX = event.changedTouches[0].clientX;
    }, { passive: true });

    lightbox.addEventListener('touchend', (event) => {
        touchEndX = event.changedTouches[0].clientX;
        const delta = touchEndX - touchStartX;
        if (Math.abs(delta) < 45) return;
        if (delta > 0) {
            showPrev();
        } else {
            showNext();
        }
    }, { passive: true });
}

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
    initRoomImageLightbox();
});
