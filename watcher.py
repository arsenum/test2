import os
import time
import subprocess
import socket
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CombinedChangeHandler(FileSystemEventHandler):
    def __init__(self, app_command, pip_command, port, debounce_time=2):
        self.app_command = app_command
        self.pip_command = pip_command
        self.port = port
        self.app_process = None
        self.last_modified = 0
        self.debounce_time = debounce_time
        self.restart_in_progress = False
        self.restart_app()

    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def kill_process_on_port(self, port):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        print(f"Killing process {proc.pid} using port {port}")
                        proc.kill()
                        proc.wait()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def wait_for_port(self, port, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_port_available(port):
                return True
            self.kill_process_on_port(port)
            time.sleep(1)
        return False

    def restart_app(self):
        if self.restart_in_progress:
            return
        self.restart_in_progress = True
        if self.app_process:
            print("Terminating the app...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing the app...")
                self.app_process.kill()
                self.app_process.wait()
            time.sleep(1)  # Add a small delay to ensure the process is terminated
        print("Waiting for port to become available...")
        if self.wait_for_port(self.port):
            print("Starting the app...")
            self.app_process = subprocess.Popen(self.app_command, shell=True)
        else:
            print(f"Port {self.port} did not become available within the timeout period.")
        self.restart_in_progress = False

    def on_modified(self, event):
        print("Event detected")
        current_time = time.time()
        if event.src_path.endswith(".py") and (current_time - self.last_modified > self.debounce_time):
            self.last_modified = current_time
            print(f"{event.src_path} has been modified, restarting the app...")
            if event.src_path.endswith("requirements.txt"):
                print(f"{event.src_path} has been modified, running pip install...")
                subprocess.run(self.pip_command, shell=True)
            self.restart_app()

if __name__ == "__main__":
    path = "/shared"
    app_command = "python /shared/server.py"
    pip_command = "pip install --no-cache-dir -r /shared/requirements.txt"
    port = 7860  # Replace with the port your app uses
    event_handler = CombinedChangeHandler(app_command, pip_command, port)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
