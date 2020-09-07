import socket
import sys
import threading
import time
import random


# this help to locate the file.
def check_location(prev, curr, next, file):
    a = file % 256
    b = [abs(a - curr), abs(256 + curr - a), abs(a - next), abs(256 + next - a), abs(a - prev), abs(256 + prev - a)]
    return b.index(min(b)) < 2


class Peer:
    def __init__(self, id, first, second, mss, drop_rate):
        self.id = id
        self.first = first
        self.first_loss = 0
        self.second = second
        self.second_loss = 0
        self.first_prev = None
        self.second_prev = None
        self.mss = mss
        self.rate = drop_rate
        self.statue = True
        self.test_port = 50000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_start = 1
        self.ack = 0
        self.time = time.time()

    def ping(self, name):
        if name == self.first:
            time.sleep(1)
            self.sock.sendto('first peer {}'.format(self.id).encode(), ('localhost', self.first + self.test_port))
        else:
            time.sleep(14)
            self.sock.sendto('second peer {}'.format(self.id).encode(), ('localhost', self.second + self.test_port))
        try:
            self.sock.settimeout(1)
            data, addr = self.sock.recvfrom(1024)
        except socket.timeout:
            if name == self.first:
                self.first_loss += 1
                if self.first_loss == 3:
                    print('Peer {} is no longer alive.'.format(self.first))
                    self.first = self.second
                    print('My first successor is now peer {}.'.format(self.first))
                    temp = self.TCPclient(self.second + self.test_port, 'next successor')
                    self.second = int(temp)
                    print('My second successor is now peer {}'.format(self.second))
            if name == self.second:
                self.second_loss += 1
                if self.second_loss == 3:
                    print('Peer {} is no longer alive.'.format(self.second))
                    print('My first successor is now peer {}'.format(self.first))
                    temp = self.TCPclient(self.first + self.test_port, 'next successor')
                    self.second = int(temp)
                    print('My second successor is now peer {}'.format(self.second))
        else:
            print("A ping response message was received from {}".format(data.decode()))

    def UDPclient(self):
        while self.statue:
            time.sleep(1)
            self.ping(self.first)
            self.ping(self.second)

    def UDPserver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', self.id + self.test_port))
        while self.statue:
            data, addr = sock.recvfrom(1024)
            data = data.decode().split()
            if "first" in data:
                self.first_prev = int(data[-1])
            else:
                self.second_prev = int(data[-1])
            print('A ping request message was received from peer {}'.format(data[-1]))
            sock.sendto('peer {}'.format(self.id).encode(), addr)

    def TCPclient(self, port, message):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', port))
        sock.send(message.encode())
        recv = sock.recv(1024)
        sock.close()
        try:
            recv = recv.decode()
        except:
            pass
        if type(recv) != bytes:
            if 'next' in recv:
                return recv.split()[-1]
            if 'allow' in recv:
                return True
        if type(recv) == bytes:
            print('We now start receiving the file ...... ')
            file = open('receiver_log.txt', 'w')
            file2 = open('received_file.pdf', 'wb')
            while recv != b'finish':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', port))
                file.write('rcv\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2), self.file_start,
                                                                  len(recv), self.ack))
                file2.write(recv)
                mss = len(recv)
                self.file_start += mss
                file.write(
                    'snd\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2), 0, mss, self.file_start))
                sock.sendall('ACKMSS {} {} {}'.format(0, mss, self.file_start).encode())
                recv = sock.recv(1024)
            file.close()
            file2.close()
            print('The file is received.')

        sock.close()
        # return True

    def TCPserver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', self.id + self.test_port))
        sock.listen(100)
        while self.statue:
            message, addr = sock.accept()
            sentence = message.recv(1024).decode().split()
            if 'next' in sentence:
                replay = 'next {}'.format(self.first)
                message.send(replay.encode())
            if 'depart' in sentence:
                print('Peer {} will depart from the network.'.format(sentence[1]))
                if int(sentence[1]) == self.first:
                    self.first = int(sentence[2])
                    self.second = int(sentence[3])
                else:
                    self.second = int(sentence[2])
                print('My first successor is now peer {}.'.format(self.first))
                print('My second successor is now peer {}.'.format(self.second))
                message.send('allow quit'.encode())
            if 'request' in sentence:
                if not check_location(self.first_prev, self.id, self.first, int(sentence[2])):
                    print('File {} is not stored here.'.format(sentence[2]))
                    new_message = 'File request {} {} {}'.format(sentence[2], sentence[3], self.first)
                    message.send('None'.encode())
                    self.TCPclient(self.first + self.test_port, new_message)
                    print('File request message has been forwarded to my successor.')
                else:
                    print('File {} is here.'.format(sentence[2]))
                    print('A response message, destined for peer {}, has been sent.'.format(sentence[3]))
                    message.send('None'.encode())
                    self.TCPclient(self.test_port + int(sentence[3]),
                                   'file here {} {} {}'.format(sentence[2], sentence[3],
                                                               self.id))  # filename, request peer, response peer.
            if 'here' in sentence:
                print(
                    'Received a response message from peer {}, which has the file {}.'.format(sentence[4], sentence[2]))
                message.send('None'.encode())
                # print('We now start receiving the file ……… ')
                self.TCPclient(int(sentence[4]) + self.test_port,
                               'ACKMSS {} {} {} {}'.format(self.file_start, self.mss, self.ack, sentence[2]))
            if 'ACKMSS' in sentence:
                self.file_start = int(sentence[1])
                self.mss = int(sentence[2])
                self.ack = int(sentence[3])
                filename = sentence[-1] + '.pdf'
                file = open(filename, 'rb')
                piece = file.read(self.mss)
                file2 = open('sender_log.txt', 'w')
                mss = self.mss
                print('We now start sending the file ......')
                flag = 0
                while piece:
                    if self.rate * 10 <= random.randint(0, 10):
                        message.send(piece)
                        if not flag:
                            file2.write('snd\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2),
                                                                               self.file_start, mss, self.ack))
                        else:
                            file2.write(
                                'RTX\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2),
                                                                       self.file_start, mss, self.ack))
                        flag = 0
                    else:
                        if not flag:
                            file2.write('Drop\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2),
                                                                                self.file_start, mss, self.ack))
                            flag += 1
                        else:
                            file2.write(
                                'RTX/Drop\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2),
                                                                            self.file_start, mss, self.ack))
                    sock.settimeout(1)
                    try:
                        message, addr = sock.accept()
                        sentence = message.recv(self.mss).decode().split()
                    except socket.timeout:
                        pass
                    else:
                        file2.write(
                            'rev\t\t{}\t\t{}\t\t{}\t\t{}\n'.format(round(time.time() - self.time, 2), sentence[1],
                                                                   sentence[2], sentence[3]))
                        self.file_start = int(sentence[3])
                        self.ack = 0
                        piece = file.read(self.mss)
                        if len(piece) != mss:
                            mss = len(piece)
                        if not piece:
                            break
                sock.settimeout(None)
                message.send('finish'.encode())
                print('The file is sent.')
                file.close()
                file2.close()
        sock.close()

    def input_command(self):
        while self.statue:
            command = input().split()
            if 'request' in command:
                message = 'File request {} {} {}'.format(command[-1], self.id, self.first)
                print('File request message for {} has been sent to my successor.'.format(command[-1]))
                self.TCPclient(self.first + self.test_port, message)

            if 'quit' in command:
                message = 'depart {} {} {}'.format(self.id, self.first, self.second)
                if self.TCPclient(self.first_prev + self.test_port, message):
                    time.sleep(1)
                    if self.TCPclient(self.second_prev + self.test_port, message):
                        self.statue = False


def main():
    peer = Peer(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
    # peer=Peer(1,3,5,300,0.3)

    # Initialize the client and server thread of each peer
    # Sending ping request to its successors and catch for response
    UDPclient = threading.Thread(target=peer.UDPclient, args=())
    UDPserver = threading.Thread(target=peer.UDPserver, args=())
    TCPserver = threading.Thread(target=peer.TCPserver, args=())

    user_input = threading.Thread(target=peer.input_command)

    UDPclient.start()
    UDPserver.start()
    TCPserver.start()
    user_input.start()


if __name__ == "__main__":
    main()
