import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the directory to monitor and the target file name
directory_to_watch = "/data/ASV19"  # Replace with your directory path
specific_file_name = "paired_REV_REV_ASV19.txt"

class FileWatcherHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the created file matches the specific file name
        if event.is_directory:
            return
        
        file_name = os.path.basename(event.src_path)
        if file_name == specific_file_name:
            # Create a copy with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.txt"
            new_file_path = os.path.join(directory_to_watch, new_file_name)
            
            try:
                with open(event.src_path, 'r') as original_file:
                    content = original_file.read()
                with open(new_file_path, 'w') as new_file:
                    new_file.write(content)
                print(f"File copied as: {new_file_name}")
            except Exception as e:
                print(f"Error copying file: {e}")

if __name__ == "__main__":
    event_handler = FileWatcherHandler()
    observer = Observer()
    
    # Set the observer to watch the directory
    observer.schedule(event_handler, directory_to_watch, recursive=False)
    observer.start()
    
    print("Monitoring started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitoring.")
        observer.stop()
    observer.join()
