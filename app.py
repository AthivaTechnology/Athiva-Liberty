import os
import sys
from jinja2 import Environment, FileSystemLoader
import boto3
from boto3.dynamodb.conditions import Key
import json
import requests
import jwt



dynamodb = boto3.resource('dynamodb')

table_name = "transactions"
table = dynamodb.Table(table_name)




def lambda_handler(event, context):

    token = event['authorizationToken']

    decoded = jwt.decode(token, options={"verify_signature": False})

    operator_name=decoded['name']



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

            response = table.put_item(
                Item={
                    "Operator Name": operator_name,
                    }
            )


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
    
    
    event = {}

    lambda_handler(event,'')