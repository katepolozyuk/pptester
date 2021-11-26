import os
import sys


def assertion(condition:bool, message:str) -> None:
    if not condition:
        print(message)
        sys.exit(1)


def file_assertion(path:str) -> None:
    assertion(os.path.exists(path), f'Path [{path}] is invalid')
    assertion(os.path.isfile(path), f'Path [{path}] is not a file')


def directory_assertion(path:str) -> None:
    assertion(os.path.exists(path), f'Path [{path}] is invalid')
    assertion(os.path.isdir(path), f'Path [{path}] is not a directory')