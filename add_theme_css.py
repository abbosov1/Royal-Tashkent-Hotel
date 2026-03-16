def add_css():
    css_content = r"""
/* Light Mode Variables override */
body.light-mode {
  background-color: #f0f4f8;
  color: #2c3e50;
}

body.light-mode header {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

body.light-mode .logo h1,
body.light-mode nav ul li a {
  color: #2c3e50;
}

body.light-mode .hero {
  /* Keep background dark for hero text visibility unless specified */
}

body.light-mode .hero-content h1,
body.light-mode .hero-content p {
  color: #ffffff;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

body.light-mode .section-header {
  color: #2c3e50;
}

body.light-mode .room-card,
body.light-mode .testimonial-card,
body.light-mode .booking-card,
body.light-mode .admin-card,
body.light-mode .dashboard-card {
  background: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

body.light-mode .room-info h3,
body.light-mode .room-info p,
body.light-mode .testimonial-content p,
body.light-mode .testimonial-author h4,
body.light-mode .dashboard-card p,
body.light-mode .admin-card h3,
body.light-mode table,
body.light-mode th,
body.light-mode td {
  color: #2c3e50;
}

body.light-mode table {
  background: #ffffff;
}

body.light-mode th {
  background: #e2e8f0;
}

body.light-mode tr {
  border-bottom: 1px solid #e2e8f0;
}

body.light-mode tr:hover {
  background-color: #f8fafc;
}

body.light-mode .form-group input,
body.light-mode .form-group select,
body.light-mode .form-group textarea,
body.light-mode input[type="text"],
body.light-mode input[type="email"],
body.light-mode input[type="password"],
body.light-mode input[type="date"],
body.light-mode input[type="number"],
body.light-mode input[type="file"] {
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  color: #1e293b;
}

body.light-mode .form-group label {
  color: #475569;
}

body.light-mode .modal-content {
  background: #ffffff;
  color: #2c3e50;
}

body.light-mode .modal-content h2 {
  color: #2c3e50;
  border-bottom: 1px solid #e2e8f0;
}

body.light-mode footer {
  background-color: #e2e8f0;
  color: #2c3e50;
}

body.light-mode footer h3,
body.light-mode footer p,
body.light-mode footer a {
  color: #2c3e50;
}

body.light-mode footer a:hover {
  color: #d4af37;
}

body.light-mode .social-links a {
  color: #2c3e50;
  background: #cbd5e1;
}

body.light-mode .social-links a:hover {
  background: #d4af37;
  color: #ffffff;
}

/* Base override for default text if not specifically targeted */
body.light-mode p, body.light-mode h1, body.light-mode h2, body.light-mode h3, body.light-mode h4, body.light-mode h5, body.light-mode h6 {
  color: #2c3e50;
}

body.light-mode .hero h1, body.light-mode .hero p {
    color: #ffffff;
}
"""

    with open("app/static/css/style.css", "r", encoding="utf-8") as f:
        content = f.read()

    if "body.light-mode" not in content:
        with open("app/static/css/style.css", "a", encoding="utf-8") as f:
            f.write("\n" + css_content + "\n")
        print("Light mode CSS appended successfully.")
    else:
        print("CSS already contains light mode.")

add_css()
