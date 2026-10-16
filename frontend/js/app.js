// Registro de Service Worker para PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((reg) => console.log('Service Worker registrado:', reg.scope))
      .catch((err) => console.log('Fallo en Service Worker:', err));
  });
}

// Instalación PWA (Botón Instalar)
let deferredPrompt;
const btnInstall = document.getElementById('btnInstall');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (btnInstall) {
    btnInstall.style.display = 'flex';
  }
});

if (btnInstall) {
  btnInstall.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`Respuesta a instalación: ${outcome}`);
    deferredPrompt = null;
    btnInstall.style.display = 'none';
  });
}

// Elementos DOM
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const previewName = document.getElementById('previewName');
const previewSize = document.getElementById('previewSize');
const removeFileBtn = document.getElementById('removeFileBtn');
const submitBtn = document.getElementById('submitBtn');
const providerBadge = document.getElementById('providerBadge');
const mockBanner = document.getElementById('mockBanner');

const sourceLangSelect = document.getElementById('sourceLang');
const targetLangSelect = document.getElementById('targetLang');
const toneSelect = document.getElementById('tone');

const progressCard = document.getElementById('progressCard');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const progressMessage = document.getElementById('progressMessage');
const downloadArea = document.getElementById('downloadArea');
const downloadBtn = document.getElementById('downloadBtn');

// Modal de Configuración
const settingsModal = document.getElementById('settingsModal');
const btnSettings = document.getElementById('btnSettings');
const btnCloseModal = document.getElementById('btnCloseModal');
const btnCancelModal = document.getElementById('btnCancelModal');
const btnSaveConfig = document.getElementById('btnSaveConfig');
const btnOpenConfigFromBanner = document.getElementById('btnOpenConfigFromBanner');

const radioFree = document.getElementById('radioFree');
const radioGemini = document.getElementById('radioGemini');
const radioMock = document.getElementById('radioMock');
const cardFree = document.getElementById('cardFree');
const cardGemini = document.getElementById('cardGemini');
const cardMock = document.getElementById('cardMock');
const geminiKeyArea = document.getElementById('geminiKeyArea');
const geminiApiKeyInput = document.getElementById('geminiApiKeyInput');

let selectedFile = null;
let currentEventSource = null;

// Cargar y mostrar configuración del proveedor
async function loadConfig() {
  try {
    const res = await fetch('/api/v1/config');
    if (!res.ok) return;
    const config = await res.json();

    // Resetear clases seleccionadas
    cardFree.classList.remove('selected');
    cardGemini.classList.remove('selected');
    cardMock.classList.remove('selected');

    if (config.provider === 'gemini') {
      providerBadge.textContent = '✨ GEMINI IA';
      providerBadge.className = 'badge-mode gemini';
      mockBanner.classList.add('hidden');
      radioGemini.checked = true;
      cardGemini.classList.add('selected');
      geminiKeyArea.style.display = 'block';
      if (config.has_gemini_key) {
        geminiApiKeyInput.placeholder = `Clave guardada (${config.masked_key})`;
      }
    } else if (config.provider === 'mock') {
      providerBadge.textContent = '🧪 MODO: MOCK';
      providerBadge.className = 'badge-mode mock';
      mockBanner.classList.remove('hidden');
      radioMock.checked = true;
      cardMock.classList.add('selected');
      geminiKeyArea.style.display = 'none';
    } else {
      // Por defecto modo FREE
      providerBadge.textContent = '🌟 AUTOMÁTICO GRATIS';
      providerBadge.className = 'badge-mode free';
      mockBanner.classList.add('hidden');
      radioFree.checked = true;
      cardFree.classList.add('selected');
      geminiKeyArea.style.display = 'none';
    }
  } catch (err) {
    providerBadge.textContent = 'Desconectado';
    providerBadge.style.color = '#ef4444';
  }
}
loadConfig();

// Abrir / Cerrar Modal
function openModal() {
  settingsModal.classList.add('active');
}
function closeModal() {
  settingsModal.classList.remove('active');
}

btnSettings.addEventListener('click', openModal);
providerBadge.addEventListener('click', openModal);
btnOpenConfigFromBanner.addEventListener('click', openModal);
btnCloseModal.addEventListener('click', closeModal);
btnCancelModal.addEventListener('click', closeModal);

settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) closeModal();
});

// Cambiar selección en radios
radioFree.addEventListener('change', () => {
  cardFree.classList.add('selected');
  cardGemini.classList.remove('selected');
  cardMock.classList.remove('selected');
  geminiKeyArea.style.display = 'none';
});

radioGemini.addEventListener('change', () => {
  cardGemini.classList.add('selected');
  cardFree.classList.remove('selected');
  cardMock.classList.remove('selected');
  geminiKeyArea.style.display = 'block';
});

radioMock.addEventListener('change', () => {
  cardMock.classList.add('selected');
  cardFree.classList.remove('selected');
  cardGemini.classList.remove('selected');
  geminiKeyArea.style.display = 'none';
});

// Guardar Ajustes
btnSaveConfig.addEventListener('click', async () => {
  let selectedProvider = 'free';
  if (radioGemini.checked) selectedProvider = 'gemini';
  if (radioMock.checked) selectedProvider = 'mock';

  const key = geminiApiKeyInput.value.trim();

  btnSaveConfig.disabled = true;
  btnSaveConfig.textContent = selectedProvider === 'gemini' ? 'Verificando con Google...' : 'Guardando...';

  try {
    const res = await fetch('/api/v1/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: selectedProvider,
        gemini_api_key: key || undefined
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Error al guardar configuración');
    }

    closeModal();
    await loadConfig();
    
    if (selectedProvider === 'gemini') {
      alert('✅ ¡Clave de Gemini verificada y activada con éxito! Ya puedes traducir tus documentos.');
    } else if (selectedProvider === 'free') {
      alert('🌟 ¡Traductor Automático Gratuito activado! Listo para traducir sin claves.');
    } else {
      alert('Modo Simulado activado.');
    }

  } catch (err) {
    alert(`❌ ${err.message}`);
  } finally {
    btnSaveConfig.disabled = false;
    btnSaveConfig.textContent = 'Guardar Ajustes';
  }
});

// Drag & Drop
['dragenter', 'dragover'].forEach(name => {
  dropzone.addEventListener(name, (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(name => {
  dropzone.addEventListener(name, (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', (e) => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelected(files[0]);
  }
});

dropzone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    handleFileSelected(fileInput.files[0]);
  }
});

function handleFileSelected(file) {
  const validExts = ['.docx'];
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

  if (!validExts.includes(ext)) {
    alert(`Por ahora solo se admiten archivos Word (${validExts.join(', ')}).`);
    return;
  }

  selectedFile = file;
  previewName.textContent = file.name;
  previewSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
  filePreview.classList.add('active');
  dropzone.style.display = 'none';
  submitBtn.disabled = false;
}

removeFileBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  filePreview.classList.remove('active');
  dropzone.style.display = 'block';
  submitBtn.disabled = true;
});

// Enviar formulario e iniciar traducción
submitBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  submitBtn.disabled = true;
  downloadArea.classList.remove('active');
  progressCard.classList.add('active');
  progressFill.style.width = '5%';
  progressPercent.textContent = '5%';
  progressMessage.textContent = 'Subiendo archivo al servidor...';
  progressMessage.style.color = '#94a3b8';

  const formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('source_lang', sourceLangSelect.value);
  formData.append('target_lang', targetLangSelect.value);
  formData.append('tone', toneSelect.value);

  try {
    const uploadRes = await fetch('/api/v1/translate/upload', {
      method: 'POST',
      body: formData
    });

    if (!uploadRes.ok) {
      const err = await uploadRes.json();
      throw new Error(err.detail || 'Error en la subida del documento');
    }

    const job = await uploadRes.json();
    listenToProgress(job.task_id);

  } catch (error) {
    progressMessage.textContent = `Error: ${error.message}`;
    progressMessage.style.color = '#ef4444';
    submitBtn.disabled = false;
  }
});

// Escuchar progreso en tiempo real mediante Server-Sent Events (SSE)
function listenToProgress(taskId) {
  if (currentEventSource) {
    currentEventSource.close();
  }

  currentEventSource = new EventSource(`/api/v1/translate/stream/${taskId}`);

  currentEventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    let pct = 10;
    if (data.total_steps > 0) {
      pct = Math.round((data.progress / data.total_steps) * 100);
    }
    if (pct < 10 && data.status === 'processing') pct = 15;
    if (data.status === 'completed') pct = 100;

    progressFill.style.width = `${pct}%`;
    progressPercent.textContent = `${pct}%`;
    progressMessage.textContent = data.message;

    if (data.status === 'completed') {
      currentEventSource.close();
      downloadArea.classList.add('active');
      downloadBtn.href = `/api/v1/translate/download/${taskId}`;
      downloadBtn.download = `traducido_${selectedFile.name}`;
      submitBtn.disabled = false;
    } else if (data.status === 'failed') {
      currentEventSource.close();
      progressMessage.textContent = `Error: ${data.error || data.message}`;
      progressMessage.style.color = '#ef4444';
      submitBtn.disabled = false;
    }
  };

  currentEventSource.onerror = () => {
    currentEventSource.close();
    pollStatus(taskId);
  };
}

async function pollStatus(taskId) {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`/api/v1/translate/status/${taskId}`);
      const data = await res.json();
      
      let pct = data.total_steps > 0 ? Math.round((data.progress / data.total_steps) * 100) : 50;
      if (data.status === 'completed') pct = 100;

      progressFill.style.width = `${pct}%`;
      progressPercent.textContent = `${pct}%`;
      progressMessage.textContent = data.message;

      if (data.status === 'completed') {
        clearInterval(interval);
        downloadArea.classList.add('active');
        downloadBtn.href = `/api/v1/translate/download/${taskId}`;
        downloadBtn.download = `traducido_${selectedFile.name}`;
        submitBtn.disabled = false;
      } else if (data.status === 'failed') {
        clearInterval(interval);
        progressMessage.textContent = `Error: ${data.error || data.message}`;
        progressMessage.style.color = '#ef4444';
        submitBtn.disabled = false;
      }
    } catch (e) {
      clearInterval(interval);
    }
  }, 1000);
}
