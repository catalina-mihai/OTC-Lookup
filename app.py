from flask import Flask, render_template, request, jsonify
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

            # Log the fetched API data for debugging
            print("Fetched API data:", api_data)
            print("Processed dropdown data:", all_data)

            # Pass all_data to the template
            return render_template('index.html', all_data=all_data)
        else:
            return "Error fetching API data", 500

    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/get_filtered_data', methods=['POST'])
def get_filtered_data():
    try:
        # Get the selected asset class from the request
        asset_class = request.json.get('assetClass')

        # For debugging, print the selected asset class
        print(f"Selected Asset Class: {asset_class}")

        # Step 1: Get the access token
        access_token = get_access_token()

        # Step 2: Fetch data from the API
        api_data = fetch_api_data(access_token)

        # Step 3: Filter the data based on the selected asset class
        filtered_data = {
            'instrumentType': [],
            'useCase': [],
            'level': [],
            'templateVersion': []
        }

        for item in api_data:
            if item['assetClass'] == asset_class:
                filtered_data['instrumentType'].append(item['instrumentType'])
                filtered_data['useCase'].append(item['useCase'])
                filtered_data['level'].append(item['level'])
                filtered_data['templateVersion'].append(item['templateVersion'])

        # Remove duplicates from the filtered data
        filtered_data['instrumentType'] = list(set(filtered_data['instrumentType']))
        filtered_data['useCase'] = list(set(filtered_data['useCase']))
        filtered_data['level'] = list(set(filtered_data['level']))
        filtered_data['templateVersion'] = list(set(filtered_data['templateVersion']))

        # Log the filtered data for debugging
        print("Filtered Data:", filtered_data)

        return jsonify(filtered_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    try:
        # Get the submitted data
        data = request.json
        print("Search Data:", data)  # For debugging

        # Process the search request here
        # Example: Make another API call based on the received data
        # Replace the following line with the actual API endpoint and logic
        results = {"message": "Search executed successfully", "data": data}  # Mock response

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
