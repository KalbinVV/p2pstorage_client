import logging
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import ConnectionLostPackage

from StorageClient import StorageClient


def handle_command(client: StorageClient, command_name: str, args: list[str]) -> None:
    match command_name:
        case 'connect':
            handle_connect_command(client, args)
        case 'q':
            handle_connection_lost_command(client)
        case 'disconnect':
            handle_connection_lost_command(client)


def handle_connect_command(client: StorageClient, args: list[str]) -> None:
    host = args[0]
    port = int(args[1])

    addr = SocketAddress(host, port)

    connection_thread = threading.Thread(target=client.run, args=(addr,), daemon=True)
    connection_thread.start()


def handle_connection_lost_command(client: StorageClient) -> None:
    connection_lost_package = ConnectionLostPackage()

    connection_lost_package.send(client.get_socket())

    logging.info(f'Leaving {client.get_server_address()} server...')
