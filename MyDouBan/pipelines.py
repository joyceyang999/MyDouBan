# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MyDouBan.database as db
from MyDouBan.items import User,UserFollow

cursor = db.connection.cursor() #获得游标

class MydoubanPipeline(object):
    #根据豆瓣id获得用户
    def get_user(self,item):
        sql = 'SELECT * FROM users WHERE douban_id=%s' % item['douban_id']
        print(sql) #SELECT * FROM users WHERE douban_id=2472913
        cursor.execute(sql)
        return cursor.fetchone()

    #保存用户
    def save_user(self,item):
        # item是字典，keys为列表，values为元组，field与temp为字符串
        keys = item.keys()
        values = tuple(item.values())
        fields = ','.join(keys)
        temp = ','.join(['%s'] * len(keys))
        sql = 'INSERT INTO users (%s) VALUES (%s)' % (fields, temp) #
        print(sql) #INSERT INTO users (douban_user_url,douban_id,nickname,head_thumb,created_at) VALUES (%s,%s,%s,%s,%s)
        cursor.execute(sql, tuple(i.strip() for i in values))
        return db.connection.commit()

    #更新用户
    def update_user(self,item):
        douban_id = item.pop('douban_id') #删除豆瓣id的键值对
        keys = item.keys()
        values = tuple(item.values()) # item.values() 类型：<class 'collections.abc.ValuesView'> 如果用list(item.values())强制转换还是ValuesView
        fields = ['%s=' % i + '%s' for i in keys]
        sql = 'UPDATE users SET %s WHERE douban_id=%s' % (','.join(fields), douban_id)
        print(sql) #UPDATE users SET douban_user_url=%s,nickname=%s,head_thumb=%s,created_at=%s WHERE douban_id=1947334
        cursor.execute(sql, values)
        return db.connection.commit()

    def process_item(self, item, spider):
        if isinstance(item, User):
            '''
            User
            '''
            exist = self.get_user(item)
            if exist == None: #如果当前douban_id对应用户不存在
                try:
                    self.save_user(item)
                    print('用户%s已添加至数据库！' % item['douban_id'])
                except Exception as e:
                    print(item)
                    print(e)
            else: #若已存在应当更新
                self.update_user(item)
                print('用户%s已更新！' % exist['douban_id'])
        #return item
