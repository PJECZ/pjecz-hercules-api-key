"""
Unit tests for funcionarios_oficinas
"""

import unittest

import requests

from tests import config


class TestFuncionariosOficinas(unittest.TestCase):
    """Tests for funcionarios_oficinas"""

    def test_get_funcionarios_oficinas(self):
        """Test GET method for funcionarios_oficinas"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/funcionarios_oficinas",
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
            self.assertEqual("funcionario_id" in item, True)
            self.assertEqual("funcionario_nombre" in item, True)
            self.assertEqual("oficina_id" in item, True)
            self.assertEqual("oficina_clave" in item, True)
            self.assertEqual("descripcion" in item, True)


if __name__ == "__main__":
    unittest.main()
