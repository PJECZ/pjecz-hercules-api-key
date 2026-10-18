"""
Unit tests for arc_remesas
"""

import unittest

import requests

from tests import config


class TestArcRemesas(unittest.TestCase):
    """Tests for arc_remesas"""

    def test_get_arc_remesas(self):
        """Test GET method for arc_remesas"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/arc_remesas",
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
            self.assertEqual("autoridad_clave" in item, True)
            self.assertEqual("autoridad_descripcion" in item, True)
            self.assertEqual("autoridad_descripcion_corta" in item, True)
            self.assertEqual("num_oficio" in item, True)
            self.assertEqual("estado" in item, True)


if __name__ == "__main__":
    unittest.main()
