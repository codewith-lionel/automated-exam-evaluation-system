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
        const [statsData, recentData] = await Promise.all([
            api.get('/dashboard/stats'),
            api.get('/dashboard/recent')
        ]);
        
        // Render KPIs from stats
        if (statsData.success && statsData.stats) {
            renderKPIs(statsData.stats, user);
        }
        
        // Render charts (using recent data for now)
        if (recentData.success && recentData.recent) {
            renderCharts(recentData.recent);
        }
        
        // Render recent activity
        if (recentData.success && recentData.recent) {
            renderRecentActivity(recentData.recent);
        }
        
        loader.hide();
    } catch (error) {
        loader.hide();
        toast.error('Failed to load dashboard data');
        console.error('Dashboard error:', error);
    }
}

function renderKPIs(stats, user) {
    const kpisContainer = document.getElementById('dashboardKPIs');
    if (!kpisContainer) return;

    // Create KPI cards from stats
    const kpis = [];
    
    if (user && user.role === 'admin') {
        kpis.push(
            { icon: '📊', value: stats.total_evaluations || 0, label: 'Total Evaluations' },
            { icon: '🎯', value: `${stats.average_score || 0}%`, label: 'Average Score' },
            { icon: '👥', value: stats.total_students || 0, label: 'Total Students' }
        );
    } else {
        kpis.push(
            { icon: '📊', value: stats.total_evaluations || 0, label: 'My Evaluations' },
            { icon: '🎯', value: `${stats.average_score || 0}%`, label: 'Average Score' },
            { icon: '🏆', value: `${stats.highest_score || 0}%`, label: 'Highest Score' }
        );
    }

    kpisContainer.innerHTML = kpis.map(kpi => `
        <div class="kpi-card">
            <div class="kpi-icon">${kpi.icon}</div>
            <div class="kpi-value">${kpi.value}</div>
            <div class="kpi-label">${kpi.label}</div>
        </div>
    `).join('');
}

function getKPIIcon(tyrecentEvaluations) {
    // Generate chart data from recent evaluations
    if (recentEvaluations && recentEvaluations.length > 0) {
        // Performance Over Time Chart
        if (document.getElementById('performanceChart')) {
            const chartData = {
                labels: recentEvaluations.slice(0, 10).reverse().map(e => 
                    new Date(e.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                ),
                values: recentEvaluations.slice(0, 10).reverse().map(e => e.percentage)
            };
            renderPerformanceChart(chartData);
        }

        // Score Distribution Chart
        if (document.getElementById('scoreDistributionChart')) {
            const scores = recentEvaluations.map(e => e.percentage);
            const distribution = {
                labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
                values: [
                    scores.filter(s => s <= 20).length,
                    scores.filter(s => s > 20 && s <= 40).length,
                    scores.filter(s => s > 40 && s <= 60).length,
                    scores.filter(s => s > 60 && s <= 80).length,
                    scores.filter(s => s > 80).length
                ]
            };
            renderScoreDistributionChart(distribution);
        }
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

function renderRecentActivity(evaluations) {
    const activityContainer = document.getElementById('recentActivity');
    if (!activityContainer) return;

    if (!evaluations || evaluations.length === 0) {
        activityContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">No recent activity</div>
                <div class="empty-state-text">Your recent evaluations will appear here</div>
            </div>
        `;
        return;
    }

    activityContainer.innerHTML = `
        <ul class="activity-list">
            ${evaluations.map(eval => `
                <li class="activity-item">
                    <div class="activity-icon ${getScoreClass(eval.percentage)}">
                        ${getScoreIcon(eval.percentage)}
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${eval.subject} - ${eval.exam_type}</div>
                        <div class="activity-meta">Score: ${eval.percentage}% ${eval.username ? `• ${eval.username}` : ''}</div>
                    </div>
                    <div class="activity-time">${timeAgo(eval.created_at)}</div>
                    <a href="/results/${eval.id}" class="activity-action">View</a>
                </li>
            `).join('')}
        </ul>
    `;
}

function getScoreClass(percentage) {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'info';
    if (percentage >= 40) return 'warning';
    return 'error';
}

function getScoreIcon(percentage) {
    if (percentage >= 80) return '🏆';
    if (percentage >= 60) return '✓';
    if (percentage >= 40) return '⚠';
    return '✗';
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
