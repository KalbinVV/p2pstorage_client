import logging

from CommandsHandlers import init_commands, handle_command
from StorageClient import StorageClient


def main():
    logging.basicConfig(level=logging.DEBUG, filename='logs.log')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    storage_client = StorageClient()

    init_commands()

    logging.info('Client is started, please enter command!')

    user_input_handler(storage_client)


def user_input_handler(storage_client: StorageClient) -> None:
    running = True

    while running:
        user_input = input()

        command_parts = user_input.split()

        command_name = command_parts[0]
        args = command_parts[1:]

        handle_command(storage_client, command_name, args)

        if command_name == 'q':
            running = False


if __name__ == '__main__':
    main()
