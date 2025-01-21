import socket
import os
from pathlib import Path

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
    base_filename = Path(filename).name
    if os.path.isfile(filename):
        socket.send(base_filename.encode('utf-8'))
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

def uploadFile(socket):
    filepath = input("File name: ")
    sendFile(filepath, socket)

def receiveFile(filepath, socket):
    print("receive file")    

def ocrFile(socket):
    print("ocr file functionality")

def ocrDir(socket):
    print("ocr dir functionality")

def convertFile(socket):
    fileToConvert = input("Path to file to convert: ")
    sendFile(fileToConvert, socket)
    receiveFile(fileToConvert, socket)

def convertDir(socket):
    print("convert dir functionality")

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