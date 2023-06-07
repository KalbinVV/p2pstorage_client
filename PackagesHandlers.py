import logging
from p2pstorage_core.server.Package import Package, PackageType, ConnectionLostPackage, HostsListResponsePackage, \
    NewFileResponsePackage, FilesListResponsePackage

from StorageClient import StorageClient


def handle_package(package: Package, storage_client: StorageClient) -> None:
    match package.get_type():
        case PackageType.CONNECTION_LOST:
            handle_connection_lost(package, storage_client)
        case PackageType.HOST_CONNECT_RESPONSE:
            handle_host_connect_response(package)
        case PackageType.NEW_FILE_RESPONSE:
            handle_new_file_response(package)
        case PackageType.FILES_LIST_RESPONSE:
            handle_files_list_response(package)


def handle_connection_lost(package: Package, storage_client: StorageClient) -> None:
    connection_lost_package = ConnectionLostPackage.from_abstract(package)

    logging.warning(f'Lost connection from server {storage_client.get_server_address()}: '
                    f'{connection_lost_package.get_reason()}')

    storage_client.set_connection_active(False)


def handle_host_connect_response(package: Package):
    hosts_list_response: HostsListResponsePackage = HostsListResponsePackage.from_abstract(package)

    if hosts_list_response.is_response_approved():
        hosts = hosts_list_response.get_hosts()

        logging.info('Connected hosts: ')

        for host in hosts:
            logging.info(host)

    else:
        logging.error(f'Can\' get list of hosts: {hosts_list_response.get_reject_reason()}')


def handle_new_file_response(package: Package) -> None:
    new_file_response = NewFileResponsePackage.from_abstract(package)

    if new_file_response.is_file_approved():
        logging.info('File successful added!')
    else:
        logging.error(f'Can\'t add file: {new_file_response.get_reason()}')


def handle_files_list_response(package: Package) -> None:
    files_list_response = FilesListResponsePackage.from_abstract(package)

    if files_list_response.is_response_approved():
        logging.info('Files lists: ')

        for file_info in files_list_response.get_files():
            logging.info(file_info)
    else:
        logging.error(f'Can\'t get list of files: {files_list_response.get_reject_reason()}')
