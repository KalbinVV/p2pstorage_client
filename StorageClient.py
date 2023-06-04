import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Exceptions import EmptyHeaderException
from p2pstorage_core.server.Package import ConnectionRequestPackage, Package, ConnectionResponsePackage


class StorageClient:
    def __init__(self):
        self.__client_socket = None

        self.__address = None

        self.__running = False

        self.__server_address = None

    def get_server_address(self):
        return self.__server_address

    def get_socket(self):
        return self.__client_socket

    def is_running(self) -> bool:
        return self.__running

    def set_running(self, running: bool) -> None:
        self.__running = running

    def run(self, server_address: SocketAddress):
        self.__server_address = server_address

        logging.info(f'Try to connect to {self.__server_address}...')

        if self.try_connect():
            logging.info(f'Successful connected to {self.__server_address}!')

            self.set_running(True)
            self.handle_connection()
        else:
            logging.warning(f'Can\'t connect to {self.__server_address}!')

        self.__client_socket.close()

    def try_connect(self) -> bool:
        try:
            self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def handle_connection(self):
        while self.is_running():
            try:
                package = Package.recv(self.__client_socket)
            except EmptyHeaderException:
                logging.warning('Lost connection from server!')

                self.set_running(False)
                break

            logging.debug(f'Package from server: {package}')

            from PackageHandlers import handle_package
            handle_package(package, self)
