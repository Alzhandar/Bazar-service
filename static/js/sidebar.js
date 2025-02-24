/* filepath: /Users/lzandaribaev/Desktop/WEB/projects/sales-app/static/js/sidebar.js */
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
            this.toggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.toggleMobile) {
            this.toggleMobile.addEventListener('click', () => this.toggleMobile());
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeMobileSidebar());
        }

        // Восстанавливаем состояние при загрузке
        this.restoreState();

        // Добавляем обработчик изменения размера окна
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleSidebar() {
        if (!this.sidebar) return;

        requestAnimationFrame(() => {
            const isCollapsed = this.sidebar.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);

            // Обновляем основной контент
            if (this.mainContent) {
                this.mainContent.style.marginLeft = isCollapsed ? 
                    'var(--sidebar-collapsed-width)' : 
                    'var(--sidebar-width)';
            }
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

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    new Sidebar();
});