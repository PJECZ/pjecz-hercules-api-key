"""
Unit tests for arc_documentos
"""

import unittest

import requests

from tests import config


class TestArcDocumentos(unittest.TestCase):
    """Tests for arc_documentos"""

    def test_get_arc_documentos(self):
        """Test GET method for arc_documentos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/arc_documentos",
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
            self.assertEqual("arc_documento_tipo_id" in item, True)
            self.assertEqual("arc_documento_tipo_nombre" in item, True)
            self.assertEqual("actor" in item, True)
            self.assertEqual("demandado" in item, True)
            self.assertEqual("expediente" in item, True)
            self.assertEqual("anio" in item, True)
            self.assertEqual("expediente_numero" in item, True)
            self.assertEqual("juicio" in item, True)
            self.assertEqual("arc_juzgados_origen_claves" in item, True)
            self.assertEqual("fojas" in item, True)
            self.assertEqual("tipo_juzgado" in item, True)
            self.assertEqual("ubicacion" in item, True)


if __name__ == "__main__":
    unittest.main()
