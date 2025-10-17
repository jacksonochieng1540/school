// custom.js - School Management System
document.addEventListener('DOMContentLoaded', function() {
    initializeSchoolManagementSystem();
});

function initializeSchoolManagementSystem() {
    // Initialize all components
    initializeAlerts();
    initializeForms();
    initializeTables();
    initializeCharts();
    initializeDashboard();
    initializeNavigation();
    initializeModals();
    initializeNotifications();
    initializeRealTimeUpdates();
}

// Alert Management
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.querySelector('.btn-close')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Add click to dismiss for all alerts
    alerts.forEach(alert => {
        alert.addEventListener('click', function(e) {
            if (e.target.classList.contains('alert')) {
                const bsAlert = new bootstrap.Alert(this);
                bsAlert.close();
            }
        });
    });
}

// Form Enhancements
function initializeForms() {
    // Add loading state to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !this.classList.contains('no-loading')) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                
                // Revert after 30 seconds if still processing
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                        showNotification('Request taking longer than expected. Please try again.', 'warning');
                    }
                }, 30000);
            }
        });
    });

    // Auto-save for lengthy forms
    const autoSaveForms = document.querySelectorAll('form.auto-save');
    autoSaveForms.forEach(form => {
        let saveTimeout;
        form.addEventListener('input', function() {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveForm(this);
            }, 2000);
        });
    });

    // Enhanced select inputs
    const enhancedSelects = document.querySelectorAll('select[data-enhance]');
    enhancedSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.classList.add('is-valid');
        });
    });
}

// Table Enhancements
function initializeTables() {
    // Add hover effects to table rows
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.style.transition = 'all 0.2s ease';
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.transform = 'translateX(2px)';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.transform = 'translateX(0)';
        });
    });

    // Sortable tables
    const sortableTables = document.querySelectorAll('table[data-sortable]');
    sortableTables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.cellIndex, this.getAttribute('data-sort'));
            });
        });
    });

    // Row selection
    const selectableTables = document.querySelectorAll('table[data-selectable]');
    selectableTables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', function(e) {
                if (!e.target.tagName === 'A' && !e.target.tagName === 'BUTTON') {
                    this.classList.toggle('table-active');
                }
            });
        });
    });
}

// Dashboard Specific Functions
function initializeDashboard() {
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000);

    // Animate dashboard cards on scroll
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    dashboardCards.forEach(card => {
        observer.observe(card);
    });

    // Quick action buttons
    const quickActions = document.querySelectorAll('.quick-action-btn');
    quickActions.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                showNotification('This feature is coming soon!', 'info');
            }
        });
    });

    // Stats counter animation
    animateStatsCounters();
}

// Chart Initialization
function initializeCharts() {
    const chartContainers = document.querySelectorAll('.chart-container');
    chartContainers.forEach(container => {
        if (container.dataset.chartType) {
            initializeChart(container);
        }
    });
}

// Navigation Enhancements
function initializeNavigation() {
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentPath.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });

    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('mobile-menu-open');
        });
    }

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Modal Enhancements
function initializeModals() {
    // Auto-focus first input in modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const input = this.querySelector('input[type="text"], input[type="email"], input[type="number"]');
            if (input) {
                input.focus();
            }
        });
    });

    // Confirm dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
                e.stopImmediatePropagation();
            }
        });
    });
}

// Notification System
function initializeNotifications() {
    window.showNotification = function(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                const bsAlert = new bootstrap.Alert(notification);
                bsAlert.close();
            }
        }, duration);
    };
}

// Real-time Updates
function initializeRealTimeUpdates() {
    // Simulate real-time updates for demo
    if (document.querySelector('.activity-feed')) {
        setInterval(updateActivityFeed, 30000);
    }
    
    // Online status indicator
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
}

// Utility Functions
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time, .current-time-display');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour12: true,
        hour: '2-digit',
        minute: '2-digit'
    });
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

function animateStatsCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-counter'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            counter.textContent = Math.round(current).toLocaleString();
        }, 16);
    });
}

function sortTable(table, columnIndex, sortType) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = sortType === 'numeric';
    const isDate = sortType === 'date';
    
    const sortedRows = rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].textContent.trim();
        let bValue = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
            return aValue - bValue;
        } else if (isDate) {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
            return aValue - bValue;
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // Clear and re-append sorted rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    sortedRows.forEach(row => tbody.appendChild(row));
}

function autoSaveForm(form) {
    const formData = new FormData(form);
    // Simulate auto-save - in real implementation, you'd send to server
    console.log('Auto-saving form:', Object.fromEntries(formData));
    showNotification('Changes saved automatically', 'success', 2000);
}

function updateActivityFeed() {
    const activityFeed = document.querySelector('.activity-feed');
    if (activityFeed) {
        // Simulate new activity
        const activities = [
            'New student registration completed',
            'Grade submitted for Mathematics exam',
            'Attendance marked for Class 10A',
            'New teacher account created',
            'Report card generated for Student #123'
        ];
        
        const randomActivity = activities[Math.floor(Math.random() * activities.length)];
        const newItem = document.createElement('div');
        newItem.className = 'activity-item';
        newItem.innerHTML = `
            <small class="text-muted">${new Date().toLocaleTimeString()}</small>
            <div>${randomActivity}</div>
        `;
        
        activityFeed.insertBefore(newItem, activityFeed.firstChild);
        
        // Limit to 10 items
        if (activityFeed.children.length > 10) {
            activityFeed.removeChild(activityFeed.lastChild);
        }
    }
}

function updateOnlineStatus() {
    const statusElement = document.querySelector('.online-status');
    if (statusElement) {
        if (navigator.onLine) {
            statusElement.className = 'status-indicator online';
            statusElement.title = 'Online';
        } else {
            statusElement.className = 'status-indicator offline';
            statusElement.title = 'Offline';
            showNotification('You are currently offline. Some features may not work.', 'warning');
        }
    }
}

function initializeChart(container) {
    // Simple chart initialization - in real implementation, integrate with Chart.js or similar
    const ctx = container.querySelector('canvas');
    if (ctx) {
        // Placeholder for chart initialization
        console.log('Initializing chart for:', container.dataset.chartType);
    }
}

// Export functions for global access
window.SchoolManagement = {
    showNotification,
    updateCurrentTime,
    animateStatsCounters
};

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'danger');
});

// Page visibility handling
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible - refresh data if needed
        updateCurrentTime();
    }
});

