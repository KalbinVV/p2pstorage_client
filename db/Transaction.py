class TransactionsManager:
    def __init__(self):
        # File names
        self.__active_transactions: set[str] = set()

    def is_transaction_already_created(self, file_name: str) -> bool:
        return file_name in self.__active_transactions

    def add_transaction(self, file_name: str) -> None:
        self.__active_transactions.add(file_name)

    def remove_transaction(self, file_name: str) -> None:
        self.__active_transactions.remove(file_name)
