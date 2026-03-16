import re
with open("app/templates/dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

replacement = """<p><strong>Check-out:</strong> {{ b.check_out_date.strftime('%Y-%m-%d') }}</p>
                    <p><strong>Total Price:</strong> ${{ b.total_price }}</p>
                    
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                        <form action="/dashboard/booking/reschedule/{{ b.id }}" method="POST" style="display:flex; flex-direction:column; gap:0.5rem; margin-bottom:1rem;">
                            <label style="font-size:0.8rem; color:#aaa; text-transform:uppercase;">Reschedule Dates</label>
                            <div style="display:flex; gap:0.5rem;">
                                <input type="date" name="new_check_in" required value="{{ b.check_in_date.strftime('%Y-%m-%d') }}" style="width:100%; padding:0.5rem; background:rgba(255,255,255,0.1); border:1px solid #555; color:#fff; border-radius:5px;">
                                <input type="date" name="new_check_out" required value="{{ b.check_out_date.strftime('%Y-%m-%d') }}" style="width:100%; padding:0.5rem; background:rgba(255,255,255,0.1); border:1px solid #555; color:#fff; border-radius:5px;">
                            </div>
                            <button type="submit" class="btn-primary" style="padding:0.5rem; font-size:0.8rem; border:none; cursor:pointer;">Update Dates</button>
                        </form>
                        
                        <form action="/dashboard/booking/cancel/{{ b.id }}" method="POST" onsubmit="return confirm('Are you sure you want to cancel this booking?');">
                            <button type="submit" style="width:100%; padding:0.5rem; background:#e74c3c; color:white; border:none; border-radius:5px; cursor:pointer;">Cancel Booking</button>
                        </form>
                    </div>
                </div>"""

text = re.sub(r'<p><strong>Check-out:</strong> \{\{ b\.check_out_date\.strftime\(\?'%Y-%m-%d\?'\)\s*\}\}</p>.*?</div>', replacement, text, flags=re.DOTALL)
with open("app/templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(text)
print("done")
