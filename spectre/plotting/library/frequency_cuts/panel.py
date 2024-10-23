# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

# ChildPanel (spectrogram, line plots etc) (MAY INCLUDE COLORBAR!)
# -> implement each panel as a child class
#    -> write a class for each of our panel types
#    -> effectively implements the populate subplot method 
#    -> use a decorator to add it to a global dictionary for panel types (as per usual!)
#    -> when we call add panel (see below) it fetches the appropriate child panel
