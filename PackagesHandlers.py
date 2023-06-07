import logging
from p2pstorage_core.server.Package import Package, PackageType, ConnectionLostPackage, HostsListResponsePackage

from StorageClient import StorageClient


def handle_package(package: Package, storage_client: StorageClient) -> None:
    match package.get_type():
        case PackageType.CONNECTION_LOST:
            handle_connection_lost(package, storage_client)
        case PackageType.HOST_CONNECT_RESPONSE:
            handle_host_connect_response(package)


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