import requests

url = "https://raw.githubusercontent.com/pt1243/pyprojectsetup/main/initial_script.py"
r = requests.get(url)

with open('test.txt', 'w') as f:
    f.write(r.text)
