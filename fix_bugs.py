import os
import re

# 1. Update auth.py for 30 days expiration
with open("app/auth.py", "r") as f:
    auth_code = f.read()
auth_code = auth_code.replace("timedelta(minutes=15)", "timedelta(days=30)")
with open("app/auth.py", "w") as f:
    f.write(auth_code)

# 2. Update main.py for max_age and Base64 images
with open("app/main.py", "r") as f:
    main_code = f.read()

# Add import base64 if not exists
if "import base64" not in main_code:
    main_code = main_code.replace("import os", "import os\nimport base64")

# Update cookies
main_code = main_code.replace('httponly=True)', 'httponly=True, max_age=2592000)')

# Replace token logic if it's broken
old_add_img = """        contents = await image.read()
        if len(contents) > 10 * 1024 * 1024:
            pass
        else:
            ext = image.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            save_dir = os.path.join(BASE_DIR, "static", "images")
            save_path = os.path.join(save_dir, unique_filename)
            try:
                with open(save_path, "wb") as f_out:
                    f_out.write(contents)
                final_image_url = f"/static/images/{unique_filename}"
            except Exception as e:
                print("Upload error:", e)
                pass"""

new_add_img = """        contents = await image.read()
        if len(contents) <= 5 * 1024 * 1024:  # up to 5MB
            ext = image.filename.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
            encoded = base64.b64encode(contents).decode('utf-8')
            final_image_url = f"data:{mime};base64,{encoded}"
        else:
            print("File too large for Base64 Vercel encoding")"""

main_code = main_code.replace(old_add_img, new_add_img)

old_edit_img = """            contents = await image.read()
            if len(contents) <= 10 * 1024 * 1024:
                ext = image.filename.split('.')[-1]
                unique_filename = f"{uuid.uuid4().hex}.{ext}"
                try:
                    save_path = os.path.join(BASE_DIR, "static", "images", unique_filename)
                    with open(save_path, "wb") as f_out:
                        f_out.write(contents)
                    room.image_url = f"/static/images/{unique_filename}"
                except: pass"""

new_edit_img = """            contents = await image.read()
            if len(contents) <= 5 * 1024 * 1024:
                ext = image.filename.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                encoded = base64.b64encode(contents).decode('utf-8')
                room.image_url = f"data:{mime};base64,{encoded}"
            else:
                pass"""

main_code = main_code.replace(old_edit_img, new_edit_img)

with open("app/main.py", "w") as f:
    f.write(main_code)

# 3. Fix CSS for Autofill
css_to_add = """
/* Autofill Background Override */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active{
    -webkit-background-clip: text;
    -webkit-text-fill-color: var(--light) !important;
    transition: background-color 5000s ease-in-out 0s;
    box-shadow: inset 0 0 20px 20px transparent;
}

body.light-mode input:-webkit-autofill,
body.light-mode input:-webkit-autofill:hover, 
body.light-mode input:-webkit-autofill:focus, 
body.light-mode input:-webkit-autofill:active{
    -webkit-text-fill-color: #1C1008 !important;
}
"""

with open("app/static/css/style.css", "r") as f:
    css = f.read()

if "Autofill Background Override" not in css:
    with open("app/static/css/style.css", "w") as f:
        f.write(css + "\n" + css_to_add)

print("Applied persistent sessions, base64 Vercel image upload, and autofill CSS.")
