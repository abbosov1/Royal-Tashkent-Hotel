with open("app/static/css/style.css", "r") as f:
    css = f.read()

# Fix the autofill properly with important flags and large shadow to overwrite default entirely
css = css.replace('box-shadow: inset 0 0 20px 20px transparent;', 'box-shadow: inset 0 0 0 5000px transparent !important;')

with open("app/static/css/style.css", "w") as f:
    f.write(css)

print("Autofill box shadow fixed!")