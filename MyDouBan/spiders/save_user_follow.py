
import os
import MyDouBan.database as db
from MyDouBan.items import UserFollow

#获得连接数据库的游标
cursor = db.connection.cursor()

#从数据库中获得所有用户
def get_users():
    sql = 'SELECT douban_id from users'
    cursor.execute(sql)
    users = cursor.fetchall()
    return users

#根据用户主页地址从数据库中获得某个用户id
def get_user_from_url(user_url):
    sql = 'SELECT id from users WHERE douban_user_url=\'%s\'' % user_url
    cursor.execute(sql)
    user = cursor.fetchone()
    return user

#根据用户豆瓣ID从数据库中获得某个用户id
def get_user_from_id(douban_id):
    sql = 'SELECT id from users WHERE douban_id=%s' % douban_id
    cursor.execute(sql)
    user = cursor.fetchone()
    return user

#找出该关注关系是否已经存储
def get_user_follow(item):
    sql = 'SELECT * from user_follows WHERE user_id=%s AND user_follow_id=%s' % (item['user_id'],item['user_follow_id'])
    cursor.execute(sql)
    user = cursor.fetchone()
    return user

#保存用户关注关系
def save_user_follow(item):
    keys = item.keys()  # item是字典，keys为列表，values为元组，field与temp为字符串
    values = tuple(item.values())
    fields = ','.join(keys)
    temp = ','.join(['%s'] * len(keys))
    sql = 'INSERT INTO user_follows (%s) VALUES (%s)' % (fields, temp)
    cursor.execute(sql, tuple(i for i in values))
    return db.connection.commit()


if __name__ == '__main__':
    users = get_users()
    for user in users:
        douban_id = user['douban_id']
        user_id = get_user_from_id(douban_id)['id'] #获得当前用户的id
        filepath = '../storage/userFollow/' + '%s' % douban_id + '.txt'
        print(filepath)
        if os.path.exists(filepath):
            file = open(filepath, "r")
            for line in file:
                line = line[:-1]
                user_follow = get_user_from_url(line) #获得用户关注的对象
                if user_follow:
                    user_follow_id = user_follow['id'] #获得用户关注的对象的id
                    userFollow = UserFollow()
                    userFollow['user_id'] = user_id
                    userFollow['user_follow_id'] = user_follow_id
                    print(userFollow)
                    exist = get_user_follow(userFollow)
                    if not exist:
                        save_user_follow(userFollow)
                    else:
                        print('用户%s已经关注过%s' % (userFollow['user_id'],userFollow['user_follow_id']))
                else:
                    print('未找到%s对应用户' % line)
        else:
            print('不存在用户%s的关注文件' % user['douban_id'])









