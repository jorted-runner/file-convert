import socket
import os

def printMenu():
    print("1. See All Files")
    print("2. Download File")
    print("3. Upload File")
    print("4. Exit")

def seeAllFiles():
    print("Functionality to list all files goes here.")

def downloadFile(s):
    filename = input("File name: ")
    if filename != 'q':
        s.send(filename.encode('utf-8'))
        data = s.recv(1024)
        data = data.decode('utf-8')
        if data[:6] == 'EXISTS':
            filesize = int(data[6:])
            message = input("File Exists. Download(Y/N) -> ")
            if message.lower() == 'y':
                response = "OK"
                s.send(response.encode('utf-8'))
                output_dir = os.path.dirname("new_" + filename)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                with open("new_" + filename, 'wb') as f:
                    data = s.recv(1024)
                    totalReceived = len(data)
                    f.write(data)
                    while totalReceived < filesize:
                        data = s.recv(1024)
                        totalReceived += len(data)
                        f.write(data)
                        print(f"Percentage Downloaded: {((totalReceived / filesize) * 100):.2f}")
                    print("Download Complete")
        else:
            print("File does not exist")
        s.close()

def uploadFile(socket):
    filename = input("File name: ")
    if os.path.isfile(filename):
        socket.send(filename.encode('utf-8'))
        filesize = str(os.path.getsize(filename))
        socket.send(filesize.encode('utf-8'))
        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            while bytesToSend:
                socket.send(bytesToSend)
                bytesToSend = f.read(1024)
        socket.send(b"EOF")
    else:
        print("File does not exist")
    socket.close()

def main():
    host = '192.168.98.157'
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
                seeAllFiles()
            elif choice == 2:
                s.send(str(choice).encode('utf-8'))
                downloadFile(s)
            elif choice == 3:
                s.send(str(choice).encode('utf-8'))
                uploadFile(s)
            elif choice == 4:
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