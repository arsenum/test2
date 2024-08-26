# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app
RUN apt-get update && apt-get install -y wget \
    net-tools \
    ca-certificates \
    curl \
    gnupg \
    git\
    lsb-release

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg |  gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

RUN echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
focal stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# RUN apt-get update

RUN apt-get update && apt-get install -y docker-ce-cli

RUN wget https://dist.ipfs.io/go-ipfs/v0.7.0/go-ipfs_v0.7.0_linux-amd64.tar.gz
RUN tar -xvzf go-ipfs_v0.7.0_linux-amd64.tar.gz
RUN cd go-ipfs && \
	"./install.sh" && \
	cd .. && \
	ipfs init
# RUN echo "ipfs daemon &" >> ~/.bashrc
# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .
RUN chmod +x run.sh
# Set the command to run the application
# CMD ["python","/shared/server.py" ]
ENTRYPOINT ["/app/run.sh"]
