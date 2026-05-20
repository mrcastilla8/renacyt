import os
import sys
import subprocess
import json
import csv
import logging

# Ensure local folder is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from renacyt_connector import (
    search_by_dni,
    search_by_orcid,
    search_by_codigo,
    search_by_name,
    search_by_institution,
    RenacytConnector,
    RenacytConnectionError,
    RenacytAPIError
)

def test_programmatic_dni():
    print("Testing programmatic lookup by DNI...")
    res = search_by_dni("19809928")
    assert res is not None, "DNI lookup returned None!"
    assert res["numero_documento"] == "19809928", "DNI number mismatch!"
    assert "NESTOR GODOFREDO" in res["nombre_completo"], "Researcher name mismatch!"
    assert res["orcid"] == "0000-0002-8194-7946", "ORCID mismatch!"
    assert "_raw" in res, "Original raw response not preserved in '_raw' field!"
    assert res["fecha_inicio_vigencia"] == "31/01/2025", "Date parsing failed or incorrect!"
    print("OK: Programmatic DNI search passed!")

def test_programmatic_orcid():
    print("\nTesting programmatic lookup by ORCID...")
    res = search_by_orcid("0000-0002-8194-7946")
    assert res is not None, "ORCID lookup returned None!"
    assert res["numero_documento"] == "19809928", "DNI number mismatch!"
    assert res["codigo_registro"] == "P0156870", "Registration code mismatch!"
    print("OK: Programmatic ORCID search passed!")

def test_programmatic_codigo():
    print("\nTesting programmatic lookup by Code...")
    res = search_by_codigo("P0156870")
    assert res is not None, "Registration code lookup returned None!"
    assert res["numero_documento"] == "19809928", "DNI number mismatch!"
    print("OK: Programmatic Code search passed!")

def test_programmatic_name():
    print("\nTesting programmatic lookup by Name...")
    res = search_by_name("NESTOR GODOFREDO")
    assert isinstance(res, dict), "Search by name must return a dictionary"
    assert "total" in res and "data" in res, "Response missing 'total' or 'data' fields!"
    assert res["total"] >= 1, "Expected at least 1 match for NESTOR GODOFREDO!"
    assert len(res["data"]) >= 1, "Data list empty!"
    print("OK: Programmatic Name search passed!")

def test_failover_redundancy():
    print("\nTesting endpoint failover redundancy with intentional invalid URL...")
    # Inject a bogus base URL followed by the real active one.
    # The client should fail on the first, print warnings (if logging enabled), and successfully resolve using the second.
    connector = RenacytConnector(
        base_urls=[
            "https://invalid-host-should-fail.gob.pe/renacyt-backend",
            "https://renacyt.concytec.gob.pe/renacyt-backend"
        ],
        verify_ssl=False,
        rate_limit_delay=0.0
    )
    res = connector.search_by_dni("19809928")
    assert res is not None, "Failover client returned None!"
    assert res["numero_documento"] == "19809928", "Failover resolved to incorrect data!"
    print("OK: Endpoint Failover redundancy passed!")

def test_failover_complete_failure():
    print("\nTesting complete client failure when all endpoints are down...")
    connector = RenacytConnector(
        base_urls=[
            "https://invalid-host-should-fail-1.gob.pe/renacyt-backend",
            "https://invalid-host-should-fail-2.gob.pe/renacyt-backend"
        ],
        verify_ssl=False,
        rate_limit_delay=0.0,
        max_retries=1
    )
    try:
        connector.search_by_dni("19809928")
        assert False, "Should have failed with RenacytConnectionError!"
    except RenacytConnectionError as ce:
        print("OK: Complete failure caught correctly! Error description captured.")

def test_cli_json():
    print("\nTesting CLI JSON output...")
    cmd = [sys.executable, "-m", "renacyt_connector", "--dni", "19809928", "--delay", "0"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env)
    assert result.returncode == 0, f"CLI command failed: {result.stderr}"
    
    parsed = json.loads(result.stdout)
    assert parsed["total"] == 1, "CLI returned wrong total!"
    assert parsed["data"][0]["numero_documento"] == "19809928", "CLI returned wrong researcher!"
    print("OK: CLI JSON output passed!")

def test_cli_csv():
    print("\nTesting CLI CSV output...")
    cmd = [sys.executable, "-m", "renacyt_connector", "--name", "NESTOR GODOFREDO", "--format", "csv", "--delay", "0"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env)
    assert result.returncode == 0, f"CLI CSV command failed: {result.stderr}"
    
    # Read the CSV output
    reader = csv.DictReader(io_string := io_string_init(result.stdout))
    rows = list(reader)
    assert len(rows) >= 1, "CSV has no rows!"
    assert rows[0]["numero_documento"] == "19809928", "CSV has wrong researcher DNI!"
    assert "_raw" not in rows[0], "CSV should exclude the '_raw' key!"
    print("OK: CLI CSV output passed!")

def io_string_init(text):
    import io
    return io.StringIO(text)

def test_cli_output_file():
    print("\nTesting CLI writing directly to file...")
    temp_json = "temp_results.json"
    if os.path.exists(temp_json):
        os.remove(temp_json)
        
    cmd = [sys.executable, "-m", "renacyt_connector", "--dni", "19809928", "--output", temp_json, "--delay", "0"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env)
    assert result.returncode == 0, f"CLI Output command failed: {result.stderr}"
    assert os.path.exists(temp_json), "Output file was not created!"
    
    with open(temp_json, 'r', encoding='utf-8') as f:
        parsed = json.load(f)
    assert parsed["total"] == 1, "Written file has wrong total!"
    assert parsed["data"][0]["numero_documento"] == "19809928", "Written file has wrong DNI!"
    
    os.remove(temp_json)
    print("OK: CLI Output File writing passed!")

def test_programmatic_institution():
    print("\nTesting programmatic lookup by Institution...")
    res = search_by_institution("Universidad Nacional Mayor de San Marcos", page=1, page_size=5)
    assert isinstance(res, dict), "Search by institution must return a dictionary"
    assert "total" in res and "data" in res, "Response missing 'total' or 'data' fields!"
    assert res["total"] >= 1, "Expected at least 1 match for UNMSM!"
    assert len(res["data"]) >= 1, "Data list empty!"
    for record in res["data"]:
        assert "institucion_laboral_principal" in record, "Key 'institucion_laboral_principal' missing!"
    print("OK: Programmatic Institution search passed!")

def test_cli_institution():
    print("\nTesting CLI Institution search...")
    cmd = [sys.executable, "-m", "renacyt_connector", "--institution", "Universidad Nacional Mayor de San Marcos", "--limit", "5", "--delay", "0"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env)
    assert result.returncode == 0, f"CLI Institution command failed: {result.stderr}"
    parsed = json.loads(result.stdout)
    assert parsed["total"] >= 1, "CLI returned wrong total!"
    assert len(parsed["data"]) >= 1, "CLI returned no data!"
    print("OK: CLI Institution search passed!")

def main():
    print("==================================================")
    print("       STARTING RENACYT CONNECTOR SUITE TESTS     ")
    print("==================================================")
    
    # Configure root logging for test execution visibility
    logging.basicConfig(level=logging.WARNING)
    
    try:
        test_programmatic_dni()
        test_programmatic_orcid()
        test_programmatic_codigo()
        test_programmatic_name()
        test_failover_redundancy()
        test_failover_complete_failure()
        test_cli_json()
        test_cli_csv()
        test_cli_output_file()
        test_programmatic_institution()
        test_cli_institution()
        print("\n==================================================")
        print("          ALL TEST CASES PASSED SUCCESSFULLY      ")
        print("==================================================")
        sys.exit(0)
    except AssertionError as ae:
        print(f"\nAssertion Error during tests: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Exception during tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
