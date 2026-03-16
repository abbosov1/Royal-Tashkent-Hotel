import re
import os

# 1. Update Light Mode CSS
css_path = "app/static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

css_content = re.sub(r'/\* Light Mode Variables override \*/.*?(?=(/\*|$))', '', css_content, flags=re.DOTALL)
if "body.light-mode" in css_content:
    css_content = css_content.split('/* Light Mode Variables override */')[0]

new_light_mode = """
/* Light Mode Variables override */
body.light-mode {
  background-color: #f7f9fa; /* slightly cool warm white */
  color: #1a1a2e; /* dark navy gray instead of raw black */
}
body.light-mode h1, body.light-mode h2, body.light-mode h3, 
body.light-mode h4, body.light-mode h5, body.light-mode h6,
body.light-mode p, body.light-mode label, body.light-mode span, body.light-mode div {
  color: #1a1a2e;
}

body.light-mode header, body.light-mode nav.scrolled {
  background: rgba(255, 255, 255, 0.95) !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

body.light-mode .logo h1, body.light-mode .logo,
body.light-mode nav ul li a {
  color: #1a1a2e !important;
}

body.light-mode .hero-content h1, body.light-mode .hero-content p {
  color: #ffffff !important;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
}

body.light-mode .section-header {
  color: #1a1a2e;
}

body.light-mode .card,
body.light-mode .room-card,
body.light-mode .testimonial-card,
body.light-mode .booking-card,
body.light-mode .admin-card,
body.light-mode .dashboard-card {
  background-color: #ffffff;
  border: 1px solid #e1e8ed !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
}

body.light-mode .card *,
body.light-mode .room-card *,
body.light-mode .dashboard-card *,
body.light-mode .booking-card * {
  color: #1a1a2e;
}

body.light-mode .btn-primary {
  color: #ffffff !important;
  background-color: #c99c33;
}
body.light-mode .btn-primary:hover {
  background-color: #b58825;
}

body.light-mode input,
body.light-mode select,
body.light-mode textarea {
  background-color: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  color: #1e293b !important;
}
body.light-mode input:focus,
body.light-mode textarea:focus {
  outline: none;
  border-color: #c99c33 !important;
  box-shadow: 0 0 0 2px rgba(201,156,51,0.2) !important;
}

body.light-mode .room-item,
body.light-mode table,
body.light-mode th,
body.light-mode td {
  border-color: #e1e8ed !important;
  color: #1a1a2e !important;
}
body.light-mode table {
  background: #ffffff;
}
body.light-mode th {
  background: #f1f5f9;
}
body.light-mode tr:hover {
  background-color: #f8fafc;
}

body.light-mode .modal-content {
  background: #ffffff !important;
}

body.light-mode footer {
  background-color: #eaeff5;
}
body.light-mode footer * {
  color: #1a1a2e;
}

/* Custom File Input Styles */
.file-upload-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-upload-input {
  display: none !important;
}
.file-upload-btn {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background: var(--primary);
  color: #fff;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.85rem;
  text-transform: uppercase;
  font-family: 'Syncopate', sans-serif;
  transition: opacity 0.3s;
  box-shadow: 0 4px 6px rgba(212, 175, 55, 0.2);
}
.file-upload-btn:hover {
  opacity: 0.9;
}
.file-upload-text {
  font-size: 0.85rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
"""
css_content = css_content.rstrip() + "\n\n" + new_light_mode + "\n"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)

# 2. Add Edit Room Button and Custom File Inputs
admin_path = "app/templates/admin.html"
with open(admin_path, "r", encoding="utf-8") as f:
    admin_text = f.read()

room_item_pattern = r'(<form action="/admin/room/delete/\{\{ room\.id \}\}" method="POST".*?>\s*<button type="submit".*?>Delete</button>\s*</form>)'
def repl_edit_btn(match):
    block = match.group(1)
    if 'editRoom(' in block: return block
    new_btns = f'''<div style="display:flex; gap:0.5rem;">
                                <button type="button" class="btn-primary" style="padding:0.5rem 1rem; font-size:0.8rem; border:none; cursor:pointer;" onclick="editRoom('{{{{ room.id }}}}', '{{{{ room.name|replace(\"'\", \"\\\\'\") }}}}', '{{{{ room.description|replace(\"'\", \"\\\\'\")|replace(\"\\n\", \" \") }}}}', '{{{{ room.price_per_night }}}}')">Edit</button>
                                {block}
                            </div>'''
    return new_btns

admin_text = re.sub(room_item_pattern, repl_edit_btn, admin_text)

def ensure_custom_file_input(html_content, id_suffix):
    old_input = '<input type="file" name="image" accept="image/*">'
    if old_input in html_content:
        new_ui = f'''<div class="file-upload-wrapper">
            <label class="file-upload-btn" for="fileInput_{id_suffix}">Choose Image</label>
            <span class="file-upload-text" id="fileText_{id_suffix}">No file chosen</span>
            <input type="file" name="image" id="fileInput_{id_suffix}" class="file-upload-input" accept="image/*" onchange="document.getElementById('fileText_{id_suffix}').innerText = this.files[0] ? this.files[0].name : 'No file chosen'">
        </div>'''
        return html_content.replace(old_input, new_ui, 1)
    return html_content

admin_text = ensure_custom_file_input(admin_text, "add")
admin_text = ensure_custom_file_input(admin_text, "edit")

with open(admin_path, "w", encoding="utf-8") as f:
    f.write(admin_text)

print("CSS updated, File inputs customized, Edit button injected.")
