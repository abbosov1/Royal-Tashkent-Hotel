import sys

with open("app/static/css/style.css", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == "/* Keep background dark for hero text visibility unless specified */":
        break
    new_lines.append(line)

light_mode_css = """
/* LIGHT MODE OVERRIDES - WARM LUXURY */
body.light-mode {
  background-color: #F5F0E8;
  color: #1C1008;
}

body.light-mode p, body.light-mode h1, body.light-mode h2, body.light-mode h3, 
body.light-mode h4, body.light-mode h5, body.light-mode h6, body.light-mode label {
  color: #1C1008;
}

body.light-mode nav.scrolled {
  background-color: rgba(245, 240, 232, 0.95);
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

body.light-mode .nav-links a {
  color: #1C1008;
}

body.light-mode .logo {
  color: #1C1008;
}

body.light-mode .logo span {
  color: var(--primary);
}

body.light-mode .hero h1, body.light-mode .hero p {
  color: #ffffff;
}

body.light-mode .section-title {
  color: #1C1008;
}

/* Cards (Rooms, Testimonials, Bookings, Dashboard, Admin) */
body.light-mode .room-card,
body.light-mode .card,
body.light-mode .dashboard-card,
body.light-mode .admin-card,
body.light-mode .booking-card {
  background-color: #FFFFFF;
  border: 1px solid #E8DDD0;
  box-shadow: 0 10px 25px rgba(0,0,0,0.06);
}

body.light-mode .room-card *,
body.light-mode .card *,
body.light-mode .dashboard-card *,
body.light-mode .admin-card *,
body.light-mode .booking-card * {
  color: #1C1008;
}

/* Services */
body.light-mode .service-item {
  background-color: #FFFFFF;
  border: 1px solid #E8DDD0;
}

body.light-mode .service-item * {
  color: #1C1008;
}

body.light-mode .about p {
  color: #4A3728;
}

/* Forms */
body.light-mode .contact-form,
body.light-mode .modal-content,
body.light-mode .form-group {
  background-color: #FFFFFF;
}

body.light-mode .modal-content h2,
body.light-mode .contact-form h3 {
  color: #1C1008;
}

body.light-mode input,
body.light-mode select,
body.light-mode textarea {
  background-color: #FFFFFF;
  border: 1px solid #D4C4B0;
  color: #1C1008;
}

body.light-mode input:focus,
body.light-mode select:focus,
body.light-mode textarea:focus {
  outline: none;
  border-color: var(--primary);
}

body.light-mode input::placeholder,
body.light-mode textarea::placeholder {
  color: #7A6A58;
}

body.light-mode .btn-submit {
  background-color: #1C1008;
  color: #F5F0E8;
}

body.light-mode .btn-submit:hover {
  background-color: var(--primary);
}

body.light-mode .btn-primary {
  color: #1C1008;
}

/* Footer */
body.light-mode footer {
  background-color: #2A1F14;
}

body.light-mode footer,
body.light-mode footer *,
body.light-mode footer h3,
body.light-mode footer p,
body.light-mode footer a,
body.light-mode .social-links a {
  color: #F5F0E8;
}

body.light-mode footer a:hover,
body.light-mode .social-links a:hover {
  color: var(--primary);
}

/* Tables */
body.light-mode table {
  background-color: #FFFFFF;
  border: 1px solid #E8DDD0;
}

body.light-mode th {
  background-color: #F5F0E8;
  color: #1C1008;
}

body.light-mode td {
  color: #1C1008;
  border-bottom: 1px solid #E8DDD0;
}

body.light-mode tr:hover {
  background-color: #FDFBF7;
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

with open("app/static/css/style.css", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
    f.write(light_mode_css)

print("CSS Fixed using Python script!")
