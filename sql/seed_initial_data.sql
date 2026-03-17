-- Seed rooms and promo codes without relying on hardcoded app data.
-- Run inside DB container:
-- docker exec -i royal_tashkent_hotel_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < sql/seed_initial_data.sql

INSERT INTO rooms (name, description, price_per_night, image_url)
SELECT 'Deluxe Oasis', 'Plush king-size bed, city view.', 120, '/static/images/room1.jpg'
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE name = 'Deluxe Oasis');

INSERT INTO rooms (name, description, price_per_night, image_url)
SELECT 'Executive Suite', 'Panoramic views, exclusive lounge access.', 250, '/static/images/room2.jpg'
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE name = 'Executive Suite');

INSERT INTO rooms (name, description, price_per_night, image_url)
SELECT 'Royal Penthouse', 'Ultimate luxury. Private terrace, jacuzzi.', 800, '/static/images/room3.jpg'
WHERE NOT EXISTS (SELECT 1 FROM rooms WHERE name = 'Royal Penthouse');

INSERT INTO promo_codes (code, discount_percent, is_active)
SELECT 'ROYAL10', 10, TRUE
WHERE NOT EXISTS (SELECT 1 FROM promo_codes WHERE code = 'ROYAL10');

INSERT INTO promo_codes (code, discount_percent, is_active)
SELECT 'VIP15', 15, TRUE
WHERE NOT EXISTS (SELECT 1 FROM promo_codes WHERE code = 'VIP15');

INSERT INTO promo_codes (code, discount_percent, is_active)
SELECT 'WELCOME7', 7, TRUE
WHERE NOT EXISTS (SELECT 1 FROM promo_codes WHERE code = 'WELCOME7');
