"""This is a Python script that defines an AWS CloudFormation custom resource handler. It uses the boto3 library to
interact with AWS services based on the input event and responds to the CloudFormation service with the result of the
operation.

The script contains the following functions:

sendResponse(event, context, status, message): This function sends a response back to AWS CloudFormation after the
custom resource operation is completed. It takes the event, context, status, and message as arguments and creates an
HTTP PUT request with the response data.

execute(action, properties): This function takes an action and properties as arguments, performs the requested action
using boto3, and returns the result as a tuple (status, message). It first splits the action string into client and
function names, then creates a boto3 client, and finally calls the specified function with the provided properties.

handler(event, context): This is the main Lambda function handler. It takes event and context as arguments, processes
the input event, and calls the appropriate functions based on the request type and mode specified in the event."""

from urllib2 import build_opener, HTTPHandler, Request
import base64
import boto3
import httplib
import json

def sendResponse(event, context, status, message):
    body = json.dumps({
        "Status": status,
        "Reason": message,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "PhysicalResourceId": event["ResourceProperties"]["Action"],
        "Data": {},
    })

    request = Request(event['ResponseURL'], data=body)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(body))
    request.get_method = lambda: 'PUT'

    opener = build_opener(HTTPHandler)
    response = opener.open(request)

def execute(action, properties):
    action = action.split(".")

    if len(action) != 2:
        return "FAILED", "Invalid boto3 call: {}".format(".".join(action))

    client, function = action[0], action[1]

    try:
        client = boto3.client(client.lower())
    except Exception as e:
        return "FAILED", "boto3 error: {}".format(e)

    try:
        function = getattr(client, function)
    except Exception as e:
        return "FAILED", "boto3 error: {}".format(e)

    properties = {
        key[0].lower() + key[1:]: value
        for key, value in properties.items()
    }

    try:
        function(**properties)
    except Exception as e:
        return "FAILED", "boto3 error: {}".format(e)

    return "SUCCESS", "Completed successfully"

def handler(event, context):
    print("Received request:", json.dumps(event, indent=4))

    request = event["RequestType"]
    properties = event["ResourceProperties"]

    if any(prop not in properties for prop in ("Action", "Properties")):
        print("Bad properties", properties)
        return sendResponse(event, context, "FAILED", "Missing required parameters")

    mode = properties["Mode"]

    if request == mode or request in mode:
        status, message = execute(properties["Action"], properties["Properties"])
        return sendResponse(event, context, status, message)

    return sendResponse(event, context, "SUCCESS", "No action taken")