import logging

from CommandsHandlers import init_commands, handle_command, InvalidArgsCommandException, InvalidCommandException
from StorageClient import StorageClient


def init_logger() -> None:
    logging.basicConfig(level=logging.DEBUG, filename='logs.log')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()

    console.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] > %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def main():
    init_logger()

    storage_client = StorageClient()

    init_commands()

    logging.info('Client is started, please enter command!')

    user_input_handler(storage_client)


def user_input_handler(storage_client: StorageClient) -> None:
    running = True

    while running:
        try:
            user_input = input()

            command_parts = user_input.split()

            command_name = command_parts[0]
            args = command_parts[1:]

            try:
                handle_command(storage_client, command_name, args)
            except (InvalidArgsCommandException, InvalidCommandException) as e:
                logging.error(e)

            if command_name == 'q':
                running = False
        except KeyboardInterrupt:
            running = False

            storage_client.set_connection_active(False)
            storage_client.get_socket().close()


if __name__ == '__main__':
    main()
import logging

from CommandsHandlers import init_commands, handle_command, InvalidArgsCommandException, InvalidCommandException
from StorageClient import StorageClient


def init_logger() -> None:
    logging.basicConfig(level=logging.DEBUG, filename='logs.log')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()

    console.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] > %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def main():
    init_logger()

    storage_client = StorageClient()

    init_commands()

    logging.info('Client is started, please enter command!')

    user_input_handler(storage_client)


def user_input_handler(storage_client: StorageClient) -> None:
    running = True

    while running:
        try:
            user_input = input()

            command_parts = user_input.split()

            command_name = command_parts[0]
            args = command_parts[1:]

            try:
                handle_command(storage_client, command_name, args)
            except (InvalidArgsCommandException, InvalidCommandException) as e:
                logging.error(e)

            if command_name == 'q':
                running = False
        except KeyboardInterrupt:
            running = False

            if storage_client.is_connection_active():
                storage_client.set_connection_active(False)
                storage_client.get_socket().close()


if __name__ == '__main__':
    main()
