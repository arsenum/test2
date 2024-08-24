# Use BusyBox 1.36.1 (glibc) on Debian 12 as the base image
FROM busybox:1.36.1-glibc





# Create a simple script to print "Hello, World!"
RUN echo 'echo "Hello, World!"' > /hello.sh

# Make the script executable
RUN chmod +x /hello.sh

# Set the script as the entry point
ENTRYPOINT ["/hello.sh"]
