"""
Arc Remesas Documentos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ArcRemesaDocumentoOut(BaseModel):
    """Esquema para entregar documentos en remesas"""

    id: int
    arc_documento_id: int
    arc_remesa_id: int
    anomalia: str | None
    fojas: int
    tipo_juzgado: str
    model_config = ConfigDict(from_attributes=True)


class OneArcRemesaDocumentoOut(BaseModel):
    """Esquema para entregar un documento en remesa"""

    success: bool
    message: str
    data: ArRemesaDocumentoOut | None = None
