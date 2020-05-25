import requests

class Login():
    def __init__(self):
        self.data={}
        self.data['appid'] = 'wxff3f8e88fb2c6acf'
        self.data['secret'] = 'd1f8785c5aa54bd97be0c79cdea2a0c9'
        self.data['grant_type'] = 'authorization_code'
    def sent_out(self):
        res = requests.get('https://api.weixin.qq.com/sns/jscode2session', self.data)
        return eval(res.text)
    def set(self,inf):
        self.data['js_code']=inf
