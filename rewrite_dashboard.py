import re

with open("app/templates/dashboard.html", "r") as f:
    html = f.read()

# Make the Dashboard look way more premium
new_style = """
    <style>
        body { background: var(--dark); color: var(--light); padding-top: 100px; font-family: 'Playfair Display', serif; }
        .dashboard-container { max-width: 1100px; margin: 0 auto; padding: 2rem; }
        .header-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(203, 168, 124, 0.2); padding-bottom: 2rem; margin-bottom: 3rem; }
        h2 { font-size: 2.5rem; letter-spacing: 1px; color: var(--light); }
        .booking-card { 
            background: rgba(255,255,255,0.02); padding: 2.5rem; border-radius: 12px; margin-bottom: 1.5rem; 
            display: grid; grid-template-columns: 1fr auto; gap: 2rem; align-items: start; 
            border: 1px solid rgba(255,255,255,0.05); transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); backdrop-filter: blur(10px);
        }
        .booking-card:hover { transform: translateY(-5px); border-color: rgba(203, 168, 124, 0.4); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }
        .booking-info h4 { font-family: 'Syncopate', sans-serif; font-size: 1.4rem; color: var(--primary); margin-bottom: 1rem; letter-spacing: 2px; text-transform: uppercase; }
        .booking-info p { color: #ccc; margin-bottom: 0.5rem; font-size: 1rem; }
        .alert.success { background: rgba(50, 255, 50, 0.1); border: 1px solid rgba(50, 255, 50, 0.3); padding: 1rem; text-align: center; border-radius: 8px; margin-bottom: 2rem; color: #a5d6a7; }
        
        .price-tag { font-size: 2rem; color: var(--primary); font-family: 'Playfair Display', serif; margin-bottom: 0.5rem; font-weight: bold; }
        .status-tag { font-size: 0.75rem; color: #aaa; text-transform: uppercase; letter-spacing: 2px; font-family: 'Syncopate', sans-serif; margin-bottom: 1.5rem; }

        .theme-input {
            width: 100%; padding: 0.8rem 1rem; background: rgba(255,255,255,0.03) !important; 
            border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 6px !important; color: var(--light) !important; 
            font-family: inherit; font-size: 0.9rem; transition: all 0.3s;
        }
        .theme-input:focus { border-color: var(--primary) !important; outline: none; background: rgba(255,255,255,0.06) !important; }

        .action-form { background: rgba(0,0,0,0.2); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); }
        .action-label { font-size: 0.75rem; color: var(--primary); text-transform: uppercase; font-family: 'Syncopate', sans-serif; letter-spacing: 1px; margin-bottom: 1rem; display: block; }

        button.btn-primary { border-radius: 30px; font-size: 0.8rem; padding: 0.8rem 1.5rem; transition: all 0.3s; text-transform: uppercase; letter-spacing: 1px; border: 1px solid transparent; }
        button.btn-primary:hover { box-shadow: 0 5px 15px rgba(203, 168, 124, 0.3); background: transparent; border-color: var(--primary); color: var(--primary); }

        .btn-danger { background: #5A1E1E !important; color: white !important; border: 1px solid transparent !important; padding: 0.8rem 1.5rem !important; border-radius: 30px !important; cursor: pointer; font-family: 'Syncopate', sans-serif; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s; width: 100%; }
        .btn-danger:hover { background: transparent !important; border-color: #E74C3C !important; color: #E74C3C !important; box-shadow: 0 5px 15px rgba(231,76,60,0.2); }

        /* Light Mode Overrides for these specific elements handled in global stylesheet, but ensure local inputs stay neat */
        body.light-mode .booking-card { background: #ffffff; border: 1px solid #E8DDD0; box-shadow: 0 10px 25px rgba(0,0,0,0.06); }
        body.light-mode h2, body.light-mode .booking-info p, body.light-mode .status-tag, body.light-mode .price-tag { color: #1C1008; }
        body.light-mode .theme-input { background: #fff !important; border: 1px solid #D4C4B0 !important; color: #1C1008 !important; }
        body.light-mode .action-form { background: #fdfbf7; border-color: #E8DDD0; }
        body.light-mode .btn-danger { background: #1C1008 !important; }
        body.light-mode .btn-danger:hover { background: #E74C3C !important; border-color: #E74C3C !important; color: #fff !important; }
        body.light-mode .btn-primary { color: #fff; background: var(--primary); }
    </style>
"""

# Apply styles
html = re.sub(r'<style>.*?</style>', new_style, html, flags=re.DOTALL)

# Refactor the bookings section slightly to match new layout properly
old_booking = r'<div style="text-align: right;">\s*<p style="font-size:1\.5rem; color:var\(--primary\)">\$\{\{ b\.total_price \}\}</p>\s*<p style="font-size:0\.8rem; color:#aaa;">Status: Confirmed</p>\s*<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba\(255,255,255,0\.1\); text-align:left;">\s*<form action="/dashboard/booking/reschedule/\{\{ b\.id \}\}" method="POST" style="display:flex; flex-direction:column; gap:0\.5rem; margin-bottom:1rem;">\s*<label style="font-size:0\.8rem; color:#aaa; text-transform:uppercase;">Reschedule</label>\s*<div style="display:flex; gap:0\.5rem;">\s*<input type="date" name="new_check_in" required value="\{\{ b\.check_in_date\.strftime\(\'%Y-%m-%d\'\) \}\}" style="width:100\%; padding:0\.5rem; background:rgba\(255,255,255,0\.1\); border:1px solid #555; border-radius:5px;" class="theme-input">\s*<input type="date" name="new_check_out" required value="\{\{ b\.check_out_date\.strftime\(\'%Y-%m-%d\'\) \}\}" style="width:100\%; padding:0\.5rem; background:rgba\(255,255,255,0\.1\); border:1px solid #555; border-radius:5px;" class="theme-input">\s*</div>\s*<button type="submit" class="btn-primary" style="padding:0\.5rem; font-size:0\.8rem; border:none; cursor:pointer;">Update Dates</button>\s*</form>\s*<form action="/dashboard/booking/cancel/\{\{ b\.id \}\}" method="POST" onsubmit="return confirm\(\'Are you sure you want to cancel this booking\?\'\);">\s*<button type="submit" style="width:100\%; padding:0\.5rem; background: #5A1E1E; color:white; border:none; border-radius:5px; cursor:pointer;">Cancel Booking</button>\s*</form>\s*</div>\s*</div>'

new_booking = """
                <div style="text-align: right;">
                    <div class="price-tag">${{ b.total_price }}</div>
                    <div class="status-tag">Status: Confirmed</div>
                    
                    <div class="action-form">
                        <form action="/dashboard/booking/reschedule/{{ b.id }}" method="POST" style="display:flex; flex-direction:column; gap:1rem; margin-bottom:1.5rem; text-align:left;">
                            <label class="action-label">Reschedule Stay</label>
                            <div style="display:flex; gap:0.5rem;">
                                <input type="date" name="new_check_in" required value="{{ b.check_in_date.strftime('%Y-%m-%d') }}" class="theme-input" title="Check In">
                                <input type="date" name="new_check_out" required value="{{ b.check_out_date.strftime('%Y-%m-%d') }}" class="theme-input" title="Check Out">
                            </div>
                            <button type="submit" class="btn-primary" style="width: 100%;">Update Dates</button>
                        </form>
                        
                        <form action="/dashboard/booking/cancel/{{ b.id }}" method="POST" onsubmit="return confirm('Are you sure you want to cancel this booking?');">
                            <button type="submit" class="btn-danger">Cancel Booking</button>
                        </form>
                    </div>
                </div>
"""

html = re.sub(old_booking, new_booking, html, flags=re.DOTALL)

with open("app/templates/dashboard.html", "w") as f:
    f.write(html)
print("Updated dashboard.html styled completely")
