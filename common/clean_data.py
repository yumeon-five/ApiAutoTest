"""
测试数据清理

【背景】创建入库单（POST /asn/list/）是写接口，每跑一次自动化就往库里加一条数据，
跑几十次就积一堆：列表查询的 count / results 会被上一次运行的数据干扰，
测试库也越来越乱。这里提供两种清理方式：

1. clean_asn_by_api() —— 走接口删除（DELETE /asn/list/{id}/），
   由 conftest.py 的 clean_history_data 夹具在会话开始前自动执行，保证每次运行都是干净起点。
   两个注意点：
   - WMS 的删除是「软删除」（把 is_delete 置为 True），数据行仍在表里，只是不再出现在列表接口里。
     对自动化来说够用：列表的 count / results 不会再算上历史测试数据。
   - 接口只允许删除 asn_status=1 的主单，其它状态会跳过并记录日志，不会阻断清理。

2. clean_asn_by_db() —— 直连 SQLite 物理删除 asnlist / asndetail / scanner 三张表里的测试数据。
   scanner（条码）表没有删除接口，要真正把测试数据从库里清掉只能走这种方式。
   默认是预览模式（dry-run），只打印将要删除的内容；确认后再加 --yes 真删：
       python common/clean_data.py            # 预览要删什么
       python common/clean_data.py --yes      # 真正执行物理删除

【如何识别测试数据】用例里把 creater 写成 api_auto_${get_run_id()}（见 testcase/asn/asn_create.yaml），
所以按 creater 前缀 api_auto 就能把自动化造的数据和手工数据区分开。
前缀可以在 conf/conf.ini 的 [CLEAN] 段配置。
"""
import os
import sqlite3
import sys

import requests

# 兼容两种运行方式：python common/clean_data.py 和 python -m common.clean_data。
# 直接跑脚本时 sys.path[0] 是 common/ 目录，import 不到 common / conf 包，
# 所以先把项目根目录加进 sys.path（必须放在下面的包导入之前）。
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from common.recordlog import logs
from common.readyaml import ReadYamlData
from conf.operationConfig import OperationConfig
from conf.setting import DIR_PATH

# 测试数据标识前缀，与 testcase/asn/asn_create.yaml 里 creater 的写法保持一致
DEFAULT_CREATER_PREFIX = 'api_auto'


def _is_business_error(resp_json):
    """
    判断响应体是不是业务错误。

    本项目用自定义异常处理（utils/my_exceptions.py）把 DRF 的异常统一包成
    HTTP 200 + {"status_code": 4xx/5xx, ...}，所以不能只看 HTTP 状态码；
    正常返回的业务对象里没有 status_code 这个键（入库单里叫 asn_status）。
    """
    code = resp_json.get('status_code') if isinstance(resp_json, dict) else None
    return code is not None and str(code) != '200'


def _load_host_and_token():
    """从 conf.ini 和 extract.yaml 里取被测系统地址与认证 token"""
    host = OperationConfig().get_envi('host')
    if not host:
        raise RuntimeError('conf/conf.ini 里读不到 [api_envi] host，请先复制 conf.ini.example 并填写')
    try:
        token = ReadYamlData().get_extract_yaml('token')
    except KeyError:
        token = None
    if not token:
        raise RuntimeError('extract.yaml 里没有 token，请先跑一次用例（前置登录夹具会写入 token）')
    return host, token


def clean_asn_by_api(creater_prefix=DEFAULT_CREATER_PREFIX):
    """
    按 creater 前缀，通过接口软删除自动化创建的入库单主单。

    :param creater_prefix: 测试数据标识前缀
    :return: {'found': 匹配条数, 'deleted': 已删除, 'skipped': 跳过, 'details': [明细说明]}
    """
    host, token = _load_host_and_token()
    url = f'{host}/asn/list/'
    headers = {'token': token, 'Accept': 'application/json'}
    summary = {'found': 0, 'deleted': 0, 'skipped': 0, 'details': []}

    # 先按 creater 模糊查询（接口的 creater 支持 icontains 过滤），
    # 再在本地用 startswith 复核一遍：模糊查询可能命中「中间包含该前缀」的数据，不能直接删
    res = requests.get(url,
                       params={'creater__icontains': creater_prefix, 'page': 1,
                               'max_page': 1000, 'format': 'json'},
                       headers=headers, timeout=10)
    body = res.json()
    if _is_business_error(body):
        raise RuntimeError(f'查询待清理数据失败：{body}')

    targets = [item for item in (body.get('results') or [])
               if str(item.get('creater', '')).startswith(creater_prefix)]
    summary['found'] = len(targets)

    for item in targets:
        asn_id = item.get('id')
        asn_code = item.get('asn_code')
        # 接口只允许删除状态为 1 的主单，其它状态（已到货/已上架等）跳过，不阻断清理
        if item.get('asn_status') != 1:
            summary['skipped'] += 1
            summary['details'].append(
                f'跳过 {asn_code}(id={asn_id})：asn_status={item.get("asn_status")}，'
                f'接口只允许删除状态为 1 的主单')
            continue

        del_res = requests.delete(f'{url}{asn_id}/', headers=headers, timeout=10)
        try:
            del_body = del_res.json()
        except ValueError:
            del_body = {'detail': f'响应不是 JSON：{del_res.text[:200]}'}

        if _is_business_error(del_body):
            summary['skipped'] += 1
            summary['details'].append(f'删除失败 {asn_code}(id={asn_id})：{del_body}')
        else:
            summary['deleted'] += 1
            summary['details'].append(f'已删除 {asn_code}(id={asn_id})')

    return summary


def clean_asn_by_db(creater_prefix=DEFAULT_CREATER_PREFIX, sqlite_path=None, dry_run=True):
    """
    直连 SQLite 物理删除测试数据：asnlist（主单）+ asndetail（明细）+ scanner（条码）。

    说明：这是绕过接口直接改库，只适合本地/测试环境，生产库不要用。
    :param creater_prefix: 测试数据标识前缀，按 asnlist.creater 前缀匹配
    :param sqlite_path: SQLite 文件路径，缺省取 conf.ini 的 [DB] sqlite_path
    :param dry_run: True 只预览不删除（默认）
    :return: {'asn': 主单数, 'detail': 明细数, 'scanner': 条码数}
    """
    path = sqlite_path or OperationConfig().get_db_conf('sqlite_path') \
        or os.path.join(DIR_PATH, '..', 'GreaterWMS', 'db.sqlite3')
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f'找不到 SQLite 文件：{path}（可在 conf.ini 的 [DB] sqlite_path 里配置）')

    con = sqlite3.connect(path)
    try:
        codes = [row[0] for row in
                 con.execute('select asn_code from asnlist where creater like ?', (f'{creater_prefix}%',))]
        detail_cnt = scanner_cnt = 0
        if codes:
            marks = ','.join('?' * len(codes))
            detail_cnt = con.execute(
                f'select count(*) from asndetail where asn_code in ({marks})', codes).fetchone()[0]
            scanner_cnt = con.execute(
                f"select count(*) from scanner where mode='ASN' and code in ({marks})", codes).fetchone()[0]

        print(f'数据库文件：{path}')
        print(f'匹配 creater like "{creater_prefix}%" 的入库单主单：{len(codes)} 条')
        if codes:
            print(f'  单号：{codes}')
        print(f'  级联数据：商品明细 {detail_cnt} 条，scanner 条码 {scanner_cnt} 条')

        if dry_run:
            print('\n【预览模式】没有删除任何数据。确认无误后执行：python common/clean_data.py --yes')
        elif not codes:
            print('\n没有匹配的数据，无需删除。')
        else:
            marks = ','.join('?' * len(codes))
            con.execute(f'delete from asndetail where asn_code in ({marks})', codes)
            con.execute(f"delete from scanner where mode='ASN' and code in ({marks})", codes)
            con.execute('delete from asnlist where creater like ?', (f'{creater_prefix}%',))
            con.commit()
            print(f'\n已物理删除：入库单 {len(codes)} 条、商品明细 {detail_cnt} 条、scanner 条码 {scanner_cnt} 条')

        return {'asn': len(codes), 'detail': detail_cnt, 'scanner': scanner_cnt}
    finally:
        con.close()


if __name__ == '__main__':
    # 手动物理清理入口：先预览，确认后加 --yes 真删
    result = clean_asn_by_db(dry_run='--yes' not in sys.argv)
    logs.info(f'物理清理结果：{result}')
