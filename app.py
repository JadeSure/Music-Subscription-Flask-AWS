import random
import requests
import os

from dynamoDBConnection import DynamoDBConnection
from bucketConnection import BucketConnection

from decimal import Decimal
from pprint import pprint

import json

from flask import Flask, render_template

app = Flask(__name__)
dynamoDB = DynamoDBConnection()
bucket = BucketConnection()

# for login user info
user_dict = {}
MUSIC_TABLE = 'Music'
USER_TABLE = 'Users'
BUCKET_NAME = 'musicimage25042021'


@app.route('/')
def root():
    load_music_info()
    load_users_info()
    image_handler(BUCKET_NAME)
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    pass


def __generate_users():
    base_id = 's3803990'
    base_email = '@student.rmit.edu.au'
    base_name = 'Qixiang_Cheng'

    def __random_password():
        temp_str = ""
        for i in range(6):
            ch = chr(random.randrange(ord('0'), ord('9')+1))
            temp_str += ch
        return temp_str

    for i in range(10):
        temp_list = []
        temp_list.append(base_id + str(i) + base_email)
        temp_list.append(base_name + str(i))
        temp_list.append(__random_password())

        user_dict[i] = temp_list



def load_users_info():
    dynamoDB.create_login_table(USER_TABLE)

    if len(dynamoDB.query_user(USER_TABLE, 's38039900@student.rmit.edu.au')) == 0:
        __generate_users()
        for i in range(10):
            dynamoDB.put_user_data(USER_TABLE, user_dict[i][0], user_dict[i][1], user_dict[i][2])

def load_music_info():
    music_table = dynamoDB.create_movie_table(MUSIC_TABLE)

    if len(dynamoDB.query_music(MUSIC_TABLE,'1904')) == 0:
        print('load music again')

        with open('./file/a2.json') as json_file:
            music_list = json.load(json_file, parse_float = Decimal)

        temp_response = dynamoDB.load_data(music_table, music_list['songs'])

        pprint(temp_response, sort_dicts = False)
        print(temp_response['Item'])

def image_handler(bucket_name):
    if bucket.check_bucket(bucket_name):
        print('images have been uploaded to S3 already')
        return
    if bucket.create_bucket(bucket_name):

        base_path = './image'
        with open('./file/a2.json') as json_file:
            music_list = json.load(json_file, parse_float=Decimal)

        for i in music_list['songs']:
            temp_list1 = i['img_url'].split('/')
            img_name = temp_list1[-1]

            r = requests.get(i['img_url'])
            with open(base_path+'/'+img_name, 'wb') as f:
                f.write(r.content)

            bucket.upload_file(base_path+'/'+img_name, bucket_name, img_name)

            os.remove(base_path+'/'+img_name)

        print('images uploaded success')

if __name__ == '__main__':
    app.run(host = '172.0.0.1', port=8080, debug= True)