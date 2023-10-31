import sys
import argparse
import boto3


def get_all_instance_ids(ec2_client, tag_key_name):
    # get all instance ids in the same aws group by the tag key
    # you need to handle pagination if the instances you have are larger than the return numbers
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': [tag_key_name]
            }
        ]
    )

    if 'NextToken' in response:
        print('you need consider ec2 pagination')

    instance_ids_all = set()

    # instance_ids_all = set(i['InstanceId'] for r in response['Reservations'] for i in r['Instances'])
    for r in response['Reservations']:
        for i in r['Instances']:
            instance_id = i['InstanceId']
            instance_ids_all.add(instance_id)

            # find out the terminated instances and terminate them
            for tag in i['Tags']:
                if tag['Key'] == 'Name' and tag['Value'].lower() == 'terminate':
                    print(f"terminate instance of {instance_id}, name: {tag['Value']}")

                    ec2_client.terminate_instances(InstanceIds=[instance_id])
                    instance_ids_all.remove(instance_id)

    return instance_ids_all


def get_instance_ids_with_alarm(cloudwatch_client):
    # Get all instance ids that have CloudWatch alarms
    all_alarms = []

    response = cloudwatch_client.describe_alarms()
    all_alarms.extend(response['MetricAlarms'])

    # Continue paginating through the results
    while 'NextToken' in response:
        next_token = response['NextToken']
        response = cloudwatch_client.describe_alarms(NextToken=next_token)
        all_alarms.extend(response['MetricAlarms'])

    instance_ids_with_alarm = set(alarm['Dimensions'][0]['Value'] for alarm in all_alarms if
                                  alarm['Dimensions'][0]['Name'] == 'InstanceId')

    return instance_ids_with_alarm


def add_alarm_to_instances(cloudwatch_client, instance_ids):
    # add alarm to these instances
    for instance_id in instance_ids:
        cloudwatch_client.put_metric_alarm(
            AlarmName=f'LowCPUUtilization_{instance_id}',
            ComparisonOperator='LessThanOrEqualToThreshold',
            EvaluationPeriods=8,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Period=3600,  # in seconds, so 1 hour = 3600 seconds
            Statistic='Average',
            Threshold=0.99,
            ActionsEnabled=True,
            AlarmActions=[
                f'arn:aws:automate:us-east-1:ec2:stop'  # Replace us-east-1 with your AWS region
            ],
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            Unit='Percent'
        )


def add_alarms(profile_name, tag_key_name, excluded_instance_ids):
    print(f'start add alarms for {profile_name}')

    session = boto3.Session(profile_name=profile_name, region_name='us-east-1')

    # Create ec2 and cloudwatch client
    ec2_client = session.client('ec2')
    cloudwatch_client = session.client('cloudwatch')

    instance_ids_all = get_all_instance_ids(ec2_client, tag_key_name)

    instance_ids_with_alarm = get_instance_ids_with_alarm(cloudwatch_client)

    instance_ids_no_alarm = instance_ids_all - instance_ids_with_alarm
    print('instance_ids_no_alarm:', instance_ids_no_alarm)

    instance_ids_need_alarm = instance_ids_no_alarm - excluded_instance_ids
    print('instance_ids_need_alarm:', instance_ids_need_alarm)

    add_alarm_to_instances(cloudwatch_client, instance_ids_need_alarm)

    print(f'finish add alarms for {profile_name}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--exclude", type=str, required=False, default='')
    excluded_instance_str = parser.parse_args().exclude

    excluded_instance_ids = set(excluded_instance_str.split(',')) if excluded_instance_str else set()  # 'i-07cbdf681a26690ad'
    print('\nexcluded_instance_ids', excluded_instance_ids)

    # profile_name1 = sys.argv[1]
    # profile_name2 = sys.argv[2]
    # tag_key = sys.argv[3]

    profile_name1 = 'dl'
    profile_name2 = 'nlp'
    tag_key = 'gw-email'

    print(profile_name1, profile_name2, tag_key, '\n')

    add_alarms(profile_name1, tag_key, excluded_instance_ids)

    add_alarms(profile_name2, tag_key, excluded_instance_ids)
