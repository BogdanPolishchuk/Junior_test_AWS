import boto3
import time
from botocore.exceptions import ClientError

#create or check security group:
print("==============Create Security Group:==============")

try:
    ec2 = boto3.client('ec2')

    response = ec2.create_security_group(GroupName='SSH_HTTP_2', Description='SSH_HTTP_by_python', VpcId='vpc-b8daecde')
    security_group_id = response['GroupId']
    print('Security Group Created %s in existing vpc: vpc-b8daecde.' % (security_group_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    response2 = ec2.describe_security_groups(
        GroupNames=[
            'SSH_HTTP_2',
        ],
    )
    security_group_id = response2.get('SecurityGroups', [{}])[0].get('GroupId', '')
    print(e)
    print("Security Group exist: ", security_group_id)


print("==================================================")


#create instance:

print("==================Create Instance:================")

response3 = ec2.run_instances(
    BlockDeviceMappings=[
        {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': 8,
                'VolumeType': 'gp2'
            },
        },
    ],
    ImageId='ami-028188d9b49b32a80',
    UserData='''#!/bin/bash
        lsblk > /tmp/check_lsblk
        sudo parted /dev/xvdc mktable gpt
        sudo parted /dev/xvdc mkpart primary 0% 100%
        sudo mkfs.ext4 /dev/xvdc1
        sudo mkdir /mnt/added_disk
        sudo chmod 660 /mnt/added_disk/
        sudo mount /dev/xvdc1 /mnt/added_disk
        lsblk > /tmp/check_lsblk2''',
    InstanceType='t2.micro',
    KeyName='Bogdan_eu-west-1',
    MaxCount=1,
    MinCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
            {'Key': 'task', 'Value': 'test_junior_by_python'}, 
            {'Key': 'Name', 'Value': 'Bogdan_Polishchuk_python'},
            ]
        },
    ],
    Monitoring={
        'Enabled': False
    },
    SecurityGroupIds=[
        security_group_id,
    ],
)

instance_id = response3.get('Instances', [{}])[0].get('InstanceId', '')
print("Created instange ID: ", instance_id)
print('==================================================')

#create volume:

print("==================Create Volume:==================")

response4 = ec2.create_volume(
    AvailabilityZone='eu-west-1b', 
    Size=1, VolumeType='standard', 
    Encrypted=False, 
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
            {'Key': 'task', 'Value': 'test_junior_by_python'}, 
            {'Key': 'Name', 'Value': 'Bogdan_Polishchuk'},
            ]
        },
    ]
)

volume_Id = response4['VolumeId']
print("Created volume ID: ", volume_Id)

print('==================================================')

#check instance status
print("==================Check instance status:==========")

while True:
    try:
        response6 = ec2.describe_instance_status(
            InstanceIds=[
                instance_id,
            ],
        )
        status = response6.get('InstanceStatuses', [{}])[0].get('InstanceStatus', '').get('Status','')
        print("Instance status is: ", status)
        break
    except IndexError:
        print("---wait 5 second!---")
        time.sleep(5)
        continue

print('==================================================')

#attache volume:

print("==================Attache Volume:=================")

response5 = ec2.attach_volume(
    Device='/dev/sdc',
    InstanceId=instance_id,
    VolumeId=volume_Id,
)

print("Volume - ", response5['VolumeId']," is attached as :", response5['Device'], " to instance :",  response5['InstanceId'])
print('==================================================')





