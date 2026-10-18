"""
Unit tests for ofi_documentos_destinatarios
"""

import unittest

import requests

from tests import config


class TestOfiDocumentosDestinatarios(unittest.TestCase):
    """Tests for ofi_documentos_destinatarios"""

    def test_get_ofi_documentos_destinatarios(self):
        """Test GET method for ofi_documentos_destinatarios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/ofi_documentos_destinatarios",
                headers={"X-Api-Key": config["api_key"]},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)

        # Validar el contenido de la respuesta
        contenido = response.json()
        self.assertEqual("success" in contenido, True)
        self.assertEqual("message" in contenido, True)
        self.assertEqual("data" in contenido, True)

        # Validar que se haya tenido éxito
        self.assertEqual(contenido["success"], True)

        # Validar los datos
        self.assertEqual(type(contenido["data"]), list)
        for item in contenido["data"]:
            self.assertEqual("id" in item, True)
            self.assertEqual("ofi_documento_id" in item, True)
            self.assertEqual("usuario_email" in item, True)
            self.assertEqual("usuario_nombre" in item, True)
            self.assertEqual("usuario_autoridad_clave" in item, True)
            self.assertEqual("con_copia" in item, True)
            self.assertEqual("fue_leido" in item, True)
            self.assertEqual("fue_leido_tiempo" in item, True)


if __name__ == "__main__":
    unittest.main()
