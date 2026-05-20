# Conector RENACYT - Python Module & CLI

Un conector en Python de alta confiabilidad y **sin dependencias externas** (usa únicamente la biblioteca estándar de Python) para realizar consultas de investigadores en el Registro Nacional de Investigadores en Ciencia, Tecnología y de Innovación Tecnológica (RENACYT) de CONCYTEC, Perú.

Este conector está diseñado para ser integrado de forma transparente en otros módulos del sistema de gestión (SGPI), así como para ser ejecutado como una herramienta de línea de comandos (CLI) ágil y versátil.

## Características

* **Cero Dependencias:** No requiere `pip install requests` u otras librerías. Utiliza `urllib.request`, `ssl` y `json` nativos de Python.
* **Tolerancia a Fallos y Redundancia (Failover):** Si el servidor principal de RENACYT cae, el módulo cambia automáticamente y de forma transparente a un endpoint de respaldo.
* **Control de Tasa (Rate Limiting):** Retardo inteligente configurable (1.0s por defecto) para evitar bloqueos de IP o cortafuegos gubernamentales.
* **Reintentos Robustos (Exponential Backoff):** Reintenta peticiones en caso de fallos transitorios en el servidor de CONCYTEC.
* **Evasión de SSL:** Ignora por defecto los certificados SSL vencidos o mal configurados comunes en infraestructuras públicas.
* **Normalización de Datos:** Convierte marcas de tiempo en milisegundos (`1738336493067`) a formato legible de fecha (`DD/MM/YYYY`), traduciendo campos complejos a un diccionario en formato `snake_case`, sin perder detalles (la respuesta original y cruda del servidor se guarda íntegra en la clave `_raw`).

---

## Estructura de Datos Normalizada

Cada registro de investigador retornado por el API se transforma en una estructura uniforme:

```json
{
  "id": 33267,
  "codigo_registro": "P0156870",
  "tipo_documento": "DNI",
  "numero_documento": "19809928",
  "apellido_paterno": "TAIPE",
  "apellido_materno": "CAMPOS",
  "nombres": "NESTOR GODOFREDO",
  "nombre_completo": "NESTOR GODOFREDO TAIPE CAMPOS",
  "email": "nestor.taipe@unsch.edu.pe",
  "orcid": "0000-0002-8194-7946",
  "cti_vitae": "156870",
  "grupo": "N",
  "nivel": "V",
  "condicion": "Activo",
  "institucion_laboral_principal": "UNIVERSIDAD NACIONAL DE SAN CRISTOBAL DE HUAMANGA",
  "institucion_laboral_actual": "UNIVERSIDAD NACIONAL DE SAN CRISTOBAL DH",
  "genero": "Masculino",
  
  "fecha_inicio_vigencia": "31/01/2025",
  "fecha_fin_vigencia": "31/01/2027",
  "fecha_registro_activo": "31/01/2025",
  "fecha_ingreso_renacyt": "07/05/2020",
  "fecha_ultima_prod_cientifica": "01/09/2025",
  
  "calificaciones_previas": "...",
  
  "_raw": { ... } // Respuesta 100% idéntica y cruda del servidor
}
```

---

## Uso Programático (Integración en Python)

Para usar este módulo en otro script del sistema, basta con copiar la carpeta `renacyt_connector` en la raíz de su proyecto o añadirla al `sys.path`.

### 1. Consultas Rápidas (Funciones de Paquete)

```python
from renacyt_connector import search_by_dni, search_by_orcid, search_by_name

# Buscar por DNI (Retorna un diccionario de investigador o None)
investigador = search_by_dni("19809928")
if investigador:
    print(f"Nombre: {investigador['nombre_completo']}")
    print(f"Nivel: {investigador['nivel']}")
    print(f"Fecha Ingreso: {investigador['fecha_ingreso_renacyt']}")

# Buscar por ORCID
investigador = search_by_orcid("0000-0002-8194-7946")

# Buscar por Nombres (Retorna un dict con {'total': int, 'data': list})
resultados = search_by_name("NESTOR GODOFREDO")
print(f"Encontrados: {resultados['total']}")
```

### 2. Uso Avanzado con Cliente Configurado (`RenacytConnector`)

```python
from renacyt_connector import RenacytConnector, RenacytConnectionError, RenacytAPIError

# Configurar cliente personalizado
cliente = RenacytConnector(
    verify_ssl=False,          # Ignorar validación SSL de CONCYTEC
    rate_limit_delay=2.0,      # Esperar 2 segundos entre consultas
    timeout=10,                # Límite de conexión
    max_retries=5              # 5 intentos en errores de red
)

try:
    # Buscar usando criterios de filtro personalizados del backend
    criterios = [
        {
            "id": 14,
            "campo": "a.nivel",
            "valor": "V",
            "operadorBusqueda": "=",
            "operadorLogico": "and"
        }
    ]
    
    res = cliente.search(criterios, page=1, page_size=5)
    print(f"Investigadores en Nivel V encontrados en la página 1: {len(res['data'])}")
    
except RenacytConnectionError as ce:
    print(f"Error crítico de red/servidor caído: {ce}")
except RenacytAPIError as ae:
    print(f"Error de protocolo o formato del API: {ae}")
```

---

## Uso en Línea de Comandos (CLI)

Ejecute la suite de comandos desde la terminal utilizando `python -m renacyt_connector`.

### Opciones Disponibles

| Bandera | Descripción |
| --- | --- |
| `-d, --dni` | Consulta exacta de investigador por número de DNI o Pasaporte. |
| `-o, --orcid` | Consulta exacta de investigador por ID ORCID. |
| `-c, --code` | Consulta exacta de investigador por Código RENACYT. |
| `-n, --name` | Búsqueda parcial de investigadores por nombres o apellidos. |
| `-p, --page` | Número de página a retornar (por defecto: `1`). |
| `-l, --limit` | Registros por página a retornar (por defecto: `10`). |
| `-f, --format` | Formato de salida: `json`, `json-compact`, o `csv` (por defecto: `json`). |
| `-out, --output` | Guarda los resultados directamente a una ruta de archivo local en lugar de mostrarlos en pantalla. |
| `--ssl-verify` | Habilita la validación estricta de certificados SSL. |
| `--delay` | Establece el retardo en segundos entre llamadas (por defecto: `1.0`). |
| `-v, --verbose` | Muestra logs internos de diagnóstico (conexiones, retenciones, etc.) en `stderr`. |

### Ejemplos en Consola

#### 1. Buscar por DNI y ver en formato JSON formateado
```bash
python -m renacyt_connector --dni 19809928
```

#### 2. Buscar por nombre y exportar a archivo CSV limpio
```bash
python -m renacyt_connector --name "NESTOR GODOFREDO" --format csv --output nestor.csv
```

#### 3. Buscar por ORCID e ignorar demoras de tasa (consultar inmediatamente)
```bash
python -m renacyt_connector --orcid 0000-0002-8194-7946 --delay 0 --format json-compact
```

#### 4. Búsqueda de nombres paginada con logs informativos
```bash
python -m renacyt_connector --name "GODOFREDO" --page 2 --limit 5 --verbose
```
