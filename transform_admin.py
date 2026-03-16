import re

with open("app/templates/admin.html", "r") as f:
    html = f.read()

# I want to inject an elegant dashboard overview at the top.
# For this, we'll find the title 'Dashboard Overview' and prepend an overview section.

overview_html = """
        <div class="admin-overview" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="card admin-card" style="text-align: center; border-bottom: 3px solid var(--primary);">
                <h4 style="color:#aaa; font-size: 0.9rem; text-transform: uppercase;">Total Rooms</h4>
                <div style="font-size: 2.5rem; font-family: 'Syncopate', sans-serif; margin-top: 0.5rem;">{{ rooms|length }}</div>
            </div>
            <div class="card admin-card" style="text-align: center; border-bottom: 3px solid var(--primary);">
                <h4 style="color:#aaa; font-size: 0.9rem; text-transform: uppercase;">Total Bookings</h4>
                <div style="font-size: 2.5rem; font-family: 'Syncopate', sans-serif; margin-top: 0.5rem;">{{ bookings|length }}</div>
            </div>
            <div class="card admin-card" style="text-align: center; border-bottom: 3px solid var(--primary);">
                <h4 style="color:#aaa; font-size: 0.9rem; text-transform: uppercase;">Registered Users</h4>
                <div style="font-size: 2.5rem; font-family: 'Syncopate', sans-serif; margin-top: 0.5rem;">{{ users|length }}</div>
            </div>
            <div class="card admin-card" style="text-align: center; border-bottom: 3px solid var(--primary);">
                <h4 style="color:#aaa; font-size: 0.9rem; text-transform: uppercase;">Revenue</h4>
                <div style="font-size: 2.5rem; font-family: 'Syncopate', sans-serif; margin-top: 0.5rem;">${{ bookings|sum(attribute='total_price') }}</div>
            </div>
        </div>
"""

# Only add if it's not already there
if 'class="admin-overview"' not in html:
    html = html.replace('<h2 style="font-family:\'Syncopate\', sans-serif; margin-bottom:2rem;">Dashboard Overview</h2>', 
                        '<h2 style="font-family:\'Syncopate\', sans-serif; margin-bottom:2rem;">Admin Dashboard</h2>\n' + overview_html)


# Fix the modal styling which was clunky. 
# We need to target the edit modal elements specifically.
modal_style = '''
    <style>
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.8);
            backdrop-filter: blur(8px);
        }
        .modal-content {
            background-color: var(--dark);
            margin: 10% auto;
            padding: 3rem;
            border: 1px solid var(--primary);
            width: 90%;
            max-width: 500px;
            border-radius: 12px;
            position: relative;
            box-shadow: 0 25px 50px rgba(0,0,0,0.5);
            color: var(--light);
        }
        .close {
            color: var(--primary);
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            transition: color 0.3s;
        }
        .close:hover,
        .close:focus {
            color: #fff;
            text-decoration: none;
        }
        /* Specific input overrides for the modal to make it sleek */
        .modal-content input[type="text"], 
        .modal-content input[type="number"], 
        .modal-content textarea {
            background-color: rgba(255,255,255,0.03);
            border: none;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            border-radius: 4px 4px 0 0;
            color: var(--light);
            padding: 1rem;
            transition: all 0.3s;
        }
        .modal-content input:focus, 
        .modal-content textarea:focus {
            border-bottom: 2px solid var(--primary);
            outline: none;
            background-color: rgba(255,255,255,0.06);
        }
        .modal-content label {
            color: var(--primary);
            font-family: 'Syncopate', sans-serif;
            font-size: 0.75rem;
            margin-bottom: 0.5rem;
        }
    </style>
'''

# Put it before </head> if not there
if '.modal {' not in html:
    html = html.replace('</head>', modal_style + '\n</head>')


with open("app/templates/admin.html", "w") as f:
    f.write(html)

print("Admin panel transformed!")
