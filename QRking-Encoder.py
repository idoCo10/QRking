import os
import base64
import py7zr
import qrcode


base_path = os.path.join(os.getenv("USERPROFILE"), "Desktop", "Scripts", "QRking")
compressed_file = os.path.join(base_path, "PreQRCompressed.7z")
output_folder = os.path.join(base_path, "QR-Encoded")

file = os.path.join(base_path, "test.mp4")



def compress_file(input_file, output_archive):
    """Compress only the file into a .7z archive using py7zr."""
    with py7zr.SevenZipFile(output_archive, 'w') as archive:
        archive.write(input_file, arcname=os.path.basename(input_file))  # Compress only the file
    print(f"File compressed to: {output_archive}")

def encode_file_to_qr(file, output_folder, chunk_size=1000):
    """Encode a file into multiple QR codes."""
    with open(file, 'rb') as f:
        file_data = f.read()

    # Encode the file into base64
    encoded_data = base64.b64encode(file_data).decode('utf-8')

    # Split the encoded data into chunks
    chunks = [encoded_data[i:i + chunk_size] for i in range(0, len(encoded_data), chunk_size)]

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate QR codes for each chunk
    for i, chunk in enumerate(chunks):
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_M
        )
        try:
            qr.add_data(chunk)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(os.path.join(output_folder, f"{i + 1}.png"))
        except ValueError as e:
            print(f"Failed to encode chunk {i + 1} into a QR code. Error: {e}")
            continue

        # Show progress
        progress = (i + 1) / len(chunks) * 100
        print(f"Progress: {progress:.2f}% - QR {i + 1} of {len(chunks)} created.")

    print(f"File encoded into {len(chunks)} QR codes in: {output_folder}")

def main():
    compress_file(file, compressed_file)  # Compress the original file only
    encode_file_to_qr(compressed_file, output_folder)  # Then encode the compressed file into QR codes

    # Delete the compressed file after QR code generation
    if os.path.exists(compressed_file):
        os.remove(compressed_file)
        print(f"Temporary compressed file deleted: {compressed_file}")

if __name__ == "__main__":
    main()
