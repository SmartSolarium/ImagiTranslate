document.addEventListener('DOMContentLoaded', () => {
    // Referenze Dom Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const uploadContentDefault = document.getElementById('upload-content-default');
    const imageGallery = document.getElementById('image-gallery');
    const batchProgress = document.getElementById('batch-progress');
    const resultsGallery = document.getElementById('results-gallery');
    const translateBtn = document.getElementById('translate-btn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    
    const sourceLangSel = document.getElementById('source-lang');
    const targetLangSel = document.getElementById('target-lang');
    const apiKeyInput = document.getElementById('api-key');
    
    const resultContainer = document.getElementById('result-container');
    
    const toast = document.getElementById('error-message');

    let currentFiles = [];

    // ----- Gestione File Upload -----

    // Click per caricare file
    browseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    dropZone.addEventListener('click', (e) => {
        if(e.target !== browseBtn && e.target.closest('.remove-btn') === null) {
            fileInput.click();
        }
    });

    // Quando un file viene selezionato (browse)
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Eventi Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    // Processa il file
    function handleFiles(files) {
        if (files.length > 0) {
            Array.from(files).forEach(file => {
                // Validazione base
                if (!file.type.match('image.*')) {
                    showError(`Il file ${file.name} non è un'immagine valida.`);
                    return;
                }

                if (file.size > 10 * 1024 * 1024) { // 10MB limit
                    showError(`L'immagine ${file.name} è troppo grande. Massimo 10 MB.`);
                    return;
                }
                
                // Evita duplicati basandosi sul nome+dimensione
                const isDuplicate = currentFiles.some(f => f.name === file.name && f.size === file.size);
                if (!isDuplicate) {
                    currentFiles.push(file);
                }
            });
            
            updateGalleryUI();
            enableTranslateBtn();
        }
    }

    function updateGalleryUI() {
        imageGallery.innerHTML = '';
        
        if (currentFiles.length === 0) {
            uploadContentDefault.style.display = 'flex';
            imageGallery.style.display = 'none';
        } else {
            uploadContentDefault.style.display = 'none';
            imageGallery.style.display = 'flex';
            
            currentFiles.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const item = document.createElement('div');
                    item.className = 'gallery-item';
                    item.innerHTML = `
                        <img src="${e.target.result}" alt="preview">
                        <button class="remove-btn" data-index="${index}">×</button>
                    `;
                    imageGallery.appendChild(item);
                    
                    // Aggiungi listener per la rimozione
                    item.querySelector('.remove-btn').addEventListener('click', (evt) => {
                        evt.stopPropagation();
                        currentFiles.splice(index, 1);
                        updateGalleryUI();
                        enableTranslateBtn();
                    });
                };
                reader.readAsDataURL(file);
            });
        }
    }

    function enableTranslateBtn() {
        if (currentFiles.length > 0 && targetLangSel.value && apiKeyInput.value.trim() !== '') {
            translateBtn.disabled = false;
        } else {
            translateBtn.disabled = true;
        }
    }

    // Aggiungi listener per API key input per sbloccare il bottone
    apiKeyInput.addEventListener('input', enableTranslateBtn);

    // ----- Chiamata API al Backend -----

    translateBtn.addEventListener('click', async () => {
        if (currentFiles.length === 0) return;

        // UI State: Loading
        translateBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'block';
        
        // Setup per batch process
        resultContainer.style.display = 'block';
        resultsGallery.innerHTML = '';
        batchProgress.textContent = `(0/${currentFiles.length})`;
        
        // Scorri fluido ai risultati
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

        let successCount = 0;

        // Purtroppo la maggior parte dei server Flask di sviluppo supporta caricamenti asincroni uno alla volta per stabilità
        // Faremo le chiamate in modo sequenziale per ogni file per gestire i risultati mano a mano
        for (let i = 0; i < currentFiles.length; i++) {
            const currentFile = currentFiles[i];
            
            // Prepara il FormData per il file corrente
            const formData = new FormData();
            formData.append('image', currentFile);
            formData.append('source_lang', sourceLangSel.value);
            formData.append('target_lang', targetLangSel.value);
            formData.append('api_key', apiKeyInput.value.trim());

            batchProgress.textContent = `(Traduzione in corso ${i+1}/${currentFiles.length}...)`;

            try {
                const response = await fetch('/translate', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    successCount++;
                    // Appendi il blocco risultato dinamicamente
                    appendResultBox(currentFile, data.image, i);
                } else {
                    throw new Error(data.error || `Errore per ${currentFile.name}`);
                }

            } catch (error) {
                console.error("Errore di traduzione:", error);
                showError(`[File: ${currentFile.name}] ${error.message}`);
                
                // Metti anche un box di errore visibile
                appendErrorBox(currentFile.name);
            }
        }
        
        // UI State: Reset Button
        batchProgress.textContent = `(${successCount}/${currentFiles.length} Completati)`;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
        translateBtn.disabled = false;
    });

    function appendResultBox(fileObj, translatedBase64, index) {
        // Genera dataURL originale per il confronto
        const reader = new FileReader();
        reader.onload = (e) => {
            const originalBase64 = e.target.result;
            
            const container = document.createElement('div');
            container.className = 'image-comparison';
            container.style.width = "100%";
            container.style.marginTop = "2rem";
            container.style.paddingBottom = "2rem";
            container.style.borderBottom = "1px solid var(--glass-border)";
            
            container.innerHTML = `
                <div style="width:100%; text-align:left; margin-bottom:1rem; color:var(--text-muted);">
                    File: <strong>${fileObj.name}</strong>
                </div>
                <div style="display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center; width:100%;">
                    <div class="img-box">
                        <span class="badge">Originale</span>
                        <img src="${originalBase64}" alt="Originale">
                    </div>
                    <div class="img-box">
                        <span class="badge highlight">Tradotta</span>
                        <img src="${translatedBase64}" alt="Tradotta" id="translated-img-${index}">
                    </div>
                </div>
                <button class="btn-secondary download-btn-dynamic" data-index="${index}" style="margin-top:1rem;">Scarica Immagine</button>
            `;
            
            resultsGallery.appendChild(container);
            
            // Aggiungi click listener per il download programmatico
            const dlBtn = container.querySelector('.download-btn-dynamic');
            dlBtn.addEventListener('click', (evt) => {
                evt.preventDefault();
                const imgSrc = document.getElementById(`translated-img-${index}`).src;
                
                const link = document.createElement("a");
                link.href = imgSrc;
                link.download = `Tradotta_${fileObj.name}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
        };
        reader.readAsDataURL(fileObj);
    }
    
    function appendErrorBox(filename) {
        const container = document.createElement('div');
        container.style.width = "100%";
        container.style.marginTop = "2rem";
        container.style.padding = "1rem";
        container.style.background = "rgba(255, 77, 79, 0.1)";
        container.style.border = "1px solid var(--danger)";
        container.style.borderRadius = "12px";
        container.style.color = "var(--danger)";
        container.innerHTML = `<strong>Errore durante la traduzione del file:</strong> ${filename}`;
        resultsGallery.appendChild(container);
    }

    // ----- Utils -----

    function showError(message) {
        toast.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    }


});
