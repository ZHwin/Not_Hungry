#修改112—114为你自己的青龙
#续期会记录并且上传IP跟CK 防内鬼
# -*- coding:utf-8 -*-
"""
cron: 15 0 * * *
new Env('饿了么续期');
"""

import requests
import json

class Qleopn:
    def __init__(self, q_url, c_id, c_secret):
        self.q_url = q_url
        self.c_id = c_id
        self.c_secret = c_secret
        self.token = None
        self.headers = None
        self.ck = None
        self.success_count = 0
        self.failure_count = 0

    def get_token(self):
        """获取token"""
        try:
            url = f'{self.q_url}open/auth/token?client_id={self.c_id}&client_secret={self.c_secret}'
            r = requests.get(url)
            if r.status_code == 200 and r.json()['code'] == 200:
                self.token = r.json()['data']['token']
                self.headers = {
                    "Authorization": f"Bearer {self.token}",
                    "accept": "application/json",
                    "Content-Type": "application/json",
                }
                print(f"获取token成功: {self.token}")
            else:
                print(f"获取token失败，响应代码: {r.status_code}, 响应内容: {r.text}")
        except requests.exceptions.RequestException as e:
            print(f"获取token异常: {e}")

    def get_allenvs_and_update_ck(self):
        """获取elmck变量并刷新cookie"""
        try:
            url = f'{self.q_url}open/envs'
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200 and r.json()['code'] == 200:
                data = r.json()['data']
                for i in data:
                    if i['name'] == 'elmck':  # 刷新elmck变量
                        self.ck = i['value']
                        # 过滤掉 'chushi=undefined;' 和 'chushi;'
                        self.ck = self.ck.replace('chushi=undefined;', '').replace('chushi;', '').strip()
                        qlid = i['id']  
                        remarks = i.get('remarks', '') 
                        self.renew_ck_and_update_env(qlid, remarks)
            else:
                print(f"获取环境变量失败，响应代码: {r.status_code}, 响应内容: {r.text}")
        except requests.exceptions.RequestException as e:
            print(f"获取环境变量异常: {e}")

    def renew_ck_and_update_env(self, qlid, remarks):
        """通过API调用进行CK续期，并将结果更新到elm变量中"""
        try:
            url = 'http://elmxqq.p1.hpnu.cn/elmxq'
            request_body = {
                'cookie': self.ck
            }
            response = requests.post(url, json=request_body)
            if response.status_code == 200 and "刷新成功" in response.text:
                response_json = response.json()
                new_cookie = response_json.get("cookie")
                expiration_time = response_json.get("expirationTime")

                if new_cookie:
                    self.update_env(new_cookie, qlid, remarks)
                    print(f"cookie刷新成功，新cookie: {new_cookie}, 有效期至: {expiration_time}")
                    self.success_count += 1
                else:
                    print(f"刷新成功，但未返回新的cookie信息: {response.text}")
                    self.failure_count += 1
            else:
                print(f"刷新失败: {response.text}")
                self.failure_count += 1
        except Exception as e:
            print(f"刷新时发生异常: {e}")
            self.failure_count += 1

    def update_env(self, new_cookie, qlid, remarks):
        """更新elmck的值为新的cookie"""
        try:
            url = f'{self.q_url}open/envs'
            data = {
                "value": new_cookie,
                "name": 'elmck',
                "remarks": remarks,
                "id": qlid
            }
            response = requests.put(url, headers=self.headers, data=json.dumps(data))
            if response.status_code == 200:
                print("环境变量更新成功")
            else:
                print(f"更新环境变量失败，响应代码: {response.status_code}, 响应内容: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"更新环境变量时发生异常: {e}")

    def summarize(self):
        """输出总结信息"""
        print(f"\n====== 总结 ======\n")
        print(f"✅ 刷新成功的cookie数量：{self.success_count}")
        print(f"❌ 刷新失败的cookie数量：{self.failure_count}")

if __name__ == '__main__':
    ql_url = ''
    client_id = ''
    client_secret = ''
    
    run = Qleopn(ql_url, client_id, client_secret)
    run.get_token()
    run.get_allenvs_and_update_ck()
    run.summarize() 
