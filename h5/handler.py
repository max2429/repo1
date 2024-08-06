#!/usr/bin/python3

import os
import sys
import datetime
import urllib.parse


cont_types = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'swf': 'application/x-shockwave-flash',
}


class Handler:
    def __init__(self, request, root_dir):
        self.request = request
        self.root_dir = root_dir
        self.base = os.getcwd()
        self.full_path = os.path.normpath(self.base + self.root_dir)


    def parse_request(self, request):
        pr = request.split('\r\n\r\n')[0].split(' ')
        method = pr[0]
        try:
            url = pr[1].split('?')[0]
            return (method, urllib.parse.unquote(url.replace('%20', ' ')))
        except Exception:
            return method, ''

    def parse_content_type(self, url):
        if os.path.isfile(self.full_path + url):
            try:
                ext =  url.split('.')[-1]
                if ext in cont_types.keys():
                    return cont_types[ext]
            except Exception:
                return 'text/html;charset=UTF-8'
        return 'text/html;charset=UTF-8'

    def generate_code(self, method, url):
        if method not in ['GET', 'HEAD']:
            return ('HTTP/1.1 405 Method not allowed\r\n', 405)
        path = self.full_path + url
        if not os.path.exists(path) or not os.path.abspath(path).startswith(self.base):
            return ('HTTP/1.1 404 Not found\r\n', 404)
        if os.path.isdir(path) and path != self.full_path + '/':
            if not os.path.exists(os.path.join(path, 'index.html')):
                return ('HTTP/1.1 404 Not found\r\n', 404)
        return ('HTTP/1.1 200 OK\r\n', 200)

    def render_html(self, html_file):
        with open(html_file, 'rb') as html:
            data = html.read()
        return data

    def generate_body(self, code, url):
        path = self.full_path + url
        if code == 404:
            return b'<h1>404</h1><p>Not found</p>'
        if code == 405:
            return b'<h1>405</h1><p>Method not allowed</p>'
        if path == self.full_path + '/':
             return bytes('\r\n'.join( '<p>' + repr(e).replace("'", '') + '</p>' for e in os.listdir(path)).encode())
        if os.path.isfile(path) and os.path.abspath(path).startswith(self.base):
            return self.render_html(path)
        if os.path.isdir(path):
            if os.path.exists(os.path.join(path, 'index.html')):
                return self.render_html(os.path.join(path, 'index.html'))
        return b'<p>No such file or directory</p>'

    def get_content_length(self, url, response_prase):
        path = self.full_path + url
        if os.path.isfile(path) and os.path.abspath(path).startswith(self.base):
            content_length = 'Content-Length: ' + str(os.path.getsize(path))
        elif url == self.root_dir:
            content_length = 'Content-Length: ' + str(len('\r\n'.join( '<p>' + repr(e).replace("'", '') + '</p>' for e in os.listdir(path)).encode()))
        elif os.path.isdir(path) and 'index.html' in os.listdir(path):
            indexfile = os.path.join(path + 'index.html') if os.path.exists(os.path.join(path + 'index.html')) else os.path.join(path + '/index.html')
            content_length = 'Content-Length: ' + str(os.path.getsize(indexfile))
        else:
            content_length = 'Content-Length: ' + str(len(response_prase))
        return content_length

    def generate_headers(self, method, url):
        response_msg, code = self.generate_code(method, url)
        server = 'Server: python ' + sys.version.split('[')[0].strip() + ' ' +  sys.version.split('[')[1].strip().replace(']', '') + '\r\n'
        date = 'Date: ' + datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT') + '\r\n'
        content_type = 'Content-Type: ' + self.parse_content_type(url) + '\r\n'
        content_length = self.get_content_length(url, response_msg) + '\r\n'
        conn = 'Connection: close\r\n\r\n'
        headers = ''.join([response_msg, server, date, content_type, content_length, conn])
        return headers, code, response_msg

    def generate_response(self, request):
        method, url = self.parse_request(request)
        headers, code, response_msg = self.generate_headers(method, url)
        if method not in ['GET', 'HEAD']:
            return response_msg.encode()
        if method == 'HEAD':
            return headers.encode()
        return headers.encode() + self.generate_body(code, url)


