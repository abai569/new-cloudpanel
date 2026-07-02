from django.shortcuts import render, HttpResponse
from django.http.response import JsonResponse
from django.db.models import Q
from django.views import View


from apps.do import models, tasks
from apps.users.views import Pagination
from libs.utils import DateTimeToStr
from libs.do import DoApi

class DoAccountView(View):
    def get(self, request):
        q = Q()

        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(token__icontains=wd) | Q(email__icontains=wd), Q.AND)

        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(token__icontains=wd) | Q(email__icontains=wd) |  Q(droplet_limit__icontains=wd), Q.AND)

        data_list = models.Account.objects.filter(q).order_by('-id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        _data_list = []
        for data in data_list[start:end]:
            _data = {
                'id': data.id,
                'token': data.token,
                'name': data.name,
                'email': data.email,
                'password': data.password,
                'uuid': data.uuid,
                'month_to_date_balance': data.month_to_date_balance.replace('-', ''),
                'status': data.status,
                'server_count': data.get_server_count(),
                'droplet_limit': data.droplet_limit,
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

    # 添加账号
    def post(self, request):
        token = request.POST.get('token', '').strip()
        name = request.POST.get('name', '').strip()

        if models.Account.objects.filter(token=token).first():
            return JsonResponse({'code': 20001, 'message': f'该 Token 已存在, 无法重复添加'})
        doApi = DoApi(token)
        if not doApi.get_account():
            return JsonResponse({'code': 20001, 'message': f'无效 token, 无法添加'})
        _data = {
            'token': token,
            'name': name,
            'email': doApi.account_info['email'],
            'uuid': doApi.account_info['uuid'],
            'status': doApi.account_info['status'],
            'droplet_limit': doApi.account_info['droplet_limit']
        }
        if models.Account.objects.create(**_data):
            return JsonResponse({'code': 20000, 'message': '账号添加成功'})
        return JsonResponse({'code': 20001, 'message': '操作失败'})

    def delete(self, request):
        account_id = request.GET.get('account_id')
        # print(account_id)
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

    def update(self, request):
        pass

        # if not status:

class DoAccountUpdateView(View):
    def get(self, request):
        account_id = request.GET.get('account_id')
        account_info = models.Account.objects.filter(id=account_id).first()

        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': '账号不存在, 无法操作'
            })
        message, status = account_info.update_account()
        account_info.update_droplets()
        return JsonResponse({
            'code': 20000 if status else 20001,
            'message': message
        })

class DoDropletsListView(View):
    def get(self, request):
        q = Q()
        # 搜索
        if request.GET.get('wd'):
            wd = request.GET.get('wd', '').strip()
            q.add(Q(name__icontains=wd) | Q(ip__icontains=wd), Q.AND)

        if request.GET.get('account_name'):
            wd = request.GET.get('account_name', '').strip()
            q.add(Q(account__token__icontains=wd) | Q(account__email__icontains=wd), Q.AND)

        if request.GET.get('username'):
            wd = request.GET.get('username', '').strip()
            q.add(Q(account__username__icontains=wd), Q.AND)

        _data_list = []
        data_list = models.Droplets.objects.filter(q).order_by('-create_time', 'id')

        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)
        data_count = data_list.count()
        start, end = Pagination(page, limit, data_count)

        for data in data_list[start:end]:
            _data = {
                'id': data.id,
                'name': data.name,
                'droplet_id': data.droplet_id,
                'ip': data.ip,
                'memory': data.memory,
                'vcpus': data.vcpus,
                'disk': data.disk,
                'status': data.status,
                'image_slug': data.image_slug,
                'region_slug': DoApi.get_region_dist().get(data.region_slug, data.region_slug),
                'create_time': DateTimeToStr(data.create_time),
                'update_time': DateTimeToStr(data.update_time),
                'account': data.account.email
            }
            _data_list.append(_data)


        account_list = list(models.Account.objects.filter().order_by('-id').values('id', 'name'))

        return JsonResponse({
            'code': 20000,
            'message': '获取成功',
            'data': {
                'total': data_count,
                'account_list': account_list,
                'image_list': DoApi.get_images(),
                'region_list': DoApi.get_region_map(),
                'price_list': DoApi.get_price_map(),
                'items': _data_list
            }
        })

    # 创建api
    def post(self, request):
        name = request.POST.get('name', '')
        account_id = request.POST.get('account_id', '')
        password = request.POST.get('password', '')
        image_id = request.POST.get('image_id', '')
        count = request.POST.get('count', 1)
        _type = request.POST.get('type', '')
        region = request.POST.get('region', '')
        if '' in [_type, region, image_id, account_id]:
            return JsonResponse({
                'code': 20001,
                'message': '参数错误'
            })
        # 判断账号是否存在
        account_info = models.Account.objects.filter(id=account_id).first()
        if not account_info:
            return JsonResponse({
                'code': 20001,
                'message': '账号不存在'
            })
        doApi = DoApi(account_info.token)
        message, status = doApi.create_droplet(name, password, image=image_id, region=region, size=_type, count=count)
        # message, status = 'sss', True
        if status:
            tasks.beat_update_do_account(account_info.id, account=False)
            # 创建成功之后需要更新api

        return JsonResponse({
            'code': 20000 if status else 20001,
            'message': message
        })

    # 删除实例
    def delete(self, request):
        droplet_id = request.GET.get('server_id', False)
        droplet_info = models.Droplets.objects.filter(id=droplet_id).first()
        if not droplet_info:
            return JsonResponse({
                'code': 20001,
                'message': '实例不存在'
            })

        doApi = DoApi(droplet_info.account.token)
        if doApi.delete_droplet(droplet_info.droplet_id):
            tasks.beat_update_do_account(droplet_info.account.id, account=False)
            return JsonResponse({
                'code': 20000,
                'message': '实例删除成功, 列表等待更新之后会自动删除。'
            })

        return JsonResponse({
            'code': 20001,
            'message': '实例删除失败。'
        })