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

def send_file(file, filename, file_extension, socket):
    print(f"Sending {filename}")
    new_name = f"{filename}{file_extension}"
    metadata = {"filesize": os.path.getsize(file), "filename": new_name}
    socket.send(json.dumps(metadata).encode('utf-8'))
    with open(file, 'rb') as f:
        bytesToSend = f.read(1024)
        while bytesToSend:
            socket.send(bytesToSend)
            bytesToSend = f.read(1024)
    socket.send(b"EOF")  # Send EOF once file transmission is complete
    print(f"{filename} sent")

def receiveFile(name, socket, addr):
    metadata = json.loads(socket.recv(1024).decode('utf-8'))
    filesize = int(metadata['filesize'])
    filename = metadata['filename']
    port = addr[1]
    dirname = "server_files/" + str(port)
    os.mkdir(dirname)
    filename = dirname + "/" + filename    
    with open(filename, 'wb') as f:
        totalReceived = 0
        while totalReceived < int(filesize):
            data = socket.recv(1024)
            if b"EOF" in data:
                f.write(data.replace(b"EOF", b""))
                break
            totalReceived += len(data)
            f.write(data)

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

def convertFile(addr, name, socket):
    receiveFile(name, socket, addr)
    dir = f"server_files/{str(addr[1])}"
    files = util.fetch_all_files(dir)
    for file in files:
        file_name, file_extension = util.get_file_details(file)
        file_extension = file_extension.lower()
        if file_extension == ".txt":
            util.txt_to_pdf(dir, file_name, file_extension)
        elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
            util.image_to_pdf(dir, file_name, file_extension)
        elif file_extension == ".heic":
            jpg_file = os.path.join(dir, file_name + ".jpg")
            util.convert_heic_to_jpg(file, jpg_file)
            util.image_to_pdf(file_name, ".jpg")
        elif file_extension == ".msg":
            print("msg to pdf")
        elif file_extension == ".docx":
            print("maybe")
        elif file_extension == ".doc":
            print("maybe")
        else:
            print("unable to convert file")
        os.remove(file)
    files = util.fetch_all_pdf_files(dir)
    for file in files:
        file_name, file_extension = util.get_file_details(file)
        send_file(file, file_name, file_extension, socket)
        os.remove(file)
    os.rmdir(dir)


def convertAllFiles(name, socket):
    print("converting files")

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
                convertAllFiles("convertAllThread", c)
            elif choice == "8":
                print("Client Disconnected")
                break
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    c.close()

def main():
    host = '192.168.98.157'
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



    