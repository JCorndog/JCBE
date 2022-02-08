import zmq
import numpy as np
import threading


class MessageHandler(threading.Thread):
    def __init__(self, port: int = 5555, verbose=False):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")
        print(f'Server listening on port {port}')
        self.incoming_message = None
        self.outgoing_message = None
        self.outgoing_message_ready_lock = threading.Lock()
        self.outgoing_message_ready_lock.acquire()
        self.incoming_message_ready_lock = threading.Lock()
        self.incoming_message_ready_lock.acquire()

    def run(self):
        first_message = True
        while True:
            self.receive_message()
            self._send_message()

    def receive_message(self):
        self.incoming_message = self.socket.recv()
        self.incoming_message_ready_lock.release()
        if self.verbose:
            print('Message received')

    def _send_message(self) -> None:
        self.outgoing_message_ready_lock.acquire()
        self.socket.send(bytes_to_send)
        if self.verbose:
            print('Message sent')

    def get_message(self):
        self.incoming_message_ready_lock.acquire()
        return self.incoming_message

    def send_message(self, data):
        self.outgoing_message = data
        self.outgoing_message_ready_lock.release()


class Communicator:
    def __init__(self):
        self.message_handler = MessageHandler()
        self.message_handler.daemon = True
        self.message_handler.start()

    def get_data(self) -> bytes:
        return self.message_handler.get_message()

    def get_image(self):
        message = self.get_data()
        dims = int.from_bytes(message[:4], 'little'), int.from_bytes(message[4:8], 'little'), 3
        array_received = np.frombuffer(message[8:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received

    def send_data(self, data) -> None:
        self.message_handler.send_message(data)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cv2

    bytes_to_send = b'\xb9\xb6\x871\x05Q\x00<\x89\xfc,9\xcd\xce\xd3:\xc1\x1b\x8c:\xba\xbam;b\xca\x8e8\xef\xb4J<\x99\xd9/:\r\xa5\xa69\xb2\xdf\x9c7\x0ej!6m\x7f#8\xb0\xbf\xb9:C3\xa8>Y\xd0\xaf>\xdb\x87\x83<\r\x93\xbe<\x80\xce}>`C!:\xfar\x898\x1e\xcb\x0b:4\xf7%<\xb8F\x978^\x07\x8e5\xe0\xd4\x949\xa9\xb1|6\xed\xc8l1Q\xb4\x820F\n\xf00\xc9\xf6%1v\xa4\x840B\x10\x121\xe8\xd6\x9d0\n%(1W\x86\x891q\n\x1e1\xf3qL1c\x87\x8a1\x9d\x0c\xaf0\xc7\\\xf70\x89\xe271a\x06\x0c1\xdbeH1\x18\xbcN1\xef\xec.1\x14\xb0H1f\xa1\xc20CR/1o\xeb81\xc9\x96O1\x0e\x11O1\xd0\x99\x081\xa7Q\x051\xbe\x13\xd50\xe1\x8121f\x7f?1\xd6\xd2\xb61R*A1\x9d\x1a\x8f0\rQ\xd50\xcd\xf5\n1'

    communicator = Communicator()
    img = None
    while True:
        array_received = communicator.get_image()
        print('Message Read')
        print('Sending')
        communicator.send_data(bytes_to_send)
        print(array_received.shape)
        cv2.imshow('Frame', array_received)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # cv2.imshow('Frame',array_received)
        # cv2.waitKey(25)
