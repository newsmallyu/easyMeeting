# -*- coding: utf-8 -*-
#!/usr/bin/python3
# ubuntu16.04LTS

import json
import time
import datetime
import urllib.request as request
import urllib.parse as parse
from wsgiref.simple_server import make_server

if __name__ == '__main__':
    import db
else:
    from cgi import db

"""
用户登录、注册相关
"""
def newCookieExpires(exdays):
    t = time.time() + exdays * 24 * 60 * 60
    return time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.localtime(t))

def handleSignup(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    # json format- {name: xx, password: xx, verify: xx}
    json_body = json.loads(json_body)

    new_user = db.createUser(json_body['name'],
                             json_body['password'],
                             json_body['verify'])
    return json.dumps(new_user)

def handleSignin(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    # json format- {name: xx, password: xx, verify: xx}
    json_body = json.loads(json_body)

    # TODO: 返回值需要重新考虑
    new_user = db.loginUser(json_body['name'], json_body['s_password'])
    if new_user:
        return json_body

"""
预定会议室相关
"""
def handleAddMeeting(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    # json format-
    #      {timestamp: xx, title: xx, room: xx, start: xx, end: xx}
    json_body = json.loads(json_body)
    new_meeting = db.addMeeting(json_body["timestamp"],
                                json_body["title"],
                                json_body["room"],
                                json_body["start"],
                                json_body["end"],
                                json_body["user_name"])
    return new_meeting

def handleQueryMeeting(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    # json format-
    #      {start_timestamp: xx, end_timestamp: xx}
    json_body = json.loads(json_body)
    print(json_body)
    meetings = db.queryMeetings(json_body["start_timestamp"],
                                json_body["end_timestamp"])
    return meetings

def showEnviron(environ):
    html = "<table>\n"
    for k, v in environ.items():
        html += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, v)
    html += "</table>\n"
    return html


def handlemanagerMeeting(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    json_body = json.loads(json_body)
    if(json_body["name"] == "admin"):
        meetings = db.queryMeetingALL()
    else:
        meetings = db.queryMeetingByUser(json_body["name"])
    return meetings


def handleDeletemeeting(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    json_body = json.loads(json_body)
    result = db.deleteMeetingById(json_body)
    return result

#对接nas系统 先根据code请求nas得到token 再用token获取userinfo
def handleSiginAd(environ):
    json_body_length = int(environ['CONTENT_LENGTH'])
    json_body = environ['wsgi.input'].read(json_body_length).decode('utf-8')
    if json_body:
        json_body = json.loads(json_body)
    user = None
    if json_body:
        urlad = "http://10.16.75.22:9898/api/token"
        datatemp = {"Code": json_body, "SiteKey": "2vwnh2mdcq1j820zuu1yfm1r3p", "SiteSecret": "35b1jdyhh7igp2uti8i5anhcnl05yp97ygauqfk2nd0ad5660h2w"}
        proxy = request.ProxyHandler({'https': 's1firewall:8080'})
        auth = request.HTTPBasicAuthHandler()
        opener = request.build_opener(proxy, auth, request.HTTPHandler)
        request.install_opener(opener)
        req = request.Request(urlad)
        req.add_header('Content-Type', 'application/json')
        response = request.urlopen(req, json.dumps(datatemp).encode())
        jsonBody = json.loads(response.read())
        token = jsonBody["Token"]
        if token:
            urlgetuser= "http://10.16.75.22:9898/api/user?token="
            proxy = request.ProxyHandler({'https': 's1firewall:8080'})
            auth = request.HTTPBasicAuthHandler()
            opener = request.build_opener(proxy, auth, request.HTTPHandler)
            request.install_opener(opener)
            res = request.urlopen(urlgetuser+token)
            user = json.loads(res.read())["UserName"]
    return user



def application(environ, start_response):
    url = environ['PATH_INFO']    # /easyMeeting/xxxx
    url = url.split("/")[2]
    print(url)
    if url == "signup":
        start_response('200 OK',
                       [('Content-Type', 'application/json;charset="utf-8"')])
        body = handleSignup(environ)
        #html += showEnviron(environ)
        return [body.encode("utf-8")]
    elif url == "signin":
        body = handleSignin(environ)
        #html += showEnviron(environ)

        # 登录成功则发送cookie到client保存用户名和密码信息
        # TODO: 密码需加密处理
        headers = [('Content-Type', 'application/json;charset="utf-8"')]
        if body:
            if body["rember_me"]:
                headers.append(('Set-Cookie',
                                'name={};Expires={};'
                                .format(body['name'], newCookieExpires(30))))
                headers.append(('Set-Cookie',
                                's_password={};Expires={};'
                                .format(body['s_password'], newCookieExpires(30))))
            else:
                headers.append(('Set-Cookie', 'name={};'.format(body['name'])))
                headers.append(('Set-Cookie', 's_password={};'.format(body['s_password'])))

        start_response('200 OK', headers)
        body = json.dumps(body)
        return [body.encode("utf-8")]
    elif url == "signinAd":
        body = handleSiginAd(environ)
        headers = [('Content-Type', 'application/json;charset="utf-8"')]
        if body:
            headers.append(('Set-Cookie', 'name={};'.format(body)))
            headers.append(('Set-Cookie', 'islogin={};'.format("true")))
        start_response('200 OK', headers)
        body = json.dumps(body)
        return [body.encode("utf-8")]
    elif url == "addmeeting":
        start_response('200 OK',
                       [('Content-Type','application/json;charset="utf-8"')])
        body = handleAddMeeting(environ)
        #html += showEnviron(environ)
        return [json.dumps(body).encode("utf-8")]
    elif url == "querymeetings":
        start_response('200 OK',
                       [('Content-Type','application/json;charset="utf-8"')])
        body = handleQueryMeeting(environ)
        #html += showEnviron(environ)
        return [json.dumps(body).encode("utf-8")]
    elif url == "managermeeting":
        start_response('200 OK',
                       [('Content-Type','application/json;charset="utf-8"')])
        body = handlemanagerMeeting(environ)
        return [json.dumps(body).encode("utf-8")]
    elif url == "deletemeeting":
        start_response('200 OK',
                       [('Content-Type', 'application/json;charset="utf-8"')])
        result = handleDeletemeeting(environ)
        return [json.dumps(result).encode("utf-8")]

if __name__ == '__main__':
    print(newCookieExpires(30))
    print(newCookieExpires(-1))
