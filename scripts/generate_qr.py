import qrcode
import os

def generate_museum_qrs():
    base_url = "https://museum-chatbott.onrender.com"
    artifacts = [
        {"id": 1, "name": "Ethnographic_Museum"},
        {"id": 2, "name": "King's_Palace_Museum"},
        {"id": 3, "name": "Museum_Ingabo"},
        {"id": 4, "name": "Campaign_Against_Genocide_Museum"},
        {"id": 5, "name": "National_History_Museum"},
        {"id": 6, "name": "Rwanda_Art_Museum"}
    ]

    output_dir = "qr_codes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating QR codes in {output_dir}...")

    for art in artifacts:
        # Create the specific URL for each artifact
        url = f"{base_url}/?id={art['id']}"
        
        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        filename = f"QR_{art['id']}_{art['name']}.png"
        path = os.path.join(output_dir, filename)
        img.save(path)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    generate_museum_qrs()
