import re

with open("app/templates/admin.html", "r") as f:
    html = f.read()

# Replace the whole <style> inside admin.html to make it absolutely gorgeous.
new_style = """
    <style>
        body { background: var(--dark); color: var(--light); padding-top: 100px; font-family: 'Playfair Display', serif; }
        .admin-container { max-width: 1300px; margin: 0 auto; padding: 2rem; }
        
        /* Modern Cards */
        .card { 
            background: rgba(255,255,255,0.03); 
            padding: 2.5rem; 
            border-radius: 16px; 
            border: 1px solid rgba(255,255,255,0.05); 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.4); }

        h2, h3, h4 { font-family: 'Syncopate', sans-serif; letter-spacing: 1px; color: var(--primary); }

        /* Widgets */
        .admin-overview { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }
        .widget { background: rgba(255,255,255,0.02); border-left: 3px solid var(--primary); padding: 1.5rem; border-radius: 8px; }
        .widget-title { color: #888; font-size: 0.75rem; text-transform: uppercase; font-family: 'Syncopate', sans-serif; letter-spacing: 2px; margin-bottom: 0.5rem; }
        .widget-value { font-size: 2.2rem; font-weight: bold; color: var(--light); font-family: 'Playfair Display', serif; }

        /* Grids */
        .grid-2 { display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; margin-bottom: 3rem; }

        /* Form Controls */
        .form-group { margin-bottom: 1.5rem; position: relative; }
        label { display: block; font-size: 0.75rem; font-family: 'Syncopate', sans-serif; text-transform: uppercase; color: var(--primary); margin-bottom: 0.8rem; letter-spacing: 1px; }
        input[type="text"], input[type="number"], textarea { 
            width: 100%; 
            padding: 1rem 1.2rem; 
            background: rgba(255,255,255,0.03); 
            border: 1px solid rgba(255,255,255,0.08); 
            color: var(--light); 
            border-radius: 8px; 
            font-family: inherit;
            font-size: 1rem;
            transition: all 0.3s; 
        }
        input:focus, textarea:focus { outline: none; border-color: var(--primary); background: rgba(255,255,255,0.06); box-shadow: 0 0 0 4px rgba(203, 168, 124, 0.1); }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 1.2rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        th { color: #888; font-family: 'Syncopate', sans-serif; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        tr { transition: background 0.3s; }
        tr:hover { background: rgba(255,255,255,0.02); }

        /* Room Items */
        .room-item {
            display: flex; justify-content: space-between; align-items: center; 
            padding: 1.2rem; margin-bottom: 1rem; background: rgba(255,255,255,0.02); 
            border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; transition: all 0.3s;
        }
        .room-item:hover { background: rgba(255,255,255,0.04); border-color: var(--primary); }
        .room-title { font-size: 1.2rem; font-family: 'Playfair Display', serif; color: var(--light); }
        .room-price { font-size: 0.9rem; color: var(--primary); font-family: 'Syncopate', sans-serif; margin-top: 0.3rem;}

        /* Custom Modal Styling */
        #editModal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); z-index: 2000;
            justify-content: center; align-items: center;
        }
        .modal-content {
            background: var(--dark); padding: 3rem; border-radius: 16px; 
            border: 1px solid rgba(203, 168, 124, 0.3); width: 100%; max-width: 550px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6); position: relative;
        }
        .close-btn {
            position: absolute; top: 20px; right: 20px; font-size: 1.8rem; cursor: pointer; color: #888; transition: color 0.3s;
        }
        .close-btn:hover { color: var(--primary); }

        button.action-btn { background: transparent; color: var(--light); border: 1px solid rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 30px; cursor: pointer; transition: all 0.3s; font-family: 'Syncopate', sans-serif; font-size: 0.7rem; text-transform: uppercase; }
        button.action-btn:hover { background: var(--primary); color: var(--dark); border-color: var(--primary); }
        
        .btn-danger { background: #5A1E1E !important; color: white !important; border: none; padding: 0.5rem 1rem; border-radius: 30px; cursor: pointer; font-family: 'Syncopate', sans-serif; font-size: 0.7rem; text-transform: uppercase; transition: all 0.3s; }
        .btn-danger:hover { background: #E74C3C !important; box-shadow: 0 5px 15px rgba(231,76,60,0.3); }

        /* Light Mode Overrides for these specific elements handled in global stylesheet, but ensure local inputs stay neat */
        body.light-mode .card, body.light-mode .widget { background: #ffffff; border: 1px solid #E8DDD0; box-shadow: 0 10px 25px rgba(0,0,0,0.06); }
        body.light-mode .widget-value, body.light-mode .room-title { color: #1C1008; }
        body.light-mode input[type="text"], body.light-mode input[type="number"], body.light-mode textarea { background: #fff; border: 1px solid #E8DDD0; color: #1C1008; }
        body.light-mode .room-item { background: #fff; border: 1px solid #E8DDD0; }
        body.light-mode .room-item:hover { background: #fdfbf7; border-color: var(--primary); }
        body.light-mode table th { border-bottom: 1px solid #E8DDD0;}
        body.light-mode td { border-bottom: 1px solid #E8DDD0; color: #1C1008;}
        body.light-mode tr:hover { background: #fdfbf7; }
        body.light-mode .modal-content { background: #ffffff;  border: 1px solid var(--primary); }
    </style>
"""

# Apply styles
html = re.sub(r'<style>.*?</style>', new_style, html, flags=re.DOTALL)

# Re-structure the editModal specifically
old_modal = r'<div id="editModal".*?</form>\s*</div>\s*</div>'
new_modal = """
    <div id="editModal">
        <div class="modal-content">
            <span class="close-btn" onclick="document.getElementById('editModal').style.display='none'">&times;</span>
            <h3 style="margin-bottom:2rem; text-align:center;">Edit Room</h3>
            <form id="editForm" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Room Name</label>
                    <input type="text" name="name" id="editName" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" id="editDesc" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label>Price Per Night ($)</label>
                    <input type="number" name="price_per_night" id="editPrice" required>
                </div>
                <div class="form-group">
                    <label>New Image (optional)</label>
                    <div class="file-upload-wrapper">
                        <label class="file-upload-btn" for="fileInput_edit">Choose Image</label>
                        <span class="file-upload-text" id="fileText_edit">No file chosen</span>
                        <input type="file" name="image" id="fileInput_edit" class="file-upload-input" accept="image/*" onchange="document.getElementById('fileText_edit').innerText = this.files[0] ? this.files[0].name : 'No file chosen'">
                    </div>
                </div>
                <button type="submit" class="btn-primary" style="width:100%; margin-top:1.5rem; border-radius: 8px; padding: 1.2rem;">Update Room Details</button>
            </form>
        </div>
    </div>
"""
html = re.sub(old_modal, new_modal, html, flags=re.DOTALL)

# Let's fix the "Overview" section. Wait, we injected it in transform_admin.py, so it might exist. Let's rebuild the main layout inside body just to be sure
# Actually, I'll just rely on what's there but convert "Total Rooms" style into "widget" class.
html = html.replace('class="card admin-card" style="text-align: center; border-bottom: 3px solid var(--primary);"', 'class="widget"')
html = html.replace('class="admin-overview" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;"', 'class="admin-overview"')
html = html.replace('<h4 style="color:#aaa; font-size: 0.9rem; text-transform: uppercase;">', '<div class="widget-title">')
html = html.replace('</h4>', '</div>')
html = html.replace('<div style="font-size: 2.5rem; font-family: \'Syncopate\', sans-serif; margin-top: 0.5rem;">', '<div class="widget-value">')

# Modify the buttons in Manage Rooms to look sleeker
html = html.replace('style="padding:0.5rem 1rem; font-size:0.8rem; border:none; cursor:pointer;"', 'class="action-btn"')
html = html.replace('class="btn-danger" style="background:#5A1E1E; color:#fefefe; border:none; padding:0.5rem 1rem; border-radius:5px; cursor:pointer;"', 'class="btn-danger"')
# Make inner divs in room-item sleeker
html = html.replace('<div>\n                            <strong>{{ room.name }}</strong>', '<div class="room-info">\n                            <div class="room-title">{{ room.name }}</div>')
html = html.replace('<div style="font-size:0.8rem; color:#aaa;">${{ room.price_per_night }} / night</div>', '<div class="room-price">${{ room.price_per_night }} / night</div>')


with open("app/templates/admin.html", "w") as f:
    f.write(html)
print("Updated admin.html with modern widgets and smooth inputs")
