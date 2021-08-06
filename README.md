# WeWorkFinanceSDK-py

对企业微信[获取会话内容](https://open.work.weixin.qq.com/api/doc/90000/90135/91774) C 语言 SDK 的 python 封装。

## 使用方式

```
# 初始化
sdk = WeWorkFinanceSDK(corp_id, secret, [open('private.key').read()])

# 获得聊天记录
sdk.get_chat_data(sequence_id)

# 获取媒体文件
sdk.get_media_data(sdkfileid)

```


## 关于 ctypes

### 为什么在 Slice 中 `buf` 与 Media 中 `data` 定义为 `c_void_p`

的确 ctypes 会将定义为 `c_char_p` 数据转换成 string 。但数据是一个二进制文件时，会导致文件内容被截断， ctypes文档明确说明 `c_char_p` 会被 `NUL terminated`。所以使用 `c_void_p`，然后使用 `string_at(buf, len)`。


## 参考文档

[Python ctypes](https://docs.python.org/3.9/library/ctypes.html)


## 依赖

[PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/)

