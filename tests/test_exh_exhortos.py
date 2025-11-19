"""
Unit tests for exh_exhortos
"""

import unittest

import requests
from faker import Faker

from tests import config


class TestExhExhortos(unittest.TestCase):
    """Tests for exh_exhortos"""

    def test_get_exh_exhortos(self):
        """Test GET method for exh_exhortos"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/exh_exhortos",
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
            self.assertEqual("exhorto_origen_id" in item, True)

    def test_post_exh_exhortos(self):
        """Test POST method for exh_exhortos"""

        # Preparar el Faker
        faker = Faker("es_MX")

        # Definir la parte actora
        parte_actor_genero = faker.random_element(elements=("M", "F"))
        if parte_actor_genero == "M":
            parte_actor_nombre = faker.first_name_male()
            parte_actor_apellido_paterno = faker.last_name_male()
            parte_actor_apellido_materno = faker.last_name_male()
        else:
            parte_actor_nombre = faker.first_name_female()
            parte_actor_apellido_paterno = faker.last_name_female()
            parte_actor_apellido_materno = faker.last_name_female()
        parte_actor = {
            "nombre": parte_actor_nombre,
            "apellido_paterno": parte_actor_apellido_paterno,
            "apellido_materno": parte_actor_apellido_materno,
            "genero": parte_actor_genero,
            "es_persona_moral": False,
            "tipo_parte": 1,  # 1 es actora
            "tipo_parte_nombre": "",  # Va vacío porque tipo_parte NO es 3
        }

        # Definir la parte demandada
        # Definir si es una persona moral o física
        es_persona_moral = faker.random_element(elements=(True, False))
        if es_persona_moral:
            parte_demandado = {
                "es_persona_moral": True,
                "nombre": faker.company(),
                "tipo_parte": 2,  # 2 es demandado
            }
        else:
            # Definir la parte demandada
            parte_demandado_genero = faker.random_element(elements=("M", "F"))
            if parte_demandado_genero == "M":
                parte_demandado_nombre = faker.first_name_male()
                parte_demandado_apellido_paterno = faker.last_name_male()
                parte_demandado_apellido_materno = faker.last_name_male()
            else:
                parte_demandado_nombre = faker.first_name_female()
                parte_demandado_apellido_paterno = faker.last_name_female()
                parte_demandado_apellido_materno = faker.last_name_female()
            parte_demandado = {
                "nombre": parte_demandado_nombre,
                "apellido_paterno": parte_demandado_apellido_paterno,
                "apellido_materno": parte_demandado_apellido_materno,
                "genero": parte_demandado_genero,
                "es_persona_moral": False,
                "tipo_parte": 2,  # 2 es demandado
                "tipo_parte_nombre": "",  # Va vacío porque tipo_parte NO es 3
            }

        # Prerapar los archivos
        archivos = []
        num_archivos = faker.random_int(min=1, max=5)
        for i in range(num_archivos):
            archivo = {
                "nombre_archivo": faker.file_name(),
                "tipo_documento": faker.random_int(min=1, max=3),
                "url": faker.url(),
            }
            archivos.append(archivo)

        # Consultar materias que tengan acceso a exhortos
        try:
            respuesta_materia = requests.get(
                url=f"{config['api_base_url']}/api/v5/materias",
                headers={"X-Api-Key": config["api_key"]},
                timeout=config["timeout"],
                params={"en_exh_exhortos": True},
            )
        except requests.exceptions.ConnectionError as error:
            self.fail(error)
        self.assertEqual(respuesta_materia.status_code, 200)

        # Validar el contenido de la respuesta de las materias
        contenido = respuesta_materia.json()
        self.assertEqual("success" in contenido, True)
        self.assertEqual("message" in contenido, True)
        self.assertEqual("data" in contenido, True)
        self.assertEqual(contenido["success"], True)

        # Tomar los datos de las materias
        materias_data = contenido["data"]
        self.assertGreater(len(materias_data), 0)

        # Elegir una clave de materia de forma aleatoria
        materia_clave = materias_data[faker.random_int(min=1, max=len(materias_data)) - 1]["clave"]

        # Consultar autoridades de la materia previamente elegida y que no estén extintas
        try:
            respuesta_autoridad = requests.get(
                url=f"{config['api_base_url']}/api/v5/autoridades",
                headers={"X-Api-Key": config["api_key"]},
                timeout=config["timeout"],
                params={"materia_clave": materia_clave, "es_extinto": False},
            )
        except requests.exceptions.ConnectionError as error:
            self.fail(error)
        self.assertEqual(respuesta_autoridad.status_code, 200)

        # Validar el contenido de la respuesta de las autoridades
        contenido = respuesta_autoridad.json()
        self.assertEqual("success" in contenido, True)
        self.assertEqual("message" in contenido, True)
        self.assertEqual("data" in contenido, True)
        self.assertEqual(contenido["success"], True)

        # Extraer las claves de las autoridades
        autoridades_data = contenido["data"]
        self.assertGreater(len(autoridades_data), 0)

        # Definir un número aleatorio para la autoridad de origen
        autoridad_origen_num = faker.random_int(min=1, max=len(autoridades_data)) - 1

        # Definir un número aleatorio para la autoridad de origen, en un ciclo para evitar que sea la misma que la de origen
        autoridad_destino_num = autoridad_origen_num
        while autoridad_destino_num == autoridad_origen_num:
            autoridad_destino_num = faker.random_int(min=1, max=len(autoridades_data)) - 1

        # Extraer datos del listado y asignarlos a la autoridad de origen
        autoridad_origen_clave = autoridades_data[autoridad_origen_num]["clave"]
        autoridad_origen_nombre = autoridades_data[autoridad_origen_num]["descripcion"]

        # Extraer datos del listado y asignarlos a la autoridad de destino
        autoridad_destino_clave = autoridades_data[autoridad_destino_num]["clave"]

        # Definir el exhorto
        exh_exhorto = {
            "autoridad_clave": autoridad_destino_clave,
            "exh_area_clave": faker.random_element(elements=("TRC-OCP", "SLT-OCP")),
            "exhorto_origen_id": str(faker.pystr(min_chars=16, max_chars=16)).upper(),
            "materia_clave": materia_clave,
            "juzgado_origen_id": autoridad_origen_clave,
            "juzgado_origen_nombre": autoridad_origen_nombre,
            "numero_expediente_origen": f"{faker.random_int(min=1, max=999)}/2025",
            "tipo_juicio_asunto_delitos": "DIVORCIO",
            "fojas": faker.random_int(min=1, max=99),
            "dias_responder": faker.random_int(min=5, max=31),
            "exh_exhorto_partes": [parte_actor, parte_demandado],
            "exh_exhorto_archivos": archivos,
        }

        # Insertar el exhorto
        try:
            respuesta = requests.post(
                url=f"{config['api_base_url']}/api/v5/exh_exhortos",
                headers={"X-Api-Key": config["api_key"]},
                timeout=config["timeout"],
                json=exh_exhorto,
            )
        except requests.exceptions.ConnectionError as error:
            self.fail(error)
        self.assertEqual(respuesta.status_code, 200)

        # Validar el contenido de la respuesta
        contenido = respuesta.json()
        self.assertEqual("success" in contenido, True)
        self.assertEqual("message" in contenido, True)
        self.assertEqual("data" in contenido, True)

        # Validar que se haya tenido éxito
        if contenido["success"] is False:
            print(contenido["message"])
        self.assertEqual(contenido["success"], True)

        # Validar los datos
        self.assertEqual(type(contenido["data"]), dict)
        item = contenido["data"]
        self.assertEqual("id" in item, True)
        self.assertEqual("autoridad_clave" in item, True)
        self.assertEqual("exh_area_clave" in item, True)
        self.assertEqual("municipio_origen_clave" in item, True)
        self.assertEqual("municipio_origen_nombre" in item, True)
        self.assertEqual("exhorto_origen_id" in item, True)
        self.assertEqual("municipio_destino_clave" in item, True)
        self.assertEqual("municipio_destino_nombre" in item, True)
        self.assertEqual("materia_clave" in item, True)
        self.assertEqual("materia_nombre" in item, True)
        self.assertEqual("juzgado_origen_id" in item, True)
        self.assertEqual("juzgado_origen_nombre" in item, True)
        self.assertEqual("numero_expediente_origen" in item, True)
        self.assertEqual("tipo_juicio_asunto_delitos" in item, True)
        self.assertEqual("fojas" in item, True)
        self.assertEqual("dias_responder" in item, True)
        self.assertEqual("remitente" in item, True)
        self.assertEqual("estado" in item, True)
        self.assertEqual("exh_exhorto_partes" in item, True)
        self.assertEqual("exh_exhorto_archivos" in item, True)
        self.assertEqual(item["autoridad_clave"], autoridad_destino_clave)
        self.assertEqual(item["materia_clave"], materia_clave)
        self.assertEqual(item["juzgado_origen_id"], autoridad_origen_clave)
        self.assertEqual(item["juzgado_origen_nombre"], autoridad_origen_nombre)
        self.assertEqual(item["tipo_juicio_asunto_delitos"], "DIVORCIO")


if __name__ == "__main__":
    unittest.main()
