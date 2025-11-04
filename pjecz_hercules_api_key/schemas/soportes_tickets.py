"""
Soportes Tickets, esquemas
"""

from pydantic import BaseModel, ConfigDict


class SoporteTicketOut(BaseModel):
    """Esquema para entregar Soportes Tickets"""

    id: int
    funcionario_nombre: str
    soporte_categoria_nombre: str
    usuario_nombre: str
    descripcion: str
    estado: str
    resolucion: str
    soluciones: str
    departamento: str
    model_config = ConfigDict(from_attributes=True)


class OneSoporteTicketOut(BaseModel):
    """Esquema para entregar un Soporte Ticket"""

    success: bool
    message: str
    data: SoporteTicketOut | None = None
