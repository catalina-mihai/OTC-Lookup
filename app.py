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
    #GET request is sent
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
                if template_version not in all_data['templateVersion'][asset_class][instrument_type][use_case][level]:
                    all_data['templateVersion'][asset_class][instrument_type][use_case][level].append(template_version)

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






#Frontend Interaction
#-the index.html template contains the HTML structure, including dropdown menus which will be populated with data from API
#-JavaScript code handles dropdowns which are interrelated.
    #when user chooses an option from the first dropdown, a JavaScript function is triggered
    #this function modifies the second dropdown's available options based on user selection, so only relevant choises are presented

#Initial Page Load (First GET request)
#-populates the initial dropdown menus with assetClass, instrumentType, useCase, level and templateVersion
#-fetched data will be stored in memory (session storage) on the client side
#-user will make selections one by onw from the dropdowns and based on the choices, the subsequent available options are changed dynamically
#-user continues to make choices across the first 4 dropdown, the fifth one not being mandatory.
#-if user does make the choice to fill in the template.Version then that will have repercursions on the options after the second API call. If left blank, all the options available will be displayed

#Automatic triggered event? / Button: POST request
#-POST request sends users choices as parameters, server sends these selections to external API which in turn returns additional options to populate the next set of dropdowns
#-Server Side: Use the access token to make another POST request to the API, sending the user's initial selections to retrieve additional dropdown options.
#-Server Side: Process the API response and update the data structure accordingly.
#-JavaScript gathers all selected values, AJAX POST request to a designated endpoint (/additional_dropdowns)
#- define a new Flask route (/additional_dropdowns.html)to generate the HTML for the new dropdowns based on the API  response
#-send the rendered HTML back to the client as part of the AJAX response

#Render Updated page
#- inject additional dropdowns/fields. Upon successful AJAX response from the server, the returned HTML snippet (additional_dropdowns.html) is injected into the designated placeholder (#additionalDropdowns)
#- the user interacts with input fields, dropsdowns, dates etc
#-JavaScript doesn't need to dynamically updated other fields based on selections because in the additional selections is always the same number of options

#SEARCH button, AJAX POST request
#- JavaScript sends collected data to the server to a designated endpoint (/search)

#Server fetches SEARCH results
#-

#Render results to user

#The dynamically changing fields based on user input will indeed affect what you send to the API, and that needs to be handled carefully. Here's a detailed breakdown of how the dynamic nature of your inputs influences the request payload and how we can ensure that the API receives the correct information:
"""

Flask is running in debug=True. While this is helpful during development, make sure to disable it in production to avoid leaking sensitive information.
"""
