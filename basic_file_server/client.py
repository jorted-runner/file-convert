import socket
import os

def main():
    host = '127.0.0.1'
    port = 5056

    s = socket.socket()
    s.connect((host, port))

    filename = input("Filename? -> ")

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

if __name__ == "__main__":
    main()