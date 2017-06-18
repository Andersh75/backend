from app import app
import requests

@app.route("/")
def hello():
    uri = "https://mdn.github.io/learning-area/javascript/oojs/json/superheroes.json"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
       return "Connection Errsssss"
    Jresponse = uResponse.text
    # return "Hello World!"
    return Jresponse
