import socket
import threading
import os

def RetrFile(name, socket):
    filename = socket.recv(1024).decode('utf-8')
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

def main():
    host = '127.0.0.1'
    port = 5056

    s = socket.socket()
    s.bind((host, port))

    s.listen(5)

    print("Server Started")

    while True:
        c, addr = s.accept()

        print("client connected ip: " + str(addr))

        t = threading.Thread(target=RetrFile, args=("retrThread", c))
        t.start()

if __name__ == "__main__":
    main()



    