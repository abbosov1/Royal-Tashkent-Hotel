with open("app/templates/index.html", "r", encoding="utf-8") as f:
    text = f.read()

amenities_block = """
                        <div style="font-size:0.8rem; margin:1rem 0; color:var(--primary); display:flex; flex-wrap:wrap; gap:10px;">
                            {% if 'wifi' in room.description.lower() or 'wi-fi' in room.description.lower() %}<span>📶 Free Wi-Fi</span>{% endif %}
                            {% if 'pool' in room.description.lower() %}<span>🏊 Private Pool</span>{% endif %}
                            {% if 'gym' in room.description.lower() %}<span>🏋️ Gym Access</span>{% endif %}
                            {% if 'breakfast' in room.description.lower() %}<span>🍳 Breakfast Included</span>{% endif %}
                            {% if 'tv' in room.description.lower() %}<span>📺 Smart TV</span>{% endif %}
                            {% if 'view' in room.description.lower() %}<span>🏙️ City View</span>{% endif %}
                            {% if 'jacuzzi' in room.description.lower() %}<span>🛁 Jacuzzi</span>{% endif %}
                            {% if 'terrace' in room.description.lower() %}<span>🌅 Terrace</span>{% endif %}
                        </div>"""

if "📶 Free Wi-Fi" not in text:
    text = text.replace("<p>{{ room.description }}</p>", f"<p>{{{{ room.description }}}}</p>{amenities_block}")

with open("app/templates/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Amenities added to index.html")
