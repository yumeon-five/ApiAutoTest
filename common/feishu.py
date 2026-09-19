# ------------------------------------------------------------
# 文件作用：飞书机器人通知模块，用于推送测试执行结果。
# 核心操作：
#   1) generate_sign：以 "timestamp\n密钥" 作为 HmacSHA256 的 key、空串作为 msg，
#      计算签名后做 Base64 编码（飞书要求时间戳单位为「秒」，且签名不做 urlEncode）；
#   2) send_fs_msg：向自定义机器人 Webhook POST JSON，msg_type=text，
#      @全员用 <at user_id="all"> 标签实现。
# Webhook 与密钥从 conf/conf.ini 的 [FEISHU] 段读取，不再写死在代码里。
# ------------------------------------------------------------
import base64
import hashlib
import hmac
import time

import requests

from common.recordlog import logs
from conf.operationConfig import OperationConfig


def generate_sign(secret):
    """
    飞书自定义机器人签名。

    官方算法：以 "{timestamp}\n{secret}" 作为 HMAC-SHA256 的 key，对空串做签名，再 Base64。
    :param secret: 机器人的签名校验密钥（没开签名校验时传空字符串）
    :return: (时间戳, 签名)
    """
    timestamp = str(int(time.time()))
    str_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(str_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return timestamp, base64.b64encode(hmac_code).decode('utf-8')


def send_fs_msg(content_str, at_all=True):
    """
    向飞书群机器人推送文本消息。
    :param content_str: 消息正文
    :param at_all: 是否 @所有人
    :return: 飞书返回的响应体（dict）；没配 webhook 时返回 None
    """
    conf = OperationConfig()
    url = conf.get_feishu_conf('webhook')
    secret = conf.get_feishu_conf('secret') or ''
    keyword = (conf.get_feishu_conf('keyword') or '').strip()

    if not url:
        logs.warning('conf.ini 里没有配置 [FEISHU] webhook，跳过飞书通知')
        return None

    timestamp, sign = generate_sign(secret)
    text = f'<at user_id="all">所有人</at>\n{content_str}' if at_all else content_str

    # 机器人如果开了「自定义关键词」安全设置，消息文本里必须包含设置的关键词之一，
    # 否则飞书返回 19024 Key Words Not Found。关键词填在 conf.ini 的 [FEISHU] keyword，
    # 这里自动拼到消息最前面（飞书是对整个 content.text 做包含判断，放哪都行，放前面最直观）
    if keyword:
        text = f'{keyword}\n{text}'
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {"text": text},
    }

    res = requests.post(url, json=data,
                        headers={'Content-Type': 'application/json;charset=utf-8'},
                        timeout=10)

    # 飞书是「HTTP 200 + 响应体里带错误码」，所以必须看响应体，只看状态码会漏掉失败
    try:
        body = res.json()
    except ValueError:
        logs.error(f'飞书通知返回的不是 JSON：{res.text[:200]}')
        return None

    # 自定义机器人失败时会返回错误码，例如 19021 签名不对、19024 关键词不匹配
    if body.get('code') == 0 or body.get('StatusCode') == 0:
        logs.info(f'飞书通知发送成功：{body}')
    else:
        logs.error(f'飞书通知发送失败（错误码 {body.get("code") or body.get("StatusCode")}）：{body}')
    return body