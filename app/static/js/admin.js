function editRoom(id, name, desc, amenities, price) {
  const modal = document.getElementById('editModal');
  const form = document.getElementById('editForm');
  const nameInput = document.getElementById('editName');
  const descInput = document.getElementById('editDesc');
  const amenitiesInput = document.getElementById('editAmenities');
  const priceInput = document.getElementById('editPrice');

  if (!modal || !form || !nameInput || !descInput || !amenitiesInput || !priceInput) {
    return;
  }

  modal.style.display = 'flex';
  form.action = '/admin/room/edit/' + id;
  nameInput.value = name;
  descInput.value = desc;
  amenitiesInput.value = amenities || '';
  priceInput.value = price;
}

function closeEditModal() {
  const modal = document.getElementById('editModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

function togglePwd(button) {
  const input = button.previousElementSibling;
  if (!input) {
    return;
  }

  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = '🙈';
  } else {
    input.type = 'password';
    button.textContent = '👁️';
  }
}

function bindRoomEditButtons() {
  document.querySelectorAll('.edit-room-btn').forEach((button) => {
    button.addEventListener('click', () => {
      editRoom(
        button.dataset.roomId,
        button.dataset.roomName,
        button.dataset.roomDesc,
        button.dataset.roomAmenities,
        button.dataset.roomPrice
      );
    });
  });
}

function bindModalClose() {
  const closeButton = document.querySelector('[data-close-modal]');
  if (closeButton) {
    closeButton.addEventListener('click', closeEditModal);
  }

  const modal = document.getElementById('editModal');
  if (modal) {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) {
        closeEditModal();
      }
    });
  }
}

function bindPasswordToggles() {
  document.querySelectorAll('[data-password-toggle]').forEach((button) => {
    button.addEventListener('click', () => togglePwd(button));
  });
}

function bindFileInputLabels() {
  const mappings = [
    { input: 'fileInput_add', text: 'fileText_add' },
    { input: 'fileInput_edit', text: 'fileText_edit' },
    { input: 'fileInput_add_extra', text: 'fileText_add_extra', multiple: true },
    { input: 'fileInput_edit_extra', text: 'fileText_edit_extra', multiple: true }
  ];

  mappings.forEach((mapping) => {
    const input = document.getElementById(mapping.input);
    const text = document.getElementById(mapping.text);
    if (!input || !text) {
      return;
    }

    input.addEventListener('change', () => {
      if (mapping.multiple) {
        text.textContent = input.files.length ? `${input.files.length} files selected` : 'No files chosen';
        return;
      }
      text.textContent = input.files[0] ? input.files[0].name : 'No file chosen';
    });
  });
}

function bindConfirmForms() {
  document.querySelectorAll('form[data-confirm]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      const message = form.dataset.confirm || 'Are you sure?';
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });
}

function readImageAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ''));
    reader.onerror = () => reject(new Error('Failed to read image'));
    reader.readAsDataURL(file);
  });
}

function loadImage(dataUrl) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error('Failed to load image'));
    image.src = dataUrl;
  });
}

async function compressImageFile(file, options = {}) {
  if (!file || !file.type.startsWith('image/')) {
    return file;
  }

  const maxDimension = options.maxDimension || 1600;
  const maxBytes = options.maxBytes || 450 * 1024;
  const outputType = 'image/jpeg';
  const fileBaseName = (file.name || 'image').replace(/\.[^/.]+$/, '');

  const sourceData = await readImageAsDataUrl(file);
  const sourceImage = await loadImage(sourceData);

  let width = sourceImage.width;
  let height = sourceImage.height;
  const largest = Math.max(width, height);
  if (largest > maxDimension) {
    const ratio = maxDimension / largest;
    width = Math.max(1, Math.round(width * ratio));
    height = Math.max(1, Math.round(height * ratio));
  }

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) {
    return file;
  }
  context.drawImage(sourceImage, 0, 0, width, height);

  let quality = 0.82;
  let blob = await new Promise((resolve) => canvas.toBlob(resolve, outputType, quality));
  if (!blob) {
    return file;
  }

  while (blob.size > maxBytes && quality > 0.45) {
    quality -= 0.08;
    blob = await new Promise((resolve) => canvas.toBlob(resolve, outputType, quality));
    if (!blob) {
      return file;
    }
  }

  if (blob.size >= file.size) {
    return file;
  }

  return new File([blob], `${fileBaseName}.jpg`, {
    type: outputType,
    lastModified: Date.now()
  });
}

async function optimizeAdminImagesBeforeSubmit(event) {
  const form = event.currentTarget;
  if (!form || form.dataset.optimizedSubmit === '1') {
    return;
  }

  event.preventDefault();

  const mainInput = form.querySelector('input[name="image"]');
  const extrasInput = form.querySelector('input[name="extra_images"]');

  try {
    if (mainInput?.files?.length && typeof DataTransfer !== 'undefined') {
      const mainFile = mainInput.files[0];
      const optimizedMain = await compressImageFile(mainFile, {
        maxDimension: 1800,
        maxBytes: 700 * 1024,
      });
      const dtMain = new DataTransfer();
      dtMain.items.add(optimizedMain);
      mainInput.files = dtMain.files;
    }

    if (extrasInput?.files && extrasInput.files.length && typeof DataTransfer !== 'undefined') {
      const selected = Array.from(extrasInput.files);
      const limited = selected.slice(0, 5);
      const optimizedExtras = [];

      for (const file of limited) {
        const optimized = await compressImageFile(file, {
          maxDimension: 1600,
          maxBytes: 450 * 1024,
        });
        optimizedExtras.push(optimized);
      }

      const dtExtras = new DataTransfer();
      optimizedExtras.forEach((file) => dtExtras.items.add(file));
      extrasInput.files = dtExtras.files;

      const extraText = form.querySelector('#fileText_add_extra, #fileText_edit_extra');
      if (extraText) {
        extraText.textContent = `${optimizedExtras.length} files selected`;
      }
    }
  } catch (error) {
    console.error('Image optimization failed:', error);
  }

  form.dataset.optimizedSubmit = '1';
  form.submit();
}

function bindUploadOptimization() {
  const forms = document.querySelectorAll('form[action="/admin/room/add"], #editForm');
  forms.forEach((form) => {
    form.addEventListener('submit', optimizeAdminImagesBeforeSubmit);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  bindRoomEditButtons();
  bindFileInputLabels();
  bindModalClose();
  bindPasswordToggles();
  bindConfirmForms();
  bindUploadOptimization();
});

window.togglePwd = togglePwd;
window.closeEditModal = closeEditModal;
