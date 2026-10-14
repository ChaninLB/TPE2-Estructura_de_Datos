from datetime import date


# =====================================================================
# CLASE BASE: lo que los tres modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # ---- ÚNICO MÉTODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por los tres modelos.
        cls es la clase que llamó: Estudiante, Materia o Matricula."""
        datos = dict(datos)                 # copia, para no tocar el original
        id_registro = datos.pop("id")       # saco el id
        return cls(id_registro, **datos)    # el resto son los campos del modelo

    # ---- MÉTODOS DE INSTANCIA ----
    def a_diccionario(self):
        # Objeto -> diccionario. Cada hijo agrega sus campos.
        return {"id": self.id}

    def etiqueta(self):
        # POLIMORFISMO: cada hijo la reescribe a su manera
        return f"registro {self.id}"

    def __str__(self):
        # Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        # así que cada modelo se imprime distinto sin cambiar esta línea.
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Cliente (y mañana, de Estudiante)
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        # Sobrescribe y EXTIENDE la del padre
        return f"{super().etiqueta()} · {self.email} · {self.carnet} · {self.carrera or 'sin carrera'}"


# =====================================================================
# ÚNICA CLASE CON ATRIBUTOS Y MÉTODOS ESTÁTICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aquí viven los ejemplos de lo estático."""

    # ATRIBUTOS ESTÁTICOS (de clase): existen una sola vez, no por objeto
    CUPOS_MAXIMOS = 30         # regla del negocio, igual para todos los productos
    CUPOS_MINIMOS = 5
    NOTA_APROBACION = 14
    total_creados = 0         # contador compartido
    
    def __init__(self, id_registro, nombre, codigo, creditos, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo.upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)
        Materia.total_creados += 1        # se modifica en la CLASE, no en self

    # MÉTODOS ESTÁTICOS: reglas que no necesitan ningún producto concreto
    @staticmethod
    def es_nota_valida(valor):
        try:
            nota = float(valor)
            return nota >= 0 and nota <= 20
        except (TypeError, ValueError):
            return False

    # MÉTODOS DE INSTANCIA: necesitan los datos de ESTE producto
    def cupo_bajo(self):
        return self.cupos <= Materia.CUPOS_MINIMOS

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.cupos > 0:
            self.cupos -= 1

    def liberar_cupo(self):
        self.cupos += 1

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        alerta = " ⚠ ncupos bajos" if not self.hay_cupo() else ""
        return f"{self.codigo} - {self.nombre} · {self.creditos} creditos · cupo {self.cupos}{alerta}"


# =====================================================================
class Matricula(ModeloBase):
    """Venta simple: un cliente, un producto, una cantidad."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def estado(self):
        if self.nota >= Materia.NOTA_APROBACION:
            return "aprobado"
        else:
            return "reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"{self.periodo} {self.materia_id} "
                f"{self.estado()}")
