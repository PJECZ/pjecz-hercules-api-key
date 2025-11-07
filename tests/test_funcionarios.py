"""
Unit tests for funcionarios
"""

import unittest

import requests

from tests import config


class TestFuncionarios(unittest.TestCase):
    """Tests for funcionarios"""

    def test_get_funcionarios(self):
        """Test GET method for funcionarios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/funcionarios",
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
            self.assertEqual("nombres" in item, True)
            self.assertEqual("apellido_paterno" in item, True)
            self.assertEqual("apellido_materno" in item, True)
            self.assertEqual("curp" in item, True)
            self.assertEqual("email" in item, True)
            self.assertEqual("puesto" in item, True)
            self.assertEqual("en_funciones" in item, True)
            self.assertEqual("en_soportes" in item, True)
            self.assertEqual("nombre" in item, True)


if __name__ == "__main__":
    unittest.main()
