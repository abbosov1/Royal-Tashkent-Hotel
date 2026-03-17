import re

with open("app/templates/admin.html", "r") as f:
    html = f.read()

# Change the grid layout to single column so "Manage Rooms" expands fully.
html = html.replace(
    ".grid-2 { display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; margin-bottom: 3rem; }",
    ".grid-2 { display: grid; grid-template-columns: 1fr; gap: 2rem; margin-bottom: 3rem; }"
)

with open("app/templates/admin.html", "w") as f:
    f.write(html)
print("Updated admin layout grid")
