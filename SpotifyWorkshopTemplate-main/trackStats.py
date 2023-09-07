# File used to connect with the API
from requests import post, get
import json
from urllib.parse import urlencode

import base64
from dotenv import load_dotenv
import os
import datetime 

# Accessing Information from your .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

class SpotifyAPI(object):

    # Our Access Token Need to Make Requests to the Spotify Web API
    access_token = None
    # The time when our Access Token Will Expire
    access_token_expires = None
    # A boolean value indicating whether our access token is Expired or Not
    access_token_expired = True
    # Our Client ID
    client_id = None
    # Our Client Secret
    client_secret = None
    # The Endpoint to Request a Token
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_creds(self):

        """
            Returns a base64 encoded string
        """

        client_id = self.client_id
        client_secret = self.client_secret
        # Ensuring client_id and client_secrets have values
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client secret")
        # Auth String BEFORE encoding
        auth_string = client_id + ":" + client_secret
        # This is currently a string, but to encode the string using base64, we need to convert it into BYTES
        # Convert the String Into Bytes
        auth_bytes = auth_string.encode()
        # Encode String in Base64
        encoded_auth = base64.b64encode(auth_bytes)

        return encoded_auth.decode()

    ############################
    #   SET UP TOKEN HEADERS   #
    ############################

    def get_token_header(self):

        """
            Returns the headers necessary to request an access token
        """
        
        client_creds_b64 = self.get_client_creds()

        return {
            # INSERT: TOKEN HEADERS    
            "Authorization": "Basic " + client_creds_b64,
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    ############################
    #     SET UP TOKEN DATA    #
    ############################

    def get_token_data(self):

        """
            Returns the data necessary to request an access token
        """

        return {
            # INSERT: TOKEN DATA
            "grant_type": "client_credentials",
        }

    ############################
    # RETRIEVE AN ACCESS TOKEN #
    ############################

    def perform_auth(self):

        """
            Returns True if an access token is successfully obtained
        """

        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_header()

        # INSERT: Performing the Request
        response = post(token_url, data=token_data, headers=token_headers)

        # INSERT: Check if Request is Valid
        valid_request = response.status_code in range(200, 299)

        if not valid_request:
            print(response.status_code)
            raise Exception("Could not authenticate Client")

        # INSERT: Pulling Necessary Data from the Response
        now = datetime.datetime.now()
        data = response.json()
        print(data)
        # INSERT: Access Token
        access_token = data["access_token"]
        self.access_token = access_token
        # INSERT: Expires In
        expires_in = data["expires_in"]
        # INSERT: The time when the token will expire
        expires = now + datetime.timedelta(seconds=expires_in)
        print(expires)
        self.access_token_expires = expires
        self.access_token_expired = False
        
        return True

    def get_access_token(self):

        """
            Retrieves the current access token; refreshes the token if it is expired
        """

        auth_done = self.perform_auth()
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    ###############################
    #   SET UP RESOURCE HEADERS   #
    ###############################

    def get_resource_header(self):

        """
            Retrieve the headers necessary to make an authenticated API call
        """

        access_token = self.get_access_token()

        headers = {
            #INSERT: RESOURCE HEADERS
            "Authorization" : "Bearer " + access_token,
            "Content-Type": "application/json"
        }

        return headers

    #######################################################
    # Performing a Search Query Given A Track & An Artist #
    #######################################################

    def search(self, query=None, search_type='track'):
        """
            Returns the JSON response of an request made to the Search endpoint
        """

        if query == None:
            raise Exception("A query is required")
        
        if isinstance(query, dict):
            #turns a dictionary into a list
            query_list = [ k + ":" + v for k,v in query.items()]
            query = " ".join(query_list)

        query_params = urlencode({"q": query, "type": search_type.lower(), "limit": "1"})

        headers = self.get_resource_header()

        # INSERT: The Endpoint we wish to Query
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = endpoint + "?" + query_params

        # INSERT: The GET Request
        response = get(lookup_url, headers=headers)
        
        if response.status_code not in range(200,299):
            return {}
        
        return response.json()
    
    ######################################
    # PERFORMING AN AUDIO ANALYSIS QUERY #
    ######################################

    def get_audio_analysis(self, _id):
        """
            Returns the JSON response of an request made to the Audio Analysis
        """

        if _id == None:
            raise Exception("An id is required")

        headers = self.get_resource_header()
        
        # INSERT: The Endpoint we wish to Query
        endpoint = "https://api.spotify.com/v1/audio-features/"
        lookup_url = endpoint + str(_id)

        # INSERT: The GET Request
        response = get(lookup_url, headers=headers)

        if response.status_code not in range(200,299):
            return {}
        
        return response.json()

spotify = SpotifyAPI(client_id, client_secret)
spotify.perform_auth()


# type python3 dashFrontend.py to run