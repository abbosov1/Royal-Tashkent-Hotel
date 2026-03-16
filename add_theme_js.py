import re

def update_templates():
    nav_item = r"""
                <li><a href="javascript:void(0)" onclick="toggleTheme()" id="theme-icon" style="cursor:pointer; font-size: 1.2rem;">☀️</a></li>
    """
    js_code = r"""
    <script>
        function setTheme(theme) {
            document.body.classList.toggle(light-mode, theme === light);
            localStorage.setItem(theme, theme);
            const icon = document.getElementById(theme-icon);
            if(icon) {
                icon.innerText = theme === light ? 🌙 : ☀️;
            }
        }

        function toggleTheme() {
            const currentTheme = localStorage.getItem(theme) || dark;
            const newTheme = currentTheme === light ? dark : light;
            setTheme(newTheme);
        }

        document.addEventListener(DOMContentLoaded, () => {
            const savedTheme = localStorage.getItem(theme) || dark;
            setTheme(savedTheme);
        });
    </script>
    """

    for filename in ["app/templates/index.html", "app/templates/admin.html", "app/templates/dashboard.html", "app/templates/login.html"]:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add theme toggle to header nav
        if "toggleTheme()" not in content:
            if "</ul>" in content:
                content = content.replace("</ul>", nav_item + "\n            </ul>")
        
        # Add JS before closing body
        if "function setTheme" not in content:
             content = content.replace("</body>", js_code + "\n</body>")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

update_templates()
print("JS updated in all templates.")
