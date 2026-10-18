"""
Registro Estatal de Personas Sancionadas por Violencia contra las Mujeres (REPSVM)
"""

from pydantic import BaseModel, ConfigDict


class RepsvmAgresorOut(BaseModel):
    """Esquema para entregar REPSVM Agresores"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    consecutivo: int
    delito_generico: str
    delito_especifico: str
    es_publico: bool
    nombre: str
    numero_causa: str
    pena_impuesta: str
    observaciones: str | None = None
    sentencia_url: str | None = None
    tipo_juzgado: str
    tipo_sentencia: str
    model_config = ConfigDict(from_attributes=True)
