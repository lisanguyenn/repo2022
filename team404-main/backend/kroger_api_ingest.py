import requests
from requests.auth import HTTPBasicAuth
from requests_oauth2client import BearerToken
from requests_oauth2client import OAuth2Client
from requests_oauth2client import OAuth2ClientCredentialsAuth

import os
import json

kroger_token_url = "https://api.kroger.com/v1/connect/oauth2/token?grant_type=client_credentials&scope=product.compact"
kroger_base_url = "https://api.kroger.com/v1/"

client_id = os.environ['KROGER_CLIENT_ID']
client_secret = os.environ['KROGER_CLIENT_SECRET']

scope_endpoint = "product.compact"

def get_oauthclient(token_url, client_id, client_secret):
  oauth2client = OAuth2Client(
    token_endpoint = token_url,
    auth =(client_id, client_secret)
  )
  return oauth2client

def get_location_session(oauth):
  auth = OAuth2ClientCredentialsAuth(
    oauth
  )
  session = requests.Session()
  session.auth = auth 
  return session

def query_location_from_session(session, zipcode, radius_in_miles = None, limit = None, chain = None):
  #TODO: input validation
  payload = {"filter.zipCode.near": str(zipcode)}  
  
  if limit != None:
    payload['filter.limit'] = str(limit) 
  if radius_in_miles != None:
    payload['filter.radiusInMiles'] = str(radius_in_miles)
  if chain != None:
    payload['filter.chain'] = str(chain)

  resp = session.get(kroger_base_url+"/locations", params=payload)
  return resp

def query_price_from_session(session, search_term, location_id, limit = None):
   #TODO: input validation
  """Using a location_id, query products along with their price at a location"""
  payload = {"filter.locationId" : str(location_id), "filter.term" : str(search_term)}
  
  if limit != None:
    payload['filter.limit'] = str(limit) 

  resp = session.get(kroger_base_url+"/products", params=payload)
  return resp
  


if __name__ == "__main__":
  location_id = None

  authclient = get_oauthclient(kroger_token_url, client_id, client_secret)
  req = get_location_session(authclient)

  #do a query for the first ralphs in this zip code
  store_response= query_location_from_session(req, 92128, chain="Ralphs")
  
  location_results = store_response.json()['data']

  if len(location_results) > 0:
    location_id = location_results[0]['locationId']

  product_query = "Milk"

  if location_id != None:
    price_response = query_price_from_session(req, product_query, location_id)
    print(price_response.json())
  

