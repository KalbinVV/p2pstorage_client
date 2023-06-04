import logging
from p2pstorage_core.server.Package import Package, PackageType, ConnectionLostPackage

from StorageClient import StorageClient


def handle_package(package: Package, storage_client: StorageClient) -> None:
    match package.get_type():
        case PackageType.CONNECTION_LOST:
            handle_connection_lost(package, storage_client)


def handle_connection_lost(package: Package, storage_client: StorageClient) -> None:
    connection_lost_package: ConnectionLostPackage = ConnectionLostPackage.from_abstract(package)

    logging.info(f'Lost connection from server {storage_client.get_server_address()}: '
                 f'{connection_lost_package.get_reason()}')

    storage_client.set_running(False)
