// Dashboard - Load data and render charts

document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/dashboard') {
        initDashboard();
    }
});

async function initDashboard() {
    const user = getCurrentUser();
    
    if (!user) {
        protectPage();
        return;
    }

    try {
        loader.show('Loading dashboard...');
        
        // Load dashboard data
        const data = await api.get('/dashboard/stats');
        
        // Render KPIs
        renderKPIs(data.kpis);
        
        // Render charts
        renderCharts(data.charts);
        
        // Render recent activity
        renderRecentActivity(data.recentActivity);
        
        loader.hide();
    } catch (error) {
        loader.hide();
        toast.error('Failed to load dashboard data');
        console.error('Dashboard error:', error);
    }
}

function renderKPIs(kpis) {
    const kpisContainer = document.getElementById('dashboardKPIs');
    if (!kpisContainer) return;

    kpisContainer.innerHTML = kpis.map(kpi => `
        <div class="kpi-card">
            <div class="kpi-icon">${getKPIIcon(kpi.type)}</div>
            <div class="kpi-value">${kpi.value}</div>
            <div class="kpi-label">${kpi.label}</div>
            ${kpi.trend ? `
                <div class="kpi-trend ${kpi.trend > 0 ? 'up' : 'down'}">
                    ${kpi.trend > 0 ? '↑' : '↓'} ${Math.abs(kpi.trend)}%
                </div>
            ` : ''}
        </div>
    `).join('');
}

function getKPIIcon(type) {
    const icons = {
        evaluations: '📊',
        average_score: '🎯',
        students: '👥',
        pending: '⏳',
        completed: '✓',
        total_papers: '📄'
    };
    return icons[type] || '📈';
}

function renderCharts(charts) {
    // Performance Over Time Chart
    if (charts.performanceOverTime && document.getElementById('performanceChart')) {
        renderPerformanceChart(charts.performanceOverTime);
    }

    // Score Distribution Chart
    if (charts.scoreDistribution && document.getElementById('scoreDistributionChart')) {
        renderScoreDistributionChart(charts.scoreDistribution);
    }

    // Subject Performance Chart
    if (charts.subjectPerformance && document.getElementById('subjectPerformanceChart')) {
        renderSubjectPerformanceChart(charts.subjectPerformance);
    }
}

function renderPerformanceChart(data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Score',
                data: data.values,
                borderColor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--accent-blue').trim(),
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-primary').trim()
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--border-color').trim()
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-secondary').trim()
                    }
                },
                x: {
                    grid: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--border-color').trim()
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-secondary').trim()
                    }
                }
            }
        }
    });
}

function renderScoreDistributionChart(data) {
    const ctx = document.getElementById('scoreDistributionChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Number of Students',
                data: data.values,
                backgroundColor: [
                    'rgba(248, 81, 73, 0.8)',
                    'rgba(210, 153, 34, 0.8)',
                    'rgba(88, 166, 255, 0.8)',
                    'rgba(63, 185, 80, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-primary').trim()
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--border-color').trim()
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-secondary').trim()
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-secondary').trim()
                    }
                }
            }
        }
    });
}

function renderSubjectPerformanceChart(data) {
    const ctx = document.getElementById('subjectPerformanceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Average Score',
                data: data.values,
                borderColor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--accent-green').trim(),
                backgroundColor: 'rgba(63, 185, 80, 0.2)',
                pointBackgroundColor: getComputedStyle(document.documentElement)
                    .getPropertyValue('--accent-green').trim()
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-primary').trim()
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--border-color').trim()
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-secondary').trim()
                    },
                    pointLabels: {
                        color: getComputedStyle(document.documentElement)
                            .getPropertyValue('--text-primary').trim()
                    }
                }
            }
        }
    });
}

function renderRecentActivity(activities) {
    const activityContainer = document.getElementById('recentActivity');
    if (!activityContainer) return;

    if (!activities || activities.length === 0) {
        activityContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">No recent activity</div>
                <div class="empty-state-text">Your recent activities will appear here</div>
            </div>
        `;
        return;
    }

    activityContainer.innerHTML = `
        <ul class="activity-list">
            ${activities.map(activity => `
                <li class="activity-item">
                    <div class="activity-icon ${activity.type}">
                        ${getActivityIcon(activity.type)}
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-meta">${activity.description}</div>
                    </div>
                    <div class="activity-time">${timeAgo(activity.timestamp)}</div>
                </li>
            `).join('')}
        </ul>
    `;
}

function getActivityIcon(type) {
    const icons = {
        success: '✓',
        info: 'ℹ',
        warning: '⚠'
    };
    return icons[type] || 'ℹ';
}

// Refresh dashboard
function refreshDashboard() {
    initDashboard();
}

// Export stats
async function exportStats(format = 'pdf') {
    try {
        loader.show('Exporting statistics...');
        
        const response = await api.get(`/dashboard/export?format=${format}`);
        
        if (response.success) {
            downloadFile(response.url, `dashboard-stats.${format}`);
            toast.success('Statistics exported successfully');
        }
        
        loader.hide();
    } catch (error) {
        loader.hide();
        toast.error('Failed to export statistics');
        console.error('Export error:', error);
    }
}
