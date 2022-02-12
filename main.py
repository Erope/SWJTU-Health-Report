import requests, re, json, sys, codecs
from bs4 import BeautifulSoup
from aes import encryptAES
from config import *

sys.path.append('.')
requests.packages.urllib3.disable_warnings()
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

cas_url = 'https://cas.swjtu.edu.cn/authserver/login?service=http://xgsys.swjtu.edu.cn/cas/onelogin.aspx?type=SPCP'

result = '西南交大健康填报\n'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78'
}

def submit():
    global result
    session = requests.Session()
    r = session.get(cas_url, headers=header)

    soup = BeautifulSoup(r.text, 'lxml')
    salt = soup.find(id='pwdDefaultEncryptSalt').get('value')
    lt = soup.find(attrs={"name": "lt"}).get('value')
    execution = soup.find(attrs={"name": "execution"}).get('value')
    encpwd = encryptAES(pwd, salt)
    result += 'Try to Login...\n'
    data = {
        'username': username,
        'password': encpwd,
        'lt': lt,
        'dllt': 'userNamePasswordLogin',
        'execution': execution,
        '_eventId': 'submit',
        'rmShown': 1
    }

    r = session.post(cas_url, data=data, headers=header, timeout=10)

    if str(username) in r.text and 'SPCPTest3' in r.text:
        result +=  "登陆成功！\n"
    else:
        result +=  "登陆失败！\n"
        return

    jump_url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
    for i in jump_url:
        if 'SPCPTest3' in i:
            r = session.get(i, headers=header, timeout=10)
            break

    soup = BeautifulSoup(r.text, 'lxml')
    status = soup.find(class_='plat-title').span.text
    result += f"当前状态: {status}\n"

    if status != "开启中":
        result += '退出中...\n'
        return

    r = session.get('http://xgsys.swjtu.edu.cn/SPCPTest3/Web/Report/Index', headers=header, timeout=10)
    if '我已阅读承诺书，并保证按承诺书内容执行。' not in r.text:
        result += '或许已经填报过了？退出中...\n'
        return

    r = session.post('http://xgsys.swjtu.edu.cn/SPCPTest3/Web/Report/Index', data=submit_data, headers=header, timeout=10)
    if '提交成功！' in r.text:
        result += '信息申报完成！\n'
    else:
        result += '填报失败！请自行填报！\n'

def main():
    global result
    for _ in range(5):
        try:
            submit()
            break
        except BaseException as e:
            result += '出错，重试中...\n'
            result += str(e) + '\n'
            continue
    print(result)
    # Push
    if push_plus_token:
        headers = {'Content-Type': 'application/json'}
        data = {
            'token': push_plus_token,
            'title': '西南交大健康填报',
            'content': result
        }
        requests.post(url='http://www.pushplus.plus/send', headers=headers, data=json.dumps(data))

if __name__ == '__main__':
    main()

def main_handler(event, context):
    main()
