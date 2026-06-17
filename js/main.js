/* ============================================
   CRECE - Main Global JavaScript Logic
   Centro Regional de Educación
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Scroll Event for Navbar Styling
    const navbar = document.getElementById('main-nav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
        
        // Initial check on page load (if loaded mid-scroll)
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        }
    }

    // 2. Mobile Menu Toggle
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileOverlay = document.getElementById('mobile-overlay');
    const closeMenuBtn = document.getElementById('close-menu-btn');

    if (menuBtn && mobileMenu && mobileOverlay) {
        const toggleMenu = (open) => {
            if (open) {
                mobileMenu.classList.add('open');
                mobileOverlay.classList.add('open');
                document.body.style.overflow = 'hidden'; // Prevent background scrolling
            } else {
                mobileMenu.classList.remove('open');
                mobileOverlay.classList.remove('open');
                document.body.style.overflow = '';
            }
        };

        menuBtn.addEventListener('click', () => toggleMenu(true));
        mobileOverlay.addEventListener('click', () => toggleMenu(false));
        if (closeMenuBtn) {
            closeMenuBtn.addEventListener('click', () => toggleMenu(false));
        }

        // Close mobile menu on clicking any navigation link
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => toggleMenu(false));
        });
    }

    // 3. Highlight Current Page Link in Navigation
    const currentPath = window.location.pathname;
    const filename = currentPath.substring(currentPath.lastIndexOf('/') + 1) || 'index.html';
    
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === filename || (filename === 'index.html' && href === '#') || (filename === 'index.html' && href === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // 4. Intersection Observer for Scroll Animations
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    if ('IntersectionObserver' in window && animatedElements.length > 0) {
        const animationObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const animationType = entry.target.getAttribute('data-animate');
                    
                    // Add appropriate class based on attribute value
                    if (animationType === 'fade-in') {
                        entry.target.classList.add('animate-fade-in');
                    } else if (animationType === 'fade-in-up') {
                        entry.target.classList.add('animate-fade-in-up');
                    } else if (animationType === 'slide-left') {
                        entry.target.classList.add('animate-slide-left');
                    } else if (animationType === 'slide-right') {
                        entry.target.classList.add('animate-slide-right');
                    } else if (animationType === 'scale-in') {
                        entry.target.classList.add('animate-scale-in');
                    }
                    
                    // Stop observing once animated
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px' // Trigger slightly before element enters viewport
        });

        animatedElements.forEach(element => {
            // Apply initial opacity to avoid flashing
            element.style.opacity = '0';
            animationObserver.observe(element);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        animatedElements.forEach(element => {
            element.style.opacity = '1';
        });
    }
});
