from common.recordlog import logs
from conf.OperationConfig import OperationConfig
import pymysql
from pymysql import cursors

conf = OperationConfig()

# class ConnectMysql:
#     '''连接读取mysql数据库的数据'''
#
#     def __init__(self):
#         mysql_conf = {
#             'host': conf.get_mysql('host'),
#             'port': int(conf.get_mysql('port')),
#             'user': conf.get_mysql('username'),
#             'password': conf.get_mysql('password'),
#             'database': conf.get_mysql('database')
#         }
#         try:
#             self.conn = pymysql.connect(**mysql_conf, charset='utf8')
#             print(self.conn)
#             self.cursor = self.conn.cursor()
#             # logs.info('''成功连接数据库:\nhost:{},port:{},user:{},password:{},database{}'''.format(**mysql_conf))
#         except Exception as e:
#             logs.error(e)
#
#     def close(self):
#         if self.conn and self.cursor:
#             self.cursor.close()
#             self.conn.close()
#
#     def query(self, sql):
#         '''查询数据'''
#         try:
#             self.cursor.execute(sql)
#             self.conn.commit()
#             res = self.cursor.fetchall()
#             return res
#         except Exception as e:
#             logs.error(e)
#         finally:
#             self.close()
#
#     def insert(self, sql):
#         pass
#
#     def update(self, sql):
#         pass
#
#     def delete(self, sql):
#         pass

class ConnectMysql():
    def __init__(self):
        self.conn_dict = {
            'host':conf.get_mysql('host'),
            'port':int(conf.get_mysql('port')),
            'user':conf.get_mysql('username'),
            'password':conf.get_mysql('password'),
            'db':conf.get_mysql('database')
        }
        try:
            self.conn = pymysql.connect(**self.conn_dict)
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        except Exception as e:
            logs.error(e)

    def query(self,sql):
        try:
            if self.conn and self.cur:
                self.cur.execute(sql)
                self.conn.commit()
                res = self.cur.fetchall()

            return res
        except Exception as e:
            logs.error(e)
        finally:
            self.close()


    def close(self):
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()

if __name__ == '__main__':
    conn = ConnectMysql()
    search = conn.query('select * from products')
    print(search)
