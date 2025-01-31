#!/usr/bin/expect
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

spawn ./SDRplay_RSP_API-Linux-3.15.2.run

expect {
    -re "lsusb\\?" {
        send "y\r"
        exp_continue
    }
    -re {Press y and RETURN} {
        send "y\r"
        exp_continue
    }
    -re {Press RETURN to view the license agreement} {
        send "\r"
        exp_continue
    }
    -re {'q' to quit} {
        send "q\r"
        exp_continue
    }
    -re {\[y/n\]} {
        send "y\r"
        exp_continue
    }
    eof
}
