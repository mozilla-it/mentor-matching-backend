import requests
import json
import pandas as pd


query = """query {
	findLearner(email: "kmoir@mozilla.com") {
		id
	}
}"""

#url = 'http://127.0.0.1:5000/graphql'
url = 'https://us-central1-imposing-union-227917.cloudfunctions.net/mentoring_http/graphql'

r = requests.post(url, json={'query': query})
print(r.status_code)
print(r.text)

json_data = json.loads(r.text)
