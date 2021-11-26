import os
import mariadb

from utils.validation import directory_assertion
from utils.route import find_directory_path, normalize_path


def wait_for_mariadb(address:str, port:int, db_name:str, user:str, password:str) -> None:
    waiting = True
    while waiting:
        try:
            connection = mariadb.connect(host = address, user = user, password = password, database = db_name)
            connection.ping()
            waiting = False
            print("The database is up -- proceding")
        except mariadb.Error as e:
            print (e)


def build_mariadb_endpoint(address:str, port:int, db_name:str, user:str, password:str) -> str:
    route = f"{user}:{password}@{address}:{port}/{db_name}"
    return f"mariadb+mariadbconnector://{route}"


def build_sqlite_local_endpoint(root:str, db_folder:str, db_name:str, db_suffix:str) -> str:
    route = __build_database_local_route(root, db_folder, db_name, db_suffix)
    return f"sqlite:///{route}"


def build_sqlite_memory_endpoint() -> str:
    return "sqlite:///:memory:"


def __build_database_local_route(root:str, db_folder:str, db_name:str, db_suffix:str) -> str:
    directory_path = find_directory_path(root, db_folder)
    directory_assertion(directory_path)
    return normalize_path(os.path.abspath(f"{directory_path}/{db_name}.{db_suffix}"))
