import glob

html_files = glob.glob("app/templates/*.html")
for path in html_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We replace inline color:#fff with color:inherit specifically inside input/form styling where it conflicts with light mode
    content = content.replace("color:#fff;", "color:inherit;")
    content = content.replace("color: white;", "color: inherit;")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("HTML inputs color cleaned.")