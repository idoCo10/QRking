import os
import base64
import py7zr
from pyzbar.pyzbar import decode
from PIL import Image
import sys

base_path = os.path.join(os.getenv("USERPROFILE"), "Desktop", "Scripts", "QRking")
output_file = os.path.join(base_path, "PostQRCompressed.7z") # The output is compressed file
input_folder = os.path.join(base_path, "QR-Encoded")



def decode_qr_image(image_path):
    """Decodes a single QR image using pyzbar."""
    img = Image.open(image_path)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')  # Decode as UTF-8 string
    return None  # No QR code detected


def recreate_compressed_file_from_qrs(input_folder, output_file):
    """Decodes QR codes and reconstructs the compressed file."""
    # Get all QR code images and sort them in numerical order
    qr_files = sorted(
        [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.png')],
        key=lambda x: int(os.path.splitext(os.path.basename(x))[0])  # Sort by numerical order
    )

    if not qr_files:
        print("No QR codes found in the folder.")
        return

    file_data = bytearray()

    # Decode each QR code and extract the base64-encoded data
    total_files = len(qr_files)
    for i, qr_file in enumerate(qr_files):
        data = decode_qr_image(qr_file)
        if data:
            try:
                decoded_chunk = base64.b64decode(data)  # Decode base64 data to binary
                file_data.extend(decoded_chunk)
                print(f"Decoded QR code: {qr_file}")
            except Exception as e:
                print(f"Failed to decode base64 from {qr_file}: {e}")
        else:
            print(f"Failed to decode {qr_file}. Trying next QR.")

        # Calculate and display progress
        progress = (i + 1) / total_files * 100  # Corrected to show progress for each QR
        sys.stdout.write(f"\rProgress: {progress:.2f}% - QR {i + 1} of {total_files}")
        sys.stdout.flush()  # Ensure the progress gets printed immediately

    print()  # To move to a new line after the progress bar is finished

    # Write the decoded file to the output compressed file
    if file_data:
        with open(output_file, 'wb') as f:
            f.write(file_data)
        print(f"Recreated compressed file saved as: {output_file}")
    else:
        print("No data was decoded. Unable to recreate file.")


def decompress_file(compressed_file, base_path):
    """Decompresses the 7z file, renames the extracted file, and deletes the compressed file."""
    with py7zr.SevenZipFile(compressed_file, mode='r') as archive:
        file_names = archive.getnames()  # Get the names of files inside the archive
        archive.extractall(path=base_path)

    if file_names:
        original_file_name = file_names[0]  # Assuming there's only one file inside the archive
        base_name, ext = os.path.splitext(original_file_name)
        decoded_file_name = f"{base_name}_decoded{ext}"
        original_path = os.path.join(base_path, original_file_name)
        decoded_path = os.path.join(base_path, decoded_file_name)

        # Rename the file to include "_decoded"
        os.rename(original_path, decoded_path)
        print(f"Decompressed file renamed to: {decoded_path}")
    else:
        print("No files found inside the archive.")

    # Delete the compressed file after extraction
    if os.path.exists(compressed_file):
        os.remove(compressed_file)
        print(f"Deleted compressed file: {compressed_file}")


def main():
    recreate_compressed_file_from_qrs(input_folder, output_file)  # Recreate the compressed file from QR codes
    decompress_file(output_file, base_path)  # Decompress the file, rename it, and delete the .7z file


if __name__ == "__main__":
    main()
