import os
import json
from pathlib import Path

class Utils:
    # Check if a file exists. Return Bool
    def file_exists(self, file):
        return os.path.isfile(file)
    
    # Check if a directory exists. Return Bool
    def dir_exists(self, dir):
        return os.path.isdir(dir)
   
    # Retrieve all files from directory, and return list of files
    def fetch_all_files(self, folder):
        target_files = []
        for file_name in os.listdir(folder):
            full_path = os.path.join(folder, file_name)
            if not self.dir_exists(full_path):
                target_files.append(full_path)
        return target_files
    
    # Retrieve all files from directory, and return list of PDF files
    def fetch_all_pdf_files(self, folder):
        target_files = []
        for file_name in os.listdir(folder):
            if file_name.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder, file_name)):
                target_files.append(os.path.join(folder, file_name))
        return target_files

    # Take file path and return file name and file extension. Example: INPUT: /path/to/folder/test.txt RETURN: test, .txt
    def get_file_details(self, file_path):
        file_name_with_ext = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(file_name_with_ext)
        return file_name, file_extension

    # Used by server and client to Send File
    def sendFile(self, filename, conn):
        try:
            # file metadata
            base_filename = Path(filename).name
            metadata = json.dumps({"filesize": os.path.getsize(filename), "filename": base_filename})
            metadata_length = len(metadata).to_bytes(4, byteorder="big")

            # Send metadata length and metadata
            conn.send(metadata_length)
            conn.send(metadata.encode('utf-8'))

            # Send file content
            with open(filename, 'rb') as f:
                while chunk := f.read(1024):
                    conn.send(chunk)
            print(f"File sent: {filename}")
        except Exception as e:
            print(f"Error in sendFile: {e}")

    # Used by server and client to Receive File
    def receiveFile(self, conn, save_dir):
        try:
            # Receive metadata length and metadata only
            metadata_length = conn.recv(4)  # Fixed-length header for metadata size
            if not metadata_length:
                raise ValueError("No metadata length received")
            metadata_size = int.from_bytes(metadata_length, byteorder="big")

            metadata = json.loads(conn.recv(metadata_size).decode('utf-8'))
            filesize = metadata['filesize']
            filename = metadata['filename']
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, filename)

            # Receive file content
            with open(filepath, 'wb') as f:
                totalReceived = 0
                while totalReceived < filesize:
                    data = conn.recv(1024)
                    if not data:
                        break
                    totalReceived += len(data)
                    f.write(data)
            print(f"File received: {filepath}")
        except Exception as e:
            print(f"Error in receiveFile: {e}")
