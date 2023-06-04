import logging
import threading
from typing import Optional

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

from StorageClient import StorageClient


def main():
    logging.basicConfig(level=logging.DEBUG)

    storage_client = StorageClient()

    server_address = input('Enter server address (host:port): ')

    splitted_server_address = server_address.split(':')
    host, port = splitted_server_address[0], int(splitted_server_address[1])

    user_input_thread: Optional[threading.Thread] = None

    try:
        user_input_thread = threading.Thread(target=user_input_handler, args=(storage_client,))
        user_input_thread.start()

        storage_client.run(SocketAddress(host, port))
    except KeyboardInterrupt:
        pass

    logging.info('Stopping...')


def user_input_handler(storage_client: StorageClient) -> None:
    while storage_client.is_running():
        print('!')
        user_input = input()
        print(user_input)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
