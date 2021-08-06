# WeWorkFinanceSDK-py

对企业微信[获取会话内容](https://open.work.weixin.qq.com/api/doc/90000/90135/91774) C 语言SDK的 python 封装。

## 使用方式

```
# 初始化
sdk = WeWorkFinanceSDK(corp_id, secret, [open('private.key').read()])

# 获得聊天记录
sdk.get_chat_data(sequence_id)

# 获取媒体文件
sdk.get_media_data(sdkfileid)

```


## 参考文档

[Python ctypes](https://docs.python.org/3.9/library/ctypes.html)


## 依赖

[PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/)

