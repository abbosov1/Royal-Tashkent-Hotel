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

if(menuToggle) {
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
}
