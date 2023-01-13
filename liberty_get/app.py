import os
import sys
from jinja2 import Environment, FileSystemLoader
import boto3
from boto3.dynamodb.conditions import Key
import json
import requests
import jwt

session = boto3.Session(profile_name='my-develop-profile')

dynamodb = session.resource('dynamodb','ap-south-1')

table_name = "transactions"
table = dynamodb.Table(table_name)




def lambda_handler(event, context):
    if 'httpMethod' in event and event['httpMethod']=='POST':
    
        #print(event)

        body=json.loads(event['body'])
        pk=body['pk']
        sk=body['sk']
        status=body['send_status']
        responce = table.update_item(
                Key={'pk':pk,
                    'sk':sk},
                UpdateExpression="SET send_status = :send_status",
                ExpressionAttributeValues={
                        ':send_status': status
                    },
                ReturnValues="UPDATED_NEW"
                )
        print(responce)
            
        return {
            "statusCode": 200,
            "body": json.dumps({"key":"value"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
                }
            }
    else:
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"), encoding="utf8"))
        
        # print(json.dumps(event))
   
        if "queryStringParameters" in event and "pk" in event["queryStringParameters"] and "sk" in event["queryStringParameters"]:
            pk = event["queryStringParameters"]["pk"]
            sk = event["queryStringParameters"]["sk"]
            print(pk)
            print(sk)
        
        


            template = env.get_template("index.html")

            


            get_data = table.get_item(
                TableName="transactions",
            Key={
                'pk':pk,
                'sk':sk
            }
            )

            html = template.render(
            items=get_data
            )
        
            print(get_data)
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

if __name__=='__main__':
    
    
    event = {
    "requestContext": {
        "elb": {
            "targetGroupArn": "arn:aws:elasticloadbalancing:ap-south-1:301838289846:targetgroup/Libert-MyTar-4FB3DKK33DBI/fab264f515218b9a"
        }
    },
    "httpMethod": "POST",
    "path": "/",
    "queryStringParameters": {},
    "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-length": "77",
        "content-type": "application/json",
        "host": "www.dev.pennysaver.in",
        "postman-token": "56b10ea6-3254-4638-ad69-7fd99ebf0126",
        "user-agent": "PostmanRuntime/7.30.0",
        "x-amzn-trace-id": "Root=1-63bfe358-42c790dd041f59fc6e48b09c",
        "x-forwarded-for": "117.206.137.132",
        "x-forwarded-port": "443",
        "x-forwarded-proto": "https"
    },
    "body": "{\r\n    \"pk\":\"dlmdlmd\",\r\n    \"sk\":\"63bc\",\r\n    \"send_status\":\"Success\"\r\n}",
    "isBase64Encoded": False
    }

    lambda_handler(event,'')