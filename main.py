import logging
import threading
from typing import Optional

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

from StorageClient import StorageClient


def main():
    logging.basicConfig(level=logging.DEBUG)

    storage_client = StorageClient()

    user_input_handler(storage_client)


def user_input_handler(storage_client: StorageClient) -> None:
    running = True

    while running:
        user_input = input()

        command_parts = user_input.split()

        command_name = command_parts[0]
        args = command_parts[1:]

        print(command_name, args)

        from Commands import handle_command
        handle_command(storage_client, command_name, args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
