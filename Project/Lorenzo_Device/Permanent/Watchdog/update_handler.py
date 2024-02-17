import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import os
import signal
import shutil
import subprocess
import zipfile

def print_arrow():
    print("    |  |  ")
    print("    |  |  ")
    print("  ---------")
    print("  \\      /")
    print("   \\    /")
    print("    \\  /")
    print("     \\/")
    print(f"\n:: Update Handler ::\n")
    
folder_to_watch = './TCU' # Define the folder to monitor

def update_file(event):
    global observer
    process = subprocess.Popen(["pgrep", "-f", "OS.py"], stdout=subprocess.PIPE, text=True)
    output, _ = process.communicate()
    pid_to_kill_list = output.splitlines()
    #If the new item is a directory
    if not event.is_directory and ('downloads' in event.src_path):
        print(f"src_path type: {type(event.src_path)}")
        print(f"New file downloaded: {event.src_path}")
        for pid_to_kill in pid_to_kill_list:
            print(f"Pid to kill: {pid_to_kill}")
            os.kill(int(pid_to_kill), signal.SIGTERM)
            #os.kill(int(pid_to_kill), signal.SIGINT) #Kill the process
            
        process = subprocess.Popen(["pgrep", "-f", "start.sh"], stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate()
        pid_to_kill_list = output.splitlines()
        for pid_to_kill in pid_to_kill_list:
            print(f"Pid to kill: {pid_to_kill}")
            os.kill(int(pid_to_kill), signal.SIGTERM) #Kill the process
        if '.zip' in event.src_path:
            with zipfile.ZipFile(event.src_path, 'r') as zip_ref:
                zip_ref.extractall(folder_to_watch)
        else:
            shutil.copy(event.src_path, folder_to_watch)          
        print("File updated!")
        #process = subprocess.Popen(["python3", "telemetry.py"])
        #print(f"{pid_to_kill} created")
        observer.stop()
  
        
# Define the event handler
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        update_file(event)
                     
    def on_modified(self, event):
        update_file(event)
            
            
def main():
    global observer
    print_arrow()
    
    # Create an observer
    #observer = Observer()
    #event_handler = DownloadHandler()
    # Attach the event handler to the observer
    #observer.schedule(event_handler, folder_to_watch, recursive=True)
    #observer.daemon = True
    # Start the observer in a separate thread
    #observer.start()
    # Wait for the observer to finish operations
    #observer.join()
    
    while True:
        # Create an observer
        observer = Observer()
        event_handler = DownloadHandler()
        # Attach the event handler to the observer
        observer.schedule(event_handler, folder_to_watch, recursive=True)
        observer.daemon = True
        # Start the observer in a separate thread
        observer.start()
        # Wait for the observer to finish operations
        observer.join()
    
if __name__ == "__main__":
    main()
    
