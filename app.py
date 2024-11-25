from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from flask_cors import CORS
import requests
import logging
import os
import json
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key')  # Change in production

# Set up logging to file
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_access_token():
    """Get token from session or raise error"""
    if 'access_token' not in session:
        raise Exception("No valid token. Please log in.")
    return session['access_token']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        # OAuth2 token request
        api_domain_uri = "https://api.regtechdatahub.com/connect/token"
        data = {
            "grant_type": "password",
            "client_id": "client",
            "client_secret": "",
            "scope": "api1",
            "username": username,
            "password": password
        }

        response = requests.post(api_domain_uri, data=data)

        if response.status_code == 200:
            token_data = response.json()
            session['access_token'] = token_data.get('access_token')
            session['token_expiry'] = time.time() + token_data.get('expires_in', 3600)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', 
                                 error="Invalid credentials. Please check your api.regtechdatahub.com username and password.")

    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return render_template('login.html', 
                             error="An error occurred during login. Please try again.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
        response_json = response.json()
        # Load field hierarchy from JSON file
        def load_field_hierarchy():
            hierarchy_path = 'field_hierarchy.json'
            
            if not os.path.exists(hierarchy_path):
                logging.error("field_hierarchy.json does not exist in the expected path.")
                print("field_hierarchy.json does not exist.")
                return {}

            try:
                with open(hierarchy_path, 'r') as file:
                    field_hierarchy = json.load(file)
                    logging.info("Field hierarchy loaded successfully.")
                    print("Field hierarchy loaded successfully.")
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding error: {e}")
                print("JSON decoding error:", e)
                field_hierarchy = {}
            
            return field_hierarchy

        # Add field hierarchy, correlation ID, and date to response JSON
        field_hierarchy = load_field_hierarchy()
        response_json['field_hierarchy'] = field_hierarchy


        # Log final response
        logging.info(f"Final Response JSON: {json.dumps(response_json, indent=4)}")
        print(response_json)

        return response_json
    else:
        raise Exception(f"Error fetching attributes from API: {response.text}")
           
def fetch_instrument_data(access_token, payload):
    api_url = "https://api.regtechdatahub.com/api/OtcInstruments/Template/Instruments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # Log the headers being sent
    logging.info(f"Request Headers: {headers}")

    # Log the payload being sent
    logging.info(f"Request Payload: {payload}")
    response = requests.post(api_url, headers=headers, json=payload)
    print('x-correlation-id:', response.headers['x-correlation-id'])
    print('date:', response.headers['date'])
    logging.info(f"API Response Status: {response.status_code}")

    logging.info(f"x-correlation-id: {response.headers.get('x-correlation-id')}")
    logging.info(f"Date header: {response.headers.get('date')}")
    logging.info(f"API Response Status: {response.status_code}")
    logging.info(f"API Response Text: {response.text}")
    response = requests.post(api_url, headers=headers, json=payload)
    correlation_id = response.headers.get('x-correlation-id')
    date = response.headers.get('date')
    print('response', response)
    print('date:', date)

    # logging.info(f"response1 {response.text"})
    if response.status_code == 200:

        #                  response['instruments']['no instruments found']=
        #                           {"identifier": 'no instruments', 
        #                           "attributes" : payload.attributes, 
        #                         "derived" : payload.header}

        # Inject correlation_id directly into the JSON response before returning
        response_json = response.json()
        print(response_json)
                # Load field hierarchy from JSON file
 

        # Modify response if no instruments are found
        if response_json.get('instrumentCount', 0) == 0:
            no_instruments = {
                "identifier": "No instruments",
                "annaDsbStatus": "",
                "classificationType": "",
                "lastUpdateDateTime": date,
                "attributes": payload.get('attributes', {}),
                "derived": payload.get('header', {})
            }
            response_json['instruments'] = {"no instruments found": no_instruments}
            logging.info("No instruments found; default instrument information added.")


        logging.info(f"response1 {response_json}")
        print(response_json)

        response_json['correlation_id'] = correlation_id
        response_json['date'] = date
        logging.info(f"Final Response JSON: {json.dumps(response_json, indent=4)}")
        print(response_json)

        return response_json
    else:
        logging.error(f"API returned an error: {response.text}")
        print('API returned an error', response.text)
        raise Exception(f"Error fetching instruments from API: {response.text}")


@app.route('/find', methods=['POST'])
@login_required
def find():
    try:
        # Obtain access token
        access_token = get_access_token()

        # Extract JSON data sent from the client-side
        data = request.json

        # Collect header information from the nested 'header' section
        header = data.get('header', {})
        asset_class = header.get('assetClass')
        instrument_type = header.get('instrumentType')
        use_case = header.get('useCase')
        level = header.get('level')
        template_version = header.get('templateVersion')
        
        # Log the header details being processed
        logging.info(f"Header details - Asset Class: {asset_class}, Instrument Type: {instrument_type}, "
                     f"Use Case: {use_case}, Level: {level}, Template Version: {template_version}")

        # Collect dynamic fields from the "attributes" section
        dynamic_fields = data.get('attributes', {})
        logging.info(f"Dynamic attributes received: {dynamic_fields}")

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

        # Log the payload to see what is being sent
        logging.info(f"Payload being sent to the API: {payload}")

        # Fetch instrument data using the constructed payload
        instrument_data = fetch_instrument_data(access_token, payload)
        logging.info("Instrument data successfully fetched from API")
        # Return the instrument data as JSON
        return jsonify(instrument_data)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/otc-lookup')
@login_required
def otc_lookup():
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

            #print("Fetched and sorted API data:", all_data)  # Debugging output
            return render_template('otc-lookup.html', all_data=all_data)
        else:
            return "Error fetching API data", 500
    except Exception as e:
        return f"An error occurred: {e}"
@app.route('/')
@login_required
def index():
    return redirect(url_for('otc_lookup'))

@app.route('/search', methods=['POST'])
@login_required
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
