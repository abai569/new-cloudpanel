from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line
from django.conf import settings
from apps.users.models import User
import string, random


class Command(BaseCommand):
    help = '初始化/管理员'

    def handle(self, *args, **options):

        if User.objects.filter(username="admin").first():
            self.stdout.write(self.style.SUCCESS('  管理员已经存在'))
            return

        password = self.rand_pass(16)
        if User.objects.create_superuser("admin", "admin@admin.com", password):
            print("管理员创建成功\n")
            print("Username: admin\n")
            print("Password: %s\n" % password)

        self.stdout.write(self.style.SUCCESS('  初始化/管理员完成'))

    def rand_pass(self, length):
        chars = string.ascii_letters + string.digits + '!@#$%^&*._'
        return ''.join(random.sample(chars, length))
