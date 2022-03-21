import random

import zmq
import numpy as np
import threading
import queue
from warnings import warn
from enum import Enum


# class MessageHandler(threading.Thread):
#     def __init__(self, port: int = 5555, verbose=False):
#         threading.Thread.__init__(self)
#         self.verbose = verbose
#         self.context = zmq.Context()
#         self.socket = self.context.socket(zmq.REP)
#         self.socket.bind(f"tcp://*:{port}")
#         print(f'Server listening on port {port}')
#         self.incoming_message = None
#         self.incoming_message_lock = threading.Lock()
#
#         self.outgoing_message = None
#         self.outgoing_message_ready = False
#         self.outgoing_message_lock = threading.Lock()
#
#         self.send_mode = False
#
#         self.incoming_message_ready_lock = threading.Lock()
#         self.incoming_message_ready_lock.acquire()
#
#         self.stop_ex = False
#
#     def run(self):
#         while not self.stop_ex:
#             self._receive_message()
#             self._send_message()
#
#     def stop(self):
#         self.stop_ex = True
#
#     def _receive_message(self):
#         if self.send_mode:
#             return
#         self.incoming_message_lock.acquire()
#         self.incoming_message = self.socket.recv()
#         self.send_mode = True
#         if self.verbose:
#             print('Message received')
#         self.incoming_message_lock.release()
#         if self.incoming_message_ready_lock.locked():
#             self.incoming_message_ready_lock.release()
#
#     def _send_message(self) -> None:
#         if not self.send_mode or not self.outgoing_message_ready:
#             return
#         self.outgoing_message_lock.acquire()
#         self.socket.send(self.outgoing_message, flags=zmq.NOBLOCK)
#         self.outgoing_message_ready = False
#         self.outgoing_message = None
#         self.send_mode = False
#         if self.verbose:
#             print('Message sent')
#         self.outgoing_message_lock.release()
#
#     def get_message(self):
#         self.incoming_message_ready_lock.acquire()
#         self.incoming_message_lock.acquire()
#         msg = self.incoming_message
#         if msg is None:
#             raise Exception('Msg is none')
#         self.incoming_message = None
#         self.incoming_message_lock.release()
#         return msg
#
#     def send_message(self, data):
#         if self.outgoing_message_ready:
#             warn('Overwriting unsent data')
#         self.outgoing_message_lock.acquire()
#         self.outgoing_message = data
#         self.outgoing_message_ready = True
#         self.outgoing_message_lock.release()
#
#
# class MessageHandler2(threading.Thread):
#     def __init__(self, port: int = 5555, verbose=False):
#         threading.Thread.__init__(self)
#         self.verbose = verbose
#         self.context = zmq.Context()
#         self.socket = self.context.socket(zmq.REP)
#         self.socket.bind(f"tcp://*:{port}")
#         print(f'Server listening on port {port}')
#         self.incoming_message_queue = queue.Queue()
#
#         self.outgoing_message = None
#         self.outgoing_message_ready = False
#         self.outgoing_message_lock = threading.Lock()
#
#         self.send_mode = False  # if True data needs to be sent if False data needs to be received
#
#         self.incoming_message_ready_lock = threading.Lock()
#         self.incoming_message_ready_lock.acquire()
#
#         self.stop_ex = False
#
#     def run(self):
#         while not self.stop_ex:
#             self._receive_message()
#             self._send_message()
#
#     def stop(self):
#         self.stop_ex = True
#
#     def _receive_message(self):
#         if self.send_mode:
#             return
#         self.incoming_message_queue.put(self.socket.recv())
#         self.send_mode = True
#         if self.verbose:
#             print('Message received')
#
#     def _send_message(self) -> None:
#         if self.outgoing_message == b'r':
#             print('-------------------------------------------------------------------')
#         if not self.outgoing_message_ready or not self.send_mode or self.outgoing_message is None:
#             return
#         self.outgoing_message_lock.acquire()
#         self.socket.send(self.outgoing_message, flags=zmq.NOBLOCK)
#         self.outgoing_message = None
#         self.send_mode = False
#         if self.verbose:
#             print('Message sent')
#         self.outgoing_message_lock.release()
#
#     def get_message(self):
#         if self.send_mode and not self.outgoing_message_lock:
#             raise Exception('Data needs to be sent before any data can be received')
#         msg = self.incoming_message_queue.get(block=True)
#         return msg
#
#     def send_message(self, data):
#
#         if self.outgoing_message_ready:
#             warn('Overwriting unsent data')
#         self.outgoing_message_lock.acquire()
#         self.outgoing_message = data
#         self.outgoing_message_ready = True
#         self.outgoing_message_lock.release()
#
#
# class MessageHandler3(threading.Thread):
#     def __init__(self, port: int = 5555, verbose=False):
#         threading.Thread.__init__(self)
#         self.verbose = verbose
#         self.context = zmq.Context()
#         self.socket = self.context.socket(zmq.REP)
#         self.socket.bind(f"tcp://*:{port}")
#         print(f'Server listening on port {port}')
#         self.incoming_message_queue = queue.Queue(maxsize=1)
#         self.outgoing_message_queue = queue.Queue(maxsize=1)
#
#         self.data_loaded = True
#
#         self.sending_message = threading.Lock()
#         self.receiving_message = threading.Lock()
#         self.ready_to_send_msg = False
#         self.ready_to_receive_msg = False
#
#         self.waiting_for_msg_to_send = False
#         self.waiting_for_msg_to_receive = True
#
#         self.stop_ex = False
#
#     def run(self):
#         while not self.stop_ex:
#             self.__receive_message()
#             self.__send_message()
#
#     def stop(self):
#         self.stop_ex = True
#
#     def __receive_message(self):
#         self.incoming_message_queue.put(self.socket.recv())
#         if self.verbose:
#             print('Message received')
#
#     def __send_message(self) -> None:
#         self.socket.send(self.outgoing_message_queue.get(block=True))
#         if self.verbose:
#             print('Message sent')
#
#     def get_message(self):
#         if not self.data_loaded:
#             raise Exception('Data needs to be sent before any data can be received')
#         msg = self.incoming_message_queue.get(block=True)
#         self.ready_to_receive_msg = False
#         return msg
#
#     def send_message(self, data):
#
#         if not self.ready_to_send_msg:
#             raise Exception('Data needs to be received before any data can be sent')
#         self.outgoing_message_queue.put(data)
#         self.data_loaded = True
#
#
# class Communicator:
#     def __init__(self, verbose=False):
#         self.verbose = verbose
#         self.message_handler = MessageHandler2(verbose=False)
#         self.message_handler.daemon = True
#         self.message_handler.start()
#
#     def get_data(self) -> bytes:
#         return self.message_handler.get_message()
#
#     def get_image(self):
#         message = self.get_data()
#         touch = int.from_bytes(message[:4], 'little')
#         dims = int.from_bytes(message[4:8], 'little'), int.from_bytes(message[8:12], 'little'), 3
#         array_received = np.frombuffer(message[12:], dtype=np.float32)
#         array_received = array_received.reshape(dims)
#         array_received = np.rot90(array_received)
#         return array_received
#
#     def send_data(self, data) -> None:
#         if self.verbose:
#             print(data)
#         self.message_handler.send_message(data)
#
#     def stop(self):
#         self.message_handler.stop()


class SendMode(Enum):
    SENDING = 0
    RECEIVING = 1


class MessageHandler(threading.Thread):
    def __init__(self, port: int = 5555, verbose=False):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        # self.socket.setsockopt(zmq.LINGER, 0)
        # self.socket.setsockopt(zmq.COMPLETE, 1)
        self.socket.bind(f"tcp://*:{port}")

        print(f'Server listening on port {port}')
        self.incoming_message_queue = queue.Queue(maxsize=1)
        self.outgoing_message_queue = queue.Queue(maxsize=1)

        self.mode = SendMode.RECEIVING
        self.__mode = SendMode.RECEIVING
        self.data_loaded = True

        self.sending_message = threading.Lock()
        self.receiving_message = threading.Lock()
        self.ready_to_send_msg = False
        self.ready_to_receive_msg = False

        self.waiting_for_msg_to_send = False
        self.waiting_for_msg_to_receive = True

        self.__stop_ex = False

    def run(self):
        while not self.__stop_ex:
            if self.__mode == SendMode.RECEIVING:
                self.__receive_message()
            else:
                self.__send_message()

    def stop(self):
        self.__stop_ex = True

    def __receive_message(self):
        # event = self.socket.poll(timeout=300)
        # if event == 0:
        #     return

        self.incoming_message_queue.put(self.socket.recv())

        if self.verbose:
            print('Message received')
        self.__mode = SendMode.SENDING

    def __send_message(self) -> None:
        try:
            self.socket.send(self.outgoing_message_queue.get(block=True, timeout=.5))
        except queue.Empty:
            return
        else:
            self.outgoing_message_queue.task_done()
            if self.verbose:
                print('Message sent')
        self.__mode = SendMode.RECEIVING

    def get_message(self):
        if self.mode == SendMode.SENDING:
            return None, Exception('Data needs to be sent before any data can be received')
        msg = self.incoming_message_queue.get(block=True)
        self.mode = SendMode.SENDING
        return msg, None

    def send_message(self, data):
        if self.mode == SendMode.RECEIVING:
            return Exception('Data needs to be received before any data can be sent')
        self.outgoing_message_queue.put(data)
        self.mode = SendMode.RECEIVING


class Communicator:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.message_handler = MessageHandler()
        self.message_handler.daemon = True
        self.message_handler.start()

    def get_data(self) -> bytes:

        data, ex = self.message_handler.get_message()
        if ex:
            raise ex
        return data

    def get_image(self):
        message = self.get_data()
        touch = int.from_bytes(message[:4], 'little')
        dims = int.from_bytes(message[4:8], 'little'), int.from_bytes(message[8:12], 'little'), 3
        array_received = np.frombuffer(message[12:], dtype=np.float32)
        array_received = array_received.reshape(dims)
        array_received = np.rot90(array_received)
        return array_received

    def send_data(self, data) -> None:
        if self.verbose:
            print(data)
        ex = self.message_handler.send_message(data)
        if ex:
            raise ex

    def stop(self):
        self.message_handler.stop()


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
    i = 0
    while True:
        # print('Loop')
        array_received = communicator.get_image()
        # print('Message Received')
        # print('Sending')

        if i == 200:
            communicator.send_data(b'r')
            i = 0
        else:
            bytes_to_send = ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
            # print(bytes_to_send)
            communicator.send_data(bytes_to_send)
            # print(array_received.shape,array_received.dtype)
            i += 1

        cv2.imshow('Frame', array_received)
        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # exit()
        # cv2.imshow('Frame',array_received)
        # cv2.waitKey(25)
