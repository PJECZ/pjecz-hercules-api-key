"""
Unit tests for exh_tipos_diligencias
"""

import unittest

import requests

from tests import config


class TestExhTiposDiligencias(unittest.TestCase):
    """Tests for exh_tipos_diligencias"""

    def test_get_exh_tipos_diligencias(self):
        """Test GET method for exh_tipos_diligencias"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/exh_tipos_diligencias",
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
            self.assertEqual("descripcion" in item, True)


if __name__ == "__main__":
    unittest.main()
