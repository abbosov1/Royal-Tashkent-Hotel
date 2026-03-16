import re

css_path = "app/static/css/style.css"
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

# Add placeholder styling for light mode
placeholder_css = """
body.light-mode input::placeholder,
body.light-mode textarea::placeholder {
  color: #94a3b8 !important;
}
"""

if "body.light-mode input::placeholder" not in css_content:
    css_content += "\n" + placeholder_css + "\n"

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)

print("Placeholders css updated.")
