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

    socket.close()

# def ReceiveFile(name, socket):
#     filename = socket.recv(1024).
#     with open("new_" + filename, 'wb') as f:
#         data = s.recv(1024)
#         totalReceived = len(data)
#         f.write(data)
#         while totalReceived < filesize:
#             data = s.recv(1024)
#             totalReceived += len(data)
#             f.write(data)
#             print(f"Percentage Downloaded: {((totalReceived / filesize) * 100):.2f}")
#         print("Download Complete")

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

        t = threading.Thread(target=SendFile, args=("sendThread", c))
        t.start()

if __name__ == "__main__":
    main()



    