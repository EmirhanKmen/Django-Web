/**
 * Sahaflar Platformu — Core JavaScript
 * Handles UI interactions, animations, and dynamic components.
 */

// === User Menu & Hamburger Toggle ===
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) dropdown.classList.toggle('show');
}

function toggleMobileMenu() {
    const menu = document.getElementById('main-nav-menu');
    const hamburger = document.getElementById('hamburger-btn');
    if (menu && hamburger) {
        menu.classList.toggle('open');
        hamburger.classList.toggle('active');
    }
}

// Close dropdowns on outside click
document.addEventListener('click', (e) => {
    const userMenu = document.getElementById('user-menu');
    const userDropdown = document.getElementById('user-dropdown');
    if (userMenu && userDropdown && !userMenu.contains(e.target)) {
        userDropdown.classList.remove('show');
    }

    const navMenu = document.getElementById('main-nav-menu');
    const hamburger = document.getElementById('hamburger-btn');
    if (navMenu && navMenu.classList.contains('open') && hamburger && !hamburger.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('open');
        hamburger.classList.remove('active');
    }
});

// === Scroll to Top ===
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.addEventListener('scroll', () => {
    const scrollBtn = document.getElementById('scroll-top-btn');
    if (scrollBtn) {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    }
});

// === Auto-dismiss alerts ===
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.alert').forEach((alert, i) => {
        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 4000 + (i * 500));
    });

    // Animate stat values
    document.querySelectorAll('.stat-value').forEach(el => {
        const target = parseInt(el.textContent);
        if (isNaN(target)) return;
        let current = 0;
        const step = Math.max(1, Math.floor(target / 30));
        const interval = setInterval(() => {
            current += step;
            if (current >= target) { current = target; clearInterval(interval); }
            el.textContent = current.toLocaleString('tr-TR');
        }, 30);
    });

    // Animate progress bars
    document.querySelectorAll('.progress-fill').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = width; }, 200);
    });

    // Slider value display
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        const display = slider.nextElementSibling;
        if (display && display.classList.contains('slider-value')) {
            slider.addEventListener('input', () => { display.textContent = slider.value; });
        }
    });

    // Rating items
    document.querySelectorAll('.rating-group').forEach(group => {
        group.querySelectorAll('.rating-item').forEach(item => {
            item.addEventListener('click', () => {
                group.querySelectorAll('.rating-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                const input = item.querySelector('input');
                if (input) input.checked = true;
            });
        });
    });

    // Check notifications periodically (every 60 seconds)
    const notifBadge = document.getElementById('nav-notif-badge');
    if (notifBadge && document.querySelector('.user-menu')) {
        function checkNotifications() {
            fetch('/notifications/count/')
                .then(response => response.json())
                .then(data => {
                    if (data.count !== undefined) {
                        notifBadge.textContent = data.count > 99 ? '99+' : data.count;
                        notifBadge.dataset.count = data.count;
                    }
                })
                .catch(err => console.error('Error fetching notifications:', err));
        }
        
        // Initial check and set interval
        checkNotifications();
        setInterval(checkNotifications, 60000);
    }
});

// === Chart Helpers ===
const SAHAF_CHART_COLORS = ['#00F0A0', '#3B82F6', '#FFB800', '#A855F7', '#FF4D6A', '#06B6D4', '#F97316', '#EC4899'];

function createSahafChart(canvasId, type, labels, data, label = '') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: type === 'line' ? 'rgba(0,240,160,0.1)' : SAHAF_CHART_COLORS.slice(0, data.length),
                borderColor: type === 'line' ? '#00F0A0' : SAHAF_CHART_COLORS.slice(0, data.length),
                borderWidth: type === 'line' ? 2 : 1,
                fill: type === 'line',
                tension: 0.4,
                pointBackgroundColor: '#00F0A0',
                pointBorderColor: '#00F0A0',
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: type !== 'line', labels: { color: '#8899B0', font: { family: 'Inter' } } },
            },
            scales: type === 'pie' || type === 'doughnut' ? {} : {
                x: { ticks: { color: '#5A6B82' }, grid: { color: 'rgba(30,58,95,0.5)' } },
                y: { ticks: { color: '#5A6B82' }, grid: { color: 'rgba(30,58,95,0.5)' }, beginAtZero: true }
            }
        }
    });
}
