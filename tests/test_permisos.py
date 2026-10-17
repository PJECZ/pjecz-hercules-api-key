"""
Unit tests for permisos
"""

import unittest

import requests

from tests import config


class TestPermisos(unittest.TestCase):
    """Tests for permisos"""

    def test_get_permisos(self):
        """Test GET method for permisos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/permisos",
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
            self.assertEqual("rol_id" in item, True)
            self.assertEqual("rol_nombre" in item, True)
            self.assertEqual("modulo_id" in item, True)
            self.assertEqual("modulo_nombre" in item, True)
            self.assertEqual("nombre" in item, True)
            self.assertEqual("nivel" in item, True)


if __name__ == "__main__":
    unittest.main()
