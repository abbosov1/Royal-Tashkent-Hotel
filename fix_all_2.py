import glob

# 1. Fix CSS
css_file = "app/static/css/style.css"
with open(css_file, "r") as f:
    css = f.read()

# Add new CSS rules
fixes = """

/* CONTACT FORM BORDERS IN LIGHT MODE */
body.light-mode .input-group input,
body.light-mode .input-group textarea {
  border: none !important;
  border-bottom: 2px solid #D4C4B0 !important;
  background-color: transparent !important;
  border-radius: 0;
}
body.light-mode .input-group input:focus,
body.light-mode .input-group textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: none !important;
}

/* NAVBAR TEXT IN HERO (LIGHT MODE) */
body.light-mode nav:not(.scrolled) .nav-links a,
body.light-mode nav:not(.scrolled) .logo {
  color: #ffffff !important;
}

/* PRICE TAGS ON CARDS IN LIGHT MODE */
body.light-mode .price {
  background-color: var(--primary) !important;
  color: #1C1008 !important;
}
body.light-mode .price span {
  color: #1C1008 !important;
}

/* FIX DARK SECTIONS IN LIGHT MODE */
body.light-mode .dark {
  background-color: #F5F0E8 !important;
  color: #1C1008 !important;
}
body.light-mode .dark .section-title {
  color: #1C1008 !important;
}

/* DATE INPUT TEXT FIX */
input[type="date"] {
  color: #fefefe;
}
body.light-mode input[type="date"] {
  color: #1C1008 !important;
}
::-webkit-calendar-picker-indicator {
  filter: invert(1);
}
body.light-mode ::-webkit-calendar-picker-indicator {
  filter: none;
}
"""

if "/* CONTACT FORM BORDERS IN LIGHT MODE */" not in css:
    with open(css_file, "a") as f:
        f.write(fixes)

# 2. Fix HTML Templates
for html_file in glob.glob("app/templates/*.html"):
    with open(html_file, "r") as f:
        html = f.read()
    
    # Fix 'color: inherit' issues by reverting them back to --light so they are visible in dark mode
    html = html.replace('color: inherit;', 'color: var(--light);')
    html = html.replace('color:inherit;', 'color: var(--light);')
    
    # Change any red danger buttons from #e74c3c to #5A1E1E
    html = html.replace('background: #e74c3c;', 'background: #5A1E1E;')
    html = html.replace('background:#e74c3c;', 'background: #5A1E1E;')
    
    # Replace instances where class="btn-danger" is used without the inline style
    html = html.replace('class="btn-danger">', 'class="btn-danger" style="background:#5A1E1E; color:#fefefe; border:none; padding:0.5rem 1rem; border-radius:5px; cursor:pointer;">')
    html = html.replace('class="btn-danger"', 'class="btn-danger" style="background:#5A1E1E; color:#fefefe; border:none; padding:0.5rem 1rem; border-radius:5px; cursor:pointer;"')

    # Fix class="btn-danger" style="..." repetition
    html = html.replace('style="background:#5A1E1E; color:#fefefe; border:none; padding:0.5rem 1rem; border-radius:5px; cursor:pointer;" style=', 'style=')


    with open(html_file, "w") as f:
        f.write(html)

print("Fixed CSS and HTML colors explicitly!")
