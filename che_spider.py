# -*- coding:utf-8 -*-

from selenium import webdriver
import time,MySQLdb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from lxml import etree


from yz_code import picture_to_validate
from yz_code import md5




def rinse(data):
    if data:
        return data[0]
    else:
        data = [""]
        return data[0]


def parse_page():
    db = MySQLdb.connect(host='localhost', user='root', passwd='1018', db='che_db', use_unicode=True, charset='utf8')
    cursor = db.cursor()

    driver = webdriver.PhantomJS()

    driver.get('https://ics.autohome.com.cn/passport/account/login')
    # 所有用户列表
    users = [(u'元信汽车', 'layx2012,')]

    for u_info in users:
        tupian_time = time.localtime()
        print  "tupian_time>>>",tupian_time
        try:
            # 在一定时间内查找某个标签，如果该标签出现，则结束等待，如果一直不出现，就超时
            element = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.ID,'imgValidCodeDealer')))
            # 取出单个用户信息登陆
            driver.find_element_by_id('UserNameDealer').send_keys(u_info[0])
            driver.find_element_by_id('PasswordDealer').send_keys(u_info[1])
            src = driver.find_element_by_id('imgValidCodeDealer')
            src_path = src.get_attribute('src')
            # 截图验证码
            file_path = 'imgs/'+md5(str(src_path))+'.jpeg'
            # 截取整张图片
            driver.save_screenshot('screenshot.png')
            # 获取验证码在网页中的位置
            left = src.location['x']
            top = src.location['y']
            right = src.location['x'] + src.size['width']
            bottom = src.location['y'] + src.size['height']
            # 打开整张图，截取验证码位置图片
            im = Image.open('screenshot.png')
            im = im.crop((left, top, right, bottom))
            # 保存截取后的图片
            im.save(file_path)
            # 传入截取验证码的路径，上传云打码
            yzm = picture_to_validate(file_path)
            time.sleep(1)
            # 输入验证码
            driver.find_element_by_id('checkCodeDealer').send_keys(yzm)
            # 点击登录
            driver.find_element_by_id('btnDealer').click()
            time.sleep(1)
            print "start>>>>>>>>", driver.page_source
            data1 = etree.HTML(driver.page_source)
            error = data1.xpath('//div[@id="loginDealerError"]/div/text()')
            if error:
                # 刷新验证码
                driver.find_element_by_id("imgValidCodeDealer").click()
                # 输入密码
                driver.find_element_by_id('PasswordDealer').send_keys(u_info[1])
                # 清除验证码框中数据
                driver.find_element_by_id("checkCodeDealer").clear()
                src = driver.find_element_by_id('imgValidCodeDealer')
                src_path = src.get_attribute('src')
                # 截图验证码
                file_path = 'imgs/' + md5(str(src_path)) + '.jpeg'
                # 截取整张图片
                driver.save_screenshot('screenshot.png')
                # 获取验证码在网页中的位置
                left = src.location['x']
                top = src.location['y']
                right = src.location['x'] + src.size['width']
                bottom = src.location['y'] + src.size['height']
                # 打开整张图，截取验证码位置图片
                im = Image.open('screenshot.png')
                im = im.crop((left, top, right, bottom))
                # 保存截取后的图片
                im.save(file_path)
                # src.screenshot(file_path)
                # 传入截取验证码的路径，上传云打码
                yzm = picture_to_validate(file_path)
                time.sleep(1)
                # 输入验证码
                driver.find_element_by_id('checkCodeDealer').send_keys(yzm)
                # 点击登录
                driver.find_element_by_id('btnDealer').click()
                time.sleep(2)

        except Exception as e:
            print e
            driver.quit()
        else:

            content = driver.page_source
            content = etree.HTML(content)
            url = content.xpath('//div[@class="box-bd fn-clear"]/a[2]/@href')
            url = 'https:%s' % url[0]
            print url
            driver.get(url)

            # 获取总页数
            content = driver.page_source
            content = etree.HTML(content)
            # number = content.xpath('//div[@class="page-item-jump"]/text()')[0]
            # print number
            # parse = re.compile(u"/共(.*?)页")
            # number_page = parse.findall(number)[0]
            # for x in range(1,int(number_page)):
            for x in range(1, 10):
                content = driver.page_source
                content = etree.HTML(content)
                content_list = content.xpath('//table[@id="MainTable"]/tbody/tr')
                for a in content_list:
                    # 客户姓名
                    username = a.xpath('td[1]/a/text()')[0]
                    # 号码
                    content_all = a.xpath('td[2]/text()')
                    phone = content_all[0]
                    # 地址
                    address = content_all[1]
                    # 线索获得时间
                    ordertime = a.xpath('td[7]/text()')[0]
                    # 车型
                    carinfo = a.xpath('td[9]/text()')
                    carinfo = rinse(carinfo)
                    # ckey
                    str1 = phone + ordertime + carinfo
                    ckey = md5(str(str1))
                    v = cursor.execute("select ckey from cdb_userinfo WHERE ckey = '%s'" % ckey)
                    print v
                    if v:
                        pass
                    else:
                        sql = (
                            "INSERT INTO cdb_userinfo(username,phone,address,ordertime,carinfo,ckey)""VALUES (%s,%s,%s,%s,%s,%s)")
                        data = (username, phone, address, ordertime, carinfo, ckey)
                        cursor.execute(sql, data)
                        db.commit()
                driver.find_element_by_id('pageNext').click()

            driver.quit()
            cursor.close()
            db.close()






if __name__ == "__main__":
    parse_page()







