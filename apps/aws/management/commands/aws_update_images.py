from django.core.management.base import BaseCommand
from apps.aws.models import Ec2Images, Account
from libs.aws import AwsApi


IMAGE_QUERIES = [
    ('Ubuntu 24.04 LTS', '099720109477', 'ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*'),
    ('Ubuntu 22.04 LTS', '099720109477', 'ubuntu/images/hvm-ssd-gp3/ubuntu-jammy-22.04-amd64-server-*'),
    ('Debian 13', '136693071363', 'debian-13-*'),
    ('Debian 12', '136693071363', 'debian-12-*'),
    ('Debian 11', '136693071363', 'debian-11-*'),
]

STATIC_IMAGES = [
    ('Ubuntu 24.04 LTS', 'ami-0d6b1913edac0f379', 'ap-northeast-1'),
    ('Ubuntu 22.04 LTS', 'ami-07c7e04902bf289d3', 'ap-northeast-1'),
    ('Debian 12', 'ami-005f60e1d45e94295', 'ap-northeast-1'),
    ('Debian 11', 'ami-082aea917abdf1460', 'ap-northeast-1'),
    ('Ubuntu 24.04 LTS', 'ami-0a1e932e32433eab3', 'ap-southeast-1'),
    ('Ubuntu 22.04 LTS', 'ami-04731386031bf42a0', 'ap-southeast-1'),
    ('Debian 12', 'ami-04e3fbacff3c69d76', 'ap-southeast-1'),
    ('Debian 11', 'ami-06cd01c5179e80b63', 'ap-southeast-1'),
    ('Ubuntu 24.04 LTS', 'ami-04b70fa74eebaf0b8', 'us-east-1'),
    ('Ubuntu 22.04 LTS', 'ami-080e12f04d64e9d60', 'us-east-1'),
    ('Debian 12', 'ami-0eab7f7272015e6f3', 'us-east-1'),
    ('Debian 11', 'ami-0c6599df7db49d2c7', 'us-east-1'),
    ('Ubuntu 24.04 LTS', 'ami-04242e7eaf3ae699e', 'eu-west-1'),
    ('Ubuntu 22.04 LTS', 'ami-0c3996e77be06549b', 'eu-west-1'),
    ('Debian 12', 'ami-07976520a94fa5a81', 'eu-west-1'),
    ('Debian 11', 'ami-0a0b8cf6e5115744a', 'eu-west-1'),
    ('Ubuntu 24.04 LTS', 'ami-04b8631283aa63524', 'us-west-2'),
    ('Ubuntu 22.04 LTS', 'ami-01650547f28e84c8c', 'us-west-2'),
    ('Debian 12', 'ami-0ea3b65ee55bcfd28', 'us-west-2'),
    ('Debian 11', 'ami-0c0f7b0cb8e7d75e8', 'us-west-2'),
    ('Ubuntu 24.04 LTS', 'ami-053eec3a534325f3d', 'ap-south-1'),
    ('Ubuntu 22.04 LTS', 'ami-0a03b38c94424cf83', 'ap-south-1'),
    ('Debian 12', 'ami-0a3cd20ddbd5b169b', 'ap-south-1'),
    ('Debian 11', 'ami-08a7c4f9eb6edfa6d', 'ap-south-1'),
    ('Ubuntu 24.04 LTS', 'ami-03e6633f4e9382fcc', 'ap-northeast-2'),
    ('Ubuntu 22.04 LTS', 'ami-08b775db022a55aca', 'ap-northeast-2'),
    ('Debian 12', 'ami-0680e867fd8d6a449', 'ap-northeast-2'),
    ('Debian 11', 'ami-0cac8af1bc6336618', 'ap-northeast-2'),
    ('Ubuntu 24.04 LTS', 'ami-0fcf56edd656cdda3', 'eu-central-1'),
    ('Ubuntu 22.04 LTS', 'ami-076c69035370ad2e1', 'eu-central-1'),
    ('Debian 12', 'ami-01c42582923d63551', 'eu-central-1'),
    ('Debian 11', 'ami-0ca0de2a988ab7d80', 'eu-central-1'),
    ('Ubuntu 24.04 LTS', 'ami-03020643ea6faae3e', 'ap-southeast-2'),
    ('Ubuntu 22.04 LTS', 'ami-0d135c42158e6e9c7', 'ap-southeast-2'),
    ('Debian 12', 'ami-0c5af48af4106dfad', 'ap-southeast-2'),
    ('Debian 11', 'ami-07117f48f0ceb9f8f', 'ap-southeast-2'),
]


class Command(BaseCommand):
    help = 'Import EC2 AMI images from AWS dynamically, with static fallback'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing images before importing',
        )

    def handle(self, *args, **options):
        if options.get('clear'):
            count = Ec2Images.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing images.'))

        account = Account.objects.filter(status=True).first()
        if account:
            self._update_dynamic(account.key_id, account.secret)
        else:
            self.stdout.write(self.style.WARNING('No active AWS account found, using static AMI list.'))
            self._update_static()

    def _update_dynamic(self, key_id, key_secret):
        self.stdout.write('Fetching AMI images from AWS dynamically...')

        aApi = AwsApi(key_id, key_secret)
        aApi.region = 'us-east-1'
        aApi.start('ec2')

        try:
            regions_resp = aApi.client.describe_regions()
            regions = [r['RegionName'] for r in regions_resp['Regions']]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to get regions: {e}. Falling back to static list.'))
            self._update_static()
            return

        total = 0

        for display_name, owner_id, name_filter in IMAGE_QUERIES:
            for region in regions:
                try:
                    aApi.region = region
                    aApi.start('ec2')

                    paginator = aApi.client.get_paginator('describe_images')
                    for page in paginator.paginate(
                        Owners=[owner_id],
                        Filters=[
                            {'Name': 'name', 'Values': [name_filter]},
                            {'Name': 'state', 'Values': ['available']},
                            {'Name': 'virtualization-type', 'Values': ['hvm']},
                            {'Name': 'root-device-type', 'Values': ['ebs']},
                        ],
                    ):
                        for image in page.get('Images', []):
                            self._save(image['ImageId'], display_name, region)
                            total += 1
                            break
                except Exception:
                    continue

        self.stdout.write(self.style.SUCCESS(f'Updated {total} AMI images from AWS.'))

    def _update_static(self):
        total = 0
        for name, ami, region in STATIC_IMAGES:
            self._save(ami, name, region)
            total += 1
        self.stdout.write(self.style.SUCCESS(f'Loaded {total} static AMI images.'))

    def _save(self, ami, name, region):
        Ec2Images.objects.update_or_create(
            ami=ami,
            defaults={'name': name, 'region': region},
        )
