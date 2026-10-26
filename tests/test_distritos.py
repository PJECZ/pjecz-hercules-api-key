"""
Unit tests for distritos
"""

import unittest

import requests

from tests import config


class TestDistritos(unittest.TestCase):
    """Tests for distritos"""

    def test_get_distritos(self):
        """Test GET method for distritos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/distritos",
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
            self.assertEqual("nombre_corto" in item, True)
            self.assertEqual("es_distrito_judicial" in item, True)
            self.assertEqual("es_distrito" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)


if __name__ == "__main__":
    unittest.main()
