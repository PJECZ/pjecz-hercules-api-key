"""
Unit tests for dgt_entregas
"""

import unittest

import requests

from tests import config


class TestDgtEntregas(unittest.TestCase):
    """Tests for dgt_entregas"""

    def test_get_dgt_entregas(self):
        """Test GET method for dgt_entregas"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/dgt_entregas",
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
            self.assertEqual("dgt_ruta_clave" in item, True)
            self.assertEqual("archivo_nombre" in item, True)
            self.assertEqual("archivo_url" in item, True)
            self.assertEqual("archivo_public_url" in item, True)
            self.assertEqual("archivo_md5" in item, True)
            self.assertEqual("archivo_crc32c" in item, True)
            self.assertEqual("archivo_actualizado" in item, True)
            self.assertEqual("archivo_tamano" in item, True)
            self.assertEqual("expediente" in item, True)
            self.assertEqual("expediente_anio" in item, True)
            self.assertEqual("expediente_num" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("es_anomalo" in item, True)
            self.assertEqual("ultimo_evento" in item, True)
            self.assertEqual("ultimo_evento_creado" in item, True)
            self.assertEqual("archivo_uuid" in item, True)


if __name__ == "__main__":
    unittest.main()
