import socket
import threading
import os
import json

from util import Utils

util = Utils()

def sendFile(name, socket):
    filename = f"server_files/{socket.recv(1024).decode('utf-8')}"
    if os.path.isfile(filename):
        response = "EXISTS " + str(os.path.getsize(filename))
        socket.send(response.encode('utf-8'))
        userResponse = socket.recv(1024)
        userResponse = userResponse.decode("utf-8")
        if userResponse[:2] == 'OK':
            send_file(filename, socket)
    else:
        response = "ERR"
        socket.send(response.encode("utf-8"))

def send_file(file, file_name, file_extension, socket):
    print(f"Sending {file}")

    # Step 1: Send metadata
    metadata = {"filesize": os.path.getsize(file), "filename": file_name + file_extension}
    socket.send(json.dumps(metadata).encode('utf-8'))

    # Step 2: Wait for client readiness
    ack = socket.recv(1024).decode('utf-8')
    if ack != "READY":
        print(f"Client not ready for {file}")
        return

    # Step 3: Send file data
    try:
        with open(file, 'rb') as f:
            while chunk := f.read(1024):
                socket.send(chunk)
        socket.send(b"EOF")  # Explicitly send an EOF marker to indicate end of file
        print(f"{file} sent successfully")
    except Exception as e:
        print(f"Error sending file {file}: {e}")

def receiveFile(name, socket, addr):
    try:
        metadata = json.loads(socket.recv(1024).decode('utf-8'))
        filesize = metadata['filesize']
        filename = metadata['filename']
        port = addr[1]
        dirname = f"server_files/{port}"
        os.makedirs(dirname, exist_ok=True)
        filepath = os.path.join(dirname, filename)

        with open(filepath, 'wb') as f:
            totalReceived = 0
            while totalReceived < filesize:
                data = socket.recv(1024)
                if not data:
                    break
                totalReceived += len(data)
                f.write(data)
    except json.JSONDecodeError:
        print("Error: Invalid JSON received for metadata")
    except Exception as e:
        print(f"Error handling file: {e}")

def sendListFiles(name, socket):
    # Walk through the directory and list files
    directory_path = "server_files"
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            files.append(filename)
            
    file_list = "\n".join(files)
    socket.send(file_list.encode('utf-8'))

def ocrFile(name, socket):
    print("ocr file")

def ocrAllFiles(addr, name, socket):
    print("ocr all files")

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
    receiveFile(name, socket, addr)
    dir = f"server_files/{str(addr[1])}"
    files = util.fetch_all_files(dir)
    for file in files:
        convertProcess(dir, file)
    files = util.fetch_all_pdf_files(dir)
    for file in files:
        file_name, file_extension = util.get_file_details(file)
        send_file(file, file_name, file_extension, socket)
        os.remove(file)
    os.rmdir(dir)

def convertAllFiles(name, socket, addr):
    # Step 1: Receive metadata
    metadata = json.loads(socket.recv(1024).decode('utf-8'))
    num_files = metadata['numFiles']
    num_received = 0

    # Step 2: Receive files from the client
    while num_received < num_files:
        print("Receiving file...")
        receiveFile(name, socket, addr)  # Custom function to receive files
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
        for file in converted_files:
            file_name, file_extension = util.get_file_details(file)
            send_file(file, file_name, file_extension, socket)  # Custom function to send files
            # Wait for client acknowledgment
            ack = socket.recv(1024).decode('utf-8')
            if ack == "ACK":
                print(f"Client acknowledged receipt of {file}")
                os.remove(file)  # Remove file after successful transfer
            else:
                print(f"Client failed to acknowledge receipt of {file}")
        os.rmdir(dir)  # Clean up server directory after all files are sent

def ManageConnection(name, c, addr):
    while True:
        try:
            choice = c.recv(1024).decode('utf-8')
            if not choice:
                break
            elif choice == "1":
                sendListFiles("allFilesThread", c)
            elif choice == "2":
                sendFile("sendThread", c)
            elif choice == "3":
                receiveFile("receiveThread", c, addr)
            elif choice == "4":
                ocrFile("ocrThread", c)
            elif choice == "5":
                ocrAllFiles("ocrAllThread", c)
            elif choice == "6":
                convertFile(addr, "convertThread", c)
            elif choice == "7":
                convertAllFiles("convertAllThread", c, addr)
            elif choice == "8":
                print("Client Disconnected")
                break
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    c.close()

def main():
    host = '127.0.0.1'
    port = 5050

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



    