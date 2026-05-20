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

# Test 1: Search by DNI 19809928
data_dni = [
    {
        "id": 7,
        "campo": "a.numero_documento",
        "valor": "19809928",
        "operadorBusqueda": "=",
        "operadorLogico": "and"
    }
]

print("Testing search by DNI 19809928...")
req = urllib.request.Request(
    f"{base}/actoRegistral/obtenerActosRegistralesActivos/reglamento/21/pagina/1/numeroRegistros/10",
    data=json.dumps(data_dni).encode('utf-8'),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        res = json.loads(response.read().decode('utf-8'))
        print("Search by DNI Success!")
        print("Total matching:", res.get("total"))
        print(json.dumps(res.get("data"), indent=2, ensure_ascii=False))
except Exception as e:
    print("DNI search error:", e)

# Test 2: Search by Name "NESTOR GODOFREDO"
data_name = [
    {
        "id": 4,
        "campo": "a.nombres",
        "valor": "NESTOR GODOFREDO",
        "operadorBusqueda": "ilike",
        "operadorLogico": "and"
    }
]

print("\nTesting search by Name 'NESTOR GODOFREDO'...")
req = urllib.request.Request(
    f"{base}/actoRegistral/obtenerActosRegistralesActivos/reglamento/21/pagina/1/numeroRegistros/10",
    data=json.dumps(data_name).encode('utf-8'),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        res = json.loads(response.read().decode('utf-8'))
        print("Search by Name Success!")
        print("Total matching:", res.get("total"))
        print(json.dumps(res.get("data")[:2], indent=2, ensure_ascii=False))
except Exception as e:
    print("Name search error:", e)
