
import os
import MyDouBan.database as db
import requests
from lxml import etree

#获得连接数据库的游标
cursor = db.connection.cursor()

# 生成Session对象，用于保存Cookie
session = requests.Session()

#登录豆瓣，1登录成功，0登录失败
def login_douban():
    # 登录URL
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'
    # 请求头
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Referer': 'https://accounts.douban.com/passport/login?source=main'
    }
    # 传递用户名和密码
    data = {'name': '18756634595',
            'password': 'aiziyou1..',
            'remember': 'false'}
    try:
        response = session.post(login_url, headers=headers, data=data)
        response.raise_for_status() #抛出错误请求异常
    except:
        print('登录失败')
        return 0
    print('登录成功') # 打印请求结果
    return 1

#从数据库中获得所有用户
def get_users():
    sql = 'SELECT douban_id from users'
    cursor.execute(sql)
    users = cursor.fetchall()
    return users

#向文件中添加用户url
def save_url(filepath,user_url_list): #为了方便每个用户关注只保存一次，不考虑关注变动
    if not os.path.exists(filepath):
        file = open(filepath, "w+")
        for i in range(len(user_url_list)):
            # user_url_list[i]返回的是一个字典
            if '[已注销]' == user_url_list[i].text:
                continue
            else:
                file.write(str(user_url_list[i].attrib['href']) + '\n')
        print(filepath+'已保存完成')
    else:
        print(filepath + '已存在')
        pass


if __name__ == '__main__':
    users = get_users()
    for user in users:
        douban_id = user['douban_id']
        filepath = '../storage/userFollow/' + '%s' % douban_id + '.txt'
        print(filepath)
        if not os.path.exists(filepath):
            #用户全部关注人链接
            url = 'https://www.douban.com/people/%s/contacts/' % user['douban_id']
            print(url)
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
            response = session.get(url=url,headers=headers)
            #Xpath解析页面
            tree = etree.HTML(response.text)
            # 获得当前登录状态
            IF_LOGIN = tree.xpath('//div[@class="login-right"]')
            if not IF_LOGIN : #已登录
                print('已登录')
            else: #未登录（cookie失效或者第一次登录）
                print('转到登录')
                while(login_douban() == 0):
                    login_douban()
                response = session.get(url=url, headers=headers)
                tree = etree.HTML(response.text)
            user_url_list = tree.xpath('//div[@class="article"]/dl[@class="obu"]/dd/a')
            save_url(filepath,user_url_list)
        else:
            print('该用户关注列表已经获得')



