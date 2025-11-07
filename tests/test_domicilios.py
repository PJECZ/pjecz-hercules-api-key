"""
Unit tests for domicilios
"""

import unittest

import requests

from tests import config


class TestDomicilios(unittest.TestCase):
    """Tests for domicilios"""

    def test_get_domicilios(self):
        """Test GET method for domicilios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/domicilios",
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
            self.assertEqual("distrito_clave" in item, True)
            self.assertEqual("distrito_nombre" in item, True)
            self.assertEqual("edificio" in item, True)
            self.assertEqual("estado" in item, True)
            self.assertEqual("municipio" in item, True)
            self.assertEqual("calle" in item, True)
            self.assertEqual("num_ext" in item, True)
            self.assertEqual("num_int" in item, True)
            self.assertEqual("colonia" in item, True)
            self.assertEqual("cp" in item, True)
            self.assertEqual("completo" in item, True)


if __name__ == "__main__":
    unittest.main()
