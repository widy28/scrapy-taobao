__author__ = 'Administrator'
# -*- coding: utf-8 -*-

import base64


class ProxyMiddleware(object):
    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        # 设置代理ip:port
        request.meta['proxy'] = "http://YOUR_PROXY_IP:PORT"

        # Use the following lines if your proxy requires authentication
        # 如果你的代理服务器需要用户登陆的验证，请使用以下设置
        # proxy_user_pass = "USERNAME:PASSWORD"
        # # setup basic authentication for the proxy
        # encoded_user_pass = base64.encodestring(proxy_user_pass)
        # request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass