from decimal import Decimal
from pprint import pprint


import boto3
from boto3.dynamodb.conditions import Key
import json

from botocore.exceptions import ClientError


class DynamoDBConnection():
    def __init__(self, dynamoDB = None):
        if not dynamoDB:
            self.dynamoDB = boto3.resource('dynamodb')




    def create_login_table(self, table_name):
        for table in self.dynamoDB.tables.all():
            if table.name == table_name:
                print('Table',table_name, 'has been here')
                return self.dynamoDB.Table(table_name)

        table = self.dynamoDB.create_table(
            TableName = table_name,
            KeySchema = [
                {
                    'AttributeName' : 'email',
                    'KeyType' : 'HASH'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName' : 'email',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                "WriteCapacityUnits": 10
            }

        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print('Table status:', table.table_status)

        return table

    def create_movie_table(self, table_name):

        for table in self.dynamoDB.tables.all():

            if table.name == table_name:
                print('Table',table_name, 'has been here')
                return self.dynamoDB.Table(table_name)

        table = self.dynamoDB.create_table(
            TableName = table_name,
            KeySchema = [
                {
                    'AttributeName' : 'title',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'artist',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'artist',
                    'AttributeType': 'S'
                }
            ],
            # provide throughput for read capacity
            ProvisionedThroughput = {
                'ReadCapacityUnits': 10,
                "WriteCapacityUnits" : 10
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print('Table status:', table.table_status)

        return table

    def update_subscription_table(self, table_name, email, sp_music):
        table = self.dynamoDB.Table(table_name)

        response = table.update_item(
            Key = {
                'email': email
            },
            UpdateExpression = "set Info.sp_music=:sp",
            ExpressionAttributeValues={
                ':sp': sp_music
            },
            ReturnValues= "UPDATED_NEW"
        )
        return response

    def create_subscription_table(self, table_name):
        for table in self.dynamoDB.tables.all():

            if table.name == table_name:
                print('Table', table_name, 'has been here')
                return self.dynamoDB.Table(table_name)


        table = self.dynamoDB.create_table(
            TableName = table_name,
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            # provide throughput for read capacity
            ProvisionedThroughput = {
                'ReadCapacityUnits': 10,
                "WriteCapacityUnits" : 10
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print('Table status:', table.table_status)


    def load_music_data(self, my_table, json_file_read):
        for music in json_file_read:

            title = music['title']
            artist = music['artist']
            year = int(music['year'])
            web_url = music['web_url']
            img_url = music['img_url']

            print(title, artist, year, web_url, img_url)
            my_table.put_item(Item=music)

    def put_user_data(self, table_name, email, user_name, password):
        table = self.dynamoDB.Table(table_name)

        response = table.put_item(
            Item={
                'email': email,
                'user_name': user_name,
                'password': password
            }
        )
        return response

    def put_sb_music(self, table_name, email):
        table = self.dynamoDB.Table(table_name)

        response = table.put_item(
            Item={
                'email': email,
                'Info' : {}
            }
        )
        return response

    def put_music_data(self, table_name, title, artist, year, web_url, img_url):
        table = self.dynamoDB.Table(table_name)

        response = table.put_item(
            Item={
                'title': title,
                'artist': artist,
                'year': year,
                'web_url': web_url,
                'img_url': img_url
            }
        )
        return response

    def get_music_data(self, table_name, partition_key_value, sort_key_value):
        table = self.dynamoDB.Table(table_name)

        try:
            response = table.get_item(Key = {'title':partition_key_value, 'artist': sort_key_value})

        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            return response['Item']

    def check_music_table_status(self, table_name, partition_key):
        table = self.dynamoDB.Table(table_name)
        response = table.query(
            KeyConditionExpression = Key('title').eq(partition_key)
        )

        return response['Items']


    def check_sp_table_status(self, table_name, partition_key):
        table = self.dynamoDB.Table(table_name)
        response = table.query(
            KeyConditionExpression = Key('email').eq(partition_key)
        )

        return response['Items']

    def query_music_details(self, table_name, partition_key, sort_key):
        table = self.dynamoDB.Table(table_name)
        response = table.query(
            KeyConditionExpression =
            Key('title').eq(partition_key)&Key('artist').eq(sort_key)
        )

        return response['Items']

    def scan_music(self, table_name, input_dict, display_musics):
        query_table = self.dynamoDB.Table(table_name)
        a_title = ''
        b_artist = ''
        c_year = ''
        status = 0
        filter_output = ""

        if len(input_dict['title']) != 0:
            a_title = Key('title').eq(input_dict['title'])
            status = status + 1

        elif len(input_dict['artist']) != 0:
            b_artist = Key('artist').eq(input_dict['artist'])
            status = status + 2

        elif len(input_dict['year']) != 0:
            c_year = Key('year').eq(input_dict['year'])
            status = status + 4
        else:
            return -1

        if status == 7:
            filter_output = a_title & b_artist & c_year
        elif status == 6:
            filter_output = b_artist & c_year
        elif status == 5:
            filter_output = a_title & c_year
        elif status == 4:
            filter_output = c_year
        elif status == 3:
            filter_output = a_title & b_artist
        elif status == 2:
            filter_output = b_artist
        elif status == 1:
            filter_output = a_title

        scan_kwargs = {
            'FilterExpression' : filter_output,
            'ProjectionExpression': "#yr, title, artist, img_url",
            'ExpressionAttributeNames': {"#yr": "year"}
        }

        done = False
        start_key = None
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            response = query_table.scan(**scan_kwargs)
            display_musics(response.get('Items', []))
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None

    def query_user(self, table_name, partition_key):
        table = self.dynamoDB.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key('email').eq(partition_key)
        )

        return response['Items']

    # def update_item(self, partition_key_name, partition_key_value,  sort_key_name, sort_key_value,
    #                 status):
    #     table = self.dynamodb.Table(table_name)
    #
    #     response = table.update_item(
    #         Key = {
    #             partition_key_name:partition_key_value,
    #             sort_key_name: sort_key_value
    #         },
    #         UpdateExpression = "set "
    #     )

if __name__ == '__main__':
    dynamoDB = DynamoDBConnection()
    table_name = 'Music'

    movie_table = dynamoDB.create_movie_table(table_name)

    # load json file into dynamoDB
    # with open('./file/a2.json') as json_file:
    #     music_list = json.load(json_file, parse_float = Decimal)

    # put item
    # dynamoDB.load_data(movie_table, music_list['songs'])
    # temp_response = dynamoDB.put_data(table_name, '11', '11',1993, '11', '11')
    # pprint(temp_response, sort_dicts = False)
    # print(temp_response['Item'])

    # get item
    # response = dynamoDB.get_data(table_name, 'title', '#41', 'artist', 'Dave Matthews')
    # print(response)

    music = dynamoDB.check_music_table_status(table_name, '000')
    print(music)