# SPDX-FileCopyrightText: © 2024-2026 Jimmy Fitzpatrick <jimmy@spectregrams.org>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

"""The recording supervisor process.

Runs in its own OS process (spawned by the backend via ``subprocess.Popen``)
and is responsible for the lifecycle of a single recording row:

- Load the recording from the DB.
- Build the appropriate flowgraph (and post-processing) workers.
- Update the row through ``running`` to the correct terminal state.
- React to a stop request (SIGTERM from the backend) by asking the job to
  wind down gracefully.

Never invoked in-process from a backend worker: always spawned as a separate
process so that the backend can send it SIGTERM cleanly.
"""
