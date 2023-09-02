# Auto_CloudWatch

## Description
The code is for automatically adding alarms to the instances which has no alarms. It uses AWS SDK to get instances and add alarms.

## How to use
1. Install AWS CLI: `$sudo apt install awscli / $brew install awscli`
2. Go into **Command line or programmatic access**, and configure AWS IAM Identity Center credentials in the local using: `aws configure sso`
![img.png](img.png)
3. `pip install boto3`
4. Replace your profile name in the code, and run the code
5. If you run the code on the second day, because the token has expired and refresh failed, you need to run `aws sso login --sso-session your_session_name` or `aws sso login --profile your-profile-name` to login first. 
6. I prefer changing `.aws/config` and putting two profiles in the same session. So I can log in by session instead of loging in two profiles one by one.![img_1.png](img_1.png)