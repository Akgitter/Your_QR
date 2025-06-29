import requests
from PIL import Image, ImageDraw
import qrcode
import io
import base64
import os

class PersonalQRGenerator:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

    def generate_personal_qr(self, url, user_description):
        """
        Generate a personalized QR code with AI-generated imagery using Hugging Face
        
        Parameters:
        - url: The URL to encode
        - user_description: Prompt to generate background image
        
        Returns:
        - PIL Image object with the personalized QR code
        """
        ai_image = self._generate_ai_image(user_description)
        qr_img = self._create_qr_code(url)
        final_image = self._combine_images(ai_image, qr_img)
        return final_image

    def _generate_ai_image(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()

        image_data = response.content
        return Image.open(io.BytesIO(image_data)).convert("RGBA")

    def _create_qr_code(self, url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").get_image().convert("RGBA")

        new_data = []
        for item in img.getdata():
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        return img

    def _combine_images(self, background, qr_code, qr_scale=0.4, blend_strength=0.6):
        background = background.convert("RGBA")
        qr_code = qr_code.convert("RGBA")

        min_dimension = min(background.size)
        qr_size = int(min_dimension * qr_scale)

        qr_code = qr_code.resize((qr_size, qr_size), Image.LANCZOS)

        mask = Image.new("L", (qr_size, qr_size), 0)
        center = (qr_size // 2, qr_size // 2)
        max_radius = qr_size // 2

        for y in range(qr_size):
            for x in range(qr_size):
                dist = ((x - center[0])**2 + (y - center[1])**2)**0.5
                alpha = int(255 * blend_strength * (1 - dist / max_radius))
                mask.putpixel((x, y), max(alpha, 50))

        position = (
            (background.width - qr_size) // 2,
            (background.height - qr_size) // 3
        )

        region = background.crop((position[0], position[1], position[0] + qr_size, position[1] + qr_size))
        blended = Image.composite(qr_code, region, mask)
        background.paste(blended, position, mask)

        return background
