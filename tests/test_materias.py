"""
Unit tests for materias
"""

import unittest

import requests

from tests import config


class TestMaterias(unittest.TestCase):
    """Tests for materias"""

    def test_get_materias(self):
        """Test GET method for materias"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/materias",
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
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("en_sentencias" in item, True)


if __name__ == "__main__":
    unittest.main()
