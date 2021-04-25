import logging
import os

import boto3

from botocore.exceptions import ClientError

ACCESS_KEY = 'AKIATOTIIBQUUE6G5PNX'
SECRET_KEY = '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'


class BucketConnection():
    def __init__(self):
        self.s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                                 aws_secret_access_key=SECRET_KEY)


    def create_bucket(self, bucket_name, region = None):
        try:

            if region is None:

                self.s3_client.create_bucket(Bucket = bucket_name)
            else:
                s3_clent = boto3.client('s3', region_name = region)
                location = {'LocationConstraint': region
                            }
                s3_clent.create_bucket(Bucket = bucket_name, CreateBucketConfiguration = location)

        except ClientError as e:
            logging.error(e)

            return  False
        return True

    def list_bucket(self):
        response = self.s3_client.list_buckets()

        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(bucket['Name'])


    def upload_file(self, filename, bucket, object_name = None):
        '''

        :param filename: local file name path
        :param bucket: bucket name
        :param object_name: filename in the bucket
        :return:
        '''

        if object_name is None:
            object_name = filename

        try:
            response = self.s3_client.upload_file(filename, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def download_file(self, bucket_name, object_name, file_name):
        '''

        :param bucket_name:
        :param object_name: filename in the bucket
        :param file_name: filename saved in the local
        :return:
        '''
        self.s3_client.download_file(bucket_name, object_name, file_name)

if __name__ == '__main__':
    myBucketConnection = BucketConnection()
    # create_bucket('testbucket20210422yiii', "ap-southeast-2")
    myBucketConnection.list_bucket()
    # upload_file('/Users/user/Downloads/your_name.png','testbucket20210422yiii','namayiwa')
    # download_file('testbucket20210422yiii', 'namayiwa', 'yourname.jpg')

