import socket
import threading
import os

def SendFile(name, socket):
    filename = f"files/{socket.recv(1024).decode('utf-8')}"
    if os.path.isfile(filename):
        response = "EXISTS " + str(os.path.getsize(filename))
        socket.send(response.encode('utf-8'))
        userResponse = socket.recv(1024)
        userResponse = userResponse.decode("utf-8")
        if userResponse[:2] == 'OK':
            with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                socket.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    socket.send(bytesToSend)
    else:
        response = "ERR"
        socket.send(response.encode("utf-8"))

def ReceiveFile(name, socket):
    filename = socket.recv(1024).decode('utf-8')
    filesize = socket.recv(1024).decode('utf-8')
    filename = "files/" + filename
    with open(filename, 'wb') as f:
        totalReceived = 0
        while totalReceived < int(filesize):
            data = socket.recv(1024)
            if data == b"EOF":
                break
            totalReceived += len(data)
            f.write(data)

def sendListFiles(name, socket):
    # Walk through the directory and list files
    directory_path = "files"
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            files.append(filename)
            
    file_list = "\n".join(files)
    socket.send(file_list.encode('utf-8'))

def ManageConnection(name, c):
    while True:
        try:
            choice = c.recv(1024).decode('utf-8')
            if not choice:
                break
            elif choice == "1":
                sendListFiles("allFilesThread", c)
            elif choice == "2":
                SendFile("sendThread", c)
            elif choice == "3":
                ReceiveFile("receiveThread", c)
        except Exception as e:
            print(f"Error handling client: {e}")
            break
    c.close()

def main():
    host = '192.168.98.157'
    port = 5050

    s = socket.socket()
    s.bind((host, port))

    s.listen(5)

    print("Server Started")

    while True:
        c, addr = s.accept()
        print("client connected ip: " + str(addr))

        t = threading.Thread(target=ManageConnection, args=("manageThread", c))
        t.start()

if __name__ == "__main__":
    main()



    