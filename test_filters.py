import urllib.request
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = "https://renacyt.concytec.gob.pe/renacyt-backend"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(f"{base}/filtros/busquedaInvestigadores", headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        res_data = response.read().decode('utf-8')
        filters = json.loads(res_data)
        print("=== Criteria List ===")
        for f in filters:
            print(f"ID: {f.get('id')}, Name: '{f.get('nombre')}', Field: '{f.get('campo')}', AssociatedComponent: '{f.get('componenteAsociado')}'")
except Exception as e:
    print("Error:", e)
