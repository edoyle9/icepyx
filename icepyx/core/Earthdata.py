import requests
import getpass
import socket
import re
import json

#DevNote: currently this class is not tested
class Earthdata():
    """
    Initiate an Earthdata session for interacting
    with the NSIDC DAAC.

    Parameters
    ----------
    uid : string
        Earthdata Login user name (user ID).
    email : string
        Complete email address, provided as a string.
    password : string (encrypted)
        Password for Earthdata registration associated with the uid.
    capability_url : string
        URL required to access Earthdata

    Returns
    -------
    Earthdata session object after a successful login
    """
        
    def __init__(
        self,
        uid,
        email,
        capability_url,
        pswd=None,
    ):
        
        assert isinstance(uid, str), "Enter your login user id as a string"
        assert re.match(r'[^@]+@[^@]+\.[^@]+',email), "Enter a properly formatted email address"
        
        self.uid = uid
        self.email = email
        self.capability_url = capability_url
        self.pswd = pswd

    def _start_session(self):
        #Request CMR token using Earthdata credentials
        token_api_url = 'https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens'
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        data = {'token': {'username': self.uid, 'password': self.pswd,\
                          'client_id': 'NSIDC_client_id','user_ip_address': ip}
        }
        
        response = None
        response = requests.post(token_api_url, json=data, headers={'Accept': 'application/json'})
        
        #check for a valid login
        try:
            json.loads(response.content)['token']
        except KeyError: 
            try:
                print(json.loads(response.content)['errors'])
            except KeyError:
                print("There are no error messages, but an Earthdata login token was not successfully generated")
        
        token = json.loads(response.content)['token']['id']

        session = requests.session()
        s = session.get(self.capability_url)
        response = session.get(s.url,auth=(self.uid,self.pswd))

        self.session = session

    def login(self):
        """
        This function tries to log the user in to Earthdata with the
        information provided. It prompts the user for their Earthdata password,
        but will only store that information within the active session.
        If the login fails, it will ask the user to re-enter their
        username and password up to five times to try and log in.

        Examples
        --------
        >>> icepyx.core.Earthdata.Earthdata.login('sam.smith','sam.smith@domain.com')
        Earthdata Login password:  ········
        """
        self.pswd = getpass.getpass('Earthdata Login password: ')
        for i in range(5):
            try:
                session = self._start_session()
                break
            except KeyError:
                self.uid = input("Please re-enter your Earthdata user ID: ")
                self.pswd = getpass.getpass('Earthdata Login password: ')
                i = i+1
                
        else:
            raise RuntimeError("You could not successfully log in to Earthdata")
        
        return self.session


#DevGoal: try turning this into a class that uses super... an initial attempt at portions of this is below
"""
class Earthdata(requests.Session):
        
    def __init__(self, uid = uid, email = email,pswd = None):
        super(Earthdata, self).__init__() 

        assert isinstance(uid, str), "Enter your login user id as a string"
        assert re.match(r'[^@]+@[^@]+\.[^@]+',email), "Enter a properly formatted email address"
"""
