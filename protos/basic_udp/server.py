import socket

def main():
    host = '127.0.0.1'
    port = 5050

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print('Server started.')

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print('Message from: ' + str(addr))
        print('From connected user: ' + data)

        data = data.upper()
        print('Sending: ' + data)
        s.sendto(data.encode('utf-8'), addr)

if __name__ == '__main__':
    main()
