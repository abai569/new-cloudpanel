from django.core.management.base import BaseCommand
from apps.aws.models import Ec2Images, Account
from libs.aws import AwsApi


IMAGE_QUERIES = [
    ('Amazon Linux 2023', 'amazon', 'al2023-ami-2023*'),
    ('Amazon Linux 2', 'amazon', 'amzn2-ami-hvm-2.0.*'),
    ('Ubuntu 24.04 LTS', '099720109477', 'ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*'),
    ('Ubuntu 22.04 LTS', '099720109477', 'ubuntu/images/hvm-ssd-gp3/ubuntu-jammy-22.04-amd64-server-*'),
    ('Ubuntu 20.04 LTS', '099720109477', 'ubuntu/images/hvm-ssd-gp3/ubuntu-focal-20.04-amd64-server-*'),
    ('Debian 12', '136693071363', 'debian-12-*'),
    ('Debian 11', '136693071363', 'debian-11-*'),
    ('Rocky Linux 9', '679593333241', 'Rocky-9-EC2-*'),
    ('Rocky Linux 8', '679593333241', 'Rocky-8-EC2-*'),
    ('Red Hat Enterprise Linux 9', '309956199498', 'RHEL-9.*_HVM-*-x86_64-*'),
]

STATIC_IMAGES = [
    ('Amazon Linux 2', 'ami-0c1c30571d2dae5c9', 'ap-northeast-1'),
    ('Amazon Linux 2023', 'ami-01f544628f8b5f1d1', 'ap-northeast-1'),
    ('Ubuntu 24.04 LTS', 'ami-0d6b1913edac0f379', 'ap-northeast-1'),
    ('Ubuntu 22.04 LTS', 'ami-07c7e04902bf289d3', 'ap-northeast-1'),
    ('Ubuntu 20.04 LTS', 'ami-0d36ae0292c99c8ec', 'ap-northeast-1'),
    ('Debian 12', 'ami-005f60e1d45e94295', 'ap-northeast-1'),
    ('Debian 11', 'ami-082aea917abdf1460', 'ap-northeast-1'),
    ('Rocky Linux 9', 'ami-0a18fa0284bcaaae1', 'ap-northeast-1'),
    ('Amazon Linux 2', 'ami-05fb66375013a6ab6', 'ap-southeast-1'),
    ('Amazon Linux 2023', 'ami-05ec27c5e2f6186f4', 'ap-southeast-1'),
    ('Ubuntu 24.04 LTS', 'ami-0a1e932e32433eab3', 'ap-southeast-1'),
    ('Ubuntu 22.04 LTS', 'ami-04731386031bf42a0', 'ap-southeast-1'),
    ('Ubuntu 20.04 LTS', 'ami-03193de4b8eaf4e6a', 'ap-southeast-1'),
    ('Debian 12', 'ami-04e3fbacff3c69d76', 'ap-southeast-1'),
    ('Debian 11', 'ami-06cd01c5179e80b63', 'ap-southeast-1'),
    ('Rocky Linux 9', 'ami-0dc2395429ee8e1ed', 'ap-southeast-1'),
    ('Amazon Linux 2', 'ami-0fe630eb857a6ec83', 'us-east-1'),
    ('Amazon Linux 2023', 'ami-01816d07b1128cd2e', 'us-east-1'),
    ('Ubuntu 24.04 LTS', 'ami-04b70fa74eebaf0b8', 'us-east-1'),
    ('Ubuntu 22.04 LTS', 'ami-080e12f04d64e9d60', 'us-east-1'),
    ('Ubuntu 20.04 LTS', 'ami-0b69ea66ff7391e80', 'us-east-1'),
    ('Debian 12', 'ami-0eab7f7272015e6f3', 'us-east-1'),
    ('Debian 11', 'ami-0c6599df7db49d2c7', 'us-east-1'),
    ('Rocky Linux 9', 'ami-0f97cb9e4a48e3694', 'us-east-1'),
    ('Amazon Linux 2', 'ami-0cd3dfa4e37921605', 'eu-west-1'),
    ('Amazon Linux 2023', 'ami-04f35c4052ff3526d', 'eu-west-1'),
    ('Ubuntu 24.04 LTS', 'ami-04242e7eaf3ae699e', 'eu-west-1'),
    ('Ubuntu 22.04 LTS', 'ami-0c3996e77be06549b', 'eu-west-1'),
    ('Ubuntu 20.04 LTS', 'ami-0942d4e7c39f9b16d', 'eu-west-1'),
    ('Debian 12', 'ami-07976520a94fa5a81', 'eu-west-1'),
    ('Debian 11', 'ami-0a0b8cf6e5115744a', 'eu-west-1'),
    ('Rocky Linux 9', 'ami-0f73b7ebb37e06d75', 'eu-west-1'),
    ('Amazon Linux 2', 'ami-0eb14fe7b72ac2a56', 'us-west-2'),
    ('Amazon Linux 2023', 'ami-01f77a72f1b32af4e', 'us-west-2'),
    ('Ubuntu 24.04 LTS', 'ami-04b8631283aa63524', 'us-west-2'),
    ('Ubuntu 22.04 LTS', 'ami-01650547f28e84c8c', 'us-west-2'),
    ('Ubuntu 20.04 LTS', 'ami-0bc5450510e49b4b0', 'us-west-2'),
    ('Debian 12', 'ami-0ea3b65ee55bcfd28', 'us-west-2'),
    ('Debian 11', 'ami-0c0f7b0cb8e7d75e8', 'us-west-2'),
    ('Rocky Linux 9', 'ami-0187f9f491e9e9fe1', 'us-west-2'),
    ('Amazon Linux 2', 'ami-03cd80b4981c6eb15', 'ap-south-1'),
    ('Amazon Linux 2023', 'ami-03f2a1e336b42edd8', 'ap-south-1'),
    ('Ubuntu 24.04 LTS', 'ami-053eec3a534325f3d', 'ap-south-1'),
    ('Ubuntu 22.04 LTS', 'ami-0a03b38c94424cf83', 'ap-south-1'),
    ('Ubuntu 20.04 LTS', 'ami-098743f6f4b335b51', 'ap-south-1'),
    ('Debian 12', 'ami-0a3cd20ddbd5b169b', 'ap-south-1'),
    ('Debian 11', 'ami-08a7c4f9eb6edfa6d', 'ap-south-1'),
    ('Rocky Linux 9', 'ami-0261c1de32b5f7aff', 'ap-south-1'),
    ('Amazon Linux 2', 'ami-0d55f0772e90ab36e', 'ap-northeast-2'),
    ('Amazon Linux 2023', 'ami-0079aecc83d0e1c29', 'ap-northeast-2'),
    ('Ubuntu 24.04 LTS', 'ami-03e6633f4e9382fcc', 'ap-northeast-2'),
    ('Ubuntu 22.04 LTS', 'ami-08b775db022a55aca', 'ap-northeast-2'),
    ('Ubuntu 20.04 LTS', 'ami-05885a3374dfee26b', 'ap-northeast-2'),
    ('Debian 12', 'ami-0680e867fd8d6a449', 'ap-northeast-2'),
    ('Debian 11', 'ami-0cac8af1bc6336618', 'ap-northeast-2'),
    ('Rocky Linux 9', 'ami-01e1ae880be56a2e0', 'ap-northeast-2'),
    ('Amazon Linux 2', 'ami-0957e1b70bf9116ce', 'eu-central-1'),
    ('Amazon Linux 2023', 'ami-0282858abeeafdff8', 'eu-central-1'),
    ('Ubuntu 24.04 LTS', 'ami-0fcf56edd656cdda3', 'eu-central-1'),
    ('Ubuntu 22.04 LTS', 'ami-076c69035370ad2e1', 'eu-central-1'),
    ('Ubuntu 20.04 LTS', 'ami-03b5e4f04d780bdb3', 'eu-central-1'),
    ('Debian 12', 'ami-01c42582923d63551', 'eu-central-1'),
    ('Debian 11', 'ami-0ca0de2a988ab7d80', 'eu-central-1'),
    ('Rocky Linux 9', 'ami-0a922e0d8dbab93bc', 'eu-central-1'),
    ('Amazon Linux 2', 'ami-084afaa49e4ff1b7b', 'ap-southeast-2'),
    ('Amazon Linux 2023', 'ami-0f311415d39e20467', 'ap-southeast-2'),
    ('Ubuntu 24.04 LTS', 'ami-03020643ea6faae3e', 'ap-southeast-2'),
    ('Ubuntu 22.04 LTS', 'ami-0d135c42158e6e9c7', 'ap-southeast-2'),
    ('Ubuntu 20.04 LTS', 'ami-052be412adc9fb4a6', 'ap-southeast-2'),
    ('Debian 12', 'ami-0c5af48af4106dfad', 'ap-southeast-2'),
    ('Debian 11', 'ami-07117f48f0ceb9f8f', 'ap-southeast-2'),
    ('Rocky Linux 9', 'ami-03354734aeff7baba', 'ap-southeast-2'),
    ('Amazon Linux 2', 'ami-0891f5df7bca2761b', 'ca-central-1'),
    ('Amazon Linux 2023', 'ami-014d4a3cbfae9e7d4', 'ca-central-1'),
    ('Ubuntu 24.04 LTS', 'ami-02f0e33aa51d47a59', 'ca-central-1'),
    ('Ubuntu 22.04 LTS', 'ami-0e6d2f03cce77ecd1', 'ca-central-1'),
    ('Ubuntu 20.04 LTS', 'ami-0a4c7a97bb1824436', 'ca-central-1'),
    ('Debian 12', 'ami-073fbf9dcd2332f5a', 'ca-central-1'),
    ('Debian 11', 'ami-0d66a7a2a08be6902', 'ca-central-1'),
    ('Rocky Linux 9', 'ami-050cd5b067cc33a0f', 'ca-central-1'),
    ('Amazon Linux 2', 'ami-04e8c5e9e62dccbc9', 'eu-west-2'),
    ('Amazon Linux 2023', 'ami-064ae1ac9aa0bdf83', 'eu-west-2'),
    ('Ubuntu 24.04 LTS', 'ami-07fbfb7aec92c75f8', 'eu-west-2'),
    ('Ubuntu 22.04 LTS', 'ami-0b1d0158c3b138b4b', 'eu-west-2'),
    ('Ubuntu 20.04 LTS', 'ami-0d0812f9c03a90ea2', 'eu-west-2'),
    ('Debian 12', 'ami-0ade26c4989f98e84', 'eu-west-2'),
    ('Debian 11', 'ami-0ec587a3a569ce14a', 'eu-west-2'),
    ('Rocky Linux 9', 'ami-043e0b60a829d7ff1', 'eu-west-2'),
    ('Amazon Linux 2', 'ami-0556309845d90f931', 'eu-west-3'),
    ('Amazon Linux 2023', 'ami-0cb04d9bef9f9cf4a', 'eu-west-3'),
    ('Ubuntu 24.04 LTS', 'ami-083308531fd97f2d7', 'eu-west-3'),
    ('Ubuntu 22.04 LTS', 'ami-0195f3089aedde232', 'eu-west-3'),
    ('Ubuntu 20.04 LTS', 'ami-04f0a1bf8e35e8f96', 'eu-west-3'),
    ('Debian 12', 'ami-04318c3475ffa37be', 'eu-west-3'),
    ('Debian 11', 'ami-0c1e04d0d36e58c7f', 'eu-west-3'),
    ('Rocky Linux 9', 'ami-0a0a90a6c94df4357', 'eu-west-3'),
    ('Amazon Linux 2', 'ami-008c90f3335ecc9a1', 'sa-east-1'),
    ('Amazon Linux 2023', 'ami-0f64099af31316b7a', 'sa-east-1'),
    ('Ubuntu 24.04 LTS', 'ami-0c9c626388ab4894f', 'sa-east-1'),
    ('Ubuntu 22.04 LTS', 'ami-0bfb6e51bcdcc4fb7', 'sa-east-1'),
    ('Ubuntu 20.04 LTS', 'ami-074331f0aeed0e4f8', 'sa-east-1'),
    ('Debian 12', 'ami-0040f17bbf65e35e4', 'sa-east-1'),
    ('Debian 11', 'ami-076e22eebc501b87b', 'sa-east-1'),
    ('Rocky Linux 9', 'ami-06ac85e7cd7ba9b67', 'sa-east-1'),
    ('Amazon Linux 2', 'ami-04ae7c11677ff4de5', 'us-east-2'),
    ('Amazon Linux 2023', 'ami-03e79b7b45c17a943', 'us-east-2'),
    ('Ubuntu 24.04 LTS', 'ami-0e192a51ce204c467', 'us-east-2'),
    ('Ubuntu 22.04 LTS', 'ami-089fa6f64a3bb7746', 'us-east-2'),
    ('Ubuntu 20.04 LTS', 'ami-0a89e25a7615e4b58', 'us-east-2'),
    ('Debian 12', 'ami-091f6c46b193ac3ce', 'us-east-2'),
    ('Debian 11', 'ami-07757d45f3351e0e7', 'us-east-2'),
    ('Rocky Linux 9', 'ami-0663f9cffef568fb8', 'us-east-2'),
    ('Amazon Linux 2', 'ami-0888c1e0f72e712cd', 'us-west-1'),
    ('Amazon Linux 2023', 'ami-02579b7a11e2d06bc', 'us-west-1'),
    ('Ubuntu 24.04 LTS', 'ami-04dbd64773aa8ce89', 'us-west-1'),
    ('Ubuntu 22.04 LTS', 'ami-0ae1006c3b667af1e', 'us-west-1'),
    ('Ubuntu 20.04 LTS', 'ami-07f2c45f97dfb0faf', 'us-west-1'),
    ('Debian 12', 'ami-0d8af4b4cee939f3c', 'us-west-1'),
    ('Debian 11', 'ami-04b7b972d433282c8', 'us-west-1'),
    ('Rocky Linux 9', 'ami-0844a2a176e9c6a56', 'us-west-1'),
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
