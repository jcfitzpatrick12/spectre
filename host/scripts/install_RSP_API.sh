#!/usr/bin/expect
# SPDX-FileCopyrightText: © 2024 Jimmy Fitzpatrick <jcfitzpatrick12@gmail.com>
# This file is part of SPECTRE
# SPDX-License-Identifier: GPL-3.0-or-later

exp_internal 1

exec chmod +x ./SDRplay_RSP_API-Linux-3.14.0.run
spawn ./SDRplay_RSP_API-Linux-3.14.0.run

expect {
	-regex "identification in applications such as lsusb?" {
		send "y\r"
	}
	-regex "Press RETURN to view the license agreement" {
		send "\r"
		exp_continue
	}
	-regex "Press space to continue" {
		send "\r"
		exp_continue
	}
	-regex "Press y and RETURN" {
		send "y\r"
	}
    	-regex "\[y/n\]" {
    		send "y\r"
    		exp_continue
    	}
}

expect eof

