"""
Unit tests for exh_exhortos_partes
"""

import unittest

import requests

from tests import config


class TestExhExhortosPartes(unittest.TestCase):
    """Tests for exh_exhortos_partes"""

    def test_get_exh_exhortos_partes(self):
        """Test GET method for exh_exhortos_partes"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/exh_exhortos_partes",
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
            self.assertEqual("nombre" in item, True)
            self.assertEqual("genero" in item, True)
            self.assertEqual("es_persona_moral" in item, True)
            self.assertEqual("tipo_parte" in item, True)


if __name__ == "__main__":
    unittest.main()
