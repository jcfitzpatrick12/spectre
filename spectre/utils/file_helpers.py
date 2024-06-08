# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

import os

def cat(absolute_path: str):
    try:
        # Open the file and read its contents
        with open(absolute_path, 'r') as file:
            contents = file.read()
        # Print the contents
        print(contents)
    except FileNotFoundError:
        print(f"Error: The file at '{absolute_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied when attempting to read '{absolute_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def doublecheck_delete(fpath: str) -> None:
    proceed_with_delete = False
    while not proceed_with_delete:
        user_input = input(f"Are you sure you would like to delete '{fpath}'? [y/n]: ").strip().lower()
        if user_input == "y":
            proceed_with_delete = True
        elif user_input == "n":
            print("Operation cancelled by the user.")
            raise exit(1)
        else:
            print(f"Please enter one of [y/n], received {user_input}.")
            proceed_with_delete = False


def doublecheck_overwrite_at_path(fpath: str) -> None:
    proceed_with_overwrite = False
    while not proceed_with_overwrite:
        user_input = input(f"The file '{fpath}' already exists. Overwrite? [y/n]: ").strip().lower()
        if user_input == "y":
            proceed_with_overwrite = True
        elif user_input == "n":
            print("Operation cancelled by the user.")
            raise exit(1)
        else:
            print(f"Please enter one of [y/n], received {user_input}.")
            proceed_with_overwrite = False