import logging
import os.path
import socket
import threading

import p2pstorage_core.server.Package as Pckg
from p2pstorage_core.server import StreamConfiguration

from StorageClient import StorageClient


def handle_package(package: Pckg.Package, storage_client: StorageClient) -> None:
    match package.get_type():
        case Pckg.PackageType.CONNECTION_LOST:
            handle_connection_lost(package, storage_client)
        case Pckg.PackageType.HOST_CONNECT_RESPONSE:
            handle_host_connect_response(package)
        case Pckg.PackageType.NEW_FILE_RESPONSE:
            handle_new_file_response(package)
        case Pckg.PackageType.FILES_LIST_RESPONSE:
            handle_files_list_response(package)
        case Pckg.PackageType.FILE_CONTAINS_REQUEST:
            handle_contains_file_request(package, storage_client)
        case Pckg.PackageType.FILE_TRANSACTION_START_REQUEST:
            handle_transaction_start_request(package, storage_client)
        case Pckg.PackageType.FILE_TRANSACTION_START_RESPONSE:
            handle_transaction_start_response(package, storage_client)
        case Pckg.PackageType.NEW_HOST_CONNECTED:
            handle_new_host_connected(package)


def handle_connection_lost(package: Pckg.Package, storage_client: StorageClient) -> None:
    connection_lost_package = Pckg.ConnectionLostPackage.from_abstract(package)

    logging.warning(f'Lost connection from server {storage_client.get_server_address()}: '
                    f'{connection_lost_package.get_reason()}')

    storage_client.set_connection_active(False)


def handle_host_connect_response(package: Pckg.Package):
    hosts_list_response = Pckg.HostsListResponsePackage.from_abstract(package)

    if hosts_list_response.is_response_approved():
        hosts = hosts_list_response.get_hosts()

        logging.info('Connected hosts: ')

        for host in hosts:
            logging.info(host)

    else:
        logging.error(f'Can\' get list of hosts: {hosts_list_response.get_reject_reason()}')


def handle_new_file_response(package: Pckg.Package) -> None:
    new_file_response = Pckg.NewFileResponsePackage.from_abstract(package)

    if new_file_response.is_file_approved():
        logging.info('File successful added!')
    else:
        logging.error(f'Can\'t add file: {new_file_response.get_reason()}')


def handle_files_list_response(package: Pckg.Package) -> None:
    files_list_response = Pckg.FilesListResponsePackage.from_abstract(package)

    if files_list_response.is_response_approved():
        logging.info('Files lists: ')

        for file_info in files_list_response.get_files():
            logging.info(file_info)
    else:
        logging.error(f'Can\'t get list of files: {files_list_response.get_reject_reason()}')


def handle_contains_file_request(package: Pckg.Package, client: StorageClient) -> None:
    contains_file_request = Pckg.FileContainsRequestPackage.from_abstract(package)
    host_socket = client.get_socket()

    file_contains = False

    files_manager = client.get_files_manager()
    file_path = files_manager.get_file_path_by_name(contains_file_request.get_file_name())

    if os.path.exists(file_path):
        file_contains = True

    contains_file_response = Pckg.FileContainsResponsePackage(file_contains)
    contains_file_response.send(host_socket)


def handle_transaction_start_request(package: Pckg.Package, storage_client: StorageClient):
    transaction_start_request = Pckg.FileTransactionStartRequestPackage.from_abstract(package)

    file_name = transaction_start_request.get_file_name()
    files_manager = storage_client.get_files_manager()

    if not files_manager.is_contains_file(file_name):
        transaction_start_response = Pckg.FileTransactionStartResponsePackage(sender_addr=None,
                                                                              file_name='',
                                                                              transaction_started=False,
                                                                              reject_reason='File not exists!')
        transaction_start_response.send(storage_client.get_socket())
    else:
        establish_addr = transaction_start_request.get_establish_addr()

        logging.info(f'Transaction started: {file_name}')

        transaction_thread = threading.Thread(target=storage_client.start_transaction,
                                              args=(file_name, establish_addr), daemon=True)
        transaction_thread.start()


def handle_transaction_start_response(package: Pckg.Package, _storage_client: StorageClient):
    transaction_start_response = Pckg.FileTransactionStartResponsePackage.from_abstract(package)

    if transaction_start_response.is_transaction_started():
        sender_addr = transaction_start_response.get_sender_addr()

        logging.info('Start transaction...')

        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.connect(sender_addr)

        logging.info(f'[Transaction] Connected to {sender_addr}')

        file_name = transaction_start_response.get_file_name()

        receiving_folder = './p2p_download'

        if not os.path.exists(receiving_folder):
            os.mkdir(receiving_folder)

        downloaded_file_path = os.path.join(receiving_folder, file_name)

        logging.info(f'[Transaction] Downloading file to {downloaded_file_path}...')

        while True:
            with open(downloaded_file_path, 'ab') as file:
                data = receiver_socket.recv(StreamConfiguration.FILE_CHUNKS_SIZE)

                if not data:
                    break

                file.write(data)

        logging.info(f'[Transaction] File downloaded!')
        logging.info(f'[Transaction] Transaction is closing...')

        receiver_socket.close()
    elif not transaction_start_response.is_transaction_started():
        logging.info(f'[Transaction] Can\'t create a transaction: {transaction_start_response.get_reject_reason()}')


def handle_new_host_connected(package: Pckg.Package) -> None:
    new_host_connected_package = Pckg.NewHostConnectedPackage.from_abstract(package)

    host_addr = new_host_connected_package.get_host_addr()
    host_name = new_host_connected_package.get_host_name()

    logging.info(f'[New host] {host_addr} ({host_name}) connected!')