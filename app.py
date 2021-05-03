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

# factory method to connect dynamoDB and bucket
dynamoDB = DynamoDBConnection()
bucket = BucketConnection()

# for login user info
user_dict = {}
MUSIC_TABLE = 'Music'
USER_TABLE = 'Login'
SUBSCRIPTION_TABLE = 'Subscribe'
BUCKET_NAME = 'musicimage25042021'
BUCKET_IMAGE_BASE ="https://" + BUCKET_NAME + ".s3.amazonaws.com/"


# default root to initialize system, including build music table, load user table
@app.route('/')
def root():
    load_music_info()
    load_users_info()
    image_handler(BUCKET_NAME)
    return render_template('index.html')

# user login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    query_form = QueryForm()
    if 'username' in session:

        sub_response = dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, session['ID'])[0]['sp_music']
        # print(sub_response)
        return render_template('main.html', name = session['username'], form = query_form, sub_output = sub_response)
    if request.method == 'POST':

        curr_id = request.form['ID']
        curr_pd = request.form['password']

        error = None

        if __judge_status(curr_id, curr_pd):


            sub_response = dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, session['ID'])[0]['sp_music']


            return render_template('main.html', name = session['username'], form = query_form, sub_output = sub_response)
        else:
            error = 'email or password is invalid'
            return render_template('index.html', error = error)
    return render_template('index.html')


# register users' info
@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    register_form = RegisterForm()

    if request.method == 'POST':
        if register_form.validate_on_submit():
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password1')

            # check whether this user has registered already
            response = dynamoDB.query_user(USER_TABLE, email)
            if len(response) == 0:
                # save users info and create new user for subscription table
                dynamoDB.put_user_data(USER_TABLE, email, username, password)
                dynamoDB.put_sb_music(SUBSCRIPTION_TABLE, email)

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

    # obtain all the subscription music info in the current user in the subscription table
    sub_response = dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, session['ID'])[0]['sp_music']

    # print(sub_response)
    # the shape of response = response['Items']
    # [{'year': '1989', 'artist': 'Tom Petty', 'title': "Free Fallin'"}, {'year': '1989', 'artist': "Guns N' Roses", 'title': 'Patience'}]
    def display_musics(music_list):
        output.extend(music_list)

    query_form = QueryForm()

    if request.method == 'POST':
        if query_form.validate_on_submit():
            # obtain all the waiting search music info
            title = request.form.get('title')
            year = request.form.get('year')
            artist = request.form.get('artist')

            # save all the info into
            form_dict['title'] = title
            form_dict['year'] = year
            form_dict['artist'] = artist

            # search music in scan ways
            temp_status = dynamoDB.scan_music(MUSIC_TABLE, form_dict, display_musics)
            if temp_status == -1:
                error = 'You must input valid information!'
                return render_template('main.html', form=query_form, name=session['username'], error=error, sub_output =sub_response)

            if len(output) == 0:
                error = 'No result is retrieved. Please query again.'
                return render_template('main.html', form = query_form, name = session['username'], error = error, sub_output =sub_response)

            # attach image info for each music
            for j in output:
                img_name = j['img_url'].split("/")[-1]
                j['bucket_img_url'] = BUCKET_IMAGE_BASE + img_name

    return render_template('main.html', form = query_form, name = session['username'],  output = output, sub_output =sub_response)

# remove sub info from sub table
@app.route("/removeSub", methods=['POST'])
def removeSub():
    # obtain details from
    item_id = request.form['sub_partition_key']
    item_artist = request.form['sub_sort_key']

    # obtain info from sub table for the current user
    response_list = dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, session['ID'])[0]['sp_music']
    # print('id',item_id)
    # print('item',item_artist)

    init_index = 0

    # check the location of saved info in the list (consider about the situation of same name of partition key and different name of sort key)
    while True:

        id_index = response_list.index(item_id, init_index, len(response_list))
        # print(response_list)
        if response_list[id_index+1] == item_artist:
            del response_list[id_index: id_index+4]
            break
        else:
            init_index = id_index + 1
            continue

    dynamoDB.update_subscription_table(SUBSCRIPTION_TABLE, session['ID'], response_list)

    return redirect(url_for('main_page'))


# save subscribe info
@app.route("/addSubscribe", methods=['POST'])
def subscribe():

    # amounts = request.form.getlist('partition_key')
    # item_ids = request.form.getlist('sort_key')

    # obtain user clicked info and submit by hidden ways
    select_partition_key = request.form['partition_key']
    select_sort_key = request.form['sort_key']

    # obtain all the info from music table and put it into subscribe table
    response = dynamoDB.query_music_details(MUSIC_TABLE, select_partition_key, select_sort_key)[0]
    # print(response)
    output = []
    output.append(response['title'])
    output.append(response['artist'])
    output.append(response['year'])
    img_name = response['img_url'].split("/")[-1]
    img_url= BUCKET_IMAGE_BASE + img_name
    output.append(img_url)


    sub_response = dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, session['ID'])[0]['sp_music']

    # check wether this music info has been saved in the subscribe table
    init_index = 0
    while True:
        id_index = -1
        if select_partition_key in sub_response:
            id_index = sub_response.index(select_partition_key, init_index, len(sub_response))
            artist_index = sub_response[id_index+1]

            if artist_index == select_sort_key:
                return redirect(url_for('main_page'))
            else:
                init_index = id_index +1
        else:
            # init_index = id_index+1
            # continue
            break

    output.extend(sub_response)

    # update info into subscription table
    dynamoDB.update_subscription_table(SUBSCRIPTION_TABLE, session['ID'], output)
    return redirect(url_for('main_page'))

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


# init users
def load_users_info():
    dynamoDB.create_login_table(USER_TABLE)
    dynamoDB.create_subscription_table(SUBSCRIPTION_TABLE)

    if len(dynamoDB.query_user(USER_TABLE, 's38039900@student.rmit.edu.au')) == 0:
        __generate_users()
        for i in range(10):
            dynamoDB.put_user_data(USER_TABLE, user_dict[i][0], user_dict[i][1], user_dict[i][2])

    if len(dynamoDB.check_sp_table_status(SUBSCRIPTION_TABLE, 's38039900@student.rmit.edu.au')) == 0:
        __generate_users()
        for i in range(10):
            dynamoDB.put_sb_music(SUBSCRIPTION_TABLE, user_dict[i][0])

# init music and upload to the table
def load_music_info():
    music_table = dynamoDB.create_movie_table(MUSIC_TABLE)

    if len(dynamoDB.check_music_table_status(MUSIC_TABLE,'1904')) == 0:
        print('load music again')

        with open('./file/a2.json') as json_file:
            music_list = json.load(json_file, parse_float = Decimal)

        temp_response = dynamoDB.load_data(music_table, music_list['songs'])

        pprint(temp_response, sort_dicts = False)
        print(temp_response['Item'])

# upload image info into S3 bucket
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
