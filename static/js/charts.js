/**
 * TruthLens AI — Chart.js Visualizations Manager
 * Handles initialization, data updates, and dark/light styling for dashboard charts.
 */

class DashboardCharts {
    constructor() {
        this.verdictChart = null;
        this.scoreDistChart = null;
        this.timelineChart = null;
        this.riskRadarChart = null;
    }

    getThemeColors() {
        const isDark = document.documentElement.getAttribute("data-theme") !== "light";
        return {
            textColor: isDark ? "#9ca3af" : "#475569",
            gridColor: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(0, 0, 0, 0.06)",
            tooltipBg: isDark ? "#1f2937" : "#ffffff",
            tooltipText: isDark ? "#f3f4f6" : "#0f172a"
        };
    }

    initCharts() {
        this.initVerdictChart();
        this.initScoreDistChart();
        this.initTimelineChart();
        this.initRiskRadarChart();
    }

    initVerdictChart() {
        const ctx = document.getElementById("verdictChart")?.getContext("2d");
        if (!ctx) return;

        this.verdictChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Real / Credible", "Fake / Misinformation", "Unverified / Dubious"],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ["#10b981", "#ef4444", "#f59e0b"],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: this.getThemeColors().textColor,
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
                            padding: 14
                        }
                    }
                },
                cutout: "68%"
            }
        });
    }

    initScoreDistChart() {
        const ctx = document.getElementById("scoreDistChart")?.getContext("2d");
        if (!ctx) return;

        const colors = this.getThemeColors();
        this.scoreDistChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: ["0-25% (High Risk)", "26-50% (Dubious)", "51-75% (Moderate)", "76-100% (Credible)"],
                datasets: [{
                    label: "Articles Analyzed",
                    data: [0, 0, 0, 0],
                    backgroundColor: ["#ef4444", "#f97316", "#3b82f6", "#10b981"],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: colors.textColor, font: { size: 11 } },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: colors.textColor, precision: 0 },
                        grid: { color: colors.gridColor },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initTimelineChart() {
        const ctx = document.getElementById("timelineChart")?.getContext("2d");
        if (!ctx) return;

        const colors = this.getThemeColors();
        this.timelineChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                datasets: [
                    {
                        label: "Real Articles",
                        data: [0, 0, 0, 0, 0, 0, 0],
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.12)",
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointBackgroundColor: "#10b981"
                    },
                    {
                        label: "Fake Articles",
                        data: [0, 0, 0, 0, 0, 0, 0],
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239, 68, 68, 0.12)",
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4,
                        pointBackgroundColor: "#ef4444"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: { color: colors.textColor, font: { size: 12 } }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: colors.textColor },
                        grid: { color: colors.gridColor }
                    },
                    y: {
                        ticks: { color: colors.textColor, precision: 0 },
                        grid: { color: colors.gridColor },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    initRiskRadarChart() {
        const ctx = document.getElementById("riskRadarChart")?.getContext("2d");
        if (!ctx) return;

        const colors = this.getThemeColors();
        this.riskRadarChart = new Chart(ctx, {
            type: "radar",
            data: {
                labels: ["Clickbait Vocabulary", "Sensational Punctuation", "Headline ALL-CAPS", "Lack of Attributions", "Emotional Polarity"],
                datasets: [
                    {
                        label: "Typical Fake News",
                        data: [85, 78, 65, 80, 72],
                        backgroundColor: "rgba(239, 68, 68, 0.2)",
                        borderColor: "#ef4444",
                        pointBackgroundColor: "#ef4444"
                    },
                    {
                        label: "Typical Real News",
                        data: [12, 8, 5, 15, 18],
                        backgroundColor: "rgba(16, 185, 129, 0.2)",
                        borderColor: "#10b981",
                        pointBackgroundColor: "#10b981"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: colors.textColor, font: { size: 11 } }
                    }
                },
                scales: {
                    r: {
                        ticks: { display: false },
                        grid: { color: colors.gridColor },
                        pointLabels: { color: colors.textColor, font: { size: 10 } },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        });
    }

    updateData(stats) {
        if (!stats) return;

        // 1. Verdict chart
        if (this.verdictChart) {
            this.verdictChart.data.datasets[0].data = [
                stats.real_count || 0,
                stats.fake_count || 0,
                stats.unverified_count || 0
            ];
            this.verdictChart.update();
        }

        // 2. Score Distribution
        if (this.scoreDistChart && stats.score_distribution) {
            this.scoreDistChart.data.datasets[0].data = [
                stats.score_distribution["0-25"] || 0,
                stats.score_distribution["26-50"] || 0,
                stats.score_distribution["51-75"] || 0,
                stats.score_distribution["76-100"] || 0
            ];
            this.scoreDistChart.update();
        }

        // 3. Timeline
        if (this.timelineChart && stats.timeline && stats.timeline.length > 0) {
            this.timelineChart.data.labels = stats.timeline.map(t => t.date);
            this.timelineChart.data.datasets[0].data = stats.timeline.map(t => t.real);
            this.timelineChart.data.datasets[1].data = stats.timeline.map(t => t.fake);
            this.timelineChart.update();
        }
    }

    updateTheme() {
        const colors = this.getThemeColors();
        const charts = [this.verdictChart, this.scoreDistChart, this.timelineChart, this.riskRadarChart];
        
        charts.forEach(c => {
            if (!c) return;
            if (c.options.plugins?.legend?.labels) {
                c.options.plugins.legend.labels.color = colors.textColor;
            }
            if (c.options.scales?.x?.ticks) c.options.scales.x.ticks.color = colors.textColor;
            if (c.options.scales?.y?.ticks) c.options.scales.y.ticks.color = colors.textColor;
            if (c.options.scales?.y?.grid) c.options.scales.y.grid.color = colors.gridColor;
            if (c.options.scales?.r?.pointLabels) c.options.scales.r.pointLabels.color = colors.textColor;
            c.update();
        });
    }
}

window.dashboardCharts = new DashboardCharts();
