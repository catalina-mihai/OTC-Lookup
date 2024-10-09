from flask import Flask, render_template
import requests

app = Flask(__name__)

# Function to get the access token using OAuth2
def get_access_token():
    api_domain_uri = "https://api.regtechdatahub.com/connect/token"
    client_id = "client"
    client_secret = ""  # Add your client secret here


    # OAuth2 token request payload
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "username": username,
        "password": password
    }

    # Make a POST request to get the access token
    response = requests.post(api_domain_uri, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print(access_token)
        return access_token
    else:
        raise Exception(f"Error fetching access token: {response.text}")

# Function to fetch data from the API using the access token
def fetch_api_data(access_token):
    api_url = "https://api.regtechdatahub.com/api/OtcInstruments/Template/Headers"  # Replace with the actual API endpoint

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Make a GET request to the API
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Assuming the API returns JSON
    else:
        raise Exception(f"Error fetching data from API: {response.text}")

@app.route('/')
def index():
    try:
        # Step 1: Get the access token
        access_token = get_access_token()

        # Step 2: Fetch data from the API
        api_data = fetch_api_data(access_token)
        print(api_data)
        
        if api_data:
            # Prepare a structure to hold dropdown options
            all_data = {
                'assetClass': [],
                'instrumentType': [],
                'useCase': [],
                'level': [],
                'templateVersion': []
            }

            # Populate the dropdown options based on the API response
            for item in api_data:
                all_data['assetClass'].append(item['assetClass'])
                all_data['instrumentType'].append(item['instrumentType'])
                all_data['useCase'].append(item['useCase'])
                all_data['level'].append(item['level'])
                all_data['templateVersion'].append(item['templateVersion'])

            # Remove duplicates (optional)
            all_data['assetClass'] = list(set(all_data['assetClass']))
            all_data['instrumentType'] = list(set(all_data['instrumentType']))
            all_data['useCase'] = list(set(all_data['useCase']))
            all_data['level'] = list(set(all_data['level']))
            all_data['templateVersion'] = list(set(all_data['templateVersion']))

            # Pass all_data to the template
            
            return render_template('index.html', all_data=all_data)
        else:
            return "Error fetching API data", 500
            
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)
