import json
import requests


class LinodeApi():
    def __init__(self, token):
        self.curl = requests.session()
        self.access_token = token
        self.curl.headers = {
            'content-type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

    # 创建 linode 实例
    def create_instance(self, region, vm_size, image_id, password, name=''):
        url = 'https://api.linode.com/v4/linode/instances'
        data = {
            'image': image_id,
            'type': vm_size,
            'label': name,
            'region': region,
            "root_pass": password,
            "backups_enabled": False,
        }
        if not self.report_post(url, data):
            return False
        print(self.result)
        return True

    # 电源操作
    def power_action(self, instance_id, action):
        try:
            url = f'https://api.linode.com/v4/linode/instances/{instance_id}/{action}'
            if not self.report_post(url, data={}):
                return False
            if self.result.get('errors'):
                return False
            return True
        except:
            return False

    # 删除实例
    def delete_instance(self, linode_id):
        try:
            url = f'https://api.linode.com/v4/linode/instances/{linode_id}'
            result = self.curl.delete(url)
            if result.json().get('errors'):
                return False
            return True
        except:
            return False

    def get_token(self):
        url = 'https://api.linode.com/v4/linode/instances'
        data = {
            'class': 'standard',
        }
        ret = self.curl.get(url)
        print(ret.text)

    # 获取实例列表
    def get_instances(self):
        self.instances = []
        try:
            url = 'https://api.linode.com/v4/linode/instances'
            if not self.report_get(url): return False
            for instance in self.result['data']:
                # print(instance)
                try:
                    ipv4 = instance['ipv4'][0]
                except:
                    ipv4 = ''
                _instance = {
                    'instance_id': instance['id'],
                    'label': instance['label'],
                    'status': instance['status'],
                    'create_time': instance['created'],
                    'type': instance['type'],
                    'ipv4': ipv4,
                    'ipv6': instance['ipv6'],
                    'image': instance['image'],
                    'region': instance['region']
                }
                self.instances.append(_instance)
            return True
        except:
            return False

    def get_types(self):
        url = 'https://api.linode.com/v4/linode/types'

        self.report_get(url)

        types = []
        for _type in self.result['data']:
            _id = _type['id']
            vcpus = _type['vcpus']
            price = int(_type['price']['monthly'])
            memory = int(_type['memory'] / 1024)
            disk = int(_type['disk'] / 1024)
            # transfer = _type['transfer'] / 1024
            label = f'{vcpus}vCPUs, {memory}GB RAM, {disk}GB DISK, ${price}'
            types.append({_id: label})
        return

    # 获取账户信息
    def get_account(self):
        try:
            url = 'https://api.linode.com/v4/account'
            return self.report_get(url)
        except:
            return False

    def get_regions(self):
        url = 'https://api.linode.com/v4/regions'
        self.report_get(url)

        for _i in self.ret['data']:
            _id = _i['id']
            label = _i['label']
            print(_id, label)
            #print(f"('{_id}', '{label}'),")


    def get_images(self):
        url = 'https://api.linode.com/v4/images'
        self.report_get(url)

        print(self.ret)

        for _i in self.ret['data']:
            #print(_i)
            _id = _i['id']
            label = _i['label']
            print(f"('{_id}', '{label}'),")

    def get_bill(self):
        url = 'https://api.linode.com/v4/account'
        self.report_get(url)
        print(self.ret)

    # 统一发送请求
    def report_get(self, url):
        try:
            ret = self.curl.get(url)
            print(ret.text)
            self.result =ret.json()
            # print(self.result)
            self.ret =ret.json()
            return True
        except:
            return False

    # 统一发送请求
    def report_post(self, url, data):
        try:
            ret = self.curl.post(url, data=json.dumps(data))
            # print(ret.text)
            self.result = ret.json()
            return True
        except:
            return False

    # g6-nanode-1

if __name__ == '__main__':
    pass
    # lApi = LinodeApi()
    # lApi.get_images()