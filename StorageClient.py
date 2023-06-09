import logging
import random
import socket
from threading import Timer

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server import StreamConfiguration
from p2pstorage_core.server.Exceptions import EmptyHeaderException
import p2pstorage_core.server.Package as Pckg

from db.FilesManager import FilesManager
from db.Transaction import TransactionsManager


class StorageClient:
    def __init__(self):
        self.__client_socket = None

        self.__address = None

        self.__connection_active = False

        self.__server_address = None

        self.__files_manager: FilesManager | None = None
        self.init_files_manager()

        self.__transactions_manager = TransactionsManager()

    def init_files_manager(self):
        self.__files_manager = FilesManager()
        self.__files_manager.init_table()

    def get_files_manager(self) -> FilesManager:
        return self.__files_manager

    def get_transactions_manager(self) -> TransactionsManager:
        return self.__transactions_manager

    def get_server_address(self) -> SocketAddress:
        return self.__server_address

    def get_socket(self) -> socket.socket:
        return self.__client_socket

    def is_connection_active(self) -> bool:
        return self.__connection_active

    def set_connection_active(self, running: bool) -> None:
        self.__connection_active = running

    def run(self, server_address: SocketAddress):
        self.__server_address = server_address

        logging.info(f'Try to connect to {self.__server_address}...')

        if self.try_connect():
            new_files_package = Pckg.NewFileRequestPackage(self.get_files_manager().get_files_info())
            new_files_package.send(self.get_socket())

            self.set_connection_active(True)
            self.handle_connection()
        else:
            logging.warning(f'Can\'t connect to {self.__server_address}!')

        self.__client_socket.close()

    def try_connect(self) -> bool:
        try:
            self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__client_socket.connect(self.__server_address)

            connect_request_package = Pckg.ConnectionRequestPackage(socket.gethostname())

            connect_request_package.send(self.__client_socket)
            connect_response_package: Pckg.ConnectionResponsePackage = Pckg.Package.recv(self.__client_socket)

            if not connect_response_package.is_connection_approved():
                logging.warning(f'Eject reason: {connect_response_package.get_reason()}')
                return False
            else:
                logging.info(f'Successful connected to {self.__server_address}!')
                logging.info(connect_response_package.get_broadcast_message())

            return True

        except ConnectionError:
            return False

    def handle_connection(self):
        while self.is_connection_active():
            try:
                package = Pckg.Package.recv(self.__client_socket)
            except EmptyHeaderException:
                logging.warning('Lost connection from server!')

                self.set_connection_active(False)
                break

            logging.debug(f'Package from server: {package}')

            from PackagesHandlers import handle_package
            handle_package(package, self)

    def start_transaction(self, file_name: str, establish_addr: SocketAddress, receiver_addr: SocketAddress) -> None:
        transaction_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        file_path = self.get_files_manager().get_file_path_by_name(file_name)

        # Trick to convert from tuple
        establish_addr = SocketAddress(*establish_addr)

        # Anonymous functions for close transactions after timeout
        def close_transaction(transaction_socket: socket.socket) -> None:
            transaction_socket.close()

            logging.info(f'[Transaction] Nobody was connected, closing transaction...')

        try:
            logging.info('[Transaction] Trying to establish...')

            addr = establish_addr.host
            port = random.randint(1000, 40000)
            transaction_addr = SocketAddress(addr, port)

            transaction_server_socket.bind(transaction_addr)
            transaction_server_socket.listen()

            logging.info('[Transaction] Transaction created!')

            transaction_started_packet = Pckg.FileTransactionStartResponsePackage(sender_addr=transaction_addr,
                                                                                  receiver_addr=receiver_addr,
                                                                                  file_name=file_name)
            transaction_started_packet.send(self.get_socket())

            # Close transaction if nobody connected after 3 second
            transaction_close_timeout = Timer(3, close_transaction, args=(transaction_server_socket,))
            transaction_close_timeout.start()

            receiver_socket, receiver_addr = transaction_server_socket.accept()

            logging.info(f'[Transaction] Connected host: {receiver_addr}')

            transaction_close_timeout.cancel()

            logging.info(f'[Transaction] Sending file {file_name}...')

            with open(file_path, 'rb') as file:
                while True:
                    files_bytes = file.read(StreamConfiguration.FILE_CHUNKS_SIZE)

                    if not files_bytes:
                        break

                    receiver_socket.send(files_bytes)

            logging.info(f'[Transaction] File sent! Transaction closed.')

            receiver_socket.close()
            transaction_server_socket.close()

        except OSError:
            logging.warning(f'[Transaction] Can\'t start transaction! Reloading...')
            self.start_transaction(file_name, establish_addr, receiver_addr)
