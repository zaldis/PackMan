from typing import Protocol, Generic, TypeVar


T = TypeVar('T')


class Repo(Protocol, Generic[T]):
    def get_records(self) -> list[T]:
        ...

    def add_record(self, new_record: T) -> None:
        ...
