"""
Unit tests for repsvm_agresores
"""

import unittest

import requests

from tests import config


class TestRepsvmAgresores(unittest.TestCase):
    """Tests for repsvm_agresores"""

    def test_get_repsvm_agresores(self):
        """Test GET method for repsvm_agresores"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/repsvm_agresores",
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
            self.assertEqual("consecutivo" in item, True)
            self.assertEqual("delito_generico" in item, True)
            self.assertEqual("delito_especifico" in item, True)
            self.assertEqual("es_publico" in item, True)
            self.assertEqual("nombre" in item, True)
            self.assertEqual("numero_causa" in item, True)
            self.assertEqual("pena_impuesta" in item, True)
            self.assertEqual("observaciones" in item, True)
            self.assertEqual("sentencia_url" in item, True)
            self.assertEqual("tipo_juzgado" in item, True)
            self.assertEqual("tipo_sentencia" in item, True)


if __name__ == "__main__":
    unittest.main()
