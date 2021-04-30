import random
import requests
import os

from dynamoDBConnection import DynamoDBConnection
from bucketConnection import BucketConnection
from registerForm import  RegisterForm
from queryForm import QueryForm

from decimal import Decimal
from pprint import pprint

import json

from flask import Flask, render_template, session, url_for, redirect, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ADMAIN'

dynamoDB = DynamoDBConnection()
bucket = BucketConnection()

# for login user info
user_dict = {}
MUSIC_TABLE = 'Music'
USER_TABLE = 'Login'
SUBSCRIPTION = 'Subscribe'
BUCKET_NAME = 'musicimage25042021'
BUCKET_IMAGE_BASE ="https://" + BUCKET_NAME + ".s3.amazonaws.com/"


@app.route('/')
def root():
    load_music_info()
    load_users_info()
    image_handler(BUCKET_NAME)
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    query_form = QueryForm()
    if 'username' in session:
        return render_template('main.html', name = session['username'], form = query_form)

    curr_id = request.form['ID']
    curr_pd = request.form['password']

    error = None

    if __judge_status(curr_id, curr_pd):

        return render_template('main.html', name = session['username'], form = query_form)
    else:
        error = 'email or password is invalid'
        return render_template('index.html', error = error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    register_form = RegisterForm()

    if request.method == 'POST':
        if register_form.validate_on_submit():
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password1')

            response = dynamoDB.query_user(USER_TABLE, email)
            if len(response) == 0:
                dynamoDB.put_user_data(USER_TABLE, email, username, password)
                dynamoDB.put_sb_music(SUBSCRIPTION, email)

                return render_template('index.html', error = error)
            else:
                error = 'This email has been registered'

    return render_template('register.html', form = register_form, error = error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('ID', None)
    return render_template('index.html')



@app.route('/main', methods=['POST', 'GET'])
def main_page():
    form_dict = {}
    output = []
    # [{'year': '1989', 'artist': 'Tom Petty', 'title': "Free Fallin'"}, {'year': '1989', 'artist': "Guns N' Roses", 'title': 'Patience'}]
    def display_musics(music_list):
        output.extend(music_list)

    query_form = QueryForm()

    if request.method == 'POST':
        if query_form.validate_on_submit():
            title = request.form.get('title')
            year = request.form.get('year')
            artist = request.form.get('artist')

            form_dict['title'] = title
            form_dict['year'] = year
            form_dict['artist'] = artist

            temp_status = dynamoDB.scan_music(MUSIC_TABLE, form_dict, display_musics)
            if temp_status == -1:
                error = 'You must input valid information!'
                return render_template('main.html', form=query_form, name=session['username'], error=error)

            if len(output) == 0:
                error = 'No result is retrieved. Please query again.'
                return render_template('main.html', form = query_form, name = session['username'], error = error)

            for j in output:
                img_name = j['img_url'].split("/")[-1]
                j['bucket_img_url'] = BUCKET_IMAGE_BASE + img_name

    return render_template('main.html', form = query_form, name = session['username'],  output = output)

@app.route("/addSubscribe", methods=['POST'])
def subscribe():

    # amounts = request.form.getlist('partition_key')
    item_ids = request.form.getlist('sort_key')

    select_partition_key = request.form['partition_key']
    select_sort_key = request.form['sort_key']

    response = dynamoDB.query_music_details(MUSIC_TABLE, select_partition_key, select_sort_key)[0]
    print(response)
    output = []
    output.append(response['title'])
    output.append(response['artist'])
    output.append(response['year'])
    img_name = response['img_url'].split("/")[-1]
    img_url= BUCKET_IMAGE_BASE + img_name
    output.append(img_url)


    dynamoDB.update_subscription_table(SUBSCRIPTION, session['ID'], output)

def __judge_status(id, pd):
    response = dynamoDB.query_user(USER_TABLE, id)

    if len(response) == 0:
        return False

    if pd != response[0]['password']:
        return False

    session['ID'] = response[0]['email']
    session['username'] = response[0]['user_name']

    return True


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
    dynamoDB.create_subscription_table(SUBSCRIPTION)

    if len(dynamoDB.query_user(USER_TABLE, 's38039900@student.rmit.edu.au')) == 0:
        __generate_users()
        for i in range(10):
            dynamoDB.put_user_data(USER_TABLE, user_dict[i][0], user_dict[i][1], user_dict[i][2])

    if len(dynamoDB.check_sp_table_status(SUBSCRIPTION,'s38039900@student.rmit.edu.au')) == 0:
        __generate_users()
        for i in range(10):
            dynamoDB.put_sb_music(SUBSCRIPTION, user_dict[i][0])

def load_music_info():
    music_table = dynamoDB.create_movie_table(MUSIC_TABLE)

    if len(dynamoDB.check_music_table_status(MUSIC_TABLE,'1904')) == 0:
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
