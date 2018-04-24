#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, hashlib,urllib2, re
import requests
from datetime import *

reload(sys)
sys.setdefaultencoding("utf-8")


class APIClient(object):
    def http_request(self, url, paramDict):
        post_content = ''
        for key in paramDict:
            post_content = post_content + '%s=%s&' % (key, paramDict[key])
        post_content = post_content[0:-1]
        # print post_content
        req = urllib2.Request(url, data=post_content)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, post_content)
        return response.read()

    def http_upload_image(self, url, paramKeys, paramDict, filebytes):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        boundary = '------------' + hashlib.md5(timestr).hexdigest().lower()
        boundarystr = '\r\n--%s\r\n' % (boundary)

        bs = b''
        for key in paramKeys:
            bs = bs + boundarystr.encode('ascii')
            param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s" % (key, paramDict[key])
            # print param
            bs = bs + param.encode('utf8')
        bs = bs + boundarystr.encode('ascii')

        header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n' % (
        'sample')
        bs = bs + header.encode('utf8')

        bs = bs + filebytes
        tailer = '\r\n--%s--\r\n' % (boundary)
        bs = bs + tailer.encode('ascii')

        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                   'Connection': 'Keep-Alive',
                   'Expect': '100-continue',
                   }
        response = requests.post(url, params='', data=bs, headers=headers)
        return response.content


def picture_to_validate(file_path):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'ics.autohome.com.cn',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36 FirePHP/4Chrome'
    }
    picture = requests.get('https://ics.autohome.com.cn/passport/Account/GetDealerValidateCode',
                           headers=headers).content

    # with open(file_path,'rb') as picture:
    #     i = picture.read()
        # 触发图形验证码相关接口获取返回结果
        client = APIClient()
        paramDict = {}
        result = ''
        act = 'upload'  # raw_input('Action:')
        paramDict['username'] = 'cheyunkeji'
        paramDict['password'] = 'Cheyun8888'
        paramDict['typeid'] = '2040'
        paramDict['timeout'] = '60'
        paramDict['softid'] = '1'
        paramDict['softkey'] = 'b40ffbee5c1cf4e38028c197eb2fc751'
        paramKeys = ['username',
                     'password',
                     'typeid',
                     'timeout',
                     'softid',
                     'softkey'
                     ]
        from PIL import Image
        if picture is None:
            print 'get file error!'
            return
        else:
            img = Image.open(file_path)
            if img is None:
                print 'get file error!'
                return
            img.save("%s.gif"%file_path.split('.')[0], format="gif")
            filebytes = open("%s.gif"%file_path.split('.')[0], "rb").read()
            result = client.http_upload_image("http://api.ysdm.net/create.xml", paramKeys, paramDict, filebytes)
        res_re = r'<Result>(.*?)</Result>'
        res = re.findall(res_re, result, re.S | re.M)
        print res[0]
        return res[0]


def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        print 'md5 error!'


if __name__ == '__main__':
    picture_to_validate('https://a1.ifafootball.club/BMP/a023ldfe8db632ae.asp?t=2018/4/17%2012:57:54')
