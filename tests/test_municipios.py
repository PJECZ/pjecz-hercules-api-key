"""
Unit tests for municipios
"""

import unittest

import requests

from tests import config


class TestMunicipios(unittest.TestCase):
    """Tests for municipios"""

    def test_get_municipios(self):
        """Test GET method for municipios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/municipios",
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
            self.assertEqual("clave" in item, True)
            self.assertEqual("nombre" in item, True)
            self.assertEqual("estado_clave" in item, True)
            self.assertEqual("estado_nombre" in item, True)


if __name__ == "__main__":
    unittest.main()
