# ------------------------------------------------------------
# 文件作用：飞书机器人通知模块，用于推送测试执行结果。
# 核心操作：
#   1) generate_sign：以 "timestamp\n密钥" 作为 HmacSHA256 的 key、空串作为 msg，
#      计算签名后做 Base64 编码，得到飞书要求的 sign（时间戳单位为「秒」，不做 urlEncode）；
#   2) send_fs_msg：向飞书自定义机器人 Webhook POST JSON，msg_type=text，
#      timestamp / sign 放在 body 中，@全员通过 <at user_id="all"> 标签实现。
# ------------------------------------------------------------
import requests
import time
import hmac
import hashlib
import base64



def generate_sign():
    """
    签名计算
    把 timestamp + "\n" + 密钥 作为签名字符串（HmacSHA256 的 key），对空字符串进行签名，
    然后进行 Base64 encode，得到最终的签名（需要使用 UTF-8 字符集）。
    注意：飞书的时间戳单位是「秒」，且签名不需要 urlEncode。
    :return: 返回当前时间戳、加密后的签名
    """
    # 当前时间戳（秒）
    timestamp = str(int(time.time()))
    # 飞书机器人中的加签密钥（若未开启"签名校验"可留空字符串）
    secret = '123'
    str_to_sign = '{}\n{}'.format(timestamp, secret)
    # 以 str_to_sign 作为 key，对空串做 HmacSHA256
    hmac_code = hmac.new(str_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return timestamp, sign


def send_fs_msg(content_str, at_all=True):
    """
    向飞书机器人推送结果
    :param content_str: 发送的内容
    :param at_all: @全员，默认为True（通过在文本中插入 <at user_id="all"> 标签实现）
    :return:
    """

    timestamp_and_sign = generate_sign()
    # url(飞书机器人Webhook地址)
    url = 'https://open.feishu.cn/open-apis/bot/v2/hook/5e631fa5-4dcd-4ff6-98c5-ae7a80b4b63d'
    # @全员：飞书通过富文本标签实现，把标签拼在正文里即可
    text = f'<at user_id="all">所有人</at>\n{content_str}' if at_all else content_str
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "timestamp": timestamp_and_sign[0],
        "sign": timestamp_and_sign[1],
        "msg_type": "text",
        "content": {
            "text": text
        },
    }
    res = requests.post(url, json=data, headers=headers)
    return res.text