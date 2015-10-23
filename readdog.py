# coding=utf-8

import random

import regex as re

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

# 全局变量
# file_name应位于readdog.py相同目录下
book_name = '静静的顿河'
verfy_code = 'python3'
file_name = 'a.txt'
file_encoding = 'gb18030'

# 读入txt文件
book_text = ''
with open(file_name, encoding=file_encoding) as f:
    book_text = f.read()
    print('读入%s个字符' % format(len(book_text), ','))


# 解析flags
def process_flags(string):
    def is_this(upper_flag, s1, s2):
        if upper_flag == s1 or upper_flag == s2:
            return True
        else:
            return False

    flags = string.strip().upper().split()

    ret = 0
    for f in flags:

        if is_this(f, 'ASCII', 'A'):
            ret |= re.ASCII
        elif 'DEBUG' == f:
            ret |= re.DEBUG
        elif is_this(f, 'IGNORECASE', 'I'):
            ret |= re.IGNORECASE
        elif is_this(f, 'LOCALE', 'L'):
            ret |= re.LOCALE
        elif is_this(f, 'MULTILINE', 'M'):
            ret |= re.MULTILINE
        elif is_this(f, 'DOTALL', 'S'):
            ret |= re.DOTALL
        elif is_this(f, 'VERBOSE', 'X'):
            ret |= re.VERBOSE
        else:
            print('错误!未知的正则模式:', flag)

    return ret


class ReaddogHander(RequestHandler):

    def get(self):
        self.render('root.html', bookname=book_name)

    def post(self):
        # 验证码
        if self.get_body_argument('code') != verfy_code:
            self.render('root.html', bookname=book_name)
            return
        
        # 提交的信息
        pattern = self.get_body_argument('pattern')
        flags = process_flags(self.get_body_argument('flags'))
        try:
            size = int(self.get_body_argument('size'))
        except:
            size = -1

        # 正则
        r = re.compile(pattern, flags)
        match_iter = r.finditer(book_text)

        ret = []
        count = 0
        last_start, last_end = -1, -1
        for i, m in enumerate(match_iter):
            if size != -1 and i >= size:
                s = '<font color="green">忽略%d条以后的结果...</font>' % size
                ret.append(s)
                break

            if m.start(0) >= last_start and m.end(0) <= last_end:
                continue

            start = max(0, m.start(0) - 100)
            end = min(len(book_text), m.end(0) + 250)
            last_start = start
            last_end = end

            section = book_text[start:end]
            section = section.replace(m.group(0),
                                      '<font color="blue">' + m.group(0) + '</font>')

            count += 1
            ret.append('【' + str(count) + '】' + section)

        html = '<hr>'.join(ret)

        # 防剧透
        if len(ret) < 7:
            html += '<hr>' + '<br>' * random.randint(50, 100)

        self.render('result.html',
                    bookname=book_name,
                    result=html)

# web部分
class ReaddogApplication(Application):

    def __init__(self):
        handlers = [
            (r'/', ReaddogHander)
        ]
        settings = {
            'template_path': 'templates',
        }
        Application.__init__(self, handlers, **settings)

app = ReaddogApplication()

if __name__ == '__main__':
    http_server = HTTPServer(app)
    http_server.listen(9999)
    IOLoop.instance().start()
