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

// Mobile menu toggle
const menuToggle = document.querySelector('#mobile-menu');
const navLinks = document.querySelector('.nav-links');

if(menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    const links = navLinks.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
}

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
            }, 180);
        }

        card.querySelectorAll('.room-gallery-thumb').forEach((t) => t.classList.remove('active'));
        thumb.classList.add('active');
    });
});
document.addEventListener('DOMContentLoaded', () => {
    applyRoomFilters();
});
