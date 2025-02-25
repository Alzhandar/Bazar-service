class Sidebar {
    constructor() {
        this.init();
        this.bindEvents();
    }

    init() {
        this.sidebar = document.querySelector('.sidebar');
        this.toggle = document.querySelector('.sidebar-toggle');
        this.toggleMobile = document.querySelector('.sidebar-toggle-mobile');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.mainContent = document.querySelector('.main-content');
        this.wrapper = document.querySelector('.wrapper');
        this.restoreState();
    }

    bindEvents() {
        if (this.toggle) {
            this.toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }

        if (this.toggleMobile) {
            this.toggleMobile.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileSidebar();
            });
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', () => {
                this.closeMobileSidebar();
            });
        }

        window.addEventListener('resize', this.debounce(() => this.handleResize(), 250));
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeMobileSidebar();
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    toggleSidebar() {
        if (!this.sidebar) return;
        
        const isCollapsed = !this.sidebar.classList.contains('sidebar-collapsed');
        
        requestAnimationFrame(() => {
            this.sidebar.classList.toggle('sidebar-collapsed', isCollapsed);
            
            const icon = this.toggle.querySelector('i');
            if (icon) {
                icon.style.transform = isCollapsed ? 'rotate(180deg)' : '';
            }

            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    toggleMobileSidebar() {
        if (!this.sidebar) return;
        
        const isActive = !this.sidebar.classList.contains('active');
        
        requestAnimationFrame(() => {
            this.sidebar.classList.toggle('active', isActive);
            this.overlay.classList.toggle('active', isActive);
            document.body.style.overflow = isActive ? 'hidden' : '';
        });
    }

    closeMobileSidebar() {
        if (!this.sidebar) return;
        
        requestAnimationFrame(() => {
            this.sidebar.classList.remove('active');
            this.overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    handleResize() {
        const isMobile = window.innerWidth <= 1024;
        
        if (!isMobile && this.sidebar.classList.contains('active')) {
            this.closeMobileSidebar();
        }
    }

    restoreState() {
        if (!this.sidebar) return;

        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        
        if (isCollapsed) {
            requestAnimationFrame(() => {
                this.sidebar.classList.add('sidebar-collapsed');
                const icon = this.toggle.querySelector('i');
                if (icon) {
                    icon.style.transform = 'rotate(180deg)';
                }
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Sidebar();
});