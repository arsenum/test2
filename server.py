import gradio as gr
from image_processing import convert_to_gray_with_opacity
import ipfshttpclient
import subprocess
import os
import shutil

# Function to be called when the button is clicked
def build(input,output):
    print("Build process started!")
    #docker build -f C:\\Users\\arsen\\repos\\electron\\LilypadWorkbench\\shared\\gradio\\test2_module\\Dockerfile C:\\Users\\arsen\\repos\\electron\\LilypadWorkbench\\shared\\gradio\\test2_module
    command = [
    "docker", "build",
    "-q",
    "-f","/shared/Dockerfile",
      "."
    #"-f", "C:\\Users\\arsen\\repos\\electron\\LilypadWorkbench\\shared\\gradio\\test2_module\\Dockerfile",
    # "C:\\Users\\arsen\\repos\\electron\\LilypadWorkbench\\shared\\gradio\\test2_module"
]

    result = subprocess.run(command, capture_output=True, text=True)
    print("docker build stdout:", result.stdout)
    print("docker build stderr:", result.stderr)
   
    sha256 = result.stdout.strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # script_directory = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

    # Define the path to the template file and the new file
    template_file_path = os.path.join(script_dir, 'lilypad_module.json.template.tmpl')
    new_file_path = os.path.join(script_dir, 'lilypad_module.json.tmpl')


    # Read the contents of the template file
    with open(template_file_path, 'r') as file:
        file_contents = file.read()

    # Replace the placeholder with the sha256 value
    # sha256 = "your_sha256_value_here"  # Replace this with the actual sha256 value
    updated_contents = file_contents.replace('[IMAGE_PLACEHOLDER]', sha256)
    # updated_contents = updated_contents.replace('[JOB_NAME_PLACEHOLDER]', script_directory)


    # print(f"Replaced [IMAGE_PLACEHOLDER] with {sha256} and saved to {new_file_path}")



    #.replace("sha256:","") +".tar"
    docker_image = sha256.replace("sha256:","") +".tar"

    # result = subprocess.run(["docker", "save","-o", result.stdout.strip().replace("sha256:","") +".tar",  result.stdout.strip()], capture_output=True, text=True)
    result = subprocess.run(["docker", "save","-o", docker_image,  sha256], capture_output=True, text=True)
    print("docker save stdout:", result.stdout)
    print("docker save stderr:", result.stderr)

    docker_image_path = os.path.abspath(docker_image)
    print("Docker image saved to:", docker_image_path)

    # Move the docker_image file to the script directory


    new_docker_image_path = os.path.join(script_dir, docker_image)
    shutil.copy(docker_image_path, new_docker_image_path)

    client = ipfshttpclient.connect()
    res = client.add(new_docker_image_path)
    cid = res['Hash']
    # print("docker save stdout:", result.stdout)
    # print("docker save stdout:", result.stdout)
    print("CID:",cid)
    updated_contents = updated_contents.replace('[IMAGE_CID]', cid)

    # Write the updated contents to the new file
    with open(new_file_path, 'w') as file:
        file.write(updated_contents)

    # output = result.stdout
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    return sha256, cid
# Function to handle image processing and IPFS upload
def process_and_upload(image):
    processed_image, output_image_path = convert_to_gray_with_opacity(image)

    # Add the image to IPFS
    client = ipfshttpclient.connect()
    res = client.add(output_image_path)
    cid = res['Hash']

    return processed_image, output_image_path, cid

# Create the Gradio interface using gr.Blocks
with gr.Blocks() as demo:
    # Image processing interface
    with gr.Row():
        image_input = gr.Image(label="Input Image")
        image_output = gr.Image(label="Output Image")
    with gr.Row():
        image_path_output = gr.Textbox(label="Image Path", interactive=False)
        cid_output = gr.Textbox(label="IPFS CID", interactive=False)
        image_input.change(fn=process_and_upload, inputs=image_input, outputs=[image_output, image_path_output, cid_output])

    # Display Gradio version
    # gr.Textbox(value=get_gradio_version(), label="Gradio Version", interactive=False)

    # Build button and output
    build_output = gr.Textbox(label="Build Output", interactive=False)
    gr.Button("Build Lilypad Module").click(build, inputs=[], outputs=[build_output])
    # , outputs=build_output)

print("Starting the app...")
demo.launch(server_name="0.0.0.0", server_port=7860)

