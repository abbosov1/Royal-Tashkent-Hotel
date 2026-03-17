with open("app/templates/login.html", "r") as f:
    html = f.read()

# Make the labels explicitly white/light-beige so they are readable over the dark background
if "color: #F4EFEA !important;" not in html.split(".auth-input-group label")[1]:
    html = html.replace(
        ".auth-input-group label {",
        ".auth-input-group label { color: #F4EFEA !important;"
    )

# Force any remaining dark text definitions to pure white/light beige
html = html.replace("color: #1C1008 !important;", "color: #F4EFEA !important;")
html = html.replace("color: var(--light) !important;", "color: #F4EFEA !important;")

with open("app/templates/login.html", "w") as f:
    f.write(html)

with open("app/static/css/style.css", "r") as f:
    css = f.read()

# Replace all old transition delays which caused the white flash with the atomic background-clip fix
css += """
/* THE ULTIMATE ZERO-FLASH AUTOFILL OVERRIDE */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active {
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: #F4EFEA !important;
    transition: background-color 50000s ease-in-out 0s !important;
    box-shadow: inset 0 0 20px 20px transparent !important;
    caret-color: #F4EFEA !important;
}

body.light-mode input:-webkit-autofill,
body.light-mode input:-webkit-autofill:hover, 
body.light-mode input:-webkit-autofill:focus, 
body.light-mode input:-webkit-autofill:active {
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: #F4EFEA !important; 
    transition: background-color 50000s ease-in-out 0s !important;
    caret-color: #F4EFEA !important;
}
"""

with open("app/static/css/style.css", "w") as f:
    f.write(css)

print("CSS and HTML updated for login.")