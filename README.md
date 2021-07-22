# AWS Service Based Project - Music Subscription Application
# Introduction: In an individual project, I accomplish functions including user login, searching kinds of music based on title, artists or musical albums, which is implemented in DynamoDB, and a few two-way interactions for both S3 and DynamoDB with creating, retrieving, updating, deleting
## This project utilizes EC2, DynamoDB, S3 Bucket, Flask. If you try to deploy services into your personal computer, you need to modify Access_key and Secret_key based on your AWS account(both of S3 and DynamoDB)

## AWS DynamoDB Web Service Connection
1. signing up for AWS  
2. geting an AWS Access Key by IAM  
There are two ways to connect AWS service from backend server to AWS service by credential.    
3.1 the first way is configuring your credentials to enable authorization(by creating the credentials file or aws configure).  
3.2 use environment variables.   
```python
class DynamoDBConnection():
def __init__(self, dynamoDB = None):
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    if not dynamoDB:
        self.dynamoDB = session.resource('dynamodb')
```
[Setting Up DynamoDB(Web Service)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SettingUp.DynamoWebService.html)  
[boto3 tutorial + dynamodb](https://www.section.io/engineering-education/python-boto3-and-amazon-dynamodb-programming-tutorial/
)  
[boto3 API documentation & tutorial](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
)

## AWS S3 Bucket Service Connection
```python
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

self.s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
aws_secret_access_key=SECRET_KEY)

```

## Deploy Flask Application to Elastic BeanStalk
1. pip freeze -> requirements.txt in the local machine to fix the working environment  
2. pip install -r requirements.txt  
3. Change the name app.py name to application.py  
4. Deploy application into Elastic BeanStalk(can check below tutorials)  




## Reference
[AWS code documentation](https://docs.aws.amazon.com/code-samples/latest/catalog/python-dynamodb-TryDax-01-create-table.py.html
)  
[Tutorial of Deploying Flask into Elastic BeanStalk](https://www.youtube.com/watch?v=dhHOzye-Rms&list=LL&index=17)


