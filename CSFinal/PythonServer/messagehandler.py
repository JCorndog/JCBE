import queue
import random
import threading
from enum import Enum
from typing import Tuple, Optional

import numpy as np
import zmq


class SendMode(Enum):
    SENDING = 0
    RECEIVING = 1


class MessageHandler(threading.Thread):
    def __init__(self, port: int = 5555, verbose=False):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        self.socket.bind(f"tcp://*:{port}")

        print(f'Server listening on port {port}')
        self.incoming_message_queue = queue.Queue(maxsize=1)
        self.outgoing_message_queue = queue.Queue(maxsize=1)

        self.mode = SendMode.RECEIVING
        self.__mode = SendMode.RECEIVING

        self.__stop_ex = False

    def run(self):
        while not self.__stop_ex:
            if self.__mode == SendMode.RECEIVING:
                self.__receive_message()
            else:
                self.__send_message()

    def stop(self):
        self.__stop_ex = True

    def __receive_message(self) -> None:
        event = self.socket.poll(timeout=1000)
        if event == 0:
            return

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

    def get_message(self) -> Tuple[Optional[bytes], Optional[Exception]]:
        if self.mode == SendMode.SENDING:
            return None, Exception('Data needs to be sent before any data can be received')
        msg = self.incoming_message_queue.get(block=True)
        self.mode = SendMode.SENDING
        return msg, None

    def send_message(self, data: bytes) -> Optional[Exception]:
        if self.mode == SendMode.RECEIVING:
            return Exception('Data needs to be received before any data can be sent')
        self.outgoing_message_queue.put(data)
        self.mode = SendMode.RECEIVING


class Communicator:
    def __init__(self, port=5555, verbose: bool = False) -> None:
        self.verbose = verbose
        self.message_handler = MessageHandler(port=port, verbose=verbose)
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

    def send_data(self, data: bytes) -> None:
        if self.verbose:
            print(data)
        ex = self.message_handler.send_message(data)
        if ex:
            raise ex

    def stop(self) -> None:
        self.message_handler.stop()


if __name__ == '__main__':

    i = 0
    p = ['1', '0']
    s = ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
    b'i001'
    bytes_to_send = i.to_bytes(4, byteorder='little') + ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
    print(bytes_to_send)
    communicator = Communicator(verbose=False)
    communicator.get_data()
    img = None

    # array_received = communicator.get_image()
    communicator.send_data(bytes_to_send)

    while True:
        # print('Loop')
        array_received = communicator.get_image()
        # print('Message Received')
        # print('Sending')

        if i == 2:
            communicator.send_data(i.to_bytes(4, byteorder='little') + b'r')
            print('Reset')
            i = 0
        else:
            bytes_to_send = i.to_bytes(4, byteorder='little') + ('i' + ''.join([random.choice(p) for x in range(3)])).encode()
            # print(bytes_to_send)
            communicator.send_data(bytes_to_send)
            # print(array_received.shape,array_received.dtype)
            i += 1

        # cv2.imshow('Frame', array_received)
        # # Press Q on keyboard to  exit
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        # exit()
        # cv2.imshow('Frame',array_received)
        # cv2.waitKey(25)
