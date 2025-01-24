import socket
import threading
import os
import json
import shutil

from util import Utils

util = Utils()

def sendServerFile(name, socket):
    # Receive metadata length and metadata only
    metadata_length = socket.recv(4)  # Fixed-length header for metadata size
    if not metadata_length:
        raise ValueError("No metadata length received")
    metadata_size = int.from_bytes(metadata_length, byteorder="big")

    metadata = json.loads(socket.recv(metadata_size).decode('utf-8'))
    filename = metadata['filename']
    filename = os.path.join("server_files", filename)

    if os.path.isfile(filename):
        response = b"EXISTS"
        socket.send(response)
        util.sendFile(filename, socket)
    else:
        response = b"ERR"
        socket.send(response)

def sendListFiles(name, socket):
    directory_path = "server_files"
    files = util.fetch_all_files(directory_path)      
    file_list = "\n".join(files)
    socket.send(file_list.encode('utf-8'))

def convertProcess(dir, file):
    file_name, file_extension = util.get_file_details(file)
    file_extension = file_extension.lower()
    if file_extension == ".txt":
        util.txt_to_pdf(dir, file_name, file_extension)
        os.remove(file)
    elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
        util.image_to_pdf(dir, file_name, file_extension)
        os.remove(file)
    elif file_extension == ".heic":
        jpg_file = os.path.join(dir, file_name + ".jpg")
        util.convert_heic_to_jpg(file, jpg_file)
        util.image_to_pdf(file_name, ".jpg")
        os.remove(file)
    elif file_extension == ".msg":
        print("msg to pdf")
        os.remove(file)
    elif file_extension == ".docx":
        print("maybe")
        os.remove(file)
    elif file_extension == ".doc":
        print("maybe")
        os.remove(file)    

def convertFile(addr, name, socket):
    dir = f"server_files/{str(addr[1])}"
    util.receiveFile(name, socket, dir)
    files = util.fetch_all_files(dir)
    for file in files:
        convertProcess(dir, file)
    files = util.fetch_all_pdf_files(dir)
    for file in files:
        util.sendFile(file, socket)
        os.remove(file)
    os.rmdir(dir)

def convertAllFiles(name, socket, addr):
    # Step 1: Receive metadata
    metadata = json.loads(socket.recv(1024).decode('utf-8'))
    num_files = metadata['numFiles']
    num_received = 0

    # Step 2: Receive files from the client
    while num_received < num_files:
        dir = f"server_files/{str(addr[1])}"
        util.receiveFile(socket, dir)  # Custom function to receive files
        num_received += 1
        socket.send(b"ACK")  # Send acknowledgment for each file received
    print(f"Received {num_received}/{num_files} files")

    # Step 3: Convert received files
    if num_received == num_files:
        dir = f"server_files/{str(addr[1])}"  # Directory for client's files
        files = util.fetch_all_files(dir)

        # Process and convert each file
        for file in files:
            convertProcess(dir, file)  # Custom function to handle conversion

        # Step 4: Fetch and send back converted files
        converted_files = util.fetch_all_pdf_files(dir)
        metadata = {"numFiles": len(converted_files)}
        socket.send(json.dumps(metadata).encode('utf-8'))
        
        for file in converted_files:
            if util.file_exists(file):
                # Prepare metadata
                metadata = json.dumps({"filesize": os.path.getsize(file), "filename": os.path.basename(file)})
                metadata_length = len(metadata).to_bytes(4, byteorder='big')

                # Send metadata length and metadata
                socket.send(metadata_length)
                socket.send(metadata.encode('utf-8'))

                # Send the file
                util.sendFile(file, socket)
                ack = socket.recv(1024).decode('utf-8')  # Wait for acknowledgment
                if ack == "ACK":
                    print(f"Client acknowledged receipt of {file}")
                    os.remove(file)
                else:
                    print(f"Client failed to acknowledge receipt of {file}")
        shutil.rmtree(dir)  # Clean up server directory

def ManageConnection(name, c, addr):
    while True:
        try:
            choice = c.recv(1024).decode('utf-8')
            if not choice:
                break
            elif choice == "1":
                sendListFiles("allFilesThread", c)
            elif choice == "2":
                sendServerFile("sendThread", c)
            elif choice == "3":
                dir = "server_files"
                util.receiveFile(c, dir)
            elif choice == "4" or choice == "5":
                convertAllFiles("convertAllThread", c, addr)
            elif choice == "6":
                print("Client Disconnected")
                break
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    c.close()

def main():
    host = '127.0.0.1'
    port = 5051

    s = socket.socket()
    s.bind((host, port))

    s.listen(5)

    print("Server Started")

    while True:
        c, addr = s.accept()
        print("client connected ip: " + str(addr))

        t = threading.Thread(target=ManageConnection, args=("manageThread", c, addr))
        t.start()

if __name__ == "__main__":
    main()



    