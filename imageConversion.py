import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def decode_base64_to_image(encoded_string, output_path):
    with open(output_path, "wb") as output_file:
        output_file.write(base64.b64decode(encoded_string))

# # Example usage for encoding:
# image_path = 'asd.jpg'
# encoded_image = encode_image_to_base64(image_path)

# # Now you can send encoded_image as a dictionary value
# message_dict = {
#     "image_data": encoded_image
# }

# # Example usage for decoding:
# received_dict = {
#     "image_data": encoded_image  # Replace with the actual base64 encoded image string
# }

# encoded_image = received_dict["image_data"]
# output_path = 'decoded_image.jpg'
# decode_base64_to_image(encoded_image, output_path)