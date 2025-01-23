import socket
import os
import json
from pathlib import Path

from util import Utils

util = Utils()

def printMenu():
    print("\n---------------------------------------\n")
    print("1. See All Files")
    print("2. Download File")
    print("3. Upload File")
    print("4. O.C.R. File")
    print("5. O.C.R. Files in Directory")
    print("6. Convert File to PDF")
    print("7. Convert Files in Directory to PDF")
    print("8. Exit")

def seeAllFiles(socket):
    files = socket.recv(1024).decode('utf-8')
    file_list = files.split('\n')
    print("Available files:")
    for file in file_list:
        if file.strip():
            print(f"- {file}")

def downloadFile(socket):
    filename = input("File name: ")
    path = input("Desired Directory Path: ")
    socket.send(filename.encode('utf-8'))
    data = socket.recv(1024)
    data = data.decode('utf-8')
    if data[:6] == 'EXISTS':
        filesize = int(data[6:])
        message = input("File Exists. Download(Y/N) -> ")
        if message.lower() == 'y':
            response = "OK"
            socket.send(response.encode('utf-8'))
            if path != "":
                new_file = os.path.join(path, filename)
            else:
                new_file = filename
            with open(new_file, 'wb') as f:
                data = socket.recv(1024)
                totalReceived = len(data)
                f.write(data)
                while totalReceived < filesize:
                    data = socket.recv(1024)
                    totalReceived += len(data)
                    f.write(data)
                    print(f"Percentage Downloaded: {((totalReceived / filesize) * 100):.2f}")
                print("Download Complete")
    else:
        print("File does not exist")

def sendFile(filename, socket):
    try:
        base_filename = Path(filename).name
        metadata = {"filesize": os.path.getsize(filename), "filename": base_filename}
        socket.send(json.dumps(metadata).encode('utf-8'))

        with open(filename, 'rb') as f:
            while chunk := f.read(1024):
                socket.send(chunk)

    except BrokenPipeError:
        print("Error: Broken pipe during file transfer")
    except Exception as e:
        print(f"Unexpected error during file transfer: {e}")

def uploadFile(socket):
    filepath = input("File name: ")
    sendFile(filepath, socket)

def receiveFile(socket, metadata, dir):
    filesize = metadata['filesize']
    filename = metadata['filename']
    filename = os.path.join(dir, filename)

    # Step 2: Notify server of readiness
    socket.send(b"READY")

    # Step 3: Receive file data
    with open(filename, 'wb') as f:
        totalReceived = 0
        while totalReceived < filesize:
            data = socket.recv(1024)
            if b"EOF" in data:
                f.write(data.replace(b"EOF", b""))  # Remove EOF marker
                break
            totalReceived += len(data)
            f.write(data)
            print(f"Received {totalReceived}/{filesize} bytes ({(totalReceived / filesize) * 100:.2f}%)")
    print(f"File {filename} received successfully")

def ocrFile(socket):
    print("ocr file functionality")

def ocrDir(socket):
    print("ocr dir functionality")

def convertFile(socket):
    fileToConvert = input("Path to file to convert: ")
    if util.file_exists(fileToConvert):
        sendFile(fileToConvert, socket)
        metadata = json.loads(socket.recv(1024).decode('utf-8'))
        dir = os.path.dirname(fileToConvert)
        receiveFile(socket, metadata, dir)
    else:
        print("File does not exist")

def convertDir(socket):
    dirToConvert = input("Path to directory: ")
    if util.dir_exists(dirToConvert):
        # Step 1: Send metadata to the server
        files = util.fetch_all_files(dirToConvert)
        metadata = {"numFiles": len(files)}
        socket.send(json.dumps(metadata).encode('utf-8'))

        # Step 2: Send files to the server
        for file in files:
            if util.file_exists(file):
                sendFile(file, socket)  # Custom function to send files
                ack = socket.recv(1024).decode('utf-8')  # Wait for server acknowledgment
                if ack == "ACK":
                    print(f"Server acknowledged receipt of {file}")
                else:
                    print(f"Server failed to acknowledge receipt of {file}")
        
        # Step 3: Receive converted files back from the server
        num_received = 0
        while True:
            try:
                # Receive metadata for the file
                metadata = json.loads(socket.recv(1024).decode('utf-8'))
                filesize = metadata['filesize']
                filename = metadata['filename']
                print(f"Receiving {filename} ({filesize} bytes)...")

                # Receive the actual file
                receiveFile(socket, metadata, dirToConvert)  # Custom function to receive files
                num_received += 1
                socket.send(b"ACK")  # Send acknowledgment to server
                print(f"Received {filename} from server")
            except json.JSONDecodeError:
                print("All files received")
                break
    else:
        print("Directory does not exist, try again.")

def main():
    host = '127.0.0.1'
    port = 5050

    try:
        s = socket.socket()
        s.connect((host, port))
        print("Connected to the server.")

        running = True
        while running:
            printMenu()
            choice = None
            while not choice:
                try:
                    choice = int(input("-> "))
                except ValueError:
                    print("Invalid Input, must be an integer.")

            if choice == 1:
                s.send(str(choice).encode('utf-8'))
                seeAllFiles(s)
            elif choice == 2:
                s.send(str(choice).encode('utf-8'))
                downloadFile(s)
            elif choice == 3:
                s.send(str(choice).encode('utf-8'))
                uploadFile(s)
            elif choice == 4:
                s.send(str(choice).encode('utf-8'))
                ocrFile(s)
            elif choice == 5:
                s.send(str(choice).encode('utf-8'))
                ocrDir(s)
            elif choice == 6:
                s.send(str(choice).encode('utf-8'))
                convertFile(s)
            elif choice == 7:
                s.send(str(choice).encode('utf-8'))
                convertDir(s)
            elif choice == 8:
                s.send(str(choice).encode('utf-8'))
                print("Exiting the program.")
                running = False
            else:
                print("Invalid choice. Please select a valid option.")

        s.close()
        print("Disconnected from the server.")

    except ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()