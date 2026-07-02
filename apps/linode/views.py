from django.http.response import JsonResponse
from django.db.models import Q
from django.views import View

from . import models

from apps.users.views import Pagination
from libs.utils import DateTimeToStr

from libs.linode import LinodeApi

import json

class LinodeAccountView(View):
    def get(self, request):
        q = Q()
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(email__icontains=wd)  |  Q(token__icontains=wd)|  Q(name__icontains=wd)|  Q(note__icontains=wd), Q.AND)

        data_list = models.Account.objects.filter(q).order_by('-id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        _data_list = []
        for data in data_list[start:end]:
            # data.update_instances()
            _data = {
                'id': data.id,
                'name': data.name,
                'euuid': data.euuid,
                'email': data.email,
                'password': data.password,
                'token': data.token,
                'status': data.status,
                'balance': data.balance,
                'count': data.get_vm_count(),
                'note': data.note,
                'active_promotions': data.get_active_promotions(),
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time)
            }
            _data_list.append(_data)
        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'image_list': models.Vm.images_choices,
                'location_list': models.Vm.regions_choices,
                'vm_types': models.Vm.type_choices,
                'items': _data_list
            }
        })

    def post(self, request):
        token = request.POST.get('token', '').strip()
        name = request.POST.get('name', '').strip()
        note = request.POST.get('note', '').strip()


        if models.Account.objects.filter(token=token).first():
            return JsonResponse({'code': 20001, 'message': f'该 Token 已存在, 无法重复添加'})

        linodeApi = LinodeApi(token)
        if not linodeApi.get_account():
            return JsonResponse({'code': 20001, 'message': f'无效 token, 无法添加'})
        try:
            _data = {
                'token': token,
                'name': name,
                'note': note,
                'email': linodeApi.result['email'],
                'balance': linodeApi.result['balance'],
                'euuid': linodeApi.result['euuid'],
                'active_promotions': json.dumps(linodeApi.result['active_promotions']),
                'status': True,
            }
            if account_info := models.Account.objects.create(**_data):
                account_info.update_instances()
                return JsonResponse({'code': 20000, 'message': '账号添加成功'})
            return JsonResponse({'code': 20001, 'message': '操作失败'})
        except BaseException as e:
            return JsonResponse({'code': 20001, 'message': f'操作失败: {e}'})

# 删除 Azure 账号
class LinodeAccountDeleteView(View):
    def post(self, request):
        account_id = request.POST.get('account_id')
        account_info = models.Account.objects.filter(id=account_id).first()
        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': '账号不存在'
            })

        if account_info.delete():
            return JsonResponse({
                'code': 20000,
                'message': '删除成功'
            })
        return JsonResponse({
            'code': 20001,
            'message': '删除失败'
        })

# Azure Vm 实例列表
class LinodeVmListView(View):
    def get(self, request):
        q = Q()
        # 搜索
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(instance_id__icontains=wd) | Q(ipv4__icontains=wd)| Q(label__icontains=wd)| Q(password__icontains=wd) , Q.AND)

        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(account__name__icontains=wd) | Q(account__email__icontains=wd)| Q(account__token__icontains=wd), Q.AND)

        _data_list = []
        data_list = models.Vm.objects.filter(q).order_by('-create_time', 'id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        for data in data_list[start:end]:
            _data = {
                'id': data.id,
                'name': data.label,
                'ipv4': data.ipv4,
                'ipv6': data.ipv6,
                'instance_id': data.instance_id,
                'password': data.password,
                'type': data.get_type(),
                'image': data.get_image_display(),
                'region': data.get_region_display(),
                'status_text': data.get_status_display(),
                'status': data.status,
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time),
                'account': data.account.email,
                'account_name': data.account.name
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

# Linux Vm 操作
class LinodeVmActionView(View):
    def post(self, request):
        vm_id = request.POST.get('vm_id')
        action = request.POST.get('action', '')

        if action in '':
            return JsonResponse({
                'code': 20001,
                'message': '操作无效'
            })

        vm_info = models.Vm.objects.filter(instance_id=vm_id).first()
        if not vm_info:
            return JsonResponse({
                'code': 20001,
                'message': 'VM不存在, 请核实后操作'
            })

        action_map = {
            'boot': '开机',
            'shutdown': '关机',
            'reboot': '重启',
            'delete': '删除',
            'update': '更新',
        }

        if action in ['boot', 'shutdown', 'reboot']:
            # 电源操作
            if vm_info.vm_power_action(action):
                vm_info.account.update_instances()
                return JsonResponse({
                    'code': 20000,
                    'message': f'{vm_info.instance_id} {action_map.get(action, action)} 操作成功, 状态需要更新之后才会显示'
                })
            return JsonResponse({
                'code': 20001,
                'message': '操作失败'
            })

        if action in 'delete':
            status = vm_info.delete_linode()
            return JsonResponse({
                'code': 20000 if status else 20001,
                'message': '实例删除成功' if status else '实例删除失败'
            })

        if action in 'update':
            vm_info.account.update_instances()
            return JsonResponse({
                'code': 20000,
                'message': '更新操作成功'
            })

        if action in ['resetip']:
            if vm_info.reset_ip():
                return JsonResponse({
                    'code': 20000,
                    'message': f'更换IP操作已完成, 新IP需要几分钟才能显示。'
                })
            return JsonResponse({
                'code': 20001,
                'message': '更换IP失败'
            })

# 创建 Linode Vm 实例
class LinodeVmCreateView(View):
    def post(self, request):
        account_id = request.POST.get('account_id')
        password = request.POST.get('password', '')
        image_id = request.POST.get('image_id', '')
        vm_size = request.POST.get('type', '')
        region = request.POST.get('region', '')
        name = request.POST.get('name')
        account_info = models.Account.objects.filter(id=account_id).first()
        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': '创建失败, 账号不存在!'
            })

        if models.Vm.objects.filter(account_id=account_info.id, label=name).first():
            return JsonResponse({
                'code': 20001,
                'message': '创建失败, 实例名称不可重复!'
            })

        if '' in [region, vm_size, image_id, password]:
            return JsonResponse({
                'code': 20001,
                'message': '创建失败, 异常操作!'
            })
        message, status = account_info.create_vm(region=region, vm_size=vm_size, password=password, name=name, image_id=image_id)
        if status:
            return JsonResponse({
                'code': 20000,
                'message': '创建成功, 请返回实例列表查看!'
            })
        return JsonResponse({
            'code': 20001,
            'message': f'创建失败, {message}!'
        })