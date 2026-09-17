from common.recordlog import logs
from conf.operationConfig import OperationConfig
import pymysql
import redis
from rediscluster import RedisCluster
config = OperationConfig()

class ConnectMysql(object):
    """连接读取Mysql数据库中的数据"""
    def __init__(self):

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
            logs.error(e)

    def close(self):
        """关闭数据连接字段"""
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()

    def query(self,sql,query_type='all'):
        """
        查询数据库
        :param sql: 数据库查询语句
        :param query_type: 查询类型 所有all  不为all则查询单条数据
        :return:
        """
        try:
            self.cursor.execute(sql)
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






