"""
Unit tests for arc_remesas_documentos
"""

import unittest

import requests

from tests import config


class TestArcRemesasDocumentos(unittest.TestCase):
    """Tests for arc_remesas_documentos"""

    def test_get_arc_remesas_documentos(self):
        """Test GET method for arc_remesas_documentos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/arc_remesas_documentos",
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
            self.assertEqual("arc_documento_id" in item, True)
            self.assertEqual("arc_remesa_id" in item, True)
            self.assertEqual("anomalia" in item, True)
            self.assertEqual("fojas" in item, True)
            self.assertEqual("tipo_juzgado" in item, True)


if __name__ == "__main__":
    unittest.main()
