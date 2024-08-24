# image_processing.py
from PIL import Image
import numpy as np

def convert_to_gray_with_opacity(image, output_image_path="processed_image.png"):
    # Convert numpy array to PIL Image if necessary
    if isinstance(image, str):
        pil_image = Image.open(image)
    else:
        pil_image = Image.fromarray(image)

    # Convert to grayscale
    gray_image = pil_image.convert("L")
    # Convert to RGBA
    rgba_image = gray_image.convert("RGBA")
    # Set opacity to 0.5
    alpha = rgba_image.split()[3]
    alpha = alpha.point(lambda p: p * 0.5)
    rgba_image.putalpha(alpha)

    # Save the processed image
    rgba_image.save(output_image_path)
    
    # Convert back to numpy array for Gradio
    processed_image = np.array(rgba_image)
    
    return processed_image, output_image_path