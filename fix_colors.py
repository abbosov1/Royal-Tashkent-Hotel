with open("app/templates/login.html", "r") as f:
    text = f.read()

# Make the text explicitly white even in light mode so it can be seen over the dark overlay
text = text.replace('color: #1C1008 !important;', 'color: var(--light) !important;')

with open("app/templates/login.html", "w") as f:
    f.write(text)

with open("app/static/css/style.css", "r") as f:
    css = f.read()

# Complete override of autofill styles
old_autofill = '''input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active {
    transition: background-color 5000s ease-in-out 0s !important;
    -webkit-text-fill-color: var(--light) !important;
    box-shadow: 0 0 0px 1000px transparent inset !important;
    background-color: transparent !important;
    background-image: none !important;
    color: var(--light) !important;
}

body.light-mode input:-webkit-autofill,
body.light-mode input:-webkit-autofill:hover, 
body.light-mode input:-webkit-autofill:focus, 
body.light-mode input:-webkit-autofill:active {
    transition: background-color 5000s ease-in-out 0s !important;
    -webkit-text-fill-color: #1C1008 !important;
    box-shadow: 0 0 0px 1000px transparent inset !important;
    background-color: transparent !important;
    background-image: none !important;
    color: #1C1008 !important;
}'''

new_autofill = '''/* Unbeatable transparent autofill override */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active {
    -webkit-transition-delay: 9999s !important;
    -webkit-transition: color 9999s ease-out, background-color 9999s ease-out !important;
    -webkit-text-fill-color: var(--light) !important;
    caret-color: var(--light) !important;
}

body.light-mode input:-webkit-autofill,
body.light-mode input:-webkit-autofill:hover, 
body.light-mode input:-webkit-autofill:focus, 
body.light-mode input:-webkit-autofill:active {
    -webkit-transition-delay: 9999s !important;
    -webkit-transition: color 9999s ease-out, background-color 9999s ease-out !important;
    -webkit-text-fill-color: #1C1008 !important;
    caret-color: #1C1008 !important;
}'''

# Replace it
css = css.replace(old_autofill, new_autofill)

# For login/register, force light text since the background is always dark
css += '''\n
.auth-container input:-webkit-autofill,
.auth-container input:-webkit-autofill:hover, 
.auth-container input:-webkit-autofill:focus, 
.auth-container input:-webkit-autofill:active {
    -webkit-transition-delay: 9999s !important;
    -webkit-transition: color 9999s ease-out, background-color 9999s ease-out !important;
    -webkit-text-fill-color: var(--light) !important;
    caret-color: var(--light) !important;
}
'''

with open("app/static/css/style.css", "w") as f:
    f.write(css)

print("Done")