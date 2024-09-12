# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from abc import ABC, abstractmethod
from typing import Any

class BaseFileHandler(ABC):
    def __init__(self, 
                 parent_path: str, 
                 base_file_name: str, 
                 extension: str = None,
                 override_extension: str = None,
                 read_on_instantiation: bool = False):
        self.parent_path = parent_path
        self.file_name = base_file_name
        self.extension = extension if (override_extension is None) else override_extension
        self.file_name = base_file_name if (self.extension is None) else f"{base_file_name}.{extension}"
        self.file_path = os.path.join(self.parent_path, self.file_name)

        self.data: Any = None
        if read_on_instantiation:
            self.data = self.read()
        
        

    @abstractmethod
    def read(self) -> Any:
        pass
    

    def make_parent_path(self) -> None:
        os.makedirs(self.parent_path, exist_ok=True)
        return    


    def exists(self) -> bool:
        return os.path.exists(self.file_path) 


    def delete(self, doublecheck_delete = True) -> None:
        if not self.exists():
            return
        else:
            if doublecheck_delete:
                self.doublecheck_delete()
            os.remove(self.file_path)
        return
    

    def cat(self) -> None:
        print(self.read())
        return


    def _doublecheck_action(self, action_message: str) -> None:
        proceed_with_action = False
        while not proceed_with_action:
            user_input = input(f"{action_message} [y/n]: ").strip().lower()
            if user_input == "y":
                proceed_with_action = True
            elif user_input == "n":
                print("Operation cancelled by the user.")
                raise exit(1)
            else:
                print(f"Please enter one of [y/n], received {user_input}.")
                proceed_with_action = False


    def doublecheck_overwrite(self) -> None:
        self._doublecheck_action(action_message=f"The file '{self.file_path}' already exists. Overwrite?")


    def doublecheck_delete(self) -> None:
        self._doublecheck_action(action_message=f"Are you sure you would like to delete '{self.file_path}'?")