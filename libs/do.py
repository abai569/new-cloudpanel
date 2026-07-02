import requests

import datetime

class DoApi():
    def __init__(self, token):
        self.curl = requests.session()
        self.token = token
        self.user_data = ""
        self.api_url = 'https://api.digitalocean.com'
        self.curl.headers = {
            'Authorization': f'Bearer {token}',
            # 'Content-Type': 'application/json'
        }

    # 获取账号信息
    def get_account(self):
        try:
            url = f'{self.api_url}/v2/account'
            if not self.report_get(url):
                print('获取失败')
                return False
            self.account_info = self.result['account']
            return True
        except BaseException as e:
            print(e)
            return False

    # 获取余额
    def get_balance(self):
        try:
            url = f'{self.api_url}/v2/customers/my/balance'
            if not self.report_get(url):
                print('获取失败')
                return False
            print(self.result)
            self.balance_info = self.result
            return True
        except:
            return False

    # 获取实例列表
    def get_droplets(self, tag_name=''):
        url = f"{self.api_url}/v2/droplets?tag_name={tag_name}"
        if not self.report_get(url):
            print('获取失败')
            return False
        self.droplets = []
        # print(self.result['droplets'])
        for droplet in self.result['droplets']:
            # print(json.dumps(droplet))
            _data = {
                'droplet_id': droplet['id'],
                'name': droplet['name'],
                'memory': droplet['memory'],
                'vcpus': droplet['vcpus'],
                'disk': droplet['disk'],
                'status': droplet['status'],
                'create_time': datetime.datetime.strptime(droplet['created_at'], "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=8),
                'size_slug': droplet['size_slug'],
                'image_slug': droplet['image']['slug'],
                'region_slug': droplet['region']['slug'],
            }

            if droplet['image']['slug'] == None:
                _data['image_slug'] = ''

            for _ip in droplet['networks']['v4']:
                if _ip['type'] == 'public':
                    ip = _ip['ip_address']
                    break
                continue
            else:
                ip = ''
            _data.update({
                'ip': ip
            })
            self.droplets.append(_data)
            # self.delete_droplet(droplet['id'])
        return True

    # 创建实例
    def create_droplet(self, name='panel', password='admin7788==', count=1, region='sfo3', size='s-1vcpu-1gb', image='centos-7-x64'):
        try:
            url = f"{self.api_url}/v2/droplets"

            _data = {
                "names": [name] * int(count),
                # "name": name,
                # "user_data": USER_DATA.replace('admin7788==', password),
                "region": region,
                "size": size,
                "image": image,
                "ssh_keys": [],
                "ipv6": True,
                "tags": []
            }
            self.report_post(url, _data)
            print(self.result)
            if len(self.result['droplets']) >= 1: return '创建成功', True
            return '创建失败', False
        except BaseException as e:
            print(e)
            return f'创建失败: {e}', False

    # 获取密钥id
    def get_key_id(self):
        try:
            url = f"{self.api_url}/v2/account/keys"
            if not self.report_get(url):
                return False
            self.key_id = self.result['ssh_keys'][0]['id']
            return True
        except:
            return False

    def delete_droplet(self, droplet_id):
        try:
            url = f"{self.api_url}/v2/droplets/{droplet_id}"
            # print(url)
            ret = self.curl.delete(url, timeout=30)
            if ret.status_code == 204: return True
            return False
        except:
            return False

    @classmethod
    def get_images(cls):
        image_list = [
            'centos-7-x64',
            'centos-8-x64',
            'debian-9-x64',
            'debian-10-x64',
            'ubuntu-18-04-x64',
            'ubuntu-20-10-x64'
        ]
        return image_list

    def get_regions(self):
        try:
            url = f"{self.api_url}/v2/regions"
            if not self.report_get(url):
                print('获取失败')
                return False
            _data = []
            for region in self.result['regions']:
                _region = {
                    'name': region['name'],
                    'slug': region['slug'],
                    'sizes': region['sizes'],
                }
                _data.append(_region)
            self.regions = _data
            return True
        except:
            return False

    @classmethod
    def get_region_map(cls):
        data_list = [
            ('nyc1', '美国-纽约'),
            ('sfo3', '美国-旧金山'),
            ('ams3', '荷兰-阿姆斯特丹'),
            ('sgp1', '亚太-新加坡'),
            ('lon1', '英国-伦敦'),
            ('fra1', '德国-法兰克福'),
            ('tor1', '加拿大-多伦多'),
            ('blr1', '印度-班加罗尔')
        ]
        return data_list

    @classmethod
    def get_region_dist(cls):
        region_dist = {
            'nyc1': '美国-纽约',
            'sfo3': '美国-旧金山',
            'ams3': '荷兰-阿姆斯特丹',
            'sgp1': '亚太-新加坡',
            'lon1': '英国-伦敦',
            'fra1': '德国-法兰克福',
            'tor1': '加拿大-多伦多',
            'blr1': '印度-班加罗尔'
        }
        return region_dist

    @classmethod
    def get_price_map(cls):
        data_list = [
            ('s-1vcpu-1gb', '1H/1G/25G/1T-$5'),
            ('s-1vcpu-2gb', '1H/2G/50G/2T-$10'),
            ('s-2vcpu-2gb', '2H/2G/30G/3T-$15'),
            ('s-2vcpu-4gb', '2H/4G/80G/4T-$20'),
            ('s-4vcpu-8gb', '4H/8G/160G/5T-$40'),
            ## INTEL
            ('s-1vcpu-1gb-intel', '1H/1G/25G/1T-$6-intel'),
            ('s-1vcpu-2gb-intel', '1H/2G/50G/2T-$12-intel'),
            ('s-2vcpu-2gb-intel', '2H/2G/30G/3T-$18-intel'),
            ('s-2vcpu-4gb-intel', '2H/4G/80G/4T-$24-intel'),
            ('s-4vcpu-8gb-intel', '4H/8G/160G/5T-$48-intel'),
            ## AMD
            ('s-1vcpu-1gb-amd', '1H/1G/25G/1T-$6-amd'),
            ('s-1vcpu-2gb-amd', '1H/2G/50G/2T-$12-amd'),
            ('s-2vcpu-2gb-amd', '2H/2G/30G/3T-$18-amd'),
            ('s-2vcpu-4gb-amd', '2H/4G/80G/4T-$24-amd'),
            ('s-4vcpu-8gb-amd', '4H/8G/160G/5T-$48-amd'),
        ]
        return data_list

    # 统一get请求
    def report_get(self, url):
        try:
            ret = self.curl.get(url, headers=self.curl.headers)
            self.result = ret.json()
            return True
        except:
            return False

    # 统一get请求
    def report_post(self, url, data):
        try:
            ret = self.curl.post(url, data=data)
            self.result = ret.json()
            # print(ret.json())
            return True
        except BaseException as e:
            print(e)
            return False

    def test(self):
        url = f"{self.api_url}/v2/droplets?tag_name="
        ret = self.curl.get(url)
        print(ret.json())



if __name__ == '__main__':
    pass