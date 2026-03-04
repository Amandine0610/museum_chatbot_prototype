import qrcode
import os

# Base URL for the frontend where the museum visitor will be directed
# Since the frontend runs on Port 5173, and we want to test on our local network:
# Note: Replace this with the actual IP if testing on a separate phone
base_url = "https://museum-chatbott.onrender.com"

museums = [
    {"name": "Ethnographic_Museum_Huye", "id": 1},
    {"name": "Kings_Palace_Nyanza", "id": 2},
    {"name": "Campaign_Against_Genocide_Kigali", "id": 5},
    {"name": "Museum_Ingabo", "id": 3},
    {"name": "Rwanda_Art_Museum", "id": 4},

]

os.makedirs("qr_codes", exist_ok=True)

for m in museums:
    # URL will pass the artifact/museum ID directly to the frontend
    url = f"{base_url}/?id={m['id']}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    filepath = f"qr_codes/{m['name']}_QR.png"
    img.save(filepath)
    print(f"✅ Generated QR Code for {m['name']} -> {url}")

print("\n🎉 All QR Codes generated in the 'qr_codes/' directory. Scan these with your phone during the demo!")
