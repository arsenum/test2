import sys
import os
import ipfshttpclient
from image_processing import convert_to_gray_with_opacity

def download_from_ipfs(cid, output_path):
    client = ipfshttpclient.connect()
    client.get(cid, target=output_path)
    return output_path + "/" + cid

def main():
    if len(sys.argv) != 2:
        print("Usage: python cli.py <ipfs_cid>")
        sys.exit(1)

    ipfs_cid = sys.argv[1]

    # Define the output directory and default output image name
    output_dir = "images/output"
    os.makedirs(output_dir, exist_ok=True)
    output_image_path = os.path.join(output_dir, "processed_image.png")

    # Download the image from IPFS
    input_image_path = download_from_ipfs(ipfs_cid, "downloaded_image")

    # Process the image
    print(f"Processing image {input_image_path} ...")
    convert_to_gray_with_opacity(input_image_path, output_image_path)
    print(f"Processed image saved to {output_image_path}")

if __name__ == "__main__":
    main()
