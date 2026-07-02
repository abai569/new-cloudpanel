from django.http.response import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from django.views import View
from django.forms.models import model_to_dict

import json, datetime, logging

logger = logging.getLogger(__name__)

from apps.aws import models, tasks, forms
from apps.users.models import CommonLogs

from libs.utils import DateTimeToStr, Pagination
from libs.aws import lightsail_action, ec2_action, aga_action, _create_aga, AwsApi, get_regions, get_service_quota, EC2_TYPES

class GetLightsailInstancesView(View):
    # 获取轻量实例信息
    def get(self, request):
        q = Q(account__users_id=request.user.id)
        # 搜索
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(name__icontains=wd) | Q(os_name__icontains=wd) | Q(public_ip__icontains=wd) | Q(
                location__icontains=wd), Q.AND)

        if request.GET.get('server_id', False):
            server_id = request.GET.get('server_id')
            q.add(Q(id=server_id), Q.AND)


        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(account__name__icontains=wd) | Q(account__email__icontains=wd), Q.AND)


        if request.GET.get('username'):
            wd = request.GET.get('username', '').strip()
            q.add(Q(users__username__icontains=wd), Q.AND)


        _data_list = []
        data_list = models.Lightsail.objects.filter(q).order_by('-create_time', 'id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        for data in data_list[start:end]:
            _data = {
                'id': data.id,
                'name': data.name,
                'os_name': data.os_id,
                'price': data.price,
                'public_ip': data.public_ip,
                'status': data.status,
                'status_text': data.get_status_display(),
                'region': data.get_region_name(),
                'account': f'{data.account.name}({data.account.value}v)',
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time),
                'expire_time': DateTimeToStr(data.expire_time),
            }
            _data_list.append(_data)

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'items': _data_list
            }
        })

class LightsailInstanceActionView(View):
    # 轻量实例操作类
    def post(self, request):
        q = Q(account__users_id=request.user.id)
        action = request.POST.get('action', '')
        server_id = request.POST.get('server_id')
        q.add(Q(id=server_id), Q.AND)
        ret = models.Lightsail.objects.filter(q).first()
        # 判断实例是否存在
        if not ret: return JsonResponse({'code': 20001, 'message': '实例不存在'})


        status, req = lightsail_action(action, ret)
        if action in 'delete': ret.delete()
        if not status: return JsonResponse({'code': 20001, 'message': req})

        if action in 'reset_ip':
            ret_status = ret.reset_ip()
            return JsonResponse({'code': 20000 if ret_status else 20001, 'message': 'IP更换成功' if ret_status else 'IP更换失败'})

        if action not in ['update', 'reset_ip']: return JsonResponse({'code': 20000, 'message': '操作成功'})
        _i = req['instance']
        del _i['hardware']['disks']
        _data = {
            'name': _i['name'],
            'location': json.dumps(_i['location']),
            'hardware': json.dumps(_i['hardware']),
            'os_name': _i['blueprintName'],
            'os_id': _i['blueprintId'],
            'public_ip': _i.get('publicIpAddress', ''),
            'bundle_id': _i['bundleId'],
            'status': _i['state']['name'],
            'private_ip': _i['privateIpAddress'],
            'support_code': _i['supportCode'],
            'create_time': _i['createdAt'].strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': datetime.datetime.now(),
        }
        if models.Lightsail.objects.filter(q).update(**_data): return JsonResponse({'code': 20000, 'message': '操作成功'})
        return JsonResponse({'code': 20001, 'message': '操作失败'})

class LightsailGetRegionView(View):
    # lightsail 对应的 地区列表
    def get(self, request):

        account_id = request.GET.get('account_id', False)
        data_info = models.Account.objects.filter(id=account_id).first()

        if not data_info: return JsonResponse({'code': 20001, 'message': '账号不存在'})

        _data_list = []
        token = 'lightsail_region1'
        try:
            aApi = AwsApi(key_id=data_info.key_id, key_secret=data_info.secret)
            aApi.start('lightsail')
            logger.debug("LightsailGetRegionView cache miss, fetching from API")
            ret = cache.get(token, False)
            if ret in [None, False]:
                ret = aApi.client.get_regions(includeAvailabilityZones=True)
                logger.debug(f"LightsailGetRegionView: fetched regions, count={len(ret.get('regions', []))}")
                cache.set(token, ret, 60 * 60 * 24)
            for region in ret['regions']:
                _data = {
                    'region': region['name'],
                    'name': get_regions(region['name'])
                }
                _data_list.append(_data)
        except Exception as e:
            logger.error(f"LightsailGetRegionView error: {e}")
            return JsonResponse({
                'code': 20001,
                'message': '获取地区列表失败',
                'data': {
                    'items': _data_list
                }
            })

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'items': _data_list
            }
        })

class LightsailGetImagesView(View):
    # 轻量 对应的 镜像列表和规格
    def get(self, request):
        region = request.GET.get('region', '')
        account_id = request.GET.get('account_id', False)
        account_info = models.Account.objects.filter(id=account_id).first()

        if not account_info: return JsonResponse({'code': 20001, 'message': '账号不存在'})

        aApi = AwsApi(key_id=account_info.key_id, key_secret=account_info.secret)
        aApi.region = region
        aApi.start('lightsail')

        if not aApi.lightsail_get_bundles(): return JsonResponse({'code': 20001, 'message': '获取规格失败'})

        bundles = aApi.bundle

        get_blueprints = aApi.client.get_blueprints(
            includeInactive = True
        )
        blueprints = []
        for blueprint in get_blueprints['blueprints']:
            if blueprint['type'] == 'app' or blueprint['platform'] == 'WINDOWS': continue

            name = blueprint['blueprintId']
            if name.startswith('amazon_linux') or name.startswith('free'): continue
            blueprints.append(blueprint['blueprintId'])


        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'bundles': bundles,
                'blueprints': blueprints,
            }
        })

class LightsailCreateInstanceView(View):
    # 创建 Lightsail
    def post(self, request):
        password = request.POST.get('password', 'panel778899==')
        name = request.POST.get('name', '')
        images_id = request.POST.get('images_id', False)
        region = request.POST.get('region', False)
        bundle = request.POST.get('bundle', '')

        account_id = request.POST.get('account_id', False)
        account_info = models.Account.objects.filter(id=account_id).first()

        if not account_info: return JsonResponse({'code': 20001, 'message': '账号不存在'})

        user_data = ''
        # if account_info.create_ls(region, name, images_id, bundle, password, user_data):
        #
        #     return JsonResponse({'code': 20000, 'message': '创建成功，请刷新列表后查看'})
        # return JsonResponse({'code': 20001, 'message': '创建实例失败'})

        aApi = AwsApi(key_id=account_info.key_id, key_secret=account_info.secret)
        aApi.region = region
        aApi.start('lightsail')
        aApi.user_data = aApi.user_data.replace('admin77889900==', password)
        if not aApi.create_lightsail_instances(name, bundleId=bundle, blueprintId=images_id):
            return JsonResponse({'code': 20001, 'message': '创建实例失败'})

        _i = aApi.instance
        _data = {
            'users_id': request.user.id,
            'account_id': account_info.id,
            'name': name,
            'password': password,
            'private_ip': _i['privateIpAddress'],
            'bundle_id': _i['bundleId'],
            'location': json.dumps(_i['location']),
            'public_ip': _i.get('publicIpAddress', ''),
            'create_time': _i['createdAt'].strftime("%Y-%m-%d %H:%M:%S"),
            'expire_time': datetime.datetime.now(),
            'update_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        models.Lightsail.objects.create(**_data)
        return JsonResponse({'code': 20000, 'message': '创建成功，请刷新列表后查看'})

class GetEc2InstancesView(View):
    # 获取 Ec2 实例信息
    def get(self, request):
        q = Q(account__users_id=request.user.id)
        # 搜索
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(name__icontains=wd) | Q(instance_id__icontains=wd) | Q(public_ip__icontains=wd) | Q(
                region__icontains=wd) | Q(
                image_id=wd) , Q.AND)


        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(account__name__icontains=wd) | Q(account__email__icontains=wd), Q.AND)


        if request.GET.get('username'):
            wd = request.GET.get('username', '').strip()
            q.add(Q(users__username__icontains=wd), Q.AND)

        _data_list = []
        data_list = models.Ec2.objects.filter(q).exclude(status='terminated').order_by('-create_time', 'id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        for data in data_list[start:end]:
            _data = {
                'id': data.id,
                'name': data.name,
                'instance_id': data.instance_id,
                'price': data.price,
                'public_ip': data.public_ip,
                'status': data.status,
                'instance_type': data.instance_type,
                'is_aga': data.account.aga,
                'image_name': models.Ec2Images.get_images_name(data.image_id),
                'status_text': data.get_status_display(),
                'region': data.get_region_name(),
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time),
                'expire_time': DateTimeToStr(data.expire_time),
                'account': f'{data.account.name}({data.account.value}v)',
                'username': data.get_username(),
            }
            _data_list.append(_data)

        account_data_list = models.Account.objects.filter(status=True, ec2=True).order_by('-id')
        _account_data_list = []
        for data in account_data_list:
            _data = {
                'id': data.id,
                'name': f'{data.name}({data.get_ec2_count()}/{data.value}v)'
            }
            _account_data_list.append(_data)

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'account_list': _account_data_list,
                'items': _data_list,
                'ec2_types': EC2_TYPES,
                'username': request.user.username
            }
        })

class Ec2InstanceActionView(View):
    # Ec2实例操作类
    def post(self, request):
        try:
            # q = request.user_q
            q = Q(account__users_id=request.user.id)
            action = request.POST.get('action', '')
            server_id = request.POST.get('server_id')
            q.add(Q(id=server_id), Q.AND)
            ret = models.Ec2.objects.filter(q).first()
            # 判断实例是否存在
            if not ret: return JsonResponse({'code': 20001, 'message': 'Ec2实例不存在'})

            # 操作 aga
            if action == 'create_aga':
                ret_aga = _create_aga(ret)
                if ret_aga:
                    ip = []
                    try:
                        _data = {
                            'account_id': ret.account.id,
                            'instance_id': ret.id,
                            'arn': ret_aga['AcceleratorArn'],
                            'name': ret_aga['Name'],
                            'note': ret.name,
                            'dns_name': ret_aga['DnsName'],
                            'status': ret_aga['Status'],
                            'enabled': ret_aga['Enabled'],
                            'ip_address': ','.join(ret_aga['IpSets'][0]['IpAddresses']),
                            'create_time': datetime.datetime.now(),
                            'update_time': datetime.datetime.now()
                        }
                        models.GlobalAccelerator.objects.create(**_data)
                        ip = ret_aga['IpSets'][0]['IpAddresses']
                    except Exception as e:
                        logger.error(f"Ec2InstanceActionView create_aga error: {e}")
                    return JsonResponse({'code': 20000, 'message': '创建成功, 等待几分钟到全球加速器列表查看！', 'ip': ip})

                return JsonResponse({'code': 20001, 'message': '创建失败, 请联系管理员！'})

            status, req = ec2_action(action, ret)
            if not status: return JsonResponse({'code': 20001, 'message': req})

            if action not in ['update', 'reset_ip']:
                # .update_ec2.delay(ret.region)
                tasks.aws_update_ec2.delay(ret.account.id, ret.region)
                return JsonResponse({'code': 20000, 'message': '操作成功'})
            _instance = req
            _data = {
                # 'name': name,
                'image_id': _instance['ImageId'],
                'instance_id': _instance['InstanceId'],
                'instance_type': _instance['InstanceType'],
                'create_time': (_instance['LaunchTime'] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                'status': _instance['State']['Name'],
                'public_ip': _instance.get('PublicIpAddress', ''),
                'private_ip': _instance.get('PrivateIpAddress', ''),
                'update_time': datetime.datetime.now()
            }

            for _tag in _instance.get('Tags', []):
                if _tag.get('Key', '') not in 'Name': continue
                name = _tag.get('Value', '-')
                _data.update({'name': name})

            if models.Ec2.objects.filter(q).update(**_data): return JsonResponse({'code': 20000, 'message': '操作成功'})
            return JsonResponse({'code': 20001, 'message': '操作失败'})
        except Exception as e:
            logger.error(f"Ec2InstanceActionView error: {e}")
            return JsonResponse({'code': 20001, 'message': '操作失败', 'error': str(e)})

class GetAGAInstancesView(View):
    # 获取 AGA 实例信息
    def get(self, request):
        q = Q(account__users_id=request.user.id)
        # 搜索
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(name__icontains=wd) | Q(ip_address__icontains=wd) | Q(dns_name__icontains=wd) | Q(
                note__icontains=wd, instance__public_ip=wd, instance__name=wd), Q.AND)

        _data_list = []
        data_list = models.GlobalAccelerator.objects.filter(q).order_by('-create_time', '-id')
        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)
        for data in data_list[start:end]:

            _data = {
                'id': data.id,
                'name': data.name,
                'ip_address': data.ip_address.split(','),
                'enabled': data.enabled,
                'status': data.status,
                'status_text': data.get_status_display(),
                'dns_name': data.dns_name,
                'note': data.note,
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time)
            }
            if data.instance != None:
                _data.update({
                    'region': data.instance.get_region_name(),
                    'ec2_ip': data.instance.public_ip
                })
            _data_list.append(_data)

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'items': _data_list
            }
        })

class AgaInstanceActionView(View):
    # AGA实例操作类
    def post(self, request):
        now_time = datetime.datetime.now()

        q = Q(account__users_id=request.user.id)
        action = request.POST.get('action', '')
        server_id = request.POST.get('server_id')
        q.add(Q(id=server_id), Q.AND)
        ret = models.GlobalAccelerator.objects.filter(q).first()

        # 判断实例是否存在
        if not ret: return JsonResponse({'code': 20001, 'message': '全球加速实例不存在'})

        # 判断 action 是否正常
        if action not in ['update', 'delete', 'create_hk', 'create_jp']: return JsonResponse({'code': 20001, 'message': '无效操作'})

        status, req = aga_action(action, ret)

        if not status: return JsonResponse({'code': 20001, 'message': req})

        if action in ['create_hk', 'create_jp', 'delete']:
            return JsonResponse({'code': 20000, 'message': req})

        for instance in req:
            instance.update({
                'account_id': ret.account.id
            })
            if models.GlobalAccelerator.objects.filter(arn=instance['arn']).first():
                # 更新
                instance.update({
                    'update_time': datetime.datetime.now()
                })
                models.GlobalAccelerator.objects.filter(arn=instance['arn']).update(**instance)
                continue

            models.GlobalAccelerator.objects.create(**instance)
            continue
        models.GlobalAccelerator.objects.filter(update_time__lt=now_time, account_id=ret.account.id).delete()
        return JsonResponse({'code': 20000, 'message': '操作成功'})

class Ec2GetAccountView(View):
    # EC2
    def get(self, request):
        data_list = models.Account.objects.filter(status=True,).order_by('-id')
        _data_list = []
        for data in data_list:
            _data = {
                'id': data.id,
                'name': f'{data.name}({data.value}v)',
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time)
            }
            _data_list.append(_data)
        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'items': _data_list
            }
        })

class Ec2GetRegionView(View):
    # EC2 对应的 地区列表
    def get(self, request):

        account_id = request.GET.get('account_id', False)
        data_info = models.Account.objects.filter(id=account_id).first()

        if not data_info: return JsonResponse({'code': 20001, 'message': '账号不存在'})

        _data_list = []

        token = f'{data_info.id}-regions'

        try:
            regions = cache.get(token, False)
            if not regions:
                aApi = AwsApi(key_id=data_info.key_id, key_secret=data_info.secret)
                aApi.start('ec2')
                ret = aApi.client.describe_regions(AllRegions=False)
                regions = ret['Regions']
                cache.set(token, regions, 60 * 10)

            for region in regions:
                _data = {
                    'region': region['RegionName'],
                    'name': get_regions(region['RegionName'])
                }
                _data_list.append(_data)
        except Exception as e:
            logger.error(f"Ec2GetRegionView error: {e}")
            return JsonResponse({
                'code': 20001,
                'message': '获取地区列表失败',
                'data': {
                    'items': _data_list
                }
            })

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'items': _data_list
            }
        })

class Ec2GetImagesView(View):
    # EC2 对应的 镜像列表
    def get(self, request):
        region = request.GET.get('region', '')
        data_list = models.Ec2Images.objects.filter(region=region)
        _data_list = []
        for data in data_list:
            _data = {
                'id': data.id,
                'name': data.name,
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time)
            }
            _data_list.append(_data)
        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'items': _data_list
            }
        })

class Ec2CreateInstanceView(View):
    # 创建 EC2
    def post(self, request):
        inputData = forms.AddEc2Form(request.POST)
        if inputData.is_valid():

            data = inputData.clean()
            account_info = data.get('account_id')

            InstanceType = data.get('ec2_type', '')
            name = data.get('name', '')
            password = data.get('password', '')
            ec2_disk = data.get('ec2_disk', 10)
            ec2_count = data.get('ec2_count', 1)
            region = data.get('region')
            images_info = data.get('images_id')
            script_info = data.get('script_id', False)

            if InstanceType == '':
                InstanceType = 't2.micro'
                if region in ['ap-east-1', 'eu-north-1', 'af-south-1', 'eu-south-1', 'me-south-1']: InstanceType = 't3.micro'

            DeviceName = 'sda1' if 'Debian' not in images_info.name else 'xvda'

            if script_info:
                user_data = script_info.content
            else:
                user_data = ''

            status, result = account_info.create_ec2(region, InstanceType, name, ec2_disk, DeviceName, ec2_count, password, user_data, images_info.ami)
            if status:
                tasks.aws_update_ec2(account_info.id, region)
                return JsonResponse({'code': 20000, 'message': '创建成功'})
            return JsonResponse({'code': 20001, 'message': result})
        return JsonResponse({'code': 20001, 'message': '操作失败', 'error_data': inputData.errors})


class AwsAccountView(View):
    def get(self, request):
        q = Q()

        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(name__icontains=wd) | Q(email__icontains=wd), Q.AND)

        if request.GET.get('username'):
            wd = request.GET.get('username', '').strip()
            q.add(Q(users__username__icontains=wd), Q.AND)

        if request.GET.get('status'):
            wd = request.GET.get('status')
            q.add(Q(status=wd), Q.AND)

        if request.GET.get('value'):
            value = request.GET.get('value')
            q.add(Q(value=value), Q.AND)

        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(name__icontains=wd) | Q(email__icontains=wd) |  Q(card__icontains=wd), Q.AND)

        data_list = models.Account.objects.filter(q).order_by('-id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        _data_list = []
        for data in data_list[start:end]:
            _secret = data.secret
            masked_secret = _secret[:4] + '****' + _secret[-4:] if _secret and len(_secret) > 8 else '****'
            _data = {
                'id': data.id,
                'name': data.name,
                'email': data.email,
                'password': '****',
                'key_id': data.key_id,
                'secret': masked_secret,
                'status': data.status,
                'value': f'{data.get_ec2_count()} / {data.value}' ,
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time)
            }
            _data_list.append(_data)
        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'items': _data_list
            }
        })

    def post(self, request):
        inputData = forms.AccountForm(request.POST)
        if inputData.is_valid():
            data = inputData.clean()
            dataInfo = data.get('id', False)
            email = data.get('email', '')
            _data = {
                'name': data.get('name', ''),
                'email': data.get('email', ''),
                'password': data.get('password', ''),
                'key_id': data.get('key'),
                'note': data.get('note', ''),
                'auto_boot': data.get('auto_boot', False),
                'users_id': request.user.id,
                'secret': data.get('secret')
            }
            if not dataInfo:

                # 添加账号
                if models.Account.objects.filter(key_id=data.get('key'), secret=data.get('secret')).first():
                    return JsonResponse({'code': 20001, 'message': f'账号添加失败, 该KEY已存在。'})

                # 检测异常账号数量
                error_count = models.Account.objects.filter(users_id=request.user.id, value=0, status=False).count()
                if error_count >=3 and not request.user.is_superuser:
                    return JsonResponse({'code': 20001, 'message': f'添加失败, 防止资源浪费, 请及时删除异常账户, 当前异常账户 {error_count} 个'})

                # 测试账号是否正常
                value = get_service_quota(data.get('key'), data.get('secret'))
                if type(value) == bool:
                    return JsonResponse({'code': 20001, 'message': f'账号添加失败, 只能添加有效的账号'})

                _data.update({
                    # 'status': 1,
                    'ec2': 1,
                    'aga': 1,
                    'ip': data.get('ip', ''),
                    'card': data.get('card', ''),
                    'value': value
                })

                ret = models.Account.objects.create(**_data)
                if ret:
                    tasks.update_aws.delay(ret.id)
                    return JsonResponse({'code': 20000, 'message': f'{email} 账号添加成功', 'data': {'id': ret.id}})
                return JsonResponse({'code': 20002, 'message': f'{email} 账号添加失败'})
            if models.Account.objects.filter(id=dataInfo.id).update(**_data):
                return JsonResponse({'code': 20000, 'message': f'{email} 账号添加成功'})

            return JsonResponse({'code': 20000, 'message': f'账号更新失败'})
        return JsonResponse({'code': 20001, 'message': '操作失败', 'error_data': inputData.errors})

# 删除账号
class AwsAccountDeleteView(View):
    def post(self, request):
        account_id = request.POST.get('account_id')
        account_info = models.Account.objects.filter(id=account_id)
        if not account_info.first():
            return JsonResponse({
                'code': 20001,
                'message': '账号不存在, 无法操作'
            })
        email = account_info.first().email

        if account_info.delete():
            return JsonResponse({
                'code': 20000,
                'message': f'{email} 删除成功'
            })
        return JsonResponse({
            'code': 20000,
            'message': f'{email} 删除失败'
        })

class AwsAccountGetQuotaView(View):

    def get(self, request):
        account_id = request.GET.get('account_id')

        account_info = models.Account.objects.filter(id=account_id).first()
        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': f'账号不存在',
            })
        ret = account_info._get_service_quota()
        return JsonResponse({
            'code': 20000,
            'message': f'操作完成',
            'data': {
                'items': ret
            }
        })

# aws 更新实例
class AwsAccountUpdateView(View):

    def get(self, request):
        account_id = request.GET.get('account_id')
        account_info = models.Account.objects.filter(id=account_id).first()
        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': f'账号不存在',
            })
        tasks.update_aws(account_info.id)
        return JsonResponse({
            'code': 20000,
            'message': f'已提交至后台操作'
        })
