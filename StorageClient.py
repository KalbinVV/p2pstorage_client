import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import PackageType, ConnectionRequestPackage, Package, ConnectionResponsePackage


class StorageClient:
    def __init__(self, server_address: SocketAddress):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__address = None

    def run(self):
        logging.info(f'Try to connect to {self.__server_address}...')

        if self.try_connect():
            logging.info(f'Successful connected to {self.__server_address}!')

            running = True

            while running:
                try:
                    pass
                except KeyboardInterrupt:
                    running = False

        else:
            logging.warning(f'Can\'t connect to {self.__server_address}!')

        self.__client_socket.close()

    def try_connect(self) -> bool:
        try:
            self.__client_socket.connect(self.__server_address)

            connect_request_package = ConnectionRequestPackage()

            connect_request_package.send(self.__client_socket)

            connect_response_package: ConnectionResponsePackage = Package.recv(self.__client_socket)

            if not connect_response_package.is_connection_approved():
                logging.warning(f'Eject reason: {connect_response_package.get_reason()}')
                return False

            return True

        except ConnectionError:
            return False
