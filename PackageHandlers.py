import logging

from p2pstorage_core.server.Package import Package, PackageType

from StorageClient import StorageClient


def handle_package(package: Package, storage_client: StorageClient) -> None:
    match package.get_type():
        case PackageType.CONNECTION_LOST:
            handle_connection_lost(package, storage_client)


def handle_connection_lost(package: Package, storage_client: StorageClient) -> None:
    reason = package.get_data()

    logging.info(f'Connection from server lost: {reason}')
    storage_client.set_running(False)
