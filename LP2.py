
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=BRENT&interval=monthly&apikey=X5H5PW3ZSZ8HATP9'
r = requests.get(url)
data = r.json()

print(data)