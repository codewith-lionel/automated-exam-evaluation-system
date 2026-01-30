// Results - Listing and detail view with Chart.js

document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname === "/results") {
    initResultsList();
  } else if (window.location.pathname.startsWith("/results/")) {
    initResultDetail();
  }
});

// Results List Page
async function initResultsList() {
  try {
    loader.show("Loading results...");

    const response = await api.get("/results");

    if (response.success) {
      renderResults(response.results);
    }

    loader.hide();
  } catch (error) {
    loader.hide();
    toast.error("Failed to load results");
    console.error("Results error:", error);
  }

  // Setup filters
  setupFilters();
}

function renderResults(results) {
  const resultsGrid = document.getElementById("resultsGrid");
  if (!resultsGrid) return;

  if (!results || results.length === 0) {
    resultsGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-title">No results found</div>
                <div class="empty-state-text">Upload exam papers to see evaluation results here</div>
                <a href="/upload" class="btn btn-primary mt-lg">
                    <i class="fas fa-upload"></i> Upload Papers
                </a>
            </div>
        `;
    return;
  }

  resultsGrid.innerHTML = results
    .map((result) => {
      const scoreClass = getScoreClass(result.score);

      return `
            <div class="result-card">
                <div class="result-card-header" onclick="viewResult('${result.id}')">
                    <div>
                        <div class="result-card-title">${result.student_name || "Unknown Student"}</div>
                        <div class="result-card-meta">
                            ${result.exam_name || "Exam"} • ${formatDate(result.date)}
                        </div>
                    </div>
                    <div class="result-score ${scoreClass}">
                        ${result.score}%
                    </div>
                </div>
                <div class="result-card-body" onclick="viewResult('${result.id}')">
                    <div class="result-stats">
                        <div class="result-stat">
                            <div class="result-stat-value text-success">${result.correct || 0}</div>
                            <div class="result-stat-label">Correct</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-value text-warning">${result.partial || 0}</div>
                            <div class="result-stat-label">Partial</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-value text-danger">${result.incorrect || 0}</div>
                            <div class="result-stat-label">Incorrect</div>
                        </div>
                        <div class="result-stat">
                            <div class="result-stat-value">${result.total_questions || 0}</div>
                            <div class="result-stat-label">Total</div>
                        </div>
                    </div>
                </div>
                <div class="result-card-footer">
                    <span class="badge badge-${result.status === "completed" ? "success" : "warning"}">
                        ${result.status}
                    </span>
                    <span class="text-secondary" style="font-size: 0.875rem;">
                        ${timeAgo(result.date)}
                    </span>
                    <button class="btn btn-ghost btn-sm" onclick="event.stopPropagation(); deleteResultFromList('${result.id}')" style="margin-left: auto;" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    })
    .join("");
}

function getScoreClass(score) {
  if (score >= 90) return "excellent";
  if (score >= 75) return "good";
  if (score >= 60) return "average";
  return "poor";
}

function setupFilters() {
  const searchInput = document.getElementById("searchResults");
  const filterStatus = document.getElementById("filterStatus");
  const filterSubject = document.getElementById("filterSubject");
  const filterDate = document.getElementById("filterDate");

  if (searchInput) {
    searchInput.addEventListener(
      "input",
      debounce(() => {
        applyFilters();
      }, 300),
    );
  }

  if (filterStatus) {
    filterStatus.addEventListener("change", applyFilters);
  }

  if (filterSubject) {
    filterSubject.addEventListener("change", applyFilters);
  }

  if (filterDate) {
    filterDate.addEventListener("change", applyFilters);
  }
}

async function applyFilters() {
  const search = document.getElementById("searchResults")?.value || "";
  const status = document.getElementById("filterStatus")?.value || "";
  const subject = document.getElementById("filterSubject")?.value || "";
  const date = document.getElementById("filterDate")?.value || "";

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);
  if (subject) params.append("subject", subject);
  if (date) params.append("date", date);

  try {
    const response = await api.get(`/evaluate?${params.toString()}`);

    if (response.success) {
      renderResults(response.results);
    }
  } catch (error) {
    toast.error("Failed to apply filters");
    console.error("Filter error:", error);
  }
}

function viewResult(id) {
  window.location.href = `/results/${id}`;
}

// Result Detail Page
async function initResultDetail() {
  let evaluation_id;
  if (typeof window.result_id !== "undefined") {
    evaluation_id = window.result_id;
  } else {
    const pathParts = window.location.pathname.split("/");
    evaluation_id = pathParts[pathParts.length - 1];
  }

  try {
    loader.show("Loading result details...");

    const response = await api.get(`/results/${evaluation_id}`);

    if (response.success && response.result) {
      // Transform API response to match expected format
      const result = response.result;
      const questions = result.questions || [];

      // Calculate counts
      const totalQuestions = questions.length;
      const correct = questions.filter(
        (q) => q.obtained_marks === q.max_marks,
      ).length;
      const incorrect = questions.filter((q) => q.obtained_marks === 0).length;
      const partial = totalQuestions - correct - incorrect;

      // Create transformed result object
      const transformedResult = {
        id: result.id,
        score: result.percentage,
        total_questions: totalQuestions,
        correct: correct,
        incorrect: incorrect,
        partial: partial,
        date: result.created_at,
        student_name: result.username,
        exam_name: `${result.subject} - ${result.exam_type}`,
        subject: result.subject,
        exam_type: result.exam_type,
        total_marks: result.total_marks,
        obtained_marks: result.obtained_marks,
        status: result.status,
      };

      renderResultDetail(transformedResult);
      renderAnswerDetails(questions);
      renderResultCharts(transformedResult, questions);
    }

    loader.hide();
  } catch (error) {
    loader.hide();
    toast.error("Failed to load result details");
    console.error("Result detail error:", error);
  }
}

function renderResultDetail(result) {
  // Update page title
  const titleEl = document.getElementById("resultTitle");
  if (titleEl) {
    titleEl.textContent = result.exam_name || "Evaluation Result";
  }

  // Update evaluation date in header
  const dateEl = document.getElementById("evaluationDate");
  if (dateEl) {
    dateEl.textContent = formatDate(result.date);
  }

  // Update meta information
  const metaContainer = document.getElementById("resultMeta");
  if (metaContainer) {
    metaContainer.innerHTML = `
            <div class="result-detail-meta-item">
                <div class="result-detail-meta-label">Score</div>
                <div class="result-detail-meta-value text-${getScoreClass(result.score)}">
                    ${result.score}%
                </div>
            </div>
            <div class="result-detail-meta-item">
                <div class="result-detail-meta-label">Total Questions</div>
                <div class="result-detail-meta-value">${result.total_questions}</div>
            </div>
            <div class="result-detail-meta-item">
                <div class="result-detail-meta-label">Correct</div>
                <div class="result-detail-meta-value text-success">${result.correct}</div>
            </div>
            <div class="result-detail-meta-item">
                <div class="result-detail-meta-label">Incorrect</div>
                <div class="result-detail-meta-value text-danger">${result.incorrect}</div>
            </div>
        `;
  }

  // Update score breakdown
  const breakdownContainer = document.getElementById("scoreBreakdown");
  if (breakdownContainer) {
    breakdownContainer.innerHTML = `
            <div class="score-breakdown-item">
                <span>Correct Answers</span>
                <span class="text-success">${result.correct}</span>
            </div>
            <div class="score-breakdown-item">
                <span>Partial Credit</span>
                <span class="text-warning">${result.partial || 0}</span>
            </div>
            <div class="score-breakdown-item">
                <span>Incorrect Answers</span>
                <span class="text-danger">${result.incorrect}</span>
            </div>
            <div class="score-breakdown-item">
                <span>Total Score</span>
                <span class="text-primary">${result.score}%</span>
            </div>
        `;
  }
}

function renderAnswerDetails(questions) {
  const answersContainer = document.getElementById("answersList");
  if (!answersContainer) return;

  if (!questions || questions.length === 0) {
    answersContainer.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <div class="empty-state">
                        <div class="empty-state-icon">❓</div>
                        <div class="empty-state-title">No answers found</div>
                    </div>
                </div>
            </div>
        `;
    return;
  }

  answersContainer.innerHTML = questions
    .map((question) => {
      const percentage =
        question.max_marks > 0
          ? Math.round((question.obtained_marks / question.max_marks) * 100)
          : 0;

      const scoreClass =
        percentage >= 80
          ? "correct"
          : percentage >= 50
            ? "partial"
            : "incorrect";

      return `
            <div class="answer-item">
                <div class="answer-header">
                    <div class="answer-question">
                        <strong>Question ${question.question_number}:</strong> ${question.question_text || "N/A"}
                    </div>
                    <div class="answer-score-badge ${scoreClass}">
                        ${question.obtained_marks}/${question.max_marks} (${percentage}%)
                    </div>
                </div>
                <div class="answer-text">
                    <strong>Student Answer:</strong><br>
                    ${question.student_answer || "No answer provided"}
                </div>
                ${
                  question.model_answer
                    ? `
                    <div class="answer-text" style="border-left-color: var(--accent-green);">
                        <strong>Model Answer:</strong><br>
                        ${question.model_answer}
                    </div>
                `
                    : ""
                }
                ${
                  question.keywords_matched &&
                  question.keywords_matched.length > 0
                    ? `
                    <div class="answer-keywords">
                        <div><strong>✓ Keywords Matched:</strong></div>
                        <div class="keywords-list">
                            ${question.keywords_matched.map((kw) => `<span class="keyword-tag success">${kw}</span>`).join("")}
                        </div>
                    </div>
                `
                    : ""
                }
                ${
                  question.keywords_missed &&
                  question.keywords_missed.length > 0
                    ? `
                    <div class="answer-keywords">
                        <div><strong>✗ Keywords Missed:</strong></div>
                        <div class="keywords-list">
                            ${question.keywords_missed.map((kw) => `<span class="keyword-tag danger">${kw}</span>`).join("")}
                        </div>
                    </div>
                `
                    : ""
                }
            </div>
        `;
    })
    .join("");
}

function renderResultCharts(result) {
  // Score breakdown pie chart
  const scoreChartEl = document.getElementById("scoreChart");
  if (scoreChartEl) {
    const ctx = scoreChartEl.getContext("2d");

    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Correct", "Partial", "Incorrect"],
        datasets: [
          {
            data: [
              result.correct || 0,
              result.partial || 0,
              result.incorrect || 0,
            ],
            backgroundColor: [
              "rgba(63, 185, 80, 0.8)",
              "rgba(210, 153, 34, 0.8)",
              "rgba(248, 81, 73, 0.8)",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: getComputedStyle(document.documentElement)
                .getPropertyValue("--text-primary")
                .trim(),
              padding: 15,
            },
          },
        },
      },
    });
  }
}

// Export result as PDF
async function exportResult(resultId, format = "pdf") {
  try {
    loader.show("Exporting result...");

    const response = await api.get(
      `/evaluate/${resultId}/export?format=${format}`,
    );

    if (response.success) {
      downloadFile(response.url, `result-${resultId}.${format}`);
      toast.success("Result exported successfully");
    }

    loader.hide();
  } catch (error) {
    loader.hide();
    toast.error("Failed to export result");
    console.error("Export error:", error);
  }
}

// Delete result
async function deleteResult(resultId) {
  if (
    !confirm(
      "Are you sure you want to delete this result? This action cannot be undone.",
    )
  ) {
    return;
  }

  try {
    loader.show("Deleting result...");

    const response = await api.delete(`/results/${resultId}`);

    if (response.success) {
      toast.success("Result deleted successfully");
      setTimeout(() => {
        window.location.href = "/results";
      }, 1000);
    }

    loader.hide();
  } catch (error) {
    loader.hide();
    toast.error("Failed to delete result");
    console.error("Delete error:", error);
  }
}

// Delete result from list page (without navigation)
async function deleteResultFromList(resultId) {
  if (
    !confirm(
      "Are you sure you want to delete this result? This action cannot be undone.",
    )
  ) {
    return;
  }

  try {
    loader.show("Deleting result...");

    const response = await api.delete(`/results/${resultId}`);

    if (response.success) {
      toast.success("Result deleted successfully");
      // Reload the results list
      setTimeout(() => {
        initResultsList();
      }, 500);
    }

    loader.hide();
  } catch (error) {
    loader.hide();
    toast.error("Failed to delete result");
    console.error("Delete error:", error);
  }
}
