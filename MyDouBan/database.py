import pymysql

MYSQL_DB = 'db_douban' #数据库名称
MYSQL_USER = 'root' #用户名
MYSQL_PASS = '123456' #密码
MYSQL_HOST = 'localhost' #本地数据库

connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                             password=MYSQL_PASS, db=MYSQL_DB,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)