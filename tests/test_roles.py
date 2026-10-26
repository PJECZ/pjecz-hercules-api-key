"""
Unit tests for roles
"""

import unittest

import requests

from tests import config


class TestRoles(unittest.TestCase):
    """Tests for roles"""

    def test_get_roles(self):
        """Test GET method for roles"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/roles",
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
            self.assertEqual("nombre" in item, True)


if __name__ == "__main__":
    unittest.main()
