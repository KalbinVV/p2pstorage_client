import logging
import os.path
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import ConnectionLostPackage, NewFileRequestPackage

from StorageClient import StorageClient


def handle_command(client: StorageClient, command_name: str, args: list[str]) -> None:
    match command_name:
        case 'connect':
            handle_connect_command(client, args)
        case 'q':
            handle_connection_lost_command(client)
        case 'disconnect':
            handle_connection_lost_command(client)
        case 'send_file':
            handle_send_file_command(client, args)


def handle_connect_command(client: StorageClient, args: list[str]) -> None:
    host = args[0]
    port = int(args[1])

    addr = SocketAddress(host, port)

    connection_thread = threading.Thread(target=client.run, args=(addr,), daemon=True)
    connection_thread.start()


def handle_connection_lost_command(client: StorageClient) -> None:
    if client.is_running():
        connection_lost_package = ConnectionLostPackage()

        connection_lost_package.send(client.get_socket())

        logging.info(f'Leaving {client.get_server_address()} server...')


def handle_send_file_command(client: StorageClient, args: list[str]) -> None:
    file_path = args[0]

    if not os.path.exists(file_path):
        logging.error('Invalid file path')
        return

    file_size = os.stat(file_path).st_size
    file_name = os.path.basename(file_path)

    new_file_package = NewFileRequestPackage(file_name, file_size)
    new_file_package.send(client.get_socket())
