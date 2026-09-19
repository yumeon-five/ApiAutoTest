import os
import sqlite3

from common.recordlog import logs
from conf.operationConfig import OperationConfig
from conf.setting import DIR_PATH
import pymysql
import redis
from rediscluster import RedisCluster
config = OperationConfig()

class ConnectMysql(object):
    """连接读取Mysql数据库中的数据"""
    def __init__(self):

        # 先置空：连接失败时也要保证属性存在，
        # 否则后面 query() 的 finally 里调 close() 会抛
        # AttributeError: 'ConnectMysql' object has no attribute 'conn'，
        # 把「连不上库」这种清楚的错误盖成看不懂的报错
        self.conn = None
        self.cursor = None

        self.__mysql_conf={
            'host':config.get_mysql_conf('host'),
            'port':int(config.get_mysql_conf('port')),
            'user':config.get_mysql_conf('username'),
            'password':config.get_mysql_conf('password'),
            'database':config.get_mysql_conf('database')
        }
        try:
            self.conn = pymysql.connect(**self.__mysql_conf, charset='utf8mb4')
            # cursor=pymysql.cursors.DictCursor 字典类型显示
            # 创建游标对象:根据已经建立的数据库连接，创建一个“游标对象”，后续通过它执行 SQL 和获取查询结果。
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""成功连接到MYSQL数据库
                      host:{host}
                      port:{port}
                      db:{database}""".format(**self.__mysql_conf))
        except Exception as e:
            logs.error(f'连接 MySQL 失败：{e}')

    def close(self):
        """关闭数据连接字段"""
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()

    def query(self,sql,params=None,query_type='all'):
        """
        查询数据库
        :param sql: 数据库查询语句
        :param params: SQL 参数（配合 %s 占位符使用），避免字符串拼 SQL 带来的注入和转义问题
        :param query_type: 查询类型 所有all  不为all则查询单条数据
        :return:
        """
        try:
            # 参数化执行：pymysql 的占位符是 %s
            self.cursor.execute(sql, params) if params else self.cursor.execute(sql)
            if query_type == 'all':
                data=self.cursor.fetchall()
            else:
                data=self.cursor.fetchone()
            return data
        except AttributeError as e:
            logs.error(f'数据库查询失败,失败原因:{e}')
        finally:
            self.close()

    def delete(self, sql):
        """删除数据"""
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            logs.info('删除成功')
        except Exception as e:
            logs.error(e)
        finally:
            self.close()

    def execute(self, sql):
        """
        MYSQL数据库增删改的操作
        :param sql:数据库增删改的语句
        :return:
        """
        try:
            rows=self.cursor.execute(sql)
            #提交事物
            self.conn.commit()
            return rows
        except AttributeError as e:
            logs.error(f'数据库操作失败,失败原因:{e}')
            #如果事物异常，则回滚数据
            self.conn.rollback()
            raise

class ConnectSqlite(object):
    """
    连接 SQLite 数据库，供「数据库断言」使用（GreaterWMS 默认用 SQLite：GreaterWMS/db.sqlite3）。

    为什么用它：断言要拿库里的真实数据和接口返回值做交叉验证，
    比如「创建成功 → asnlist 表里确实有这条记录」「创建失败 → 库里不新增记录」，
    这类判定纯接口断言做不到。

    两个设计点：
    1) 以只读方式打开（uri 的 mode=ro）：断言通道不应该具备写库能力，
       避免测试代码写错 SQL 把数据改了。确实需要写库时，把 _connect 里的 uri 去掉 mode=ro 即可。
    2) row_factory 设为 sqlite3.Row：查询结果按字段名取值，
       返回 [{字段名: 值}, ...]，和 MySQL 那边的 DictCursor 保持一致，断言代码不用区分库类型。
    """
    def __init__(self):
        self.conn = None
        self.cursor = None
        path = OperationConfig().get_db_conf('sqlite_path') or '../GreaterWMS/db.sqlite3'
        # 配置里的路径是相对 auto-test 项目根目录的，这里转成绝对路径，避免受启动目录影响
        if not os.path.isabs(path):
            path = os.path.join(DIR_PATH, path)
        self.path = os.path.abspath(path)

        if not os.path.exists(self.path):
            logs.error(f'SQLite 文件不存在：{self.path}（可在 conf.ini 的 [DB] sqlite_path 里配置）')
            return
        try:
            # mode=ro 只读打开
            self.conn = sqlite3.connect(f'file:{self.path}?mode=ro', uri=True)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logs.info(f'成功连接到 SQLite 数据库：{self.path}')
        except Exception as e:
            logs.error(f'连接 SQLite 失败：{e}')

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def query(self, sql, params=None, query_type='all'):
        """
        查询数据库，返回 [{字段名: 值}, ...]（q=单条时返回 dict）
        :param sql: 查询语句，占位符用 ?
        :param params: SQL 参数，配合 ? 占位符使用，避免字符串拼 SQL
        """
        if self.cursor is None:
            logs.error('SQLite 未连接成功，无法执行查询')
            return None
        try:
            self.cursor.execute(sql, params) if params else self.cursor.execute(sql)
            if query_type == 'all':
                return [dict(row) for row in self.cursor.fetchall()]
            row = self.cursor.fetchone()
            return dict(row) if row is not None else None
        except Exception as e:
            logs.error(f'SQLite 查询失败：{e}（SQL: {sql}）')
            return None
        finally:
            self.close()


def get_db_client():
    """
    按 conf.ini 的 [DB] type 返回数据库连接对象，让「数据库断言」不绑死在某一种库上：
        type = sqlite  -> ConnectSqlite（GreaterWMS 当前用这个）
        type = mysql   -> ConnectMysql
    两种连接对象的 query(sql, params) 返回值结构一致（list[dict]），断言逻辑不用改。
    """
    db_type = (OperationConfig().get_db_conf('type') or 'sqlite').strip().lower()
    if db_type == 'mysql':
        return ConnectMysql()
    if db_type == 'sqlite':
        return ConnectSqlite()
    raise ValueError(f'conf.ini 的 [DB] type 只支持 sqlite / mysql，当前是：{db_type}')

class RedisClient:
    """从redis中读取、设置相关数据"""
    def __init__(self):
        self.__redis_conf={
            'host': config.get_redis_conf('host'),
            'port': int(config.get_redis_conf('port')),
            'username': config.get_redis_conf('username'),
            'password': config.get_redis_conf('password'),
            'db': config.get_redis_conf('db')
        }

        redis_node_str=config.get_redis_conf('startup_nodes')
        self.node_list=[]
        #startup_nodes:集群的格式[{'host':'host','port':'port'},{'host2':'host','port':'port'},{'host3':'host','port':'port'}]
        if redis_node_str:
            nodes_str_list=redis_node_str.split(',')
            for nodes_str in nodes_str_list:
                host,port=nodes_str.split(':')
                node_data={'host':host,'port':port}
                self.node_list.append(node_data)
            self.redis_cluster = RedisCluster(startup_nodes=self.node_list)
            logs.info(f'连接到redis集群服务,host:{redis_node_str}')
        elif self.__redis_conf['host'] and self.__redis_conf['port']:
            try:
                logs.info(f'连接到Redis服务器： ip:{self.__redis_conf["host"]}')
                pool=redis.ConnectionPool(**self.__redis_conf)
                self.redis_cluster=redis.Redis(connection_pool=pool)
            except Exception as e:
                logs.error(f'redis连接失败,{e}')


    @classmethod
    def redis_except(cls,e):
        """
        获取异常
        :param e:
        :return:
        """
        if "MOVED" in str(e):
            logs.error(f'请检查Redis是否使用了集群模式或者主从复制的情况，数据被迁移到了另一个Redis实例上：{e}')
        else:
            logs.error(f'Redis Error:{e}')

    def get(self,key):
        """
        获取redis里面的数据
        :param key:Redis里面的键
        :return:
        """
        try:
            value=self.redis_cluster.get(key)
            return value
        except Exception as e:
            self.redis_except(e)
            raise






