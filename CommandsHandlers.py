import logging
import os.path
import threading
from typing import Callable

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import ConnectionLostPackage, NewFileRequestPackage, HostsListRequestPackage

from StorageClient import StorageClient

commands_dict: dict[str, Callable[[StorageClient, list[str]], None]] = dict()


class InvalidCommandException(Exception):
    def __init__(self, msg: str = 'Command not exist!'):
        super().__init__(msg)


class InvalidArgsCommandException(Exception):
    def __init__(self, msg: str = 'Invalid args'):
        super().__init__(msg)


def handle_command(client: StorageClient, command_name: str, args: list[str]) -> None:
    if command_name not in commands_dict:
        raise InvalidCommandException(f'Command {command_name} not exists!')

    commands_dict[command_name](client, args)


def register_command(command_name, method: Callable[[StorageClient, list[str]], None]) -> None:
    commands_dict[command_name] = method


def init_commands() -> None:
    register_command('connect', handle_connect_command)

    register_command('q', handle_connection_lost_command)
    register_command('disconnect', handle_connection_lost_command)

    register_command('send_file', handle_send_file_command)

    register_command('hosts', handle_hosts_list_command)


def handle_connect_command(client: StorageClient, args: list[str]) -> None:
    try:
        host = args[0]
        port = int(args[1])
    except (IndexError, TypeError):
        raise InvalidArgsCommandException

    addr = SocketAddress(host, port)

    connection_thread = threading.Thread(target=client.run, args=(addr,), daemon=True)
    connection_thread.start()


def handle_connection_lost_command(client: StorageClient, _args: list[str]) -> None:
    if client.is_running():
        connection_lost_package = ConnectionLostPackage()

        connection_lost_package.send(client.get_socket())

        logging.info(f'Leaving {client.get_server_address()} server...')

        logging.info('Disconnected from server!')


def handle_send_file_command(client: StorageClient, args: list[str]) -> None:
    if len(args) < 1:
        raise InvalidArgsCommandException

    file_path = args[0]

    if not os.path.exists(file_path):
        raise InvalidArgsCommandException('Invalid file path')

    file_size = os.stat(file_path).st_size
    file_name = os.path.basename(file_path)

    new_file_package = NewFileRequestPackage(file_name, file_size)
    new_file_package.send(client.get_socket())


def handle_hosts_list_command(client: StorageClient, _args: list[str]) -> None:
    host_socket = client.get_socket()

    hosts_list_request = HostsListRequestPackage()
    hosts_list_request.send(host_socket)
