from django.core.management.base import BaseCommand
from apps.aws.models import Ec2Images


class Command(BaseCommand):
    help = '添加aws镜像'

    def handle(self, *args, **options):

        self.update_debian()
        self.update_centos()
        self.update_ubuntu()

    def update_ubuntu(self):
        ubuntu = """af-south-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0dbb0a9b02af77021	hvm
        ap-east-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-07498dac6f228478b	hvm
        ap-northeast-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-093c296276d61b583	hvm
        ap-south-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0714e655390b1d125	hvm
        ap-southeast-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-010e14b2b7ac1b58f	hvm
        ca-central-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-05d4e8b594aef7897	hvm
        eu-central-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0ce70c4057dc39200	hvm
        eu-north-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-01b771eab1ba80698	hvm
        eu-south-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0c46eb7c79452c092	hvm
        eu-west-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0d94cb8577ea0e2fd	hvm
        me-south-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-033fde578442476f0	hvm
        sa-east-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0dec7a53c83222c6f	hvm
        us-east-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-09943f9da1f1b7899	hvm
        us-west-1	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-017329b75bfa6772b	hvm
        ap-northeast-2	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0632cfe5256e6b811	hvm
        ap-southeast-2	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-04fad20d313cc0947	hvm
        eu-west-2	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-009725fa4dfe4acb0	hvm
        us-east-2	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0bcacfac640850227	hvm
        us-west-2	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-076cbb27c223df09a	hvm
        ap-northeast-3	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0e4b432b8a51684ef	hvm
        eu-west-3	xenial	16.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-06e3b9e580dd2d388	hvm
        af-south-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0c74a2e303be5a416	hvm
        ap-east-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-08a012665688e0870	hvm
        ap-northeast-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0ab632fc36b987883	hvm
        ap-south-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-02d8619fc5511c34e	hvm
        ap-southeast-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-003f52c4a47b5da6b	hvm
        ca-central-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0a150433c41a574e0	hvm
        eu-central-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-08abe5e3eba040201	hvm
        eu-north-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-043e9b9258b37163d	hvm
        eu-south-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0cd44dc59912e1f25	hvm
        eu-west-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-03f10415e8b0bfb86	hvm
        me-south-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-083b5b36ff68b8e89	hvm
        sa-east-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0ba5b33aa57289efd	hvm
        us-east-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0b4eac045bf0ceb49	hvm
        us-west-1	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0251b2fbfa840f9c7	hvm
        ap-northeast-2	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-0c81de7d11a95e229	hvm
        ap-southeast-2	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-097de812525f83fa9	hvm
        eu-west-2	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-01cbbf2ca9393b9c1	hvm
        us-east-2	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-01e2903d4911669d1	hvm
        us-west-2	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-09ec7a172423f418a	hvm
        ap-northeast-3	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-05364f130ab566199	hvm
        eu-west-3	groovy	20.10	amd64	hvm:ebs-ssd	20210224	ami-01e965db3734cd3a8	hvm
        af-south-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0e4b4778694305983	hvm
        ap-east-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-036915aa0cb1d91a1	hvm
        ap-northeast-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0ef85cf6e604e5650	hvm
        ap-south-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0b84c6433cdbe5c3e	hvm
        ap-southeast-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-05b891753d41ff88f	hvm
        ca-central-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-004c8bf91d878b99c	hvm
        eu-central-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0e0102e3ff768559b	hvm
        eu-north-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0f269726c071d0e96	hvm
        eu-south-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0f274cb646afd3475	hvm
        eu-west-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-06fd78dc2f0b69910	hvm
        me-south-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-026dde872642a6ffe	hvm
        sa-east-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0bd91caaa9bc42cf3	hvm
        us-east-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-013f17f36f8b1fefb	hvm
        us-west-1	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0121ef35996ede438	hvm
        ap-northeast-2	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0078a04747667d409	hvm
        ap-southeast-2	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-076a5bf4a712000ed	hvm
        eu-west-2	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0244a5621d426859b	hvm
        us-east-2	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-01e7ca2ef94a0ae86	hvm
        us-west-2	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-02701bcdc5509e57b	hvm
        ap-northeast-3	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0e958e6a9363c29ad	hvm
        eu-west-3	bionic	18.04 LTS	amd64	hvm:ebs-ssd	20210224	ami-0a0d71ff90f62f72a	hvm"""
        for i in ubuntu.strip().split('\n'):

            _i = i.split()
            # print(_i)
            region = _i[0]
            if _i[3] != 'LTS':

                name = f"Ubuntu {_i[2]}"
                ami = _i[-2]
            else:
                name = f"Ubuntu {_i[2]} {_i[3]}"
                ami = _i[-2]

            _data = {
                'name': name,
                'ami': ami,
                'region': region
            }
            Ec2Images.objects.create(**_data)


    def update_centos(self):
        centos = """CentOS Linux 7	us-east-2	ami-00f8e2c955f7ffa9b
CentOS Linux 7	us-east-1	ami-00e87074e52e6c9f9
CentOS Linux 7	us-west-1	ami-08d2d8b00f270d03b
CentOS Linux 7	us-west-2	ami-0686851c4e7b1a8e1
CentOS Linux 7	af-south-1	ami-0b761332115c38669
CentOS Linux 7	ap-east-1	ami-09611bd6fa5dd0e3d
CentOS Linux 7	ap-south-1	ami-0ffc7af9c06de0077
CentOS Linux 7	ap-northeast-1	ami-0ddea5e0f69c193a4
CentOS Linux 7	ap-northeast-2	ami-0e4214f08b51e23cc
CentOS Linux 7	ap-southeast-1	ami-0adfdaea54d40922b
CentOS Linux 7	ap-southeast-2	ami-03d56f451ca110e99
CentOS Linux 7	ca-central-1	ami-0a7c5b189b6460115
CentOS Linux 7	eu-central-1	ami-08b6d44b4f6f7b279
CentOS Linux 7	eu-west-1	ami-04f5641b0d178a27a
CentOS Linux 7	eu-west-2	ami-0b22fcaf3564fb0c9
CentOS Linux 7	eu-west-3	ami-072ec828dae86abe5
CentOS Linux 7	eu-south-1	ami-0fe3899b62205176a
CentOS Linux 7	eu-north-1	ami-0358414bac2039369
CentOS Linux 7	me-south-1	ami-0ac17dcdd6f6f4eb6
CentOS Linux 7	sa-east-1	ami-02334c45dd95ca1fc
CentOS Linux 8	us-east-2	ami-0ac6967966621d983
CentOS Linux 8	us-east-1	ami-056b03dba13a2c9dd
CentOS Linux 8	us-west-1	ami-04adf3fcbc8a45c54
CentOS Linux 8	us-west-2	ami-0155c31ea13d4abd2
CentOS Linux 8	af-south-1	ami-0bf6cf59605331551
CentOS Linux 8	ap-east-1	ami-0ad3314ea64676ee5
CentOS Linux 8	ap-south-1	ami-0e99c55244ca9e406
CentOS Linux 8	ap-northeast-1	ami-0d9bf167cb68ac889
CentOS Linux 8	ap-northeast-2	ami-06c6d129b47acaba9
CentOS Linux 8	ap-southeast-1	ami-05930ce55ebfd2930
CentOS Linux 8	ap-southeast-2	ami-0e8d52e2390c082c3
CentOS Linux 8	ca-central-1	ami-0557e54bb3a24f10e
CentOS Linux 8	eu-central-1	ami-0e337c7f9752d9d34
CentOS Linux 8	eu-west-1	ami-0a75a5a43b05b4d5f
CentOS Linux 8	eu-west-2	ami-00c89583fee7b879d
CentOS Linux 8	eu-west-3	ami-062fbc1f6aaecbede
CentOS Linux 8	eu-south-1	ami-0bef61145b417dff4
CentOS Linux 8	eu-north-1	ami-0e201bc52c64d7b5a
CentOS Linux 8	me-south-1	ami-0b1c03e7905253652
CentOS Linux 8	sa-east-1	ami-05a85bb881b9f8422
CentOS Stream 8	us-east-2	ami-0d97ef13c06b05a19
CentOS Stream 8	us-east-1	ami-059f1cc52e6c85908
CentOS Stream 8	us-west-1	ami-0f377b303df4963ab
CentOS Stream 8	us-west-2	ami-0ddc70e50205f89b6
CentOS Stream 8	af-south-1	ami-0d9566f77fcfa00e5
CentOS Stream 8	ap-east-1	ami-0b78c5e9b943c50be
CentOS Stream 8	ap-south-1	ami-0c45b2c735e7cbd50
CentOS Stream 8	ap-northeast-1	ami-01f328f87670cc361
CentOS Stream 8	ap-northeast-2	ami-068ba57b029f1a659
CentOS Stream 8	ap-southeast-1	ami-084be8fbdbd21b027
CentOS Stream 8	ap-southeast-2	ami-0bac9d0b7acaea5d4
CentOS Stream 8	ca-central-1	ami-02085625d206d7eb3
CentOS Stream 8	eu-central-1	ami-073a8e22592a4a925
CentOS Stream 8	eu-west-1	ami-090b347d44e58c47b
CentOS Stream 8	eu-west-2	ami-0109cc95c55669f94
CentOS Stream 8	eu-west-3	ami-0718ab19524d69434
CentOS Stream 8	eu-south-1	ami-0138a15900e393a17
CentOS Stream 8	eu-north-1	ami-08ec5ec25b9b7d5c5
CentOS Stream 8	me-south-1	ami-01b5a0aafcc2288c2
CentOS Stream 8	sa-east-1	ami-0f0c3edb7c1e023da"""
        for i in centos.strip().split('\n'):

            _i = i.split()

            if _i[1] == 'Linux':

                name = f"{_i[0]} {_i[2]}"
            else:
                name = f"{_i[0]} {_i[1]} {_i[2]}"

            _data = {
                'name': name,
                'ami': _i[-1],
                'region': _i[-2]
            }
            Ec2Images.objects.create(**_data)


    def update_debian(self):
        debian = """af-south-1 0ac613c8ba38c4ce0
ap-east-1 05b7d5ed6f439d5f6
ap-northeast-1 0f35a180aa403710c
ap-northeast-2 05343e4dcb1d8c0b6
ap-south-1 0ba0da84bb887dd8f
ap-southeast-1 075ca2a4ee6e8f7ab
ap-southeast-2 058c3dc2f9d829915
ca-central-1 0230169901f603407
eu-central-1 0f1026b68319bad6c
eu-north-1 0c592cf8a1572c631
eu-south-1 0f40464627743f691
eu-west-1 09ea48ee08b5fd32c
eu-west-2 05000c1a18d032285
eu-west-3 0e02a25f8c952eeb0
me-south-1 01fd1d8cdb95cb536
sa-east-1 0dcf8fa73ede8196a
us-east-1 07d02ee1eeb0c996c
us-east-2 0eec7e5aeb20f40ce
us-west-1 009159533df3b06da
us-west-2 010327334690f5fa5"""

        for i in debian.strip().split('\n'):

            _i = i.split()


            _data = {
                'name': "Debian 10",
                'ami': f"ami-{_i[-1]}",
                'region': _i[0]
            }
            Ec2Images.objects.create(**_data)