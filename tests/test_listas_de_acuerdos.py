"""
Unit tests for listas de acuerdos
"""

import unittest

import requests

from tests import config


class TestListasDeAcuerdos(unittest.TestCase):
    """Tests for listas de acuerdos"""

    def test_get_listas_de_acuerdos(self):
        """Test GET method for listas de acuerdos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/listas_de_acuerdos",
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
            self.assertEqual("distrito_clave" in item, True)
            self.assertEqual("distrito_nombre" in item, True)
            self.assertEqual("distrito_nombre_corto" in item, True)
            self.assertEqual("autoridad_clave" in item, True)
            self.assertEqual("autoridad_descripcion" in item, True)
            self.assertEqual("autoridad_descripcion_corta" in item, True)
            self.assertEqual("fecha" in item, True)
            self.assertEqual("descripcion" in item, True)


if __name__ == "__main__":
    unittest.main()
