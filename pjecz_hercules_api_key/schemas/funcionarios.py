"""
Funcionarios, esquemas
"""

from pydantic import BaseModel, ConfigDict


class FuncionarioOut(BaseModel):
    """Esquema para entregar Funcionarios"""

    id: int
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    curp: str
    email: str
    puesto: str
    en_funciones: bool
    en_soportes: bool
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneFuncionarioOut(BaseModel):
    """Esquema para entregar un Funcionario"""

    success: bool
    message: str
    data: FuncionarioOut | None = None
