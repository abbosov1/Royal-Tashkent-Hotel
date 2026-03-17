import re

# Fix admin.html styles (clean up duplicate <style> first)
with open("app/templates/admin.html", "r") as f:
    admin_html = f.read()

# Make sure all input types are styled correctly
admin_html = admin_html.replace(
    'input[type="text"], input[type="number"], textarea',
    'input[type="text"], input[type="number"], input[type="email"], input[type="password"], textarea'
)

with open("app/templates/admin.html", "w") as f:
    f.write(admin_html)

# Fix login background issue
with open("app/templates/login.html", "r") as f:
    login_html = f.read()

# Replace auth input group background with !important transparency
login_html = login_html.replace(
    "background: transparent;",
    "background: transparent !important;"
)

# And add specific light mode overrides directly in login to prevent global css interference
if "body.light-mode .auth-input-group input" not in login_html:
    login_html = login_html.replace('</style>', '''
        body.light-mode .auth-input-group input { 
            background: transparent !important; 
            border-bottom: 2px solid #D4C4B0 !important; 
            color: #1C1008 !important; 
        }
        body.light-mode .auth-input-group input:focus {
            border-bottom-color: var(--primary) !important;
        }
    </style>''')

with open("app/templates/login.html", "w") as f:
    f.write(login_html)

print("Done")
