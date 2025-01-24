import socket
import os
import json


from util import Utils

util = Utils()

# Display the menu options to the user
def printMenu():
    print("\n---------------------------------------\n")
    print("1. See All Files")
    print("2. Download File")
    print("3. Upload File")
    print("4. Convert File to PDF")
    print("5. Convert Files in Directory to PDF")
    print("6. Exit")

# Fetch and display all available files from the server
def seeAllFiles(socket):
    files = socket.recv(1024).decode('utf-8')
    file_list = files.split('\n')
    print("Available files:")
    for file in file_list:
        if file.strip():
            file = file.replace("server_files/", "")
            print(f"- {file}")

# Handle file download from the server
def downloadFile(socket):
    filename = input("Enter the filename to download: ")

    #send filename to server
    metadata = json.dumps({"filename": filename})
    metadata_length = len(metadata).to_bytes(4, byteorder="big")
    socket.send(metadata_length)
    socket.send(metadata.encode('utf-8'))

    exists = socket.recv(1024).decode('utf-8')
    if exists == "EXISTS":
        path = input("Desired Directory Path: ")
        util.receiveFile(socket, path)
    else:
        print(filename + " does not exists. Try again")

# Upload file to server
def uploadFile(socket):
    filepath = input("File Path: ")
    if util.file_exists(filepath):
        util.sendFile(filepath, socket)
    else:
        print("File does not exist.")

# Process to convert a single file
def convertFile(socket):
    fileToConvert = input("Path to file to convert: ")
    # Step 1: Check if user input file exists
    if util.file_exists(fileToConvert):
        # Step 2: Tell server to expect 1 file
        metadata = {"numFiles": 1}
        socket.send(json.dumps(metadata).encode('utf-8'))

        # Step 3: Send File to Server
        util.sendFile(fileToConvert, socket)
        ack = socket.recv(1024).decode('utf-8')  # Wait for server acknowledgment
        if ack == "ACK": # If acknowledged proceed to receive file
            print(f"Server acknowledged receipt of {fileToConvert}")
            # not explicitly needed, but is received to keep the server side logic simple
            metadata = json.loads(socket.recv(1024).decode('utf-8'))

            # Read metadata length
            metadata_length = int.from_bytes(socket.recv(4), byteorder='big')
            # Read metadata
            metadata = json.loads(socket.recv(metadata_length).decode('utf-8'))

            # Receive the actual file
            dir = os.path.dirname(fileToConvert)
            util.receiveFile(socket, dir)
            socket.send(b"ACK")  # Acknowledge the server
            print(f"Received file")
        else:
            print(f"Server failed to acknowledge receipt of {fileToConvert}")

    else:
        print("File does not exist")

# Process to convert all files in a directory
def convertDir(socket):
    dirToConvert = input("Path to directory: ")
    # Step 1: Verify that the directory exists
    if util.dir_exists(dirToConvert):
        files = util.fetch_all_files(dirToConvert)
        metadata = {"numFiles": len(files)}
        socket.send(json.dumps(metadata).encode('utf-8'))

        # Step 2: Send files to the server
        for file in files:
            if util.file_exists(file):
                util.sendFile(file, socket)  # Custom function to send files
                ack = socket.recv(1024).decode('utf-8')  # Wait for server acknowledgment
                if ack == "ACK":
                    print(f"Server acknowledged receipt of {file}")
                else:
                    print(f"Server failed to acknowledge receipt of {file}")
        
        # Step 3: Receive converted files back from the server
        num_received = 0

        metadata = json.loads(socket.recv(1024).decode('utf-8'))
        num_files = metadata['numFiles']

        # Step 2: Receive files from the server
        while num_received < num_files:
            # Read metadata length
            metadata_length = int.from_bytes(socket.recv(4), byteorder='big')
            # Read metadata
            metadata = json.loads(socket.recv(metadata_length).decode('utf-8'))

            # Receive the actual file
            util.receiveFile(socket, dirToConvert)
            num_received += 1
            socket.send(b"ACK")  # Acknowledge the server
            print(f"Received {num_received}/{num_files} files")

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
                convertFile(s)
            elif choice == 5:
                s.send(str(choice).encode('utf-8'))
                convertDir(s)
            elif choice == 6:
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