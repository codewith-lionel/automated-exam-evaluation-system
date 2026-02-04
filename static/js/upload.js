// File Upload - Drag-drop, validation, progress

document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname === "/upload") {
    initUpload();
  }
});

function initUpload() {
  const uploadArea = document.getElementById("uploadArea");
  const fileInput = document.getElementById("fileInput");
  const uploadForm = document.getElementById("uploadForm");
  const fileList = document.getElementById("fileList");
  const uploadButton = document.getElementById("uploadButton");

  let selectedFiles = [];
  let currentEvaluationData = null; // Store evaluation data globally

  // Click to upload
  if (uploadArea) {
    uploadArea.addEventListener("click", () => {
      fileInput.click();
    });
  }

  // File input change
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      handleFiles(e.target.files);
    });
  }

  // Drag and drop events
  if (uploadArea) {
    uploadArea.addEventListener("dragover", (e) => {
      e.preventDefault();
      uploadArea.classList.add("drag-over");
    });

    uploadArea.addEventListener("dragleave", () => {
      uploadArea.classList.remove("drag-over");
    });

    uploadArea.addEventListener("drop", (e) => {
      e.preventDefault();
      uploadArea.classList.remove("drag-over");
      handleFiles(e.dataTransfer.files);
    });
  }

  // Handle files
  function handleFiles(files) {
    const validFiles = Array.from(files).filter((file) => validateFile(file));
    selectedFiles = [...selectedFiles, ...validFiles];
    displayFileList();
  }

  // Validate file
  function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
      "application/pdf",
      "image/jpeg",
      "image/jpg",
      "image/png",
    ];

    if (!allowedTypes.includes(file.type)) {
      toast.error(
        `${file.name}: Invalid file type. Only PDF and images are allowed.`,
      );
      return false;
    }

    if (file.size > maxSize) {
      toast.error(`${file.name}: File too large. Maximum size is 10MB.`);
      return false;
    }

    return true;
  }

  // Display file list
  function displayFileList() {
    if (!fileList) return;

    if (selectedFiles.length === 0) {
      fileList.innerHTML = "";
      if (uploadButton) uploadButton.disabled = true;
      return;
    }

    if (uploadButton) uploadButton.disabled = false;

    fileList.innerHTML = `
            <h3>Selected Files (${selectedFiles.length})</h3>
            <ul class="file-list">
                ${selectedFiles
                  .map(
                    (file, index) => `
                    <li class="file-item">
                        <div class="file-icon">📄</div>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatFileSize(file.size)}</div>
                        </div>
                        <button class="file-remove" onclick="removeFile(${index})" aria-label="Remove file">
                            <i class="fas fa-times"></i>
                        </button>
                    </li>
                `,
                  )
                  .join("")}
            </ul>
        `;
  }

  // Remove file
  window.removeFile = function (index) {
    selectedFiles.splice(index, 1);
    displayFileList();
  };

  // Form submission
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      if (selectedFiles.length === 0) {
        toast.warning("Please select at least one file");
        return;
      }

      if (!validation.validateForm(uploadForm)) {
        return;
      }

      const formData = new FormData();

      // Add first file (backend expects single file with key 'file')
      if (selectedFiles.length > 0) {
        formData.append("file", selectedFiles[0]);
      }

      // Add form fields
      const examName = document.getElementById("examName")?.value;
      const examDate = document.getElementById("examDate")?.value;
      const subject = document.getElementById("subject")?.value;
      const examType = document.getElementById("examType")?.value || "Test";
      const mode = document.getElementById("mode")?.value || "offline";
      const totalMarks = document.getElementById("totalMarks")?.value;
      const answerKey = document.getElementById("answerKey")?.value;

      if (examName) formData.append("exam_name", examName);
      if (examDate) formData.append("exam_date", examDate);
      if (subject) formData.append("subject", subject || "General");
      if (examType) formData.append("exam_type", examType);
      if (mode) formData.append("mode", mode);
      if (totalMarks) formData.append("total_marks", totalMarks || 100);
      if (answerKey) formData.append("answer_key", answerKey);

      try {
        // Disable submit button
        if (uploadButton) {
          uploadButton.disabled = true;
          uploadButton.innerHTML =
            '<span class="spinner"></span> Uploading & Extracting...';
        }

        // Show progress
        showUploadProgress();

        // Upload files
        const response = await uploadWithProgress(formData);
        hideUploadProgress();

        console.log("Upload response:", response);

        if (response.success) {
          const extractedText = response.extracted_text || "";
          
          if (extractedText && extractedText.trim()) {
            toast.success("Text extracted successfully!");
          } else {
            toast.warning("File uploaded but no text was extracted. Please check the image quality.");
          }

          // Store data for later evaluation
          currentEvaluationData = {
            evaluation_id: response.evaluation_id,
            ocr_text: extractedText,
            confidence: response.confidence || 0,
            answerKey: answerKey,
            totalMarks: totalMarks,
          };

          // Show preview section
          showOCRPreview(
            currentEvaluationData.ocr_text,
            currentEvaluationData.confidence,
          );

          // Update buttons
          if (uploadButton) {
            uploadButton.style.display = "none";
          }
          document.getElementById("evaluateButton").style.display =
            "inline-flex";
        } else {
          toast.error(response.message || "Upload failed");
          if (uploadButton) {
            uploadButton.disabled = false;
            uploadButton.innerHTML =
              '<i class="fas fa-upload"></i> Upload & Extract Text';
          }
        }
      } catch (error) {
        hideUploadProgress();
        toast.error("Upload failed. Please try again.");
        console.error("Upload error:", error);

        if (uploadButton) {
          uploadButton.disabled = false;
          uploadButton.innerHTML =
            '<i class="fas fa-upload"></i> Upload & Extract Text';
        }
      }
    });
  }

  // Upload with progress
  async function uploadWithProgress(formData) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          updateUploadProgress(percentComplete);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(error);
          }
        } else {
          reject(new Error("Upload failed"));
        }
      });

      xhr.addEventListener("error", () => {
        reject(new Error("Upload failed"));
      });

      xhr.open("POST", `${API_BASE_URL}/upload`);
      xhr.send(formData);
    });
  }

  // Show upload progress
  function showUploadProgress() {
    if (!fileList) return;

    fileList.innerHTML = `
            <div class="upload-progress-item">
                <div class="upload-progress-header">
                    <span class="upload-progress-name">Uploading files...</span>
                    <span class="upload-progress-percent" id="uploadPercent">0%</span>
                </div>
                <div class="progress">
                    <div class="progress-bar" id="uploadProgressBar" style="width: 0%"></div>
                </div>
            </div>
        `;
  }

  // Update upload progress
  function updateUploadProgress(percent) {
    const progressBar = document.getElementById("uploadProgressBar");
    const percentText = document.getElementById("uploadPercent");

    if (progressBar) {
      progressBar.style.width = `${percent}%`;
    }

    if (percentText) {
      percentText.textContent = `${Math.round(percent)}%`;
    }
  }

  // Hide upload progress
  function hideUploadProgress() {
    if (fileList) {
      fileList.innerHTML = "";
    }
  }

  // Parse questions for evaluation
  function parseQuestionsForEvaluation(answerKey, extractedText, totalMarks) {
    const questions = [];

    if (!answerKey || answerKey.trim() === "") {
      // If no answer key provided, create a simple question from extracted text
      if (extractedText && extractedText.trim() !== "") {
        questions.push({
          question_number: 1,
          question_text: "General Answer Evaluation",
          model_answer:
            "Comprehensive answer covering key concepts and topics.",
          student_answer: extractedText,
          max_marks: parseInt(totalMarks) || 100,
        });
      }
      return questions;
    }

    // Parse student answers from extracted text
    const studentAnswers = parseStudentAnswers(extractedText);

    // Try to parse structured answer key (JSON format)
    try {
      const parsed = JSON.parse(answerKey);
      if (parsed.questions && Array.isArray(parsed.questions)) {
        // Use model answers from JSON and student answers from extracted text
        return parsed.questions.map((q) => {
          const qNum = q.question_number;
          return {
            question_number: qNum,
            question_text: q.question || q.question_text || "",
            model_answer: q.model_answer || q.answer || "",
            student_answer: studentAnswers[qNum] || extractedText || "",
            max_marks: q.max_marks || totalMarks / parsed.questions.length,
          };
        });
      }
    } catch (e) {
      // Not JSON, treat as plain text
    }

    // Parse line-by-line format: "Q1: question text\nA1: answer text"
    const lines = answerKey.split("\n");
    let currentQuestion = null;

    for (let line of lines) {
      line = line.trim();
      if (line === "") continue;

      // Check for question pattern (Q1:, Question 1:, etc.)
      const qMatch = line.match(/^(?:Q|Question)\s*(\d+)\s*[:.-]\s*(.+)$/i);
      if (qMatch) {
        if (currentQuestion) {
          questions.push(currentQuestion);
        }
        const qNum = parseInt(qMatch[1]);
        currentQuestion = {
          question_number: qNum,
          question_text: qMatch[2],
          model_answer: "",
          student_answer: studentAnswers[qNum] || extractedText || "",
          max_marks: totalMarks / 5, // Default to 5 questions
        };
        continue;
      }

      // Check for answer pattern (A1:, Answer 1:, etc.)
      const aMatch = line.match(/^(?:A|Answer)\s*(\d+)\s*[:.-]\s*(.+)$/i);
      if (aMatch && currentQuestion) {
        currentQuestion.model_answer = aMatch[2];
        continue;
      }

      // Otherwise, append to current question's model answer
      if (currentQuestion && currentQuestion.model_answer) {
        currentQuestion.model_answer += " " + line;
      } else if (currentQuestion) {
        currentQuestion.model_answer = line;
      }
    }

    if (currentQuestion) {
      questions.push(currentQuestion);
    }

    // If no structured format found, create single question
    if (questions.length === 0 && answerKey.trim() !== "") {
      questions.push({
        question_number: 1,
        question_text: "Answer Evaluation",
        model_answer: answerKey,
        student_answer: extractedText || "",
        max_marks: parseInt(totalMarks) || 100,
      });
    }

    return questions;
  }

  // Parse student answers from extracted text
  function parseStudentAnswers(extractedText) {
    const answers = {};

    if (!extractedText || extractedText.trim() === "") {
      return answers;
    }

    // Try to parse answers in format: "Q1: answer\nQ2: answer" or "1. answer\n2. answer"
    const lines = extractedText.split("\n");
    let currentQNum = null;
    let currentAnswer = "";

    for (let line of lines) {
      line = line.trim();

      // Check for question number patterns
      const patterns = [
        /^(?:Q|Question|Ans|Answer)\s*(\d+)\s*[:.-]\s*(.*)$/i, // Q1: answer or Answer 1: text
        /^(\d+)\s*[:.)]\s*(.*)$/, // 1. answer or 1) answer
      ];

      let matched = false;
      for (let pattern of patterns) {
        const match = line.match(pattern);
        if (match) {
          // Save previous question if exists
          if (currentQNum !== null && currentAnswer.trim()) {
            answers[currentQNum] = currentAnswer.trim();
          }

          // Start new question
          currentQNum = parseInt(match[1]);
          currentAnswer = match[2] || "";
          matched = true;
          break;
        }
      }

      // If no pattern matched and we have a current question, append to it
      if (!matched && currentQNum !== null && line) {
        currentAnswer += " " + line;
      }
    }

    // Save the last question
    if (currentQNum !== null && currentAnswer.trim()) {
      answers[currentQNum] = currentAnswer.trim();
    }

    return answers;
  }

  // Show OCR Preview
  function showOCRPreview(text, confidence) {
    const previewSection = document.getElementById("ocrPreviewSection");
    const extractedTextArea = document.getElementById("extractedText");
    const charCount = document.getElementById("charCount");
    const ocrConfidence = document.getElementById("ocrConfidence");

    if (!previewSection || !extractedTextArea) return;

    extractedTextArea.value = text;
    charCount.textContent = `${text.length} characters`;

    if (confidence) {
      const confidenceClass =
        confidence > 70 ? "success" : confidence > 40 ? "warning" : "danger";
      ocrConfidence.innerHTML = `<span class="badge badge-${confidenceClass}">OCR Confidence: ${confidence.toFixed(1)}%</span>`;
    }

    previewSection.style.display = "block";
    previewSection.scrollIntoView({ behavior: "smooth", block: "start" });

    // Update character count on input
    extractedTextArea.addEventListener("input", () => {
      charCount.textContent = `${extractedTextArea.value.length} characters`;
    });
  }

  // Evaluate button click handler
  const evaluateButton = document.getElementById("evaluateButton");
  if (evaluateButton) {
    evaluateButton.addEventListener("click", async () => {
      if (!currentEvaluationData) {
        toast.error("No evaluation data available");
        return;
      }

      evaluateButton.disabled = true;
      evaluateButton.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Evaluating...';

      try {
        // Get the (possibly edited) extracted text
        const extractedText = document.getElementById("extractedText").value;

        // Parse questions for evaluation
        const questions = parseQuestionsForEvaluation(
          currentEvaluationData.answerKey,
          extractedText,
          currentEvaluationData.totalMarks,
        );

        if (questions.length === 0) {
          toast.warning("No questions found. Please provide model answers.");
          evaluateButton.disabled = false;
          evaluateButton.innerHTML =
            '<i class="fas fa-check"></i> Proceed to Evaluation';
          return;
        }

        // Start evaluation
        loader.show("Evaluating answers...");

        const evalResponse = await api.post("/evaluate", {
          evaluation_id: currentEvaluationData.evaluation_id,
          questions: questions,
        });

        loader.hide();

        if (evalResponse.success) {
          toast.success("Evaluation completed successfully!");

          // Clear form
          selectedFiles = [];
          uploadForm.reset();
          fileList.innerHTML = "";

          // Reset current data
          const evalId =
            evalResponse.evaluation_id || currentEvaluationData.evaluation_id;
          currentEvaluationData = null;

          // Redirect to results
          setTimeout(() => {
            window.location.href = `/results/${evalId}`;
          }, 1500);
        } else {
          toast.error(evalResponse.message || "Evaluation failed");
          evaluateButton.disabled = false;
          evaluateButton.innerHTML =
            '<i class="fas fa-check"></i> Proceed to Evaluation';
        }
      } catch (error) {
        loader.hide();
        toast.error("Evaluation failed. Please try again.");
        console.error("Evaluation error:", error);
        evaluateButton.disabled = false;
        evaluateButton.innerHTML =
          '<i class="fas fa-check"></i> Proceed to Evaluation';
      }
    });
  }
}

// Batch upload handler
async function batchUpload(files) {
  const results = [];

  for (let i = 0; i < files.length; i++) {
    try {
      loader.show(`Processing file ${i + 1} of ${files.length}...`);

      const formData = new FormData();
      formData.append("file", files[i]);

      const response = await api.post("/evaluate/upload", formData);
      results.push(response);
    } catch (error) {
      console.error(`Error uploading file ${i + 1}:`, error);
      results.push({
        success: false,
        filename: files[i].name,
        error: error.message,
      });
    }
  }

  loader.hide();
  return results;
}
