from common.recordlog import logs
from conf.operationConfig import OperationConfig
import pymysql
config = OperationConfig()

class ConnectMysql(object):
    """连接读取Mysql数据库中的数据"""
    def __init__(self):
        mysql_conf={
            'host':config.get_mysql_conf('host'),
            'port':int(config.get_mysql_conf('port')),
            'user':config.get_mysql_conf('username'),
            'password':config.get_mysql_conf('password'),
            'database':config.get_mysql_conf('database')
        }
        try:
            self.conn=pymysql.connect(**mysql_conf,charset='utf8mb4')
            #cursor=pymysql.cursors.DictCursor 字典类型显示
            #创建游标对象:根据已经建立的数据库连接，创建一个“游标对象”，后续通过它执行 SQL 和获取查询结果。
            self.cursor=self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""成功连接到MYSQL数据库
                      host:{host}
                      port:{port}
                      db:{database}""".format(**mysql_conf))
        except Exception as e:
            logs.error(e)

    def close(self):
        """关闭数据连接字段"""
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()

    def query(self,sql):
        """查询数据"""
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            res=self.cursor.fetchall()
            return res
        except Exception as e:
            logs.error(e)
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

if __name__ == '__main__':
    conn=ConnectMysql()

