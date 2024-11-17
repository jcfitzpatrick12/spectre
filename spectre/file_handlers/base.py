# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from abc import ABC, abstractmethod
from typing import Any, Optional
from warnings import warn

class BaseFileHandler(ABC):
    def __init__(self, 
                 parent_path: str, 
                 base_file_name: str, 
                 extension: Optional[str] = None):
        self._parent_path = parent_path
        self._base_file_name = base_file_name
        self._extension = extension

        
    @abstractmethod
    def read(self) -> Any:
        pass
 

    @property
    def parent_path(self) -> str:
        return self._parent_path
    

    @property
    def base_file_name(self) -> str:
        return self._base_file_name
    

    @property
    def extension(self) -> Optional[str]:
        return self._extension
    

    @property
    def file_name(self) -> str:
        return self._base_file_name if (self._extension is None) else f"{self._base_file_name}.{self._extension}"
    

    @property
    def file_path(self) -> str:
        return os.path.join(self._parent_path, self.file_name)
    
    
    @property
    def exists(self) -> bool:
        return os.path.exists(self.file_path) 


    def make_parent_path(self) -> None:
        os.makedirs(self.parent_path, exist_ok=True) 
    

    def delete(self, 
               doublecheck_delete = True) -> None:
        if not self.exists:
            warn(f"{self.file_path} does not exist. No deletion taking place")
            return
        else:
            if doublecheck_delete:
                self.doublecheck_delete()
            os.remove(self.file_path)
    

    def cat(self) -> None:
        print(self.read())


    def _doublecheck_action(self, 
                            action_message: str) -> None:
        proceed_with_action = False
        while not proceed_with_action:
            user_input = input(f"{action_message} [y/n]: ").strip().lower()
            if user_input == "y":
                proceed_with_action = True
            elif user_input == "n":
                print("Operation cancelled by the user")
                raise exit(1)
            else:
                print(f"Please enter one of [y/n], received {user_input}")
                proceed_with_action = False


    def doublecheck_overwrite(self) -> None:
        self._doublecheck_action(action_message=f"The file '{self.file_path}' already exists. Overwrite?")


    def doublecheck_delete(self) -> None:
        self._doublecheck_action(action_message=f"Are you sure you would like to delete '{self.file_path}'?")