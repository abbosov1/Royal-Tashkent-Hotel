with open("app/templates/admin.html", "r") as f:
    text = f.read()

old_css = 'body.light-mode input[type="text"], body.light-mode input[type="number"], body.light-mode textarea { background: transparent !important; border: none !important; border-bottom: 2px solid #D4C4B0 !important; color: #1C1008 !important; border-radius: 0 !important; }'
new_css = 'body.light-mode input[type="text"], body.light-mode input[type="number"], body.light-mode input[type="email"], body.light-mode input[type="password"], body.light-mode textarea { background: transparent !important; border: none !important; border-bottom: 2px solid #D4C4B0 !important; color: #1C1008 !important; border-radius: 0 !important; outline: none !important; box-shadow: none !important; }'
text = text.replace(old_css, new_css)

# Also let's make sure the base inputs have no border anywhere
text = text.replace('border: none;\n            border-bottom: 2px solid rgba(255,255,255,0.2);', 'border: none !important;\n            border-bottom: 2px solid rgba(255,255,255,0.2) !important;\n            box-shadow: none !important;\n            outline: none !important;')

with open("app/templates/admin.html", "w") as f:
    f.write(text)

with open("app/templates/login.html", "r") as f:
    text2 = f.read()
text2 = text2.replace('border: none; border-bottom: 2px solid rgba(255,255,255,0.2);', 'border: none !important; border-bottom: 2px solid rgba(255,255,255,0.2) !important; box-shadow: none !important; outline: none !important;')
text2 = text2.replace('border-bottom: 2px solid #D4C4B0 !important;', 'border: none !important; border-bottom: 2px solid #D4C4B0 !important; box-shadow: none !important; outline: none !important;')
with open("app/templates/login.html", "w") as f:
    f.write(text2)

with open("app/static/css/style.css", "r") as f:
    css = f.read()

# Let's fix the webkit-autofill background issue
old_autofill = '''input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active{
    -webkit-background-clip: text;
    -webkit-text-fill-color: var(--light) !important;
    transition: background-color 5000s ease-in-out 0s;
    box-shadow: inset 0 0 0 5000px transparent !important;
}

body.light-mode input:-webkit-autofill,
body.light-mode input:-webkit-autofill:hover, 
body.light-mode input:-webkit-autofill:focus, 
body.light-mode input:-webkit-autofill:active{
    -webkit-text-fill-color: #1C1008 !important;
}'''

new_autofill = '''input:-webkit-autofill,
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
}

/* Fallback for overriding autofill styles in standard modern CSS if Webkit tricks fail */
input:-webkit-autofill::first-line {
    font-family: 'Playfair Display', serif;
}
input:-internal-autofill-selected {
    background-color: transparent !important;
}'''

css = css.replace(old_autofill, new_autofill)
with open("app/static/css/style.css", "w") as f:
    f.write(css)

print("Done")