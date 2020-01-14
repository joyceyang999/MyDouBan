import random
import string
import time
import os
import re

import MyDouBan.database as db
from scrapy import Spider,Request,FormRequest
from MyDouBan.items import User,UserFollow
cursor = db.connection.cursor()

class UserInfoSpider(Spider):
    name="user_info"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                  (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
    allowed_domains = ["douban.com"]
    sql = 'SELECT * from users'
    cursor.execute(sql)
    users = cursor.fetchall()
    num=0

    def start_requests(self):
        self.logger.info('-------start_requests--------------')
        return [Request(url="https://accounts.douban.com/passport/login", meta={"cookiejar": 1}, callback=self.login)]

    def get_nikename(self,user,response):
        regx = '//div[@class="pic"]/a/@title'
        data = response.xpath(regx).extract() #解析得到list
        if data:
            user['nickname'] = data[0]
            #self.logger.info('1------nickname:%s', data[0])
        else:
            regx = '//div[@class="pic"]/a/img/@alt'
            data = response.xpath(regx).extract()
            if data:
                user['nickname'] = data[0]
                #self.logger.info('2------nickname:%s', data[0])
            else:
                self.num = self.num +1
                filepath = '../storage/errorPages/nickname_%s.html' % str(self.num)
                file = open(filepath,"w+",encoding="utf8")
                file.write(response.text)
        return user

    def get_head_thumb(self,user,response):
        regx = '//div[@class="basic-info"]/img/@src'
        data = response.xpath(regx).extract()
        if data:
            user['head_thumb'] = data[0]
            #self.logger.info('-------head_thumb:%s', data[0])
        else:
            self.num = self.num + 1
            filepath = '../storage/errorPages/head_thumb_%s.html' % str(self.num)
            file = open(filepath, "w+", encoding="utf8")
            file.write(response.text)
        return user

    def get_douban_id(self,user,response):
        regx = '//div[@class="user-opt"]/a/@id'
        data = response.xpath(regx).extract()
        #self.logger.info('data-------douban_id:%s', data)
        if data:
            user['douban_id'] = data[0]
            return user
            #self.logger.info('-------douban_id:%s', data[0])
        else:
            regx1 = '//div[@class="mn"]/a'
            exist = data = response.xpath(regx1).extract()
            if exist:
                print('%s用户已冻结' % user ['douban_user_url'])
                return user
        self.num = self.num + 1
        filepath = '../storage/errorPages/douban_id_%s.html' % str(self.num)
        file = open(filepath, "w+", encoding="utf8")
        file.write(response.text)
        return user

    def get_created_at(self,user,response):
        regx = '//div[@class="user-info"]/div[@class="pl"]/text()'
        data = response.xpath(regx).extract()
        if data:
            result = re.search("(\d{4})-(\d{2})-(\d{2})",data[1])
            #print(data)
            if result != None:
                created_at = "%s-%s-%s 00:00:00" % (result.group(1),result.group(2),result.group(3))
                user['created_at'] = created_at
                #self.logger.info('-------created_at:%s', created_at)
                return user
        self.num = self.num + 1
        filepath = '../storage/errorPages/created_at_%s.html' % str(self.num)
        file = open(filepath, "w+", encoding="utf8")
        file.write(response.text)


    def login(self,response):
        self.logger.info('-------login--------------')
        # 登录URL
        login_url = 'https://accounts.douban.com/j/mobile/login/basic'
        # 传递用户名和密码
        data = {'name': 'XXXX',
                'password': 'XXXXX',
                'remember': 'false'}

        return [FormRequest(url=login_url,
                            method='POST',
                            meta={"cookiejar":response.meta["cookiejar"]},
                            formdata=data,
                            dont_filter=True,
                            callback=self.start_user_info)]

    def start_user_info(self,response):
        self.logger.info('-------start_user_info--------------')
        for user in self.users:
            self.user_id = user['id']
            self.filepath = '../storage/userFollow/' + '%s' % user['douban_id'] + '.txt'
            print(self.filepath)
            if not os.path.exists(self.filepath): #如果不存在该用户的关注文件
                print('不存在用户%s的关注文件' % user['douban_id'])
            else:
                file = open(self.filepath,"r")
                num = 0
                for line in file:
                    num = num + 1
                    time.sleep(1 + random.randint(2, 5))
                    line = line[:-1]
                    if num == 150:
                        break
                    self.logger.info('-------line:%s', line)
                    yield Request(line, callback=self.parse,meta={"cookiejar":True,"user_url":line})


    def parse(self, response):
        #self.logger.info('-------parse--------------')
        #print(response.meta.get("user_url"))
        if 35000 > len(response.body):
            print(response.body)
            print(response.url)
        elif 404 == response.status:
            print(response.url)
        else:
            user = User()
            user['douban_user_url'] = response.meta.get("user_url")
            self.get_douban_id(user,response)
            if user["douban_id"] != None:
                self.get_nikename(user,response)
                self.get_head_thumb(user,response)
                self.get_created_at(user,response)
                print(user)
                return user



