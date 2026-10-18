"""
Unit tests for exh_exhortos
"""

import unittest

import requests

from tests import config


class TestExhExhortos(unittest.TestCase):
    """Tests for exh_exhortos"""

    def test_get_exh_exhortos(self):
        """Test GET method for exh_exhortos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/exh_exhortos",
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
            self.assertEqual("exh_area_clave" in item, True)
            self.assertEqual("municipio_origen_clave" in item, True)
            self.assertEqual("exhorto_origen_id" in item, True)
            self.assertEqual("municipio_destino_clave" in item, True)
            self.assertEqual("materia_clave" in item, True)
            self.assertEqual("numero_expediente_origen" in item, True)
            self.assertEqual("remitente" in item, True)
            self.assertEqual("estado" in item, True)


if __name__ == "__main__":
    unittest.main()
