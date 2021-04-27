from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key
from dynamoDBConnection import DynamoDBConnection


def query_and_project_movies(title, title_range):
    # if not dynamodb:
    #     dynamodb = boto3.resource('dynamodb')
    dynamodb = DynamoDBConnection()

    table = dynamodb.dynamoDB.Table('Music')
    # print(f"Get year, title, genres, and lead actor")

    # Expression attribute names can only reference items in the projection expression.
    response = table.query(
        ProjectionExpression="title, artist, #yr",
        ExpressionAttributeNames={"#yr": "year"},
        KeyConditionExpression= Key('title').eq(title)
        # & Key('artist').between(title_range[0], title_range[1])
    )
    return response['Items']




if __name__ == '__main__':
    query_year = '1904'
    query_range = ('A', 'L')
    print(f"Get movies from {query_year} with titles from "
          f"{query_range[0]} to {query_range[1]}")
    musics = query_and_project_movies(query_year, query_range)
    for music in musics:
        print(f"\n{music['year']} : {music['title']}")
        print(music['artist'])

    temp_dict = {'Items':[3,2,1]}
    print(temp_dict.get('Items', None))
