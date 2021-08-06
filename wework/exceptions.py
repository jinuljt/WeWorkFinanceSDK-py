# -*- coding: utf-8 -*-
# created:     2021/7/9 5:33 PM
# filename:    exceptions.py
# author:      juntao liu
# email:       jinuljt@gmail.com
# description:


class WeWorkException(Exception):
    code = 0
    message = ""

    def __init__(self, code, message):
        self.code = code
        self.message = message


class WeWorkSDKInitException(WeWorkException):
    pass


class WeWorkSDKGetChatDataException(WeWorkException):
    pass


class WeWorkSDKDecryptException(WeWorkException):
    pass


class WeWorkSDKGetMediaDataException(WeWorkException):
    pass