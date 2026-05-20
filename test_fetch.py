import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://renacyt.concytec.gob.pe/buscador-ui/registro-registro-module-es2015.js"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
)

try:
    print("Fetching registro-registro-module-es2015.js...")
    with urllib.request.urlopen(req, context=ctx) as response:
        content = response.read().decode('utf-8')
        
        idx = content.find('class InvestigadoresListComponent')
        if idx != -1:
            print("--- Found class InvestigadoresListComponent ---")
            # print 15000 characters from the start of class InvestigadoresListComponent
            print(content[idx:idx + 15000])
        else:
            print("class InvestigadoresListComponent not found exactly. Searching for 'InvestigadoresListComponent ='")
            idx = content.find('InvestigadoresListComponent =')
            if idx != -1:
                print(content[idx:idx + 15000])
            
except Exception as e:
    print("Error:", e)
