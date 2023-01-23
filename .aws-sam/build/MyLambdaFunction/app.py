import os
import sys
from jinja2 import Environment, FileSystemLoader
import boto3
from boto3.dynamodb.conditions import Key
import json
import requests
import jwt
from urllib import parse
import os

from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ['TABLE_NAME']

table = dynamodb.Table(TABLE_NAME)


def get_dynamo_item(pk, sk):
    get_data = table.get_item(
        Key={
            'pk': pk,
            'sk': sk
        }
    )

    if 'Item' in get_data:
        return get_data['Item']
    return None


def lambda_handler(event, context):
    print(event)
    token = event['headers']['x-amzn-oidc-data']

    decoded = jwt.decode(token, options={"verify_signature": False})

    operator_name = decoded['name']

    print("Operator name: {} ".format(operator_name))

    if 'httpMethod' in event and event['httpMethod'] == 'POST':

        body = parse.parse_qs(event['body'])

        print("body: {} ".format(json.dumps(body)))

        pk = body['pk'][0]
        sk = body['sk'][0]
        status = body['send_status'][0]

        old_item = get_dynamo_item(pk, sk)

        if old_item is None or status not in ('enqueued', 'blocked') or old_item['send_status'] == status:
            return error_response("Update Not Allowed!")

        message = "default message"

        if 'message' in body:
            message = body['message']
        try:
            update_response = table.update_item(
                Key={'pk': pk,
                     'sk': sk},
                UpdateExpression='SET send_status = :send_status, operator_name= :operator_name, message= :message',
                ConditionExpression='attribute_exists(pk) AND attribute_exists(sk) AND send_status =:old_status',
                ExpressionAttributeValues={
                    ':send_status': status,
                    ':operator_name': operator_name,
                    ':message': message,
                    ':old_status': old_item['send_status']
                },

                ReturnValues="UPDATED_NEW"
            )
            print(response)
        except Exception as e:
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

        return {
            "statusCode": 200,
            "body": json.dumps(update_response),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        }
    elif event['path'] == '/logout':
        response1 = {
            "statusCode": 302,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Set-Cookie": "AWSELBAuthSessionCookie-0=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; domain=.dev.pennysaver.in; HttpOnly; Secure"
            },
            "body": json.dumps({"message": "Logged out successfully"})
        }
        return response1
    else:
        env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"), encoding="utf8"))

        # print(json.dumps(event))

        if "queryStringParameters" in event and "pk" in event["queryStringParameters"] and "sk" in event[
            "queryStringParameters"]:
            pk = event["queryStringParameters"]["pk"]
            sk = event["queryStringParameters"]["sk"]
            print(pk)
            print(sk)

            template = env.get_template("index.html")

            get_data = table.get_item(
                TableName="transactions",
                Key={
                    'pk': pk,
                    'sk': sk
                }
            )

            item = {}

            if 'Item' in get_data:
                item = get_data['Item']

            html = template.render(
                data=item
            )
            print(item)
            return response(html)



def response(myhtml):
    return {
        "statusCode": 200,
        "body": myhtml,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    }


def error_response(msg):
    return {
        "statusCode": 400,
        "body": msg,
        "headers": {
            "Content-Type": "text/html",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    }


if __name__ == '__main__':
    event = {}

    lambda_handler(event, '')
