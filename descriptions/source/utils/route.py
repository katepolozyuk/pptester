import os
from typing import List, Optional


def normalize_path(path:str) -> str:
    return universalize_path(os.path.abspath(path))


def universalize_path(path:str) -> str:
    return path.replace("\\", "/")


def find_working_directory() -> str:
    return os.getcwd()


def find_directory_path(roots:List[str], target_dir:str) -> Optional[str]:
    for root in roots:
        universal_path = universalize_path(root)
        for path, dirs, _ in os.walk(universal_path):
            if target_dir in dirs:
                return os.path.abspath(os.path.join(path, target_dir))

    return None
