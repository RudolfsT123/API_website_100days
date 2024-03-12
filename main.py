from flask import Flask, render_template, request
import requests
from flask_bootstrap import Bootstrap5
from api import client_id, client_secret

# Define Flask app
app = Flask(__name__)

# Initialize Bootstrap for styling
bootstrap = Bootstrap5(app)

# Artsy API credentials
client_id = client_id
client_secret = client_secret
token_url = 'https://api.artsy.net/api/tokens/xapp_token'

# Retrieve authentication token
token_response = requests.post(token_url, data={'client_id': client_id, 'client_secret': client_secret})
token_data = token_response.json()
xapp_token = token_data['token']

# Set headers for Artsy API requests
headers = {'X-Xapp-Token': xapp_token}

# Function to fetch artists from the Artsy API
def get_artists():
    response = requests.get('https://api.artsy.net/api/artists', headers=headers)
    if response.status_code == 200:
        return response.json()['_embedded']['artists']
    else:
        return []

# Function to fetch artworks from the Artsy API
def get_artworks():
    response = requests.get('https://api.artsy.net/api/artworks', headers=headers)
    if response.status_code == 200:
        artwork_links = []
        artists = []
        #print(response.json()['_embedded']['artworks'])
        for artwork in response.json()['_embedded']['artworks']:
            artwork_links.append(artwork["_links"]['artists']['href'])
            artists.append(extract_artist_id(artwork["_links"]['artists']['href']))
        return response.json()['_embedded']['artworks'], artists
    else:
        return []

# Function to extract artist ID and name from artwork link
def extract_artist_id(artwork_link):
    response = requests.get(artwork_link, headers=headers)
    if response.status_code == 200:
        artist_json = response.json()
        artist_id = artist_json['_embedded']['artists'][0]['id']
        artist_name = response.json()['_embedded']['artists'][0]['name']
        return artist_id, artist_name
    else:
        return None

# Function to fetch artworks by a specific artist
def get_artworks_from_artist(artist_id):
    params = {'artist_id': artist_id}
    response_artist = requests.get('https://api.artsy.net/api/artworks', headers=headers, params=params)
    return response_artist.json()

# Function to retrieve information about a specific artist
def get_artist_stuff(artist_id):
    response_artist2 = requests.get(f'https://api.artsy.net/api/artists/{artist_id}',  headers=headers)
    return response_artist2.json()

# Function to retrieve artists similar to a given artist
def get_similar_artists(artist_id):
    params = {'similar_to_artist_id': artist_id}
    response_similar = requests.get(f'https://api.artsy.net/api/artists/', headers=headers, params=params)
    return response_similar.json()

def get_similar_artworks(artwork_id):
    params = {'similar_to_artwork_id':artwork_id}
    response_similar_artworks = requests.get(f'https://api.artsy.net/api/artworks/', headers=headers, params=params)
    print(response_similar_artworks.json())
    artists = []
    artwork_links = []
    #print(response.json()['_embedded']['artworks'])
    for artwork in response_similar_artworks.json()['_embedded']['artworks']:
        artwork_links.append(artwork["_links"]['artists']['href'])
        artists.append(extract_artist_id(artwork["_links"]['artists']['href']))
    return response_similar_artworks.json()['_embedded']['artworks'], artists

# Route for the homepage
@app.route('/')
def index():
    artworks = get_artworks()
    return render_template('index.html', artworks=artworks[0], artists=artworks[1], zip=zip)

# Route for displaying artworks by a specific artist
@app.route('/artist')
def artist():
    artist_id = request.args.get('artist_id')
    artworks = get_artworks_from_artist(artist_id)
    artist = get_artist_stuff(artist_id)
    if not artworks['_embedded']['artworks']:  # Check if the list of artists artworks is empty
        # If the list of artists artworks is empty, render index.html
        artworks = get_artworks()
        return render_template('index.html', artworks=artworks[0], artists=artworks[1], zip=zip)
    else:
        # If the list of artists is not empty, render similar.html
        return render_template('artist.html', artworks=artworks['_embedded']['artworks'], artist=artist)

# Route for displaying artists similar to a given artist
@app.route('/similar')
def similar():
    artist_id = request.args.get('artist_id')
    artists = get_similar_artists(artist_id)
    artist_name = request.args.get('artist_name')
    if not artists['_embedded']['artists']:  # Check if the list of artists is empty
        # If the list of artists is empty, render index.html
        artworks = get_artworks()
        return render_template('index.html', artworks=artworks[0], artists=artworks[1], zip=zip)
    else:
        # If the list of artists is not empty, render similar.html
        return render_template('similar.html', artists=artists['_embedded']['artists'], name=artist_name)

  
@app.route('/similar_artworks')
def similar_artworks():
    artwork_id = request.args.get('artwork_id')
    artworks = get_similar_artworks(artwork_id)
    artist_name = request.args.get('artist_name')
    artwork_name = request.args.get('artwork_name')
    if not artworks[0]:  # Check if the list of artworks is empty
        # If the list of artworks is empty, render index.html
        artworks = get_artworks()
        return render_template('index.html', artworks=artworks[0], artists=artworks[1], zip=zip)
    else:
        # If the list of artworks is not empty, render similar.html
        return render_template('similar_artworks.html', artworks=artworks[0], artists=artworks[1], artist_name=artist_name, artwork_name=artwork_name, zip=zip)

if __name__ == '__main__':
    app.run(debug=True)
