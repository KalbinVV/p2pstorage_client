import logging
import os.path
import sqlite3
import threading
from typing import Callable

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Crypt import get_hash_of_file
from p2pstorage_core.server.FileInfo import FileInfo
import p2pstorage_core.server.Package as Pckg

from StorageClient import StorageClient


class InvalidCommandException(Exception):
    def __init__(self, msg: str = 'Command not exist!'):
        super().__init__(msg)


class InvalidArgsCommandException(Exception):
    def __init__(self, msg: str = 'Invalid args'):
        super().__init__(msg)


commands_dict: dict[str, Callable[[StorageClient, list[str]], None]] = dict()


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
    register_command('files', handle_files_list_command)

    register_command('download_by_id', handle_download_by_id_command)


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
    if client.is_connection_active():
        connection_lost_package = Pckg.ConnectionLostPackage()

        connection_lost_package.send(client.get_socket())

        logging.info(f'Leaving {client.get_server_address()} server...')

        logging.info('Disconnected from server!')


def handle_send_file_command(client: StorageClient, args: list[str]) -> None:
    if not client.is_connection_active():
        raise InvalidArgsCommandException('You should be connected to server!')

    if len(args) < 1:
        raise InvalidArgsCommandException

    file_path = args[0]

    if not os.path.exists(file_path):
        raise InvalidArgsCommandException('Invalid file path')

    file_size = os.stat(file_path).st_size
    file_hash = get_hash_of_file(file_path)
    file_name = os.path.basename(file_path)
    file_path = os.path.abspath(file_path)

    files_manager = client.get_files_manager()

    try:
        files_manager.add_file(file_name, file_path, file_size, file_hash)
    except sqlite3.IntegrityError:
        raise InvalidArgsCommandException('Files should be unique!')

    new_file_package = Pckg.NewFileRequestPackage([FileInfo(file_name, file_size, file_hash)])
    new_file_package.send(client.get_socket())


def handle_hosts_list_command(client: StorageClient, _args: list[str]) -> None:
    if not client.is_connection_active():
        raise InvalidArgsCommandException('You should be connected to server!')

    host_socket = client.get_socket()

    hosts_list_request = Pckg.HostsListRequestPackage()
    hosts_list_request.send(host_socket)


def handle_files_list_command(client: StorageClient, _args: list[str]) -> None:
    if not client.is_connection_active():
        raise InvalidArgsCommandException('You should be connected to server!')

    host_socket = client.get_socket()

    files_list_request = Pckg.FilesListRequestPackage()
    files_list_request.send(host_socket)


def handle_download_by_id_command(client: StorageClient, args: list[str]) -> None:
    if len(args) < 1:
        raise InvalidArgsCommandException('You should enter ID!')

    file_id = args[0]

    get_file_by_id_request = Pckg.GetFileByIdRequestPackage(file_id)

    get_file_by_id_request.send(client.get_socket())
