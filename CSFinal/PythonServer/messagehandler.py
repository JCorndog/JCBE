import random

import zmq
import numpy as np
import threading
from warnings import warn


class MessageHandler(threading.Thread):
    def __init__(self, port: int = 5555, verbose=False):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")
        print(f'Server listening on port {port}')
        self.incoming_message = None
        self.incoming_message_lock = threading.Lock()

        self.outgoing_message = None
        self.outgoing_message_ready = False
        self.outgoing_message_lock = threading.Lock()

        self.send_mode = False

        self.incoming_message_ready_lock = threading.Lock()
        self.incoming_message_ready_lock.acquire()

    def run(self):
        while True:
            self._receive_message()
            self._send_message()

    def _receive_message(self):
        if self.send_mode:
            return
        self.incoming_message_lock.acquire()
        self.incoming_message = self.socket.recv()
        self.send_mode = True
        if self.verbose:
            print('Message received')
        self.incoming_message_lock.release()
        if self.incoming_message_ready_lock.locked():
            self.incoming_message_ready_lock.release()

    def _send_message(self) -> None:
        if not self.send_mode or not self.outgoing_message_ready:
            return
        self.outgoing_message_lock.acquire()
        self.socket.send(self.outgoing_message, flags=zmq.NOBLOCK)
        self.outgoing_message_ready = False
        self.outgoing_message = None
        self.send_mode = False
        if self.verbose:
            print('Message sent')
        self.outgoing_message_lock.release()

    def get_message(self):
        self.incoming_message_ready_lock.acquire()
        self.incoming_message_lock.acquire()
        msg = self.incoming_message
        self.incoming_message = None
        self.incoming_message_lock.release()
        return msg

    def send_message(self, data):
        if self.outgoing_message_ready:
            warn('Overwriting unsent data')
        self.outgoing_message_lock.acquire()
        self.outgoing_message = data
        self.outgoing_message_ready = True
        self.outgoing_message_lock.release()


class Communicator:
    def __init__(self, verbose=False):
        self.message_handler = MessageHandler(verbose=verbose)
        self.message_handler.daemon = True
        self.message_handler.start()

    def get_data(self) -> bytes:
        return self.message_handler.get_message()

    def get_image(self):
        message = self.get_data()
        touch = int.from_bytes(message[:4], 'little')
        dims = int.from_bytes(message[4:8], 'little'), int.from_bytes(message[8:12], 'little'), 3
        array_received = np.frombuffer(message[12:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received

    def send_data(self, data) -> None:
        self.message_handler.send_message(data)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import cv2

    p = ['1', '0']
    s = ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
    b'i001'
    bytes_to_send = ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
    print(bytes_to_send)
    communicator = Communicator(verbose=True)
    img = None

    array_received = communicator.get_image()
    communicator.send_data(bytes_to_send)
    while True:
        print('Loop')
        array_received = communicator.get_image()
        print('Message Received')
        print('Sending')
        bytes_to_send = ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
        print(bytes_to_send)
        communicator.send_data(bytes_to_send)
        print(array_received.shape)
        cv2.imshow('Frame', array_received)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # cv2.imshow('Frame',array_received)
        # cv2.waitKey(25)
