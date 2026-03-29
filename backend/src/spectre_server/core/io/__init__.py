# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""Basic file io for common file formats."""

from ._files import Base, FileFormat, read_file

__all__ = ["Base", "FileFormat", "read_file"]
