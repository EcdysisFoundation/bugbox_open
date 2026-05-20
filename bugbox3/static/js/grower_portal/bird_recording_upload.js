/**
 * Grower bird recording upload
 */

function parseJsonContext() {
    const el = document.getElementById('json_context');
    if (!el) {
        return {};
    }
    try {
        return JSON.parse(el.textContent);
    } catch (e) {
        console.error('json_context parse error', e);
        return {};
    }
}

function postJson(url, body, csrfToken) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        credentials: 'same-origin',
        body: JSON.stringify(body),
    }).then((res) => res.json().then((data) => ({ res, data })));
}

function formatBytes(bytes) {
    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function uploadFileToS3(url, file, contentType, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('PUT', url, true);
        xhr.setRequestHeader('Content-Type', contentType || 'application/octet-stream');

        xhr.upload.onprogress = (evt) => {
            if (evt.lengthComputable && onProgress) {
                onProgress(Math.round((evt.loaded / evt.total) * 100));
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve();
            } else {
                reject(new Error(`S3 upload failed (${xhr.status})`));
            }
        };

        xhr.onerror = () => reject(new Error('Network error during upload to storage.'));
        xhr.send(file);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const ctx = parseJsonContext();
    const csrfToken = ctx.csrfToken || '';

    const codeInput = document.getElementById('sample-code-input');
    const validateBtn = document.getElementById('validate-code-btn');
    const codeMessage = document.getElementById('code-validation-message');
    const uploadSection = document.getElementById('upload-section');
    const fileInput = document.getElementById('audio-file-input');
    const startBtn = document.getElementById('start-upload-btn');
    const progressWrap = document.getElementById('upload-progress-wrap');
    const progressBar = document.getElementById('upload-progress-bar');
    const resultEl = document.getElementById('upload-result');

    let validatedCode = null;
    let validatedMeta = null;

    function showResult(type, message) {
        if (!resultEl) {
            return;
        }
        resultEl.className = `alert alert-${type}`;
        resultEl.textContent = message;
        resultEl.classList.remove('d-none');
    }

    function setCodeMessage(text, isError) {
        if (!codeMessage) {
            return;
        }
        codeMessage.textContent = text;
        codeMessage.className = isError ? 'form-text mt-2 text-danger' : 'form-text mt-2 text-success';
    }

    validateBtn?.addEventListener('click', async () => {
        const code = (codeInput?.value || '').trim();
        if (!code) {
            setCodeMessage('Enter a sample code.', true);
            return;
        }

        validateBtn.disabled = true;
        setCodeMessage('Validating…', false);

        try {
            const { res, data } = await postJson(ctx.validateCodeUrl, { sample_code: code }, csrfToken);
            if (!data.ok) {
                setCodeMessage(data.error || 'Validation failed.', true);
                validatedCode = null;
                uploadSection?.classList.add('d-none');
                return;
            }
            validatedCode = data.sample_code;
            validatedMeta = data;
            const remaining = data.bytes_remaining ?? ctx.maxBytesPerCode;
            setCodeMessage(
                `Code accepted (year ${data.year_sampled}, ${data.project_type}). `
                + `${formatBytes(remaining)} remaining for this code. Select your audio file.`,
                false,
            );
            uploadSection?.classList.remove('d-none');
            if (fileInput) {
                fileInput.disabled = false;
            }
            if (startBtn) {
                startBtn.disabled = !fileInput?.files?.length;
            }
        } catch (e) {
            setCodeMessage('Could not validate code. Please try again.', true);
        } finally {
            validateBtn.disabled = false;
        }
    });

    fileInput?.addEventListener('change', () => {
        if (startBtn) {
            startBtn.disabled = !validatedCode || !fileInput.files?.length;
        }
    });

    startBtn?.addEventListener('click', async () => {
        const file = fileInput?.files?.[0];
        if (!validatedCode || !file) {
            return;
        }

        if (file.size > ctx.maxFileBytes) {
            showResult('danger', 'File is too large.');
            return;
        }

        const bytesRemaining = validatedMeta?.bytes_remaining ?? ctx.maxBytesPerCode;
        if (file.size > bytesRemaining) {
            showResult(
                'danger',
                `This file exceeds the remaining quota for this code (${formatBytes(bytesRemaining)} left).`,
            );
            return;
        }

        startBtn.disabled = true;
        validateBtn.disabled = true;
        fileInput.disabled = true;
        progressWrap?.classList.remove('d-none');
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        }
        resultEl?.classList.add('d-none');

        try {
            const { data: initData } = await postJson(
                ctx.initiateUrl,
                {
                    sample_code: validatedCode,
                    filename: file.name,
                    content_type: file.type || 'application/octet-stream',
                    file_size: file.size,
                },
                csrfToken,
            );

            if (!initData.ok) {
                showResult('danger', initData.error || 'Could not start upload.');
                return;
            }

            await uploadFileToS3(
                initData.upload_url,
                file,
                file.type || 'application/octet-stream',
                (pct) => {
                    if (progressBar) {
                        progressBar.style.width = `${pct}%`;
                        progressBar.textContent = `${pct}%`;
                    }
                },
            );

            const { data: completeData } = await postJson(
                ctx.completeUrl,
                { upload_id: initData.upload_id },
                csrfToken,
            );

            if (!completeData.ok) {
                showResult('danger', completeData.error || 'Upload could not be finalized.');
                return;
            }

            if (progressBar) {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.style.width = '100%';
                progressBar.textContent = '100%';
            }

            showResult(
                'success',
                `Upload complete for ${completeData.sample_code} (${completeData.original_filename}, ${formatBytes(completeData.file_size_bytes)}). `
                + 'You can upload another file for this code if you have quota remaining.',
            );

            if (validatedMeta && completeData.file_size_bytes) {
                validatedMeta.bytes_used = (validatedMeta.bytes_used || 0) + completeData.file_size_bytes;
                validatedMeta.bytes_remaining = Math.max(
                    0,
                    (validatedMeta.bytes_limit || ctx.maxBytesPerCode) - validatedMeta.bytes_used,
                );
                setCodeMessage(
                    `Code ${validatedCode}: ${formatBytes(validatedMeta.bytes_remaining)} remaining. Select another file to continue.`,
                    false,
                );
            }

            fileInput.value = '';
            startBtn.disabled = true;
        } catch (e) {
            showResult('danger', e.message || 'Upload failed.');
        } finally {
            validateBtn.disabled = false;
            if (validatedCode) {
                fileInput.disabled = false;
            }
        }
    });
});
