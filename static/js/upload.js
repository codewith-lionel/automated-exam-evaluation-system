// File Upload - Drag-drop, validation, progress

document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname === '/upload') {
        initUpload();
    }
});

function initUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const fileList = document.getElementById('fileList');
    const uploadButton = document.getElementById('uploadButton');
    
    let selectedFiles = [];

    // Click to upload
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
    }

    // Drag and drop events
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });
    }

    // Handle files
    function handleFiles(files) {
        const validFiles = Array.from(files).filter(file => validateFile(file));
        selectedFiles = [...selectedFiles, ...validFiles];
        displayFileList();
    }

    // Validate file
    function validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

        if (!allowedTypes.includes(file.type)) {
            toast.error(`${file.name}: Invalid file type. Only PDF and images are allowed.`);
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
            fileList.innerHTML = '';
            if (uploadButton) uploadButton.disabled = true;
            return;
        }

        if (uploadButton) uploadButton.disabled = false;

        fileList.innerHTML = `
            <h3>Selected Files (${selectedFiles.length})</h3>
            <ul class="file-list">
                ${selectedFiles.map((file, index) => `
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
                `).join('')}
            </ul>
        `;
    }

    // Remove file
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        displayFileList();
    };

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (selectedFiles.length === 0) {
                toast.warning('Please select at least one file');
                return;
            }

            if (!validation.validateForm(uploadForm)) {
                return;
            }

            const formData = new FormData();
            
            // Add files
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            // Add form fields
            const examName = document.getElementById('examName')?.value;
            const examDate = document.getElementById('examDate')?.value;
            const subject = document.getElementById('subject')?.value;
            const totalMarks = document.getElementById('totalMarks')?.value;
            const answerKey = document.getElementById('answerKey')?.value;

            if (examName) formData.append('exam_name', examName);
            if (examDate) formData.append('exam_date', examDate);
            if (subject) formData.append('subject', subject);
            if (totalMarks) formData.append('total_marks', totalMarks);
            if (answerKey) formData.append('answer_key', answerKey);

            try {
                // Disable submit button
                if (uploadButton) {
                    uploadButton.disabled = true;
                    uploadButton.innerHTML = '<span class="spinner"></span> Uploading...';
                }

                // Show progress
                showUploadProgress();

                // Upload files
                const response = await uploadWithProgress(formData);

                if (response.success) {
                    toast.success('Files uploaded successfully! Processing...');
                    
                    // Clear form
                    selectedFiles = [];
                    uploadForm.reset();
                    fileList.innerHTML = '';
                    
                    // Redirect to results after a delay
                    setTimeout(() => {
                        window.location.href = `/results/${response.evaluation_id}`;
                    }, 2000);
                } else {
                    toast.error(response.message || 'Upload failed');
                    if (uploadButton) {
                        uploadButton.disabled = false;
                        uploadButton.innerHTML = '<i class="fas fa-upload"></i> Upload & Evaluate';
                    }
                }
            } catch (error) {
                toast.error('Upload failed. Please try again.');
                console.error('Upload error:', error);
                
                if (uploadButton) {
                    uploadButton.disabled = false;
                    uploadButton.innerHTML = '<i class="fas fa-upload"></i> Upload & Evaluate';
                }
            }
        });
    }

    // Upload with progress
    async function uploadWithProgress(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    updateUploadProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(error);
                    }
                } else {
                    reject(new Error('Upload failed'));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed'));
            });

            xhr.open('POST', `${API_BASE_URL}/upload`);
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
        const progressBar = document.getElementById('uploadProgressBar');
        const percentText = document.getElementById('uploadPercent');

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        if (percentText) {
            percentText.textContent = `${Math.round(percent)}%`;
        }
    }
}

// Batch upload handler
async function batchUpload(files) {
    const results = [];
    
    for (let i = 0; i < files.length; i++) {
        try {
            loader.show(`Processing file ${i + 1} of ${files.length}...`);
            
            const formData = new FormData();
            formData.append('file', files[i]);
            
            const response = await api.post('/evaluate/upload', formData);
            results.push(response);
            
        } catch (error) {
            console.error(`Error uploading file ${i + 1}:`, error);
            results.push({ success: false, filename: files[i].name, error: error.message });
        }
    }
    
    loader.hide();
    return results;
}
