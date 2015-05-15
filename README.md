# scrapy-taobao
scrapy模拟淘宝登陆，未加代理ip的处理。希望有好的代理处理方法分享出来。

# 确保安装了scrapy。
    self.http_user = 'xxxxxxxx'   # taobao username
    self.http_pass = 'xxxxxxxx'   # taobao password
记得修改taobao_spider.py中的用户名username和密码password。\<br>

# 运行命令
    scrapy crawl taobao
  如果用户登陆需要输入验证码，则会自动打开验证码的图片链接让客户手动输入，输入错误会重新打开验证码的图片链接供用户再次输入。

# 登陆成功的提示
    login-success, get user nick: ["user nick"]
用户看到这句代表登陆成功，可以进行一些其他数据的提取。
    
