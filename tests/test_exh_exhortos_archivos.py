"""
Unit tests for exh_exhortos_archivos
"""

import unittest

import requests

from tests import config


class TestExhExhortosArchivos(unittest.TestCase):
    """Tests for exh_exhortos_archivos"""

    def test_get_exh_exhortos_archivos(self):
        """Test GET method for exh_exhortos_archivos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/exh_exhortos_archivos",
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
            self.assertEqual("nombre_archivo" in item, True)
            self.assertEqual("tipo_documento" in item, True)
            self.assertEqual("url" in item, True)
            self.assertEqual("fecha_hora_recepcion" in item, True)
            self.assertEqual("estado" in item, True)


if __name__ == "__main__":
    unittest.main()
