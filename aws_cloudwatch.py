import sys
import boto3


def add_alarms(profile_name, tag_key):

    session = boto3.Session(profile_name=profile_name, region_name='us-east-1')

    # Create ec2 and cloudwatch client
    ec2_client = session.client('ec2')
    cloudwatch_client = session.client('cloudwatch')

    # get all instance ids in the same aws group by the tag key
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag-key',
                'Values': [tag_key]
            }
        ]
    )
    instance_ids_all = set(i['InstanceId'] for r in response['Reservations'] for i in r['Instances'])

    # Get all instance ids that have CloudWatch alarms
    alarms = cloudwatch_client.describe_alarms()
    instance_ids_with_alarm = set(alarm['Dimensions'][0]['Value'] for alarm in alarms['MetricAlarms'] if
                                  alarm['Dimensions'][0]['Name'] == 'InstanceId')

    # Get all instance ids without CloudWatch alarms
    instance_ids_no_alarm = instance_ids_all - instance_ids_with_alarm
    print(instance_ids_no_alarm)

    # add alarm to these instances
    for instance_id in instance_ids_no_alarm:
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


if __name__ == "__main__":

    # profile_name1 = sys.argv[1]
    # profile_name2 = sys.argv[2]
    # tag_key = sys.argv[3]

    profile_name1 = 'dl'
    profile_name2 = 'nlp'
    tag_key = 'gw-email'

    print(profile_name1, profile_name2, tag_key)

    print('start add alarms for dl')
    add_alarms(profile_name1, tag_key)

    print('start add alarms for nlp')
    add_alarms(profile_name2, tag_key)

    print('finish add alarms')
