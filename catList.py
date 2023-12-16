
import requests
url = 'https://api.instashipin.com/api/v1/tenancy/authToken'
payload ={
    "api_key": "6092655223372029e7404dc4"
    }
headers = {
        'Content-Type': 'application/json',
    }
response = requests.post(url, json=payload, headers=headers)
if response.status_code == 200:
        data = response.json()
        token = data['data']['response']['token_id']    
        
url = 'https://api.instashipin.com/api/v1/courier-vendor/freight-calculator'
payload = {
        "token_id": token,
        "fm_pincode": "400075",
        "lm_pincode": '400052',
        "weight": "0.5",
        "payType": "PPD",
        "collectable": ""
    }

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
        # Request was successful
        data = response.json()
        deliveryCharges = data['data']['response']['total_freight']
        print( deliveryCharges)
else:
        # Request failed
        print(f"Error: {response.status_code}, {response.text}")
