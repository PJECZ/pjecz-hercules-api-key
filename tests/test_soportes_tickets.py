"""
Unit tests for soportes tickets
"""

import unittest

import requests

from tests import config


class TestSoportesTickets(unittest.TestCase):
    """Tests for soportes tickets"""

    def test_get_soportes_tickets(self):
        """Test GET method for soportes tickets"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/soportes_tickets",
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
            self.assertEqual("funcionario_nombre" in item, True)
            self.assertEqual("soporte_categoria_nombre" in item, True)
            self.assertEqual("usuario_nombre" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("estado" in item, True)
            self.assertEqual("resolucion" in item, True)
            self.assertEqual("soluciones" in item, True)
            self.assertEqual("departamento" in item, True)


if __name__ == "__main__":
    unittest.main()
