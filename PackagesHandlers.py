import logging
import os.path

import p2pstorage_core.server.Package as Pckg

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
            handle_contains_file_request(package)


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

    if os.path.exists(contains_file_request.get_file_path()):
        file_contains = True

    contains_file_response = Pckg.FileContainsResponsePackage(file_contains)
    contains_file_response.send(host_socket)
