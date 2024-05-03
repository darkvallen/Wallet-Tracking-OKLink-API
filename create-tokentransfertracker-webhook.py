import requests

API_KEY = "YOUR_OKLINK_API_KEY"
WEBHOOK_ID = "YOUR_WEBHOOK_ID" #Get by creating Webhook Listener on https://public.requestbin.com/r

data = {
   "event": "tokenTransfer",
   "chainShortName": "eth",
   "webhookUrl": f"https://{WEBHOOK_ID}.x.pipedream.net/",
   "trackerName": "TokenTransferTracker",
   "addresses": [
       "0x42EDb543156a41dA9237c4e3408eDCeb9e1f23Fb",
       "0xe3C7adcCc2f42D41c0ce017d2984c34fd9bBb480",
       "0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5"
   ]
}

url = "https://www.oklink.com/api/v5/explorer/webhook/create-address-activity-tracker"
headers = {
    "OK-ACCESS-KEY": API_KEY
}
# Send the POST request
response = requests.post(url, json=data, headers=headers)

# Check and handle the response
if response.status_code == 200:
    data = response.json().get('data', [])
    print("Webhook configuration sent successfully")
    print(data)
    print(f"Monitoring : https://public.requestbin.com/r/{WEBHOOK_ID}")

   
   
   # Process success response if needed
else:
   print("Request failed:", response.status_code, response.text)
