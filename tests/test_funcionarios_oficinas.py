"""
Unit tests for funcionarios-oficinas
"""

import unittest

import requests

from tests import config


class TestFuncionariosOficinas(unittest.TestCase):
    """Tests for funcionarios-oficinas"""

    def test_get_funcionarios_oficinas(self):
        """Test GET method for funcionarios-oficinas"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/funcionarios_oficinas",
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
        for itme in contenido["data"]:
            self.assertEqual("funcionario_id" in itme, True)
            self.assertEqual("funcionario_nombre" in itme, True)
            self.assertEqual("oficina_id" in itme, True)
            self.assertEqual("oficina_clave" in itme, True)
            self.assertEqual("descripcion" in itme, True)


if __name__ == "__main__":
    unittest.main()
