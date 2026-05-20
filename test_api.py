import urllib.request
import urllib.parse
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Try renacyt.concytec.gob.pe first, then ctivitae.concytec.gob.pe
base_urls = [
    "https://renacyt.concytec.gob.pe/renacyt-backend",
    "https://ctivitae.concytec.gob.pe/renacyt-backend"
]

def try_request(url, method="GET", data=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json'
    }
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode('utf-8')
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            res_data = response.read().decode('utf-8')
            return True, json.loads(res_data)
    except Exception as e:
        return False, str(e)

for base in base_urls:
    print(f"\n--- Testing Base URL: {base} ---")
    
    # 1. Test GET /filtros/busquedaInvestigadores
    print("Testing GET /filtros/busquedaInvestigadores...")
    success, res = try_request(f"{base}/filtros/busquedaInvestigadores")
    if success:
        print("Success! Criteria list:")
        print(json.dumps(res[:5], indent=2, ensure_ascii=False))
        print(f"Total criteria items: {len(res)}")
    else:
        print(f"Failed: {res}")
        
    # 2. Test POST /actoRegistral/obtenerActosRegistralesActivos/reglamento/21/pagina/1/numeroRegistros/10
    print("Testing POST /actoRegistral/obtenerActosRegistralesActivos/reglamento/21/pagina/1/numeroRegistros/10 with empty filter...")
    success, res = try_request(
        f"{base}/actoRegistral/obtenerActosRegistralesActivos/reglamento/21/pagina/1/numeroRegistros/10",
        method="POST",
        data=[]
    )
    if success:
        print("Success! Data:")
        print("Total count:", res.get("total"))
        print("Sample data:")
        if "data" in res and len(res["data"]) > 0:
            print(json.dumps(res["data"][0], indent=2, ensure_ascii=False))
        else:
            print("No data in response:", res)
    else:
        print(f"Failed: {res}")
