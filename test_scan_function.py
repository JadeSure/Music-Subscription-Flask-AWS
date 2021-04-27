from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key


def scan_movies1(year_range, display_movies, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('Music')
    scan_kwargs = {
        'FilterExpression': Key('year').between(*year_range),
        'ProjectionExpression': "#yr, title, artist",
        'ExpressionAttributeNames': {"#yr": "year"}
    }

    done = False
    start_key = None
    while not done:
        if start_key:
            print('processing me')
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        display_movies(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        print(start_key)
        done = start_key is None



def scan_movies2(year_range, display_movies, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('Music')
    scan_kwargs = {
        'FilterExpression': Key('year').eq(year_range[0]),
        'ProjectionExpression': "#yr, title, artist",
        'ExpressionAttributeNames': {"#yr": "year"}
    }

    done = False
    start_key = None
    while not done:
        if start_key:
            print('processing me')
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        display_movies(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        print(start_key)
        done = start_key is None


if __name__ == '__main__':
    def print_movies(movies):
        type(movies)
        print(movies)
        # for movie in movies:
        #     print(f"\n{movie['year']} : {movie['title']}")
        #     pprint(movie['artist'])


    query_range = ('1989', '1990')
    print(f"Scanning for movies released from {query_range[0]} to {query_range[1]}...")
    scan_movies1(query_range, print_movies)

    # scan_movies2()
