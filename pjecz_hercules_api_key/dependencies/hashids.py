"""
Cifrado y descrifado de ID por medio de Hashids
"""

import re
from typing import Any

from fastapi import Depends
from hashids import Hashids

from pjecz_hercules_api_key.config.settings import Settings, get_settings

HASHID_REGEXP = re.compile("[0-9a-zA-Z]{8,16}")


def cifrar_id(
    un_id: int,
    settings: Settings = Depends(get_settings),
) -> str:
    """Cifrar ID"""
    hashids = Hashids(settings.SALT, min_length=8)
    return hashids.encode(un_id)


def descifrar_id(
    un_id_hasheado: str,
    settings: Settings = Depends(get_settings),
) -> Any:
    """Descifrar ID"""
    hashids = Hashids(settings.SALT, min_length=8)
    if HASHID_REGEXP.match(un_id_hasheado):
        pag_pago_id = hashids.decode(un_id_hasheado)
        if len(pag_pago_id) == 1:
            return pag_pago_id[0]
    return None
