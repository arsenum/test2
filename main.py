import gradio as gr
from PIL import Image



def convert_to_bw(image):
  # Convert numpy array to PIL Image
  pil_image = Image.fromarray(image)
  # Convert to grayscale
  gray_image = pil_image.convert("L")
  # Convert to RGBA
  rgba_image = gray_image.convert("RGBA")
  # Set opacity to 0.5
  alpha = rgba_image.split()[3]
  alpha = alpha.point(lambda p: p * 0.5)
  rgba_image.putalpha(alpha)
  return rgba_image




demo = gr.Interface(fn=convert_to_bw, inputs="image", outputs="image")
print("Starting the app.dd..")
demo.launch(server_name="0.0.0.0", server_port=7860)

