import requests

a = requests.post(
    url="https://js7blycjtd.execute-api.us-east-1.amazonaws.com/default/triple_barrier_meta_labeling",
    # headers={
    #     "x-api-key": "deGg5GILeox1bh9R3rQc8U7lmDZ7JEj8JpKML8uj",
    #     "api-key": "deGg5GILeox1bh9R3rQc8U7lmDZ7JEj8JpKML8uj"
    # },
    json={
  "invocationId": "invocationIdExample",
  "deliveryStreamArn": "arn:aws:kinesis:EXAMPLE",
  "region": "us-east-1",
  "records": [
    {
      "recordId": "49546986683135544286507457936321625675700192471156785154",
      "approximateArrivalTimestamp": 1495072949453,
      "data": "SGVsbG8sIHRoaXMgaXMgYSB0ZXN0IDEyMy4="
    }
  ]
}

)
print(a)
print(a.content)
print(a.text)
print(a.json())
