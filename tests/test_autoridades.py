"""
Unit tests for autoridades
"""

import unittest

import requests

from tests import config


class TestAutoridades(unittest.TestCase):
    """Tests for autoridades"""

    def test_get_autoridades(self):
        """Test GET method for autoridades"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/autoridades",
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
            self.assertEqual("distrito_clave" in item, True)
            self.assertEqual("distrito_nombre" in item, True)
            self.assertEqual("distrito_nombre_corto" in item, True)
            self.assertEqual("materia_clave" in item, True)
            self.assertEqual("materia_nombre" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("descripcion_corta" in item, True)
            self.assertEqual("es_extinto" in item, True)
            self.assertEqual("es_cemasc" in item, True)
            self.assertEqual("es_defensoria" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)
            self.assertEqual("es_notaria" in item, True)
            self.assertEqual("es_organo_especializado" in item, True)
            self.assertEqual("organo_jurisdiccional" in item, True)


if __name__ == "__main__":
    unittest.main()
