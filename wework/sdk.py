# -*- coding: utf-8 -*-
# created:     2021/7/9 5:00 PM
# filename:    sdk.py
# author:      juntao liu
# email:       jinuljt@gmail.com
# description: 企业微信 会话内容存档sdk https://open.work.weixin.qq.com/api/doc/90000/90135/91360

import json
import base64
import logging
import os
from ctypes import Structure, c_int, c_void_p, CDLL, c_char_p, c_ulonglong, c_ulong, byref, string_at

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random

from wework.exceptions import WeWorkSDKInitException, WeWorkSDKGetChatDataException, WeWorkSDKDecryptException, \
    WeWorkSDKGetMediaDataException

logger = logging.getLogger(__name__)


class Slice(Structure):
    _fields_ = [("buf", c_void_p), ("len", c_int)]


class Media(Structure):
    _fields_ = [("outindexbuf", c_void_p), ("out_len", c_int), ("data", c_void_p),
                ("data_len", c_int), ("is_finish", c_int)]


class WeWorkFinanceSDK:
    dll = None
    sdk = None
    ciphers = None

    def __init__(self, corp_id, corp_secret, private_keys):
        """
        初始化sdk

        :param corp_id: 企业id
        :param corp_secret: 企业回话内容存档密钥
        :param private_keys: 私钥列表，按照版本顺序提供。没有则填None。['version 1 rsa private key data', None, 'version 2']
        """
        self.ciphers = []
        for index, private_key in enumerate(private_keys, 1):
            if not private_key:
                logger.info(f"private key version {index} not found! ignore")
                self.ciphers.append(None)
            else:
                self.ciphers.append(
                    PKCS1_v1_5.new(RSA.importKey(private_key))
                )
        if isinstance(corp_id, str): corp_id = corp_id.encode()
        if isinstance(corp_secret, str): corp_secret = corp_secret.encode()

        self.dll = CDLL(f"{os.path.dirname(os.path.realpath(__file__))}/libWeWorkFinanceSdk_C.so")
        self.dll.NewSdk.restype = c_void_p
        self.sdk = self.dll.NewSdk()
        ret = self.dll.Init(c_void_p(self.sdk), c_char_p(corp_id), c_char_p(corp_secret))
        if ret != 0:
            logger.error(f"wework finance sdk init fail due to ret: {ret}")
            raise WeWorkSDKInitException(ret, "Init fail")

    def get_cipher(self, version):
        if len(self.ciphers) < version:
            return None
        return self.ciphers[version - 1]

    def decrypt_chat_msg(self, publickey_ver, encrypt_random_key, encrypt_chat_msg):
        dsize = SHA.digest_size
        sentinel = Random.new().read(15 + dsize)
        encrypt_random_key = base64.b64decode(encrypt_random_key)

        cipher = self.get_cipher(publickey_ver)
        if not cipher:
            logger.warning(f"public key version {publickey_ver} not loaded, can't decrypt")
            raise WeWorkSDKDecryptException(-1, f"public key version {publickey_ver} not loaded")

        decrypted_key = self.ciphers[publickey_ver - 1].decrypt(encrypt_random_key, sentinel)
        logger.info(f"version:{publickey_ver} encrypt_random_key:{encrypt_random_key} decrypted_key:{decrypted_key}")

        slice = Slice()
        ret = self.dll.DecryptData(c_char_p(decrypted_key), c_char_p(encrypt_chat_msg.encode()),
                              byref(slice))
        if ret != 0:
            logger.error(f"decrypt chat msg fail due to {ret}")
            raise WeWorkSDKDecryptException(ret, "DecryptData fail")

        return json.loads(string_at(slice.buf, slice.len))

    def get_chat_data(self, seq, limit=1000):
        """
        获取聊天记录

        :param seq: 消息顺序号
        :param limit: 一次拉取的消息条数，最大值1000条，超过1000条会返回错误
        :return:
        """
        slice = Slice()
        # 获取聊天记录
        ret = self.dll.GetChatData(
            c_void_p(self.sdk),
            c_ulonglong(seq),
            c_ulong(limit),
            c_char_p(None),
            c_char_p(None),
            c_int(10),
            byref(slice)
        )

        if ret != 0:
            logger.error(f"GetChatData fail due to ret:{ret}")
            raise WeWorkSDKGetChatDataException(ret, "GetChatData fail")

        chats_data = json.loads(string_at(slice.buf, slice.len))
        logger.info(f"get chat data response:{chats_data}")

        for chat in chats_data['chatdata']:
            chat_msg = self.decrypt_chat_msg(chat['publickey_ver'], chat['encrypt_random_key'], chat['encrypt_chat_msg'])
            chat['decrypted_chat_msg'] = chat_msg
        return chats_data['chatdata']

    def get_media_data(self, sdkfileid):
        """
        获取媒体文件数据（二进制）
        :param sdkfileid:
        :return:
        """
        if isinstance(sdkfileid, str): sdkfileid = sdkfileid.encode()

        data = b''
        media = Media()
        while True:
            ret = self.dll.GetMediaData(
                c_void_p(self.sdk),
                c_void_p(media.outindexbuf),
                c_char_p(sdkfileid),
                c_char_p(None),
                c_char_p(None),
                c_int(10),
                byref(media)
            )

            if ret != 0:
                logger.error(f"get media data fail due to {ret}")
                raise WeWorkSDKGetMediaDataException(ret, "GetMediaData fail")

            data += string_at(media.data, media.data_len)

            if media.is_finish:
                break
        return data


if __name__ == "__main__":

    sdk = WeWorkFinanceSDK(
        "CORP_ID",
        "CORP_SECRET",
        [
            open("path/to/v1/key.pem").read(),
            open("path/to/v2/key.pem").read(),
        ]
    )
    sdk.get_chat_data(0)
