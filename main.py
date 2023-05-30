import logging

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

from StorageClient import StorageClient


def main():
    logging.basicConfig(level=logging.DEBUG)

    server_address = SocketAddress('localhost', 5000)

    storage_client = StorageClient(server_address)

    logging.info('Starting...')

    storage_client.run()

    logging.info('Stopping...')


if __name__ == '__main__':
    main()
