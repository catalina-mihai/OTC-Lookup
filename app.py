from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Function for the access token using OAuth2
#API response
#-if API request is successful. the response data is returned as a JSON object
#-if there is an error, and exception is raised
def get_access_token():
    api_domain_uri = "https://api.regtechdatahub.com/connect/token"
    client_id = "client"
    client_secret = ""
    scope = "api1"
    username = "CAT"
    password = "Humr2"



    # OAuth2 token request payload
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "username": username,
        "password": password
    }

    response = requests.post(api_domain_uri, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception(f"Error fetching access token: {response.text}")

# Function to fetch data from the API using the access token
# Function to fetch data from the API using the access token
#-app calls the fetch_api_data()
    #this function constructs the API endpoint URL fx: "api/OtcInstruments/Template/Headers"
    #it prepares the headers for GET request, including the Authorization header with the access token
# Function to fetch data from the API using the access token
def fetch_api_data(access_token):
    api_url = "https://api.regtechdatahub.com/api/OtcInstruments/Template/Headers"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data from API: {response.text}")

# Function to make a POST request to fetch attributes based on user input
def fetch_attributes_data(access_token, asset_class, instrument_type, use_case, level, template_version):
    api_url = "https://api.regtechdatahub.com/api/OtcInstruments/Template/Attributes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "assetClass": asset_class,
        "instrumentType": instrument_type,
        "useCase": use_case,
        "level": level,
        "templateVersion": template_version
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching attributes from API: {response.text}")
        
# Function to fetch data from the API using the access token
def fetch_instrument_data(access_token, payload):
    api_url = "https://api.regtechdatahub.com/api/OtcInstruments/Template/Instruments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching instruments from API: {response.text}")

        
@app.route('/find', methods=['POST'])
def find():
    try:
        # Obtain access token
        access_token = get_access_token()

        # Extract JSON data sent from the client-side
        data = request.json

        # Collect header information from the form data
        asset_class = data.get('assetClass')
        instrument_type = data.get('instrumentType')
        use_case = data.get('useCase')
        level = data.get('level')
        template_version = data.get('templateVersion')

        # Collect dynamic fields from the "attributes" section
        dynamic_fields = data.get('dynamicFields', {})

        # Build the payload according to the required structure
        payload = {
            "header": {
                "assetClass": asset_class,
                "instrumentType": instrument_type,
                "useCase": use_case,
                "level": level,
                "templateVersion": template_version
            },
            "instrumentLimit": 5,  # Adjust as per your requirements
            "templateSearchDirection": "HighestToLowest",
            "extractAttributes": True,
            "extractDerived": True,
            "expiryDatesSpans": 1,
            "deriveCfiCodeProperties": True,
            "attributes": dynamic_fields  # Dynamic fields collected from the client-side
        }

        # Fetch instrument data using the constructed payload
        instrument_data = fetch_instrument_data(access_token, payload)

        # Return the instrument data as JSON
        return jsonify(instrument_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/')
def index():
    try:
        access_token = get_access_token()
        api_data = fetch_api_data(access_token)

        if api_data:
            all_data = {
                'assetClass': [],
                'instrumentType': {},
                'useCase': {},
                'level': {},
                'templateVersion': {}
            }

            for item in api_data:
                asset_class = item['assetClass']
                instrument_type = item['instrumentType']
                use_case = item['useCase']
                level = item['level']
                template_version = item['templateVersion']

                if asset_class not in all_data['assetClass']:
                    all_data['assetClass'].append(asset_class)

                if asset_class not in all_data['instrumentType']:
                    all_data['instrumentType'][asset_class] = []
                if instrument_type not in all_data['instrumentType'][asset_class]:
                    all_data['instrumentType'][asset_class].append(instrument_type)

                if asset_class not in all_data['useCase']:
                    all_data['useCase'][asset_class] = {}
                if instrument_type not in all_data['useCase'][asset_class]:
                    all_data['useCase'][asset_class][instrument_type] = []
                if use_case not in all_data['useCase'][asset_class][instrument_type]:
                    all_data['useCase'][asset_class][instrument_type].append(use_case)

                if asset_class not in all_data['level']:
                    all_data['level'][asset_class] = {}
                if instrument_type not in all_data['level'][asset_class]:
                    all_data['level'][asset_class][instrument_type] = {}
                if use_case not in all_data['level'][asset_class][instrument_type]:
                    all_data['level'][asset_class][instrument_type][use_case] = []
                if level not in all_data['level'][asset_class][instrument_type][use_case]:
                    all_data['level'][asset_class][instrument_type][use_case].append(level)

                if asset_class not in all_data['templateVersion']:
                    all_data['templateVersion'][asset_class] = {}
                if instrument_type not in all_data['templateVersion'][asset_class]:
                    all_data['templateVersion'][asset_class][instrument_type] = {}
                if use_case not in all_data['templateVersion'][asset_class][instrument_type]:
                    all_data['templateVersion'][asset_class][instrument_type][use_case] = {}
                if level not in all_data['templateVersion'][asset_class][instrument_type][use_case]:
                    all_data['templateVersion'][asset_class][instrument_type][use_case][level] = []
                if template_version not in all_data['templateVersion'][asset_class][instrument_type][use_case][
                    level]:
                    all_data['templateVersion'][asset_class][instrument_type][use_case][level].append(
                        template_version)

            # Sort lists alphabetically on the backend
            all_data['assetClass'].sort(key=lambda x: x.lower())  # Sort Asset Class
            for key in all_data['instrumentType']:
                all_data['instrumentType'][key].sort(key=lambda x: x.lower())  # Sort Instrument Type
            for key in all_data['useCase']:
                for sub_key in all_data['useCase'][key]:
                    all_data['useCase'][key][sub_key].sort(key=lambda x: x.lower())  # Sort UseCase
            for key in all_data['level']:
                for sub_key in all_data['level'][key]:
                    for sub_sub_key in all_data['level'][key][sub_key]:
                        all_data['level'][key][sub_key][sub_sub_key].sort(key=lambda x: x.lower())  # Sort Level
            for key in all_data['templateVersion']:
                for sub_key in all_data['templateVersion'][key]:
                    for sub_sub_key in all_data['templateVersion'][key][sub_key]:
                        for sub_sub_sub_key in all_data['templateVersion'][key][sub_key][sub_sub_key]:
                            all_data['templateVersion'][key][sub_key][sub_sub_key][sub_sub_sub_key].sort(key=lambda x: x.lower())  # Sort TemplateVersion

            print("Fetched and sorted API data:", all_data)  # Debugging output
            return render_template('index.html', all_data=all_data)
        else:
            return "Error fetching API data", 500
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        access_token = get_access_token()

        asset_class = data.get('assetClass')
        instrument_type = data.get('instrumentType')
        use_case = data.get('useCase')
        level = data.get('level')
        template_version = data.get('templateVersion')

        attributes_data = fetch_attributes_data(
            access_token, asset_class, instrument_type, use_case, level, template_version
        )

        return jsonify(attributes_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  
