import requests

def fdownload(i):
	url = "https://eprocure.gov.in/cppp/latestactivetenders/page=" + i
	response = requests.get(url)
	of = open("out/"+i+".html","w")
	of.write(str(response.content))

for i in range(1,21):
	fdownload(str(i))