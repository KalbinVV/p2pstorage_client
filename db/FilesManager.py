from p2pstorage_core.server.FileInfo import FileInfo

from db.SqliteSingletonManager import SqliteSingletonManager


class FilesManager:
    def __init__(self):
        self.__sqlite_manager = SqliteSingletonManager.instance()

    def init_table(self) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/create_files_table.sql')

    def add_file(self, file_name: str, file_path: str, file_size: int, file_hash: str) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/add_file.sql',
                                           (file_name, file_path, file_size, file_hash))

    def is_contains_file(self, file_name: str) -> bool:
        return (self.__sqlite_manager.execute_file('./db/sqls/contains_file_by_name.sql',
                                                   (file_name, )).fetchone() == (1,))

    def get_file_path_by_name(self, file_name: str) -> str:
        file_path = self.__sqlite_manager.execute_file('./db/sqls/get_file_path_by_name.sql',
                                                       (file_name, )).fetchone()[0]

        return file_path

    def get_files_info(self) -> list[FileInfo]:
        files_info = []

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_files.sql'):
            # Todo: Change to NamedTuple
            file_name, _, file_size, file_hash = row

            files_info.append(FileInfo(file_name, file_size, file_hash))

        return files_info
