from PIL import Image
import base64
import io
import os
import logging

def compress_image(image_path, quality=80):
    image = Image.open(image_path)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", optimize=True, quality=quality)
    return buffered.getvalue()

def encode_image_to_base64(image_path):
    compressed_image = compress_image(image_path)
    encoded_string = base64.b64encode(compressed_image).decode('utf-8')
    return encoded_string

def decode_base64_to_image(encoded_string, output_path):
    try:
        print("Decoding image:", output_path)
        decoded_bytes = base64.b64decode(encoded_string)
        img = Image.open(io.BytesIO(decoded_bytes))

        # Ensure the directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        img.save(output_path)
        print("Image saved to:", output_path)
    except Exception as e:
        print("something")
        logging.error(f"Error saving image {output_path}: {e}")

# Example usage
# encoded = encode_image_to_base64('input.jpg')
# decode_base64_to_image(encoded, 'output.jpg')