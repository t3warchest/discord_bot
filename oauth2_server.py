from flask import Flask, redirect, request, session ,render_template
import requests
import os
from urllib import parse
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')  


client_id = os.getenv('client_id')       
client_secret = os.getenv('client_secret')  
redirect_uri = 'http://localhost:5000/callback' 
token_url = 'https://discord.com/api/oauth2/token'
authorisation_url = f"https://discord.com/api/oauth2/authorize?client_id=1184429640606023740&redirect_uri={parse.quote(redirect_uri)}&response_type=code&permissions=8&scope=bot"

db_connection = mysql.connector.connect(
    host="roundhouse.proxy.rlwy.net",
    user="root",
    password="e2fD2ega3dF6CABA1e3EeFeDG1cDAhC2",
    database="railway",
    port = 47428
)
cursor = db_connection.cursor()

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    html_content = html_content.replace('{AUTH_URL}', authorisation_url)

    return html_content

@app.route('/callback')
def callback():
    print("sdjkf")
    code = request.args.get('code')

    #exchange the authorisation code for an access token
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'scope': 'bot',
    }
    response = requests.post(token_url, data=token_data)

    if response.status_code == 200:
        
        token_info = response.json()
        session['discord_token'] = token_info['access_token']
        
        #getting required info from token recieved from discord
        access_token = token_info['access_token']
        expiration = token_info['expires_in']
        refresh_token = token_info['refresh_token']
        guild = token_info['guild']
        
        #storing the tokens in mysql db
        cursor.execute("INSERT INTO token_table(access_token,expiration,refresh_token,server_name) VALUES (%s,%s,%s,%s)",(access_token,expiration,refresh_token,guild['name']))
        db_connection.commit()
        
        #getting entries to displays on the callback page
        cursor.execute("SELECT * FROM token_table")
        rows = cursor.fetchall()
        
        return render_template("callback.html",rows=rows,server_name=guild['id'])
    else:
        #redirect back to authorisation url
        return redirect(authorisation_url) 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port)
