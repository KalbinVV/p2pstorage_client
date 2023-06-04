import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import ConnectionLostPackage

from StorageClient import StorageClient


def handle_command(client: StorageClient, command_name: str, args: list[str]) -> None:
    match command_name:
        case 'connect':
            handle_connect_command(client, args)
        case 'q':
            handle_quit_command(client)


def handle_connect_command(client: StorageClient, args: list[str]) -> None:
    host = args[0]
    port = int(args[1])

    addr = SocketAddress(host, port)

    connection_thread = threading.Thread(target=client.run, args=(addr,))
    connection_thread.start()


def handle_quit_command(client: StorageClient) -> None:
    connection_lost_package = ConnectionLostPackage()
