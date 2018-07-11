# coding = utf-8
'''
版本迭代：

成绩查询1.0：
    time 2018/06/30
    by 重庆大学 任鸿翔
    need： 增加密码错误提示
'''
import re, os, json
import requests, random
import hashlib, time
from tkinter import *
from tkinter import ttk
from twilio.rest import Client
import urllib.parse, urllib.request
from pypinyin import pinyin, lazy_pinyin
url = "http://202.202.1.41"
homeUrl = "http://202.202.1.41/home.aspx"
loginUrl = 'http://202.202.1.41/_data/index_login.aspx'
scoreUrl = 'http://202.202.1.41/XSCJ/Stu_MyScore_print_rpt.aspx?xn=2017&xq=1&rpt=0&rad=2&zfx_flag=0'
username = ""
password = ""
schoolcode = "10611"
url_google = 'http://translate.google.cn'
reg_text = re.compile(r'(?<=TRANSLATED_TEXT=).*?;')
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 r'Chrome/44.0.2403.157 Safari/537.36'
last_file = ""
table = ["[CST21107] Computer Graphics", 
"[CST30101] Algorithm Analysis and Design",
"[IPT20001] Situation and Policy (4)",
"[MATH20041] Probability Theory and Mathematical Statistics I",
"[MATH20502] Mathematical model",
"[HG00058] Photographic Art Creation",
"[CST22101] Professional internship",
"[EM20401] Construction Regulations",
"[CST21108] Digital Logic",
"[CST21105] WINDOWS programming",
"[EGP20101] Slow English Listening",
"[IPT10300] Basic Principles of Marxism"]
def getView():
    view = []
    r = re.compile(
        r'<input type="hidden" name="__VIEWSTATE" value="(.*?)" \/>')
    data = requests.get(loginUrl)
    view = r.findall(data.text)
    r = re.compile(
        r'<input type="hidden" name="__VIEWSTATEGENERATOR" value="(.*?)" \/>')
    data = r.findall(data.text)
    view.append(data[0])
    return view


def checkPwd(self):
    
    p = hashlib.md5(password.encode()).hexdigest()
    
    p = hashlib.md5(
            ( username + p[0:30].upper() + schoolcode).encode()).hexdigest()
    
    return p[0:30].upper()
    
    
def login():
    #print(username)
    view = getView()
    #print(view)
    psw = checkPwd(view)
    datas = {
        '__VIEWSTATE':view[0],
        '__VIEWSTATEGENERATOR': view[1],
        'Sel_Type': ' STU',
        'txt_dsdsdsdjkjkjc': username,
        'txt_dsdfdfgfouyy': password,
        'txt_ysdsdsdskgf': '',
        'pcInfo': '',
        'typeName': '',
        'aerererdsdxcxdfgfg': '',
        'efdfdfuuyyuuckjg': psw
        }
    headers = {
        'Accept':'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3',
        'Connection':'Keep-Alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14392'
        }
    html = requests.get(homeUrl, headers = headers)
    cookies = html.cookies
    requests.post(loginUrl, headers = headers, cookies = cookies, data = datas)
    html = requests.get(scoreUrl, headers=headers, cookies=cookies)
    return html

def get(html):
    html.text.encode('utf-8')
    return html.text

def work(result):
    result = re.sub('<head>.*?</head>', "", result)
    result = re.sub('<input.*?>', "", result)
    result = re.sub('<span.*?</span>', "", result)
    result = re.sub('<table width=.857.*?</table>', "", result)
    result = re.sub('<td width=100%.*?</td>', "", result)
    result = re.sub('<td align=left.*?</td>', "", result)
    final = re.findall('<td width=[0-9]{2,3} .*?>(.*?)<br></td>', result)
    return final

def sendMessage(final):
    file1 = ""
    tmp = 0
    cnt = 0
    
    for fi in final:
        tmp  += 1
        #print(fi)
        if tmp == 2 : 
            file1 += table[cnt] + ' '
        if tmp == 7 :
            file1 += '  ->'+ "".join(lazy_pinyin(fi))+'<-  ' 
        if tmp == 9:
            file1 += '\r\n'
            tmp = 0
            cnt += 1
            
    print(file1)
    global last_file
    
    if (file1 > last_file) - (file1 < last_file) != 0 :
        #print("new score")
        last_file = file1
        account_sid = "ACcc65c5faa753a9bd11133b9c042f1efa"
        auth_token  = "37c317f4cb98b4e08feb2ef8b9b476f9"
        ##基于twilio的免费短信推送，只能推送英文字母信息，所以这个版本会将中文转换为拼音发送
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to="#在这里填入你的注册手机号#", 
            from_="#在这里填入分配给你的免费手机号#",
            body = file1)

        
    
        
def show(final):
    
    intime = open('result.html', "w")
    intime.write(final)
    os.startfile(r".\result.html")
    
    
if __name__ == "__main__":
    
    username = "#在这里填入你的学号#"
    password = "#在这里填入你的密码#"
    while 1:
        html   = login()
        result = get(html)
        final  = work(result)
        sendMessage(final)
        time.sleep(300)
