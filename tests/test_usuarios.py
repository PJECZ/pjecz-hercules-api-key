"""
Unit tests for usuarios
"""

import unittest

import requests

from tests import config


class TestUsuarios(unittest.TestCase):
    """Tests for usuarios"""

    def test_get_usuarios(self):
        """Test GET method for usuarios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/usuarios",
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
            self.assertEqual("email" in item, True)
            self.assertEqual("nombres" in item, True)
            self.assertEqual("apellido_paterno" in item, True)
            self.assertEqual("apellido_materno" in item, True)
            self.assertEqual("puesto" in item, True)

if __name__ == "__main__":
    unittest.main()
