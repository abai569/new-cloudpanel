from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings
from apps.aws.models import Account, Lightsail, Ec2, GlobalAccelerator
from apps.do.models import Account as do_account
from apps.do.tasks import update_account as do_update_account

from libs.aws import AwsApi
from apps.aws.tasks import update_aws
import datetime

import _thread



class Command(BaseCommand):
    help = '更新亚马逊全部实例'

    def handle(self, *args, **options):


        # 更新 do 全部账号
        for _account in do_account.objects.exclude(status='locked'):
            # do_update_account.delay(_account.id)
            print(f'正在更新： {_account.email}')
            _account.update_account()
            _account.update_droplets()
