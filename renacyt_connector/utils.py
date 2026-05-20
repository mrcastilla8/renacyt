import datetime
import copy

def parse_epoch_ms(ms):
    """
    Parses a millisecond epoch timestamp into a YYYY-MM-DD string.
    If parsing fails, returns None.
    """
    if ms is None:
        return None
    try:
        # Convert ms to float seconds
        seconds = float(ms) / 1000.0
        # Use UTC timezone to ensure consistency
        dt = datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc)
        return dt.strftime('%d/%m/%Y')
    except (ValueError, TypeError, OverflowError):
        return None

def normalize_researcher_record(record):
    """
    Normalizes a raw researcher record from the RENACYT API
    into a standardized, clean snake_case dictionary.
    Formats all timestamp fields in both normalized and raw representations.
    """
    if not record or not isinstance(record, dict):
        return {}
    
    nombres = record.get("nombres") or ""
    paterno = record.get("apellidoPaterno") or ""
    materno = record.get("apellidoMaterno") or ""
    
    parts = [nombres, paterno, materno]
    nombre_completo = " ".join([p.strip() for p in parts if p and p.strip()])
    
    # Format dates in the raw record
    raw_record = copy.deepcopy(record)
    for k, v in raw_record.items():
        if k.lower().startswith("fecha") and isinstance(v, (int, float)):
            parsed = parse_epoch_ms(v)
            if parsed:
                raw_record[k] = parsed
    
    return {
        "id": record.get("id"),
        "codigo_registro": record.get("codigoRegistro"),
        "tipo_documento": record.get("tipoDocumento"),
        "numero_documento": record.get("numeroDocumento"),
        "apellido_paterno": record.get("apellidoPaterno"),
        "apellido_materno": record.get("apellidoMaterno"),
        "nombres": record.get("nombres"),
        "nombre_completo": nombre_completo,
        "email": record.get("emailNotificar"),
        "orcid": record.get("orcid"),
        "cti_vitae": record.get("ctiVitae"),
        "grupo": record.get("grupo"),
        "nivel": record.get("nivel"),
        "condicion": record.get("condicion"),
        "institucion_laboral_principal": record.get("institucionLaboralPrincipal"),
        "institucion_laboral_actual": record.get("institucionLaboralActual"),
        "genero": record.get("genero"),
        
        # Date conversions
        "fecha_inicio_vigencia": parse_epoch_ms(record.get("fechaInicioVigencia")),
        "fecha_fin_vigencia": parse_epoch_ms(record.get("fechaFinVigencia")),
        "fecha_registro_activo": parse_epoch_ms(record.get("fechaRegistroActivo")),
        "fecha_ingreso_renacyt": parse_epoch_ms(record.get("fechaIngresoRenacyt")),
        "fecha_ultima_prod_cientifica": parse_epoch_ms(record.get("fechaUltimaProdCientifica")),
        
        "calificaciones_previas": record.get("calificacionesPrevias"),
        
        # Formatted raw record preserved here
        "_raw": raw_record
    }
