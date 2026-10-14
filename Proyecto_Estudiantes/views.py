from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUÉ métodos debe tener todo controlador.
# CÓMO se hace cada uno lo escribe cada controlador, de la forma más simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE CLIENTES
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiante.json"):
        self.gestor = GestorJSON(archivo)

        # Leemos el JSON y convertimos cada diccionario en un objeto Cliente
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo está bien."""
        # Al crear hay que traer los tres obligatorios; al actualizar, solo lo que cambia
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO con los emails de los OTROS clientes
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().lower()
            # CONJUNTO con los carnets de los OTROS clientes
            usados = {e.carnet for e in self.lista if e.id != id_actual}
            if carnet in usados:
                return "Ese carnet ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for estudiante in self.lista:
            if (texto in estudiante.nombre.lower()
                    or texto in estudiante.apellido.lower()
                    or texto in estudiante.email
                    or texto in estudiante.carnet.lower()
                    or texto in estudiante.carrera.lower()):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["apellido"]).strip().title(),
                          str(datos["email"]).strip().lower(),
                          str(datos.get("carnet", "")).strip().upper(),
                          str(datos.get("carrera", "")).strip().title())
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiantete is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # DIFERENCIA de conjuntos: campos que no existen en un cliente
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        # Se valida ANTES de tocar el objeto: si algo falla, no cambia nada
        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un cliente con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    # --- propio de clientes ---
    def carreras(self):
        """CONJUNTO de ciudades: sin repetidos. sorted() lo devuelve como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera})


# =====================================================================
# CONTROLADOR DE PRODUCTOS
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materia.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        # es_precio_valido es el método ESTÁTICO de Producto
        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            codigos = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos:
                return f"Ya existe una materia con el código {codigo}"

        cupos = str(datos.get("cupos", "")).strip()
        if cupos != "" and (not cupos.isdigit() or int(cupos) < 0 or int(cupos) > Materia.CUPOS_MAXIMOS):
            return f"Los cupos deben ser un entero entre 0 y {Materia.CUPOS_MAXIMOS}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for materia in self.lista:
            if texto in materia.nombre.lower():
                encontrados.append(materia)
        return encontrados

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        # Si no escribieron el stock, empieza en 0
        cupos = str(datos.get("cupos", "")).strip()
        materia = Materia(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            str(datos["codigo"]).strip().upper(),
                            int(datos.get("creditos", 3)),
                            int(cupos) if cupos != "" else Materia.CUPOS_MAXIMO)
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe un materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.precio = str(datos["codigo"])
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizado"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe un materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminado"

    # --- propio de materias ---
    def sin_cupo(self):
        bajos = []
        for materia in self.lista:
            if materia.cupo_bajo():
                bajos.append(materia)
        return bajos


# =====================================================================
# CONTROLADOR DE VENTAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        # La venta USA a los otros dos controladores.
        # Hay que pasarle los MISMOS que usa main.py.
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for Matricula in self.lista:
            datos.append(Matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id, materia_id deben ser números enteros"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe un materia con id {materia_id}"
        if not materia.hay_cupo():
            return f"No hay cupos disponible en la materia {materia.nombre}: "

        periodo = str(datos.get("periodo", "")).strip()
        if not periodo:
            return "El periodo es obligatorio"

        for mat in self.lista:
            if mat.estudiante_id == estudiante_id and mat.materia_id == materia_id and mat.periodo == periodo:
                return "El estudiante ya está matriculado en esta materia en el mismo periodo"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        # Las matriculas se buscan por fecha, ej: "2026-09"
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for matricula in self.lista:
            if texto in matricula.fecha:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        # datos = {"estudiante_id": 1, "materia_id": 2, "cupos": 3}
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(self.siguiente(),
                    int(datos["estudiante_id"]),
                    materia.id,
                    str(datos.get("periodo", "")).strip(),
                    float(datos.get("nota", 0.0)))      

        materia.ocupar_cupo()
        self.materias.guardar()                # guarda el stock nuevo en materias.json
        self.lista.append(matricula)
        self.guardar()                          # guarda la matricula en matriculas.json
        return True, f"matricula {matricula.id} registrada con exito"

    def actualizar(self, id_matricula, datos):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"
        if not datos:
            return False, "No se indicó ningún cambio"

        if "nota" in datos:
            if not Materia.es_nota_valida(datos["nota"]):
                return False, f"Nota inválida: '{datos['nota']}' (debe ser entre 0 y 20)"
            matricula.nota = float(datos["nota"])

        self.guardar()
        return True, f"Matrícula {id_matricula} actualizada"

    def eliminar(self, id_matricula):
        """Anular una matricula: se borra y el stock vuelve al producto."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matricula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo(matricula.cantidad)
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"matricula {id_matricula} anulada y cupo devuelto"

    # --- propio de matriculas ---
    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        estudiante = self.estudiantes.obtener(matricula.estudiante_id)
        materia = self.materias.obtener(matricula.materia_id)
        carrera = estudiante.carrera if estudiante else "sin carrera"

        texto = f"COMPROBANTE #{matricula.id}   fecha: {matricula.fecha}\n"
        texto += f"Estudiante : {estudiante.nombre_completo() if estudiante else 'eliminado'}\n"
        texto += f"Materia    : {materia.nombre if materia else 'eliminado'}\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota   : {matricula.nota:.1f}\n"
        texto += f"Estado : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: {estudiante_id: [matriculas de ese estudiante]}."""
        agrupadas = {}
        for matricula in self.lista:
            if matricula.estudiante_id not in agrupadas:
                agrupadas[matricula.estudiante_id] = []
            agrupadas[matricula.estudiante_id].append(matricula)
        return agrupadas

    def total_aprobadas(self):
        return sum(1 for mat in self.lista if mat.esta_aprobada())
