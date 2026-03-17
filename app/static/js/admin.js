function editRoom(id, name, desc, price) {
  const modal = document.getElementById('editModal');
  const form = document.getElementById('editForm');
  const nameInput = document.getElementById('editName');
  const descInput = document.getElementById('editDesc');
  const priceInput = document.getElementById('editPrice');

  if (!modal || !form || !nameInput || !descInput || !priceInput) {
    return;
  }

  modal.style.display = 'flex';
  form.action = '/admin/room/edit/' + id;
  nameInput.value = name;
  descInput.value = desc;
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
    { input: 'fileInput_edit', text: 'fileText_edit' }
  ];

  mappings.forEach((mapping) => {
    const input = document.getElementById(mapping.input);
    const text = document.getElementById(mapping.text);
    if (!input || !text) {
      return;
    }

    input.addEventListener('change', () => {
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

document.addEventListener('DOMContentLoaded', () => {
  bindRoomEditButtons();
  bindFileInputLabels();
  bindModalClose();
  bindPasswordToggles();
  bindConfirmForms();
});

window.togglePwd = togglePwd;
window.closeEditModal = closeEditModal;
