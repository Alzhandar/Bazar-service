class Header {
    constructor() {
        this.init();
        this.bindEvents();
    }

    init() {
        this.header = document.querySelector('.header');
        this.searchToggle = document.querySelector('.search-toggle');
        this.mobileSearch = document.querySelector('.mobile-search');
        this.mobileSearchClose = document.querySelector('.mobile-search-close');
        this.mobileOverlay = document.querySelector('.mobile-overlay');
        this.menuToggle = document.querySelector('.mobile-menu-toggle');
        this.themeToggle = document.querySelector('#themeToggle');
        this.mobileThemeToggle = document.querySelector('#mobileThemeToggle');
    }

    bindEvents() {
        if (this.searchToggle) {
            this.searchToggle.addEventListener('click', () => this.toggleMobileSearch());
        }

        if (this.mobileSearchClose) {
            this.mobileSearchClose.addEventListener('click', () => this.closeMobileSearch());
        }

        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleMobileMenu());
        }

        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => this.closeMobileMenu());
        }

        if (this.themeToggle && this.mobileThemeToggle) {
            this.themeToggle.addEventListener('click', () => this.toggleTheme());
            this.mobileThemeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleMobileSearch() {
        this.mobileSearch.classList.toggle('active');
        this.mobileOverlay.classList.toggle('active');
        document.body.style.overflow = this.mobileSearch.classList.contains('active') ? 'hidden' : '';
    }

    closeMobileSearch() {
        this.mobileSearch.classList.remove('active');
        this.mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleMobileMenu() {
        this.header.classList.toggle('mobile-menu-active');
        this.mobileOverlay.classList.toggle('active');
        document.body.style.overflow = this.header.classList.contains('mobile-menu-active') ? 'hidden' : '';
    }

    closeMobileMenu() {
        this.header.classList.remove('mobile-menu-active');
        this.mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    toggleTheme() {
        const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const icon = theme === 'dark' ? 'fa-sun' : 'fa-moon';
        this.themeToggle.querySelector('i').className = `fas ${icon}`;
        this.mobileThemeToggle.querySelector('i').className = `fas ${icon}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Header();
});