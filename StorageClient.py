import json
import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server import StreamConfiguration
from p2pstorage_core.server.Header import Header
from p2pstorage_core.server.Package import PackageType


class StorageClient:
    def __init__(self, server_address: SocketAddress):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__address = None

    def run(self):
        logging.info(f'Try to connect to {self.__server_address}...')

        if self.try_connect():
            logging.info(f'Successful connected! Your address: {self.__address}')

            running = True

            while running:
                try:
                    header_data = self.__client_socket.recv(StreamConfiguration.HEADER_SIZE)
                except KeyboardInterrupt:
                    running = False

        else:
            logging.warning(f'Can\'t connect to {self.__server_address}!')

        self.__client_socket.close()

    def try_connect(self) -> bool:
        try:
            self.__client_socket.connect(self.__server_address)
            connection_header = Header(0, PackageType.HOST_CONNECT_REQUEST,
                                       SocketAddress('', 0),
                                       self.__server_address)

            self.__client_socket.send(connection_header.encode())

            response_header_data = self.__client_socket.recv(StreamConfiguration.HEADER_SIZE)

            logging.debug(f'Response header data: {response_header_data}')

            response_header = Header.decode(response_header_data)

            logging.debug(f'Response header: {response_header}')

            if response_header.get_type() == PackageType.HOST_SUCCESSFUL_CONNECT_RESPONSE:
                logging.debug(f'Connection to {self.__server_address}...')

                package = response_header.load_package(self.__client_socket)

                logging.debug(f'Response package: {package}')

                json_response: dict = json.loads(package.to_json())

                logging.debug(f'Json response: {json_response}')

                host = json_response['host']
                port = json_response['port']

                self.__address = SocketAddress(host, port)

                return True

        except ConnectionError:
            return False

        return False
