# Auto_CloudWatch

## Description
The code is for automatically adding alarms to the instances which has no alarms. It uses AWS SDK to get instances and add alarms.

## How to use
1. Install AWS CLI: `$sudo apt install awscli / $brew install awscli`
2. Go into **Command line or programmatic access**, and configure AWS IAM Identity Center credentials in the local using: `aws configure sso`
![img.png](img.png)
3. `pip install boto3`
4. Replace your profile name in the code, and run the code
5. (Option) Use **cron** to the code daily