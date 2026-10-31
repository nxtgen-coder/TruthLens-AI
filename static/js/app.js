/**
 * TruthLens AI — Main Frontend Application Logic
 * Implements tab navigation, theme management, live AI credibility analysis,
 * interactive results rendering, history CRUD, and dashboard analytics.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        currentTab: "tab-analyze",
        currentPage: 1,
        perPage: 10,
        currentFilter: "all",
        searchQuery: "",
        samples: [],
        lastAnalysis: null,
        activeDetailRecord: null,
        activeShareRecord: null
    };

    // DOM Elements
    const elements = {
        // Theme
        themeToggleBtn: document.getElementById("themeToggleBtn"),
        themeIcon: document.getElementById("themeIcon"),
        
        // Navigation
        navTabs: document.querySelectorAll(".nav-tab"),
        tabPanes: document.querySelectorAll(".tab-pane"),
        
        // Form & Inputs
        analyzeForm: document.getElementById("analyzeForm"),
        headlineInput: document.getElementById("headlineInput"),
        contentInput: document.getElementById("contentInput"),
        headlineCount: document.getElementById("headlineCount"),
        contentCount: document.getElementById("contentCount"),
        wordCount: document.getElementById("wordCount"),
        clearFormBtn: document.getElementById("clearFormBtn"),
        submitBtn: document.getElementById("submitAnalyzeBtn"),
        samplePillsContainer: document.getElementById("samplePillsContainer"),
        
        // Result Panel
        resultEmptyState: document.getElementById("resultEmptyState"),
        resultActiveContent: document.getElementById("resultActiveContent"),
        verdictBanner: document.getElementById("verdictBanner"),
        verdictIconWrap: document.getElementById("verdictIconWrap"),
        verdictIcon: document.getElementById("verdictIcon"),
        verdictCategory: document.getElementById("verdictCategory"),
        verdictTitle: document.getElementById("verdictTitle"),
        gaugeFill: document.getElementById("gaugeFill"),
        credibilityScoreVal: document.getElementById("credibilityScoreVal"),
        confidenceVal: document.getElementById("confidenceVal"),
        riskScoreVal: document.getElementById("riskScoreVal"),
        attributionVal: document.getElementById("attributionVal"),
        probRealVal: document.getElementById("probRealVal"),
        probFakeVal: document.getElementById("probFakeVal"),
        probRealBar: document.getElementById("probRealBar"),
        probFakeBar: document.getElementById("probFakeBar"),
        realTagsContainer: document.getElementById("realTagsContainer"),
        fakeTagsContainer: document.getElementById("fakeTagsContainer"),
        explanationList: document.getElementById("explanationList"),
        copyAnalysisBtn: document.getElementById("copyAnalysisBtn"),
        viewHistoryFromAnalysisBtn: document.getElementById("viewHistoryFromAnalysisBtn"),
        
        // Dashboard
        refreshStatsBtn: document.getElementById("refreshStatsBtn"),
        kpiTotal: document.getElementById("kpiTotal"),
        kpiReal: document.getElementById("kpiReal"),
        kpiFake: document.getElementById("kpiFake"),
        kpiAvgScore: document.getElementById("kpiAvgScore"),
        
        // History
        historySearchInput: document.getElementById("historySearchInput"),
        filterBtns: document.querySelectorAll(".filter-btn"),
        historyTableBody: document.getElementById("historyTableBody"),
        paginationInfo: document.getElementById("paginationInfo"),
        paginationBtns: document.getElementById("paginationBtns"),
        exportCsvBtn: document.getElementById("exportCsvBtn"),
        exportJsonBtn: document.getElementById("exportJsonBtn"),
        clearAllHistoryBtn: document.getElementById("clearAllHistoryBtn"),
        
        // Modal
        detailModal: document.getElementById("detailModal"),
        modalTitle: document.getElementById("modalTitle"),
        modalBody: document.getElementById("modalBody"),
        modalCloseBtn: document.getElementById("modalCloseBtn"),
        modalCloseFooterBtn: document.getElementById("modalCloseFooterBtn"),
        
        // Methodology
        modelAccuracyVal: document.getElementById("modelAccuracyVal"),
        modelPrecisionVal: document.getElementById("modelPrecisionVal"),
        modelRecallVal: document.getElementById("modelRecallVal"),
        modelF1Val: document.getElementById("modelF1Val"),
        cmTN: document.getElementById("cmTN"),
        cmFP: document.getElementById("cmFP"),
        cmFN: document.getElementById("cmFN"),
        cmTP: document.getElementById("cmTP"),
        metaDatasetTotal: document.getElementById("metaDatasetTotal"),
        metaVocabSize: document.getElementById("metaVocabSize"),
        topRealVocabList: document.getElementById("topRealVocabList"),
        topFakeVocabList: document.getElementById("topFakeVocabList"),
        
        // Toast
        toastContainer: document.getElementById("toastContainer"),

        // Share Modal Elements
        shareAnalysisBtn: document.getElementById("shareAnalysisBtn"),
        shareModal: document.getElementById("shareModal"),
        shareModalCloseBtn: document.getElementById("shareModalCloseBtn"),
        shareModalCloseFooterBtn: document.getElementById("shareModalCloseFooterBtn"),
        shareHeadlinePreview: document.getElementById("shareHeadlinePreview"),
        shareVerdictBadge: document.getElementById("shareVerdictBadge"),
        shareScoreChip: document.getElementById("shareScoreChip"),
        shareUrlInput: document.getElementById("shareUrlInput"),
        copyShareUrlBtn: document.getElementById("copyShareUrlBtn"),
        nativeShareContainer: document.getElementById("nativeShareContainer"),
        nativeShareBtn: document.getElementById("nativeShareBtn"),
        shareTwitterBtn: document.getElementById("shareTwitterBtn"),
        shareWhatsappBtn: document.getElementById("shareWhatsappBtn"),
        shareLinkedinBtn: document.getElementById("shareLinkedinBtn"),
        shareTelegramBtn: document.getElementById("shareTelegramBtn"),
        shareEmailBtn: document.getElementById("shareEmailBtn"),
        copyReportTextBtn: document.getElementById("copyReportTextBtn"),
        modalShareBtn: document.getElementById("modalShareBtn")
    };

    /* -------------------------------------------------------------
       1. Theme Initialization & Switching
       ------------------------------------------------------------- */
    function initTheme() {
        const savedTheme = localStorage.getItem("truthlens_theme") || "dark";
        setTheme(savedTheme);

        elements.themeToggleBtn.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme") || "dark";
            const next = current === "dark" ? "light" : "dark";
            setTheme(next);
        });
    }

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("truthlens_theme", theme);
        if (theme === "dark") {
            elements.themeIcon.className = "fa-solid fa-sun";
        } else {
            elements.themeIcon.className = "fa-solid fa-moon";
        }
        if (window.dashboardCharts) {
            window.dashboardCharts.updateTheme();
        }
    }

    /* -------------------------------------------------------------
       2. Navigation Tabs
       ------------------------------------------------------------- */
    function initTabs() {
        elements.navTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const targetTab = tab.getAttribute("data-tab");
                switchTab(targetTab);
            });
        });
    }

    function switchTab(tabId) {
        state.currentTab = tabId;

        elements.navTabs.forEach(t => {
            const isActive = t.getAttribute("data-tab") === tabId;
            t.classList.toggle("active", isActive);
            t.setAttribute("aria-selected", isActive ? "true" : "false");
        });

        elements.tabPanes.forEach(pane => {
            pane.classList.toggle("active", pane.id === tabId);
        });

        if (tabId === "tab-dashboard") {
            loadDashboardStats();
        } else if (tabId === "tab-history") {
            loadHistory();
        } else if (tabId === "tab-methodology") {
            loadMethodologyData();
        }
    }

    /* -------------------------------------------------------------
       3. Textarea & Counters
       ------------------------------------------------------------- */
    function initCounters() {
        elements.headlineInput.addEventListener("input", updateHeadlineCount);
        elements.contentInput.addEventListener("input", updateContentCount);
        elements.clearFormBtn.addEventListener("click", clearForm);
    }

    function updateHeadlineCount() {
        const len = elements.headlineInput.value.length;
        elements.headlineCount.textContent = `${len} / 500`;
    }

    function updateContentCount() {
        const text = elements.contentInput.value;
        const len = text.length;
        elements.contentCount.textContent = `${len.toLocaleString()} / 50,000`;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        elements.wordCount.textContent = `${words.toLocaleString()} words`;
    }

    function clearForm() {
        elements.headlineInput.value = "";
        elements.contentInput.value = "";
        updateHeadlineCount();
        updateContentCount();
        elements.headlineInput.focus();
    }

    /* -------------------------------------------------------------
       4. Presets & Samples Loading
       ------------------------------------------------------------- */
    async function loadSamples() {
        try {
            const res = await fetch("/api/samples");
            const data = await res.json();
            if (data.status === "success" && data.samples) {
                state.samples = data.samples;
                renderSampleButtons();
            }
        } catch (err) {
            console.error("Failed to load sample articles:", err);
        }
    }

    function renderSampleButtons() {
        if (!elements.samplePillsContainer) return;
        elements.samplePillsContainer.innerHTML = "";
        
        state.samples.forEach(sample => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "sample-pill";
            const isReal = sample.label.toLowerCase().includes("real");
            const icon = isReal 
                ? '<i class="fa-solid fa-circle-check text-success"></i>' 
                : '<i class="fa-solid fa-triangle-exclamation text-danger"></i>';
            btn.innerHTML = `${icon} ${sample.category}: ${sample.label.split(" ")[0]}`;
            
            btn.addEventListener("click", () => {
                elements.headlineInput.value = sample.headline;
                elements.contentInput.value = sample.content;
                updateHeadlineCount();
                updateContentCount();
                showToast(`Loaded sample: ${sample.headline.slice(0, 45)}...`, "info");
                // Automatically analyze sample
                executeAnalysis();
            });
            elements.samplePillsContainer.appendChild(btn);
        });
    }

    /* -------------------------------------------------------------
       5. Analysis Execution & Rendering
       ------------------------------------------------------------- */
    function initAnalysisForm() {
        elements.analyzeForm.addEventListener("submit", (e) => {
            e.preventDefault();
            executeAnalysis();
        });

        elements.copyAnalysisBtn.addEventListener("click", copyAnalysisSummary);
        elements.viewHistoryFromAnalysisBtn.addEventListener("click", () => {
            switchTab("tab-history");
        });
    }

    async function executeAnalysis() {
        const headline = elements.headlineInput.value.trim();
        const content = elements.contentInput.value.trim();

        if (!headline && !content) {
            showToast("Please provide a headline or article text to analyze.", "warning");
            return;
        }

        // Set Loading state
        setLoading(true);

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ headline, content })
            });

            const result = await response.json();

            if (!response.ok || result.status !== "success") {
                throw new Error(result.message || "Analysis request failed.");
            }

            state.lastAnalysis = result.data;
            renderAnalysisResult(result.data);
            showToast("Credibility analysis successfully generated!", "success");

        } catch (err) {
            console.error("Analysis Error:", err);
            showToast(err.message, "danger");
        } finally {
            setLoading(false);
        }
    }

    function setLoading(isLoading) {
        elements.submitBtn.disabled = isLoading;
        const btnText = elements.submitBtn.querySelector(".btn-text");
        const spinner = elements.submitBtn.querySelector(".spinner");

        if (isLoading) {
            btnText.textContent = "Analyzing Content...";
            spinner.style.display = "inline-block";
        } else {
            btnText.textContent = "Analyze Credibility";
            spinner.style.display = "none";
        }
    }

    function renderAnalysisResult(data) {
        // Toggle view from empty state to active
        elements.resultEmptyState.style.display = "none";
        elements.resultActiveContent.style.display = "flex";

        // 1. Verdict & Category
        elements.verdictCategory.textContent = data.prediction_label;
        elements.verdictTitle.textContent = data.verdict === "Real" ? "Likely Real News" : "Likely Misinformation";
        
        elements.verdictCategory.className = `verdict-label ${data.verdict_class}`;
        elements.verdictIconWrap.className = `verdict-icon-wrap ${data.verdict_class}`;

        if (data.verdict === "Real") {
            elements.verdictIcon.className = "fa-solid fa-shield-check";
        } else if (data.verdict === "Fake") {
            elements.verdictIcon.className = "fa-solid fa-triangle-exclamation";
        } else {
            elements.verdictIcon.className = "fa-solid fa-circle-question";
        }

        // 2. Score Circular Gauge (Circumference = 2 * PI * 42 ≈ 263.89)
        const circumference = 264;
        const score = data.credibility_score;
        elements.credibilityScoreVal.textContent = Math.round(score);

        const offset = circumference - (score / 100) * circumference;
        elements.gaugeFill.style.strokeDashoffset = offset;

        if (score >= 70) {
            elements.gaugeFill.style.stroke = "var(--success)";
        } else if (score >= 45) {
            elements.gaugeFill.style.stroke = "var(--warning)";
        } else {
            elements.gaugeFill.style.stroke = "var(--danger)";
        }

        // 3. Confidence & Risk Metrics
        elements.confidenceVal.textContent = `${data.confidence}%`;
        
        const riskScore = data.linguistics.stylistic_risk_score;
        const riskText = riskScore > 50 ? "High Risk" : riskScore > 20 ? "Moderate" : "Low";
        elements.riskScoreVal.textContent = `${riskText} (${riskScore}%)`;

        const attrCount = (data.linguistics.attribution_terms_detected || []).length;
        elements.attributionVal.textContent = attrCount > 0 ? `${attrCount} Sourcing Cue(s)` : "None Flagged";

        // 4. Probability Bar
        elements.probRealVal.textContent = `${data.probability_real}%`;
        elements.probFakeVal.textContent = `${data.probability_fake}%`;
        elements.probRealBar.style.width = `${data.probability_real}%`;
        elements.probFakeBar.style.width = `${data.probability_fake}%`;

        // 5. Salient Keywords Attribution
        renderKeywords(elements.realTagsContainer, data.attributions.real_supporting_terms, "real");
        renderKeywords(elements.fakeTagsContainer, data.attributions.fake_supporting_terms, "fake");

        // 6. Linguistic Explanations
        elements.explanationList.innerHTML = "";
        data.explanation_points.forEach(point => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-angle-right text-muted"></i> <span>${point}</span>`;
            elements.explanationList.appendChild(li);
        });

        // Scroll smoothly to results on mobile devices
        if (window.innerWidth < 1024) {
            elements.resultActiveContent.scrollIntoView({ behavior: "smooth" });
        }
    }

    function renderKeywords(container, terms, type) {
        container.innerHTML = "";
        if (!terms || terms.length === 0) {
            container.innerHTML = `<span class="text-muted" style="font-size:0.75rem;">No salient ${type} terms</span>`;
            return;
        }

        terms.forEach(t => {
            const span = document.createElement("span");
            span.className = `kw-tag ${type}`;
            span.innerHTML = `${escapeHtml(t.term)}`;
            container.appendChild(span);
        });
    }

    function copyAnalysisSummary() {
        if (!state.lastAnalysis) return;
        const a = state.lastAnalysis;
        const summary = `TruthLens AI Credibility Report:
Verdict: ${a.verdict} (${a.prediction_label})
Credibility Score: ${a.credibility_score}/100
Model Confidence: ${a.confidence}%
Word Count: ${a.word_count}
Key Explanation: ${a.explanation_points.join("; ")}
Disclaimer: Predictions are algorithmic estimates, not proof of truth.`;

        navigator.clipboard.writeText(summary)
            .then(() => showToast("Analysis summary copied to clipboard!", "success"))
            .catch(() => showToast("Failed to copy to clipboard.", "danger"));
    }

    /* -------------------------------------------------------------
       6. Dashboard & Analytics
       ------------------------------------------------------------- */
    async function loadDashboardStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.status === "success") {
                const s = data.data;
                elements.kpiTotal.textContent = s.total_analyses.toLocaleString();
                elements.kpiReal.textContent = s.real_count.toLocaleString();
                elements.kpiFake.textContent = s.fake_count.toLocaleString();
                elements.kpiAvgScore.textContent = `${s.avg_credibility}%`;

                if (window.dashboardCharts) {
                    window.dashboardCharts.updateData(s);
                }
            }
        } catch (err) {
            console.error("Failed to fetch dashboard stats:", err);
            showToast("Failed to refresh analytics dashboard.", "danger");
        }
    }

    /* -------------------------------------------------------------
       7. History Log Management
       ------------------------------------------------------------- */
    function initHistory() {
        let debounceTimer = null;
        elements.historySearchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                state.searchQuery = e.target.value;
                state.currentPage = 1;
                loadHistory();
            }, 300);
        });

        elements.filterBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                elements.filterBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                state.currentFilter = btn.getAttribute("data-filter");
                state.currentPage = 1;
                loadHistory();
            });
        });

        elements.exportCsvBtn.addEventListener("click", exportHistoryCsv);
        elements.exportJsonBtn.addEventListener("click", exportHistoryJson);
        elements.clearAllHistoryBtn.addEventListener("click", clearAllHistory);

        // Modal
        elements.modalCloseBtn.addEventListener("click", closeModal);
        elements.modalCloseFooterBtn.addEventListener("click", closeModal);
        elements.detailModal.addEventListener("click", (e) => {
            if (e.target === elements.detailModal) closeModal();
        });
    }

    async function loadHistory() {
        try {
            const query = new URLSearchParams({
                page: state.currentPage,
                per_page: state.perPage,
                filter: state.currentFilter,
                search: state.searchQuery
            });

            const res = await fetch(`/api/history?${query.toString()}`);
            const data = await res.json();

            if (data.status === "success") {
                renderHistoryTable(data.data);
            }
        } catch (err) {
            console.error("Failed to load history:", err);
            showToast("Failed to load history records.", "danger");
        }
    }

    function renderHistoryTable(historyData) {
        const items = historyData.items || [];
        elements.historyTableBody.innerHTML = "";

        if (items.length === 0) {
            elements.historyTableBody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align:center; padding: 2.5rem; color: var(--text-muted);">
                        <i class="fa-solid fa-inbox" style="font-size: 2rem; margin-bottom: 0.5rem; display: block;"></i>
                        No analysis records found matching your filters.
                    </td>
                </tr>
            `;
            elements.paginationInfo.textContent = "Showing 0 entries";
            elements.paginationBtns.innerHTML = "";
            return;
        }

        items.forEach(row => {
            const tr = document.createElement("tr");
            
            const badgeClass = row.verdict === "Real" ? "badge-success" : row.verdict === "Fake" ? "badge-danger" : "badge-warning";
            const badgeIcon = row.verdict === "Real" ? "fa-circle-check" : "fa-triangle-exclamation";
            
            tr.innerHTML = `
                <td style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">#${row.id}</td>
                <td class="headline-cell" title="${escapeHtml(row.headline)}">${escapeHtml(row.headline)}</td>
                <td><span class="badge ${badgeClass}"><i class="fa-solid ${badgeIcon}"></i> ${row.verdict}</span></td>
                <td><span class="score-badge">${row.credibility_score}%</span></td>
                <td><span style="font-family: var(--font-mono);">${row.confidence}%</span></td>
                <td>${row.word_count || 0}</td>
                <td style="font-size: 0.76rem; color: var(--text-muted);">${formatTimestamp(row.created_at)}</td>
                <td>
                    <div class="action-btns">
                        <button class="action-btn" title="Share Analysis" onclick="window.shareRecordById(${row.id})">
                            <i class="fa-solid fa-share-nodes"></i>
                        </button>
                        <button class="action-btn" title="View Details" onclick="window.viewRecordDetail(${row.id})">
                            <i class="fa-solid fa-eye"></i>
                        </button>
                        <button class="action-btn delete" title="Delete Entry" onclick="window.deleteRecord(${row.id})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            elements.historyTableBody.appendChild(tr);
        });

        // Pagination controls
        const start = ((historyData.page - 1) * historyData.per_page) + 1;
        const end = Math.min(start + items.length - 1, historyData.total);
        elements.paginationInfo.textContent = `Showing ${start}-${end} of ${historyData.total} entries`;

        renderPaginationButtons(historyData.total_pages, historyData.page);
    }

    function renderPaginationButtons(totalPages, currentPage) {
        elements.paginationBtns.innerHTML = "";
        if (totalPages <= 1) return;

        // Prev
        const prev = document.createElement("button");
        prev.className = "page-btn";
        prev.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
        prev.disabled = currentPage === 1;
        prev.addEventListener("click", () => {
            state.currentPage = currentPage - 1;
            loadHistory();
        });
        elements.paginationBtns.appendChild(prev);

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                const btn = document.createElement("button");
                btn.className = `page-btn ${i === currentPage ? "active" : ""}`;
                btn.textContent = i;
                btn.addEventListener("click", () => {
                    state.currentPage = i;
                    loadHistory();
                });
                elements.paginationBtns.appendChild(btn);
            }
        }

        // Next
        const next = document.createElement("button");
        next.className = "page-btn";
        next.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
        next.disabled = currentPage === totalPages;
        next.addEventListener("click", () => {
            state.currentPage = currentPage + 1;
            loadHistory();
        });
        elements.paginationBtns.appendChild(next);
    }

    window.viewRecordDetail = async function(id) {
        try {
            const res = await fetch(`/api/history/${id}`);
            const data = await res.json();
            if (data.status === "success" && data.data) {
                openDetailModal(data.data);
            }
        } catch (err) {
            showToast("Failed to fetch record details.", "danger");
        }
    };

    window.deleteRecord = async function(id) {
        if (!confirm(`Are you sure you want to delete analysis record #${id}?`)) return;

        try {
            const res = await fetch(`/api/history/${id}`, { method: "DELETE" });
            const data = await res.json();
            if (data.status === "success") {
                showToast(`Record #${id} deleted.`, "info");
                loadHistory();
                loadDashboardStats();
            }
        } catch (err) {
            showToast("Failed to delete record.", "danger");
        }
    };

    async function clearAllHistory() {
        if (!confirm("Are you sure you want to delete ALL analysis history records? This cannot be undone.")) return;

        try {
            const res = await fetch("/api/history", { method: "DELETE" });
            const data = await res.json();
            if (data.status === "success") {
                showToast("All history records cleared.", "info");
                loadHistory();
                loadDashboardStats();
            }
        } catch (err) {
            showToast("Failed to clear history.", "danger");
        }
    }

    async function exportHistoryCsv() {
        try {
            const res = await fetch("/api/history?page=1&per_page=1000");
            const data = await res.json();
            if (!data.data || !data.data.items) return;

            const items = data.data.items;
            const headers = ["ID", "Headline", "Verdict", "Prediction Label", "Credibility Score", "Confidence", "Word Count", "Risk Score", "Timestamp"];
            const rows = items.map(i => [
                i.id,
                `"${(i.headline || '').replace(/"/g, '""')}"`,
                i.verdict,
                `"${i.prediction_label}"`,
                i.credibility_score,
                i.confidence,
                i.word_count,
                i.risk_score,
                `"${i.created_at}"`
            ]);

            const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `truthlens_history_${new Date().toISOString().slice(0, 10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showToast("CSV history exported successfully!", "success");
        } catch (err) {
            showToast("Export failed.", "danger");
        }
    }

    async function exportHistoryJson() {
        try {
            const res = await fetch("/api/history?page=1&per_page=1000");
            const data = await res.json();
            const jsonStr = JSON.stringify(data.data.items || [], null, 2);
            const blob = new Blob([jsonStr], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `truthlens_history_${new Date().toISOString().slice(0, 10)}.json`;
            link.click();
            URL.revokeObjectURL(url);
            showToast("JSON history exported successfully!", "success");
        } catch (err) {
            showToast("Export failed.", "danger");
        }
    }

    function openDetailModal(rec) {
        state.activeDetailRecord = rec;
        elements.modalTitle.textContent = `Analysis Record #${rec.id}`;
        
        const badgeClass = rec.verdict === "Real" ? "badge-success" : rec.verdict === "Fake" ? "badge-danger" : "badge-warning";
        
        elements.modalBody.innerHTML = `
            <div>
                <h4 style="font-size: 1.1rem; margin-bottom: 0.4rem;">${escapeHtml(rec.headline)}</h4>
                <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 1rem;">
                    <span class="badge ${badgeClass}">${rec.verdict}</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">&bull;</span>
                    <span style="font-size: 0.82rem; color: var(--text-secondary);">${rec.prediction_label}</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted);">&bull;</span>
                    <span style="font-size: 0.82rem; font-family: var(--font-mono);">${formatTimestamp(rec.created_at)}</span>
                </div>
            </div>

            <div class="metrics-row">
                <div class="metric-pill">
                    <span class="metric-name">Credibility Score</span>
                    <strong class="metric-value" style="color: ${rec.credibility_score >= 50 ? 'var(--success)' : 'var(--danger)'}">${rec.credibility_score}%</strong>
                </div>
                <div class="metric-pill">
                    <span class="metric-name">Confidence</span>
                    <strong class="metric-value">${rec.confidence}%</strong>
                </div>
                <div class="metric-pill">
                    <span class="metric-name">Word Count</span>
                    <strong class="metric-value">${rec.word_count || 0}</strong>
                </div>
            </div>

            ${rec.content ? `
                <div style="background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem;">
                    <h5 style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">Article Excerpt</h5>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); max-height: 150px; overflow-y: auto; line-height: 1.5;">${escapeHtml(rec.content)}</p>
                </div>
            ` : ''}

            <div style="background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem;">
                <h5 style="font-size: 0.78rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">AI Reasoning Points</h5>
                <ul class="explanation-list">
                    ${(rec.explanation || []).map(p => `<li><i class="fa-solid fa-angle-right text-muted"></i> <span>${escapeHtml(p)}</span></li>`).join('')}
                </ul>
            </div>
        `;

        elements.detailModal.classList.add("active");
    }

    function closeModal() {
        elements.detailModal.classList.remove("active");
    }

    /* -------------------------------------------------------------
       8. Methodology & Model Info
       ------------------------------------------------------------- */
    async function loadMethodologyData() {
        try {
            const res = await fetch("/api/model-info");
            const data = await res.json();
            if (data.status === "success" && data.model_info) {
                const info = data.model_info;
                if (elements.modelAccuracyVal) elements.modelAccuracyVal.textContent = `${info.accuracy}%`;
                if (elements.modelPrecisionVal) elements.modelPrecisionVal.textContent = `${info.precision}%`;
                if (elements.modelRecallVal) elements.modelRecallVal.textContent = `${info.recall}%`;
                if (elements.modelF1Val) elements.modelF1Val.textContent = `${info.f1_score}%`;

                if (info.confusion_matrix) {
                    const cm = info.confusion_matrix;
                    if (elements.cmTN) elements.cmTN.textContent = `${cm.true_negatives_fake} (TN)`;
                    if (elements.cmFP) elements.cmFP.textContent = `${cm.false_positives_real} (FP)`;
                    if (elements.cmFN) elements.cmFN.textContent = `${cm.false_negatives_fake} (FN)`;
                    if (elements.cmTP) elements.cmTP.textContent = `${cm.true_positives_real} (TP)`;
                }

                if (elements.metaVocabSize && info.vocabulary_size) {
                    elements.metaVocabSize.textContent = `${info.vocabulary_size.toLocaleString()} distinct terms`;
                }

                // Render top predictors
                if (elements.topRealVocabList && info.top_real_indicators) {
                    elements.topRealVocabList.innerHTML = info.top_real_indicators.slice(0, 10).map(item => `
                        <span class="vocab-pill kw-tag real">${escapeHtml(item.word)}</span>
                    `).join('');
                }

                if (elements.topFakeVocabList && info.top_fake_indicators) {
                    elements.topFakeVocabList.innerHTML = info.top_fake_indicators.slice(0, 10).map(item => `
                        <span class="vocab-pill kw-tag fake">${escapeHtml(item.word)}</span>
                    `).join('');
                }
            }
        } catch (err) {
            console.error("Failed to load model transparency data:", err);
        }
    }

    /* -------------------------------------------------------------
       9. Toast Notifications & Helpers
       ------------------------------------------------------------- */
    function showToast(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;

        const iconClass = type === "success" 
            ? "fa-circle-check text-success" 
            : type === "danger" 
            ? "fa-circle-xmark text-danger" 
            : type === "warning" 
            ? "fa-triangle-exclamation text-warning" 
            : "fa-circle-info";

        toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${escapeHtml(message)}</span>`;
        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(10px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3600);
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatTimestamp(ts) {
        if (!ts) return "";
        try {
            const date = new Date(ts);
            return isNaN(date.getTime()) ? ts : date.toLocaleString(undefined, { 
                month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" 
            });
        } catch {
            return ts;
        }
    }

    /* -------------------------------------------------------------
       10. Share Functionality & Routing
       ------------------------------------------------------------- */
    function initShareOptions() {
        if (elements.shareAnalysisBtn) {
            elements.shareAnalysisBtn.addEventListener("click", () => {
                if (state.lastAnalysis) {
                    openShareModal(state.lastAnalysis);
                } else {
                    showToast("No active analysis to share.", "warning");
                }
            });
        }

        if (elements.modalShareBtn) {
            elements.modalShareBtn.addEventListener("click", () => {
                if (state.activeDetailRecord) {
                    openShareModal(state.activeDetailRecord);
                }
            });
        }

        if (elements.shareModalCloseBtn) elements.shareModalCloseBtn.addEventListener("click", closeShareModal);
        if (elements.shareModalCloseFooterBtn) elements.shareModalCloseFooterBtn.addEventListener("click", closeShareModal);
        if (elements.shareModal) {
            elements.shareModal.addEventListener("click", (e) => {
                if (e.target === elements.shareModal) closeShareModal();
            });
        }

        if (elements.copyShareUrlBtn) {
            elements.copyShareUrlBtn.addEventListener("click", () => {
                const url = elements.shareUrlInput.value;
                if (!url) return;
                navigator.clipboard.writeText(url)
                    .then(() => showToast("Shareable link copied to clipboard!", "success"))
                    .catch(() => showToast("Failed to copy link.", "danger"));
            });
        }

        if (elements.copyReportTextBtn) {
            elements.copyReportTextBtn.addEventListener("click", () => {
                if (!state.activeShareRecord) return;
                const rec = state.activeShareRecord;
                const text = generateShareReportText(rec);
                navigator.clipboard.writeText(text)
                    .then(() => showToast("Formatted credibility report copied to clipboard!", "success"))
                    .catch(() => showToast("Failed to copy report text.", "danger"));
            });
        }

        // Native Web Share API
        if (elements.nativeShareBtn && navigator.share) {
            elements.nativeShareContainer.style.display = "block";
            elements.nativeShareBtn.addEventListener("click", async () => {
                if (!state.activeShareRecord) return;
                const rec = state.activeShareRecord;
                try {
                    await navigator.share({
                        title: `TruthLens AI: ${rec.verdict} (${rec.credibility_score}% Credibility)`,
                        text: `TruthLens AI evaluated: "${rec.headline}" — Verdict: ${rec.verdict} (${rec.credibility_score}/100)`,
                        url: elements.shareUrlInput.value
                    });
                    showToast("Shared successfully!", "success");
                } catch (err) {
                    if (err.name !== "AbortError") {
                        console.error("Native share error:", err);
                    }
                }
            });
        }
    }

    function generateShareReportText(rec) {
        const headline = rec.headline || "";
        const verdict = rec.verdict || "Unverified";
        const score = rec.credibility_score || 0;
        const confidence = rec.confidence || 0;
        const label = rec.prediction_label || "";
        const url = elements.shareUrlInput ? elements.shareUrlInput.value : window.location.href;
        
        return `🔍 TruthLens AI — News Credibility Report
📰 Headline: "${headline}"
⚖️ Verdict: ${verdict} (${label})
📊 Credibility Score: ${score}/100
🎯 Model Confidence: ${confidence}%
🔗 View Full Report: ${url}

⚠️ Disclaimer: TruthLens AI predictions are algorithmic estimates based on machine-learning text analysis, not definitive proof of truth or falsehood.`;
    }

    function openShareModal(rec) {
        state.activeShareRecord = rec;
        
        // Headline preview
        if (elements.shareHeadlinePreview) {
            elements.shareHeadlinePreview.textContent = rec.headline || "Analyzed Article";
        }
        
        // Verdict Badge
        if (elements.shareVerdictBadge) {
            const badgeClass = rec.verdict === "Real" ? "badge-success" : rec.verdict === "Fake" ? "badge-danger" : "badge-warning";
            const badgeIcon = rec.verdict === "Real" ? "fa-circle-check" : "fa-triangle-exclamation";
            elements.shareVerdictBadge.className = `badge ${badgeClass}`;
            elements.shareVerdictBadge.innerHTML = `<i class="fa-solid ${badgeIcon}"></i> ${rec.verdict || "Analyzed"}`;
        }
        
        // Score Chip
        if (elements.shareScoreChip) {
            elements.shareScoreChip.textContent = `${rec.credibility_score}% Credibility`;
        }
        
        // Construct Shareable Link
        const baseOrigin = window.location.origin + window.location.pathname;
        const recordId = rec.id || "";
        const shareUrl = recordId ? `${baseOrigin}?id=${recordId}` : window.location.href;
        if (elements.shareUrlInput) {
            elements.shareUrlInput.value = shareUrl;
        }

        // Social Intent URLs
        const headlineSnippet = (rec.headline || "").slice(0, 85);
        const tweetText = `🔍 TruthLens AI evaluated "${headlineSnippet}..." as ${rec.verdict} (${rec.credibility_score}/100 Credibility). Report:`;
        if (elements.shareTwitterBtn) {
            elements.shareTwitterBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}&url=${encodeURIComponent(shareUrl)}`;
        }

        const whatsappText = `🔍 *TruthLens AI Credibility Report*\n📰 *Headline:* ${rec.headline}\n⚖️ *Verdict:* ${rec.verdict} (${rec.credibility_score}/100 Credibility)\n🔗 *Inspect Report:* ${shareUrl}`;
        if (elements.shareWhatsappBtn) {
            elements.shareWhatsappBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(whatsappText)}`;
        }

        if (elements.shareLinkedinBtn) {
            elements.shareLinkedinBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
        }

        const telegramText = `TruthLens AI Credibility Report for: "${headlineSnippet}" - Verdict: ${rec.verdict} (${rec.credibility_score}/100)`;
        if (elements.shareTelegramBtn) {
            elements.shareTelegramBtn.href = `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(telegramText)}`;
        }

        const emailSubject = `TruthLens AI Credibility Analysis: ${headlineSnippet}`;
        const emailBody = generateShareReportText(rec);
        if (elements.shareEmailBtn) {
            elements.shareEmailBtn.href = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`;
        }

        if (elements.shareModal) {
            elements.shareModal.classList.add("active");
        }
    }

    function closeShareModal() {
        if (elements.shareModal) elements.shareModal.classList.remove("active");
    }

    window.shareRecordById = async function(id) {
        try {
            const res = await fetch(`/api/history/${id}`);
            const data = await res.json();
            if (data.status === "success" && data.data) {
                openShareModal(data.data);
            }
        } catch (err) {
            showToast("Failed to fetch record for sharing.", "danger");
        }
    };

    async function checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const recordId = urlParams.get("id");
        if (recordId) {
            try {
                const res = await fetch(`/api/history/${recordId}`);
                const data = await res.json();
                if (data.status === "success" && data.data) {
                    const rec = data.data;
                    elements.headlineInput.value = rec.headline || "";
                    elements.contentInput.value = rec.content || "";
                    updateHeadlineCount();
                    updateContentCount();
                    
                    const analysisData = {
                        id: rec.id,
                        headline: rec.headline,
                        headline_preview: rec.headline.slice(0, 120),
                        verdict: rec.verdict,
                        verdict_class: rec.verdict === "Real" ? "credible" : rec.verdict === "Fake" ? "fake" : "warning",
                        prediction_label: rec.prediction_label,
                        credibility_score: rec.credibility_score,
                        confidence: rec.confidence,
                        probability_real: rec.verdict === "Real" ? rec.confidence : (100 - rec.confidence),
                        probability_fake: rec.verdict === "Fake" ? rec.confidence : (100 - rec.confidence),
                        word_count: rec.word_count,
                        attributions: {
                            real_supporting_terms: rec.top_real_terms || [],
                            fake_supporting_terms: rec.top_fake_terms || []
                        },
                        linguistics: rec.linguistics || { stylistic_risk_score: rec.risk_score || 0 },
                        explanation_points: rec.explanation || []
                    };
                    state.lastAnalysis = analysisData;
                    renderAnalysisResult(analysisData);
                    switchTab("tab-analyze");
                    showToast(`Loaded shared credibility report #${recordId}`, "info");
                }
            } catch (err) {
                console.error("Failed to load shared report:", err);
            }
        }
    }

    /* -------------------------------------------------------------
       11. App Initialization
       ------------------------------------------------------------- */
    initTheme();
    initTabs();
    initCounters();
    initAnalysisForm();
    initHistory();
    initShareOptions();
    loadSamples();
    loadMethodologyData();
    checkUrlParams();

    // Initialize Chart.js
    if (window.dashboardCharts) {
        window.dashboardCharts.initCharts();
    }

    if (elements.refreshStatsBtn) {
        elements.refreshStatsBtn.addEventListener("click", () => {
            loadDashboardStats();
            showToast("Analytics refreshed.", "info");
        });
    }
});
