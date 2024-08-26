import gradio as gr
from image_processing import convert_to_gray_with_opacity
import ipfshttpclient
import subprocess
import os
import shutil

# Declare global variables
sha256 = ""
tagname = ""
updated_contents = ""
script_dir =""
new_file_path = ""
def publish_to_github():
    try:
        # Add your GitHub repository URL and branch
        repo_url = 'https://github.com/arsenum/test2.git'
        branch = 'main'

        # Commands to push to GitHub
        subprocess.run(['git', 'config', '--global', 'user.email', 'you@example.com'])
        subprocess.run(['git', 'config', '--global', 'user.name', 'Your Name'])
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Automated commit'], check=True)
        # subprocess.run(['git', 'push', repo_url, branch], check=True)
        return "Publish completed."
    except subprocess.CalledProcessError as e:
        return

# Function to be called when the button is clicked
def build(input, output):
    global sha256, tagname, updated_contents,script_dir,new_file_path

    print("Build process started!")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, 'module_name.txt'), 'r') as file:
        module_name = file.read()
    tagname = module_name.strip()

    command = [
        "docker", "build",
        "-q",
        "-t", tagname,
        "-f", "/shared/Dockerfile",
        "."
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    print("docker build stdout:", result.stdout)
    print("docker build stderr:", result.stderr)
    sha256 = result.stdout.strip()

    template_file_path = os.path.join(script_dir, 'lilypad_module.json.template.tmpl')
    new_file_path = os.path.join(script_dir, 'lilypad_module.json.tmpl')

    with open(template_file_path, 'r') as file:
        file_contents = file.read()

    updated_contents = file_contents.replace('[IMAGE_PLACEHOLDER]', sha256)

    with open(new_file_path, 'w') as file:
        file.write(updated_contents)

    return sha256

def publish_build_to_ipfs():
    global sha256, tagname, updated_contents,script_dir,new_file_path

    docker_image = sha256.replace("sha256:", "") + ".tar"

    result = subprocess.run(["docker", "save", "-o", docker_image, tagname], capture_output=True, text=True)
    print("docker save stdout:", result.stdout)
    print("docker save stderr:", result.stderr)

    docker_image_path = os.path.abspath(docker_image)
    print("Docker image saved to:", docker_image_path)

    new_docker_image_path = os.path.join(script_dir, docker_image)
    shutil.copy(docker_image_path, new_docker_image_path)

    client = ipfshttpclient.connect()
    res = client.add(new_docker_image_path)
    cid = res['Hash']
    print("CID:", cid)
    updated_contents = updated_contents.replace('[IMAGE_CID]', cid)

    with open(new_file_path, 'w') as file:
        file.write(updated_contents)

    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    return cid

# Function to handle image processing and IPFS upload
def process_and_upload(image):
    processed_image, output_image_path = convert_to_gray_with_opacity(image)

    client = ipfshttpclient.connect()
    res = client.add(output_image_path)
    cid = res['Hash']

    return processed_image, output_image_path, cid

def run_on_lilypad_network(cid):
    try:
        result = subprocess.run(['python', 'cli.py', cid], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"

# Create the Gradio interface using gr.Blocks
with gr.Blocks() as demo:
    with gr.Row():
        image_input = gr.Image(label="Input Image")
        image_output = gr.Image(label="Output Image")
    with gr.Row():
        image_path_output = gr.Textbox(label="Image Path", interactive=False)
    with gr.Row():
        cid_output = gr.Textbox(label="IPFS CID", interactive=True)
    with gr.Row():
        image_input.change(fn=process_and_upload, inputs=image_input, outputs=[image_output, image_path_output, cid_output])

    with gr.Row():
        build_button = gr.Button("Build Lilypad Module")
        build_output = gr.Textbox(label="Build Output", interactive=False)
        build_button.click(build, inputs=[], outputs=[build_output])

    with gr.Row():
        publish_button = gr.Button("Publish Docker Image to IPFS")
        publish_output = gr.Textbox(label="Docker Image CID", interactive=False)
        publish_button.click(publish_build_to_ipfs, inputs=[], outputs=[publish_output])

    with gr.Row():
        publish_button = gr.Button("Publish Module to GitHub")
        publish_output = gr.Textbox(label="Publish Output")
        publish_button.click(publish_to_github, outputs=publish_output)

    with gr.Row():
        run_button = gr.Button("Run Module on Lilypad")
        run_output = gr.Textbox(label="Run Output")
        run_button.click(run_on_lilypad_network, inputs=cid_output, outputs=run_output)

    cid_input = gr.Textbox(label="Result CID")

print("Starting the app...")
demo.launch(server_name="0.0.0.0", server_port=7860)

