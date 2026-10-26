"""
Unit tests for modulos
"""

import unittest

import requests

from tests import config


class TestModulos(unittest.TestCase):
    """Tests for modulos"""

    def test_get_modulos(self):
        """Test GET method for modulos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/modulos",
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
            self.assertEqual("nombre_corto" in item, True)
            self.assertEqual("nombre" in item, True)
            self.assertEqual("icono" in item, True)
            self.assertEqual("ruta" in item, True)
            self.assertEqual("en_navegacion" in item, True)


if __name__ == "__main__":
    unittest.main()
