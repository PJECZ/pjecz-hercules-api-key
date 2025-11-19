"""
Funcionarios-Oficinas esquemas
"""

from pydantic import BaseModel, ConfigDict


class FuncionarioOficinaOut(BaseModel):
    """Esquema para entregar funcionarios-oficinas"""

    funcionario_id: int
    funcionario_nombre: str
    oficina_id: int
    oficina_clave: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneFuncionarioOficinaOut(FuncionarioOficinaOut):
    """Esquema para entregar un funcionario-oficina"""

    success: bool
    message: str
    data: FuncionarioOficinaOut | None = None
