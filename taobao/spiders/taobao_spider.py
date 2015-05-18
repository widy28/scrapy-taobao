__author__ = 'Administrator'
# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import re
import urllib2

class TaobaoSpider(CrawlSpider):

    name = 'taobao'
    allowed_domains = ['taobao.com']
    start_urls = ['https://login.taobao.com/member/login.jhtml']
    def __init__(self, *args, **kwargs):
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        self.http_user = 'xxxxxxxxx'   # taobao username
        self.http_pass = 'xxxxxxxxx'   # taobao password
        #login form
        self.formdata = {
                        'TPL_checkcode':'',\
                        'TPL_username':self.http_user, \
                        'TPL_password':self.http_pass,\
                        }
        self.headers = {'Host':'login.taobao.com',
                        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                        'Referer' : 'https://login.taobao.com/member/login.jhtml',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Connection' : 'Keep-Alive'
                        }
        self.id = 0

    def start_requests(self):
        for i, url in enumerate(self.start_urls):
            yield FormRequest(url, meta = {'cookiejar': i},\
                                formdata = self.formdata,\
                                headers = self.headers,\
                                callback = self.login)#jump to login page

    def _log_page(self, response, filename):
        with open(filename, 'w') as f:
            try:
                f.write("%s\n%s\n%s\n" % (response.url, response.headers, response.body))
            except:
                f.write("%s\n%s\n" % (response.url, response.headers))

    def login(self, response):
        self._log_page(response, 'taobao_login.html')
        return [FormRequest.from_response(response, \
                            formdata = self.formdata,\
                            headers = self.headers,\
                            meta = {'cookiejar':response.meta['cookiejar']},\
                            callback = self.parse_item)]

    def parse_item(self, response):
        self._log_page(response, 'get_checkcode.html')
        hxs = Selector(response)
        checkcode_err = hxs.xpath('//div[@id="J_Message"]/p/text()').extract()
        # print checkcode_err[0]
        # print checkcode_err[0] == u"为了您的账户安全，请输入验证码。"
        if checkcode_err[0] == u"为了您的账户安全，请输入验证码。":
            # print 'checkcode-----'
            # return response
            checkcode_url = hxs.xpath('//img[@id="J_StandardCode_m"]/@data-src').extract()
            # print checkcode_url,'-------------'
            if not checkcode_url == False:
                import webbrowser
                webbrowser.open_new_tab(checkcode_url[0])
                #提示用户输入验证码
                checkcode = raw_input(u'input checkcode:')
                #将验证码重新添加到post的数据中
                print checkcode
                self.formdata['TPL_checkcode'] = checkcode
        return [FormRequest.from_response(response, \
                    formdata = self.formdata,\
                    headers = self.headers,\
                    meta = {'cookiejar':response.meta['cookiejar']},\
                    callback = self.get_J_HToken)]

    def get_J_HToken(self, response):
        self._log_page(response, 'get_J_HToken.html')

        hxs = Selector(response)
        J_HToken_data = hxs.xpath('//input[@id="J_HToken"]/@value').extract()
        # print J_HToken_data,'tttttt-----'
        if not J_HToken_data:
            # print u"get Token unsucc，redo"
            # print u'可能验证码错误'
            checkcode_err = hxs.xpath('//div[@id="J_Message"]/p/text()').extract()
            print checkcode_err[0]
            if checkcode_err[0] == u"验证码错误，请重新输入。":
                # print 'checkcode2222-----'
                # return response
                checkcode_url = hxs.xpath('//img[@id="J_StandardCode_m"]/@data-src').extract()
                # print checkcode_url,'-------------'
                if not checkcode_url == False:
                    import webbrowser
                    webbrowser.open_new_tab(checkcode_url[0])
                    #提示用户输入验证码
                    checkcode = raw_input(u'input checkcode:')
                    #将验证码重新添加到post的数据中
                    print checkcode
                    self.formdata['TPL_checkcode'] = checkcode
                    return [FormRequest.from_response(response, \
                                formdata = self.formdata,\
                                headers = self.headers,\
                                meta = {'cookiejar':response.meta['cookiejar']},\
                                callback = self.get_J_HToken)]
        else:
            # 此处拼接字符串需要注意 编码问题 J_HToken_data是unicode码
            get_st_url = u'https://passport.alipay.com/mini_apply_st.js?site=0&token=%s&callback=stCallback6' % J_HToken_data[0]
            # print get_st_url
            request = urllib2.Request(get_st_url)
            response = urllib2.urlopen(request)
            self._log_page(response, 'get_st.html')
            # self._log_page(response, 'get_st.html')
            pattern = re.compile('{"st":"(.*?)"}',re.S)
            result = re.search(pattern,response.read())
            #如果成功匹配
            if result:
                print u"成功获取st码"
                #获取st的值
                st = result.group(1)
                # print st,'-----st'

                stURL = 'https://login.taobao.com/member/vst.htm?st=%s&TPL_username=%s&callback=jsonp75'% (st,self.http_user)
                headers = {
                    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
                    'Host':'login.taobao.com',
                    'Connection' : 'Keep-Alive'
                }

                return Request(stURL,\
                            headers = headers,\
                            callback = self.get_check_login_success)

    def get_check_login_success(self, response):
        # 登陆成功。。可以获取订单等信息了。后续补充更新。。
        self._log_page(response, 'get_check.html')
        # 登陆成功，会自动跳转到 我的淘宝页 获取跳转的url
        pattern = re.compile(u'"url":"(.*?)"', re.S)
        # print pattern
        # print response.body
        match = re.search(pattern, response.body)
        # print match.group(1),'--------------------'
        next_url = match.group(1)
        return Request(next_url,\
                        callback = self.get_next_data)

    def get_next_data(self, response):
        self._log_page(response, 'get_next.html')
        try:
            hxs = Selector(response)
            nick = hxs.xpath('//em[@class="s-name"]/a/text()').extract()
            print "login-success, get user nick:",nick
        except:
            print u'请查看get_next.html里面是否是个人淘宝页，进行代码修改'
        return None





