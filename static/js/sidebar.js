class Sidebar {
    constructor() {
        this.init();
    }

    init() {
        this.sidebar = document.querySelector('.sidebar');
        this.toggle = document.querySelector('.sidebar-toggle');
        this.toggleMobile = document.querySelector('.sidebar-toggle-mobile');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.mainContent = document.querySelector('.main-content');

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

        this.restoreState();
    }

    toggleSidebar() {
        if (!this.sidebar) return;
        
        const isCollapsed = !this.sidebar.classList.contains('sidebar-collapsed');
        
        requestAnimationFrame(() => {
            this.sidebar.classList.toggle('sidebar-collapsed', isCollapsed);
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    toggleMobile() {
        if (!this.sidebar) return;

        requestAnimationFrame(() => {
            const isActive = this.sidebar.classList.toggle('active');
            document.body.style.overflow = isActive ? 'hidden' : '';
        });
    }

    closeMobileSidebar() {
        if (!this.sidebar) return;

        requestAnimationFrame(() => {
            this.sidebar.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    handleResize() {
        if (window.innerWidth > 1024) {
            this.closeMobileSidebar();
        }
    }

    restoreState() {
        if (!this.sidebar) return;

        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            requestAnimationFrame(() => {
                this.sidebar.classList.add('sidebar-collapsed');
                if (this.mainContent) {
                    this.mainContent.style.marginLeft = 'var(--sidebar-collapsed-width)';
                }
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Sidebar();
});