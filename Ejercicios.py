#Ejercicio 1  Quitar duplicados conservando orden
#Dada ciudades = ["Quito","Guayaquil","Quito","Cuenca","Guayaquil"], obtén una lista sin repetidos respetando el orden de aparición (un set solo no alcanza).
ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]

vistas = set()    
unicas = []         
for ciudad in ciudades:
    if ciudad not in vistas:
        vistas.add(ciudad)
        unicas.append(ciudad)

print(unicas)  

#Ejercicio 2  COntar con un diccionario
#Con la misma lista, arma un diccionario {"Quito": 2, "Guayaquil": 2, "Cuenca": 1}.
conteo = {}
for ciudad in ciudades:
    conteo[ciudad] = conteo.get(ciudad, 0) + 1    

print(conteo)
mas_repetida = max(conteo, key=conteo.get)
print(mas_repetida)

#Ejercicio 3 Conjuntos en accion
#inscritos_matematica = {"Ana","Luis","Sol","Marco"} y inscritos_ingles = {"Luis","Marco","Ruth"}. Responde con código: ¿quiénes están en las dos?, ¿quiénes solo en matemática?, ¿cuántos estudiantes distintos hay en total?
ambas       = inscritos_matematica & inscritos_ingles    
solo_mate   = inscritos_matematica - inscritos_ingles    
total       = len(inscritos_matematica | inscritos_ingles)  

print(sorted(ambas), sorted(solo_mate), total)

#Ejercicio 4 De lista de diccionario
#Con clientes = [{"id":1,"nombre":"Ana"},{"id":2,"nombre":"Luis"}], crea un diccionario {id: cliente} para acceder por id sin recorrer la lista. Luego imprime el nombre del id 2.
indice = {cliente["id"]: cliente for cliente in clientes}
print(indice[2]["nombre"])  

# Diferencia de costo:
# recorrer la lista  -> revisa hasta N registros
# indice[2]          -> una sola operación, sin importar cuántos haya

#Ejercicio 5  Tuplas como registros inmutables
#Dada ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)], imprime el mes con mayor venta y el total, usando desempaquetado de tuplas.
total = sum(monto for _mes, monto in ventas)

mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])

print(f"Total: {total}")
print(f"Mejor mes: {mejor_mes} con {mejor_monto}")

for mes, monto in ventas:              # desempaquetado en el for
    print(f"{mes:<10} {monto}")

#Ejercicio 6  Sobre el proyecto
#Agrega al Controlador la función clientes_por_ciudad() que devuelva un diccionario {"Guayaquil": ["Ana", "Luis"], "Quito": ["Sol"]}.
def clientes_por_ciudad():
    agrupados = {}
    for registro in gestor.leer():
        ciudad = registro.get("ciudad", "").title() or "Sin ciudad"
        # setdefault: si la ciudad no estaba, crea la lista vacía y luego agrega
        agrupados.setdefault(ciudad, []).append(registro["nombre"])
    return agrupados

#Ejercicio 7  ¿Instancia, de clase o estático?
#Clasifica cada método y justifica: (a) calcular el total de una venta, (b) crear un objeto Producto a partir de un diccionario, (c) saber si un precio es válido, (d) saber si un producto tiene stock bajo, (e) calcular el IVA de cualquier monto.
#(a) De instancia: usa self.cantidad y self.precio_unitario de ESA venta.
#(b) De clase: no hay objeto todavía, lo fabrica con return cls(...). Es desde_diccionario().
#(c) Estático: la regla “mayor a 0” no depende de ningún producto concreto; se usa antes de crearlo.
#(d) De instancia: compara self.stock con el atributo estático STOCK_MINIMO. Usa el objeto, así que lleva self.
#(e) Estático: recibe un monto cualquiera y devuelve otro. No necesita ningún producto.

#Ejercicio 8 Un modelo nuevo con herencia
#Agrega la clase Proveedor, que hereda de Persona y suma ruc y empresa. Escribe __init__, a_diccionario() y etiqueta() reutilizando al padre.
class Proveedor(Persona):

    def __init__(self, id_registro, nombre, apellido, email, ruc="", empresa=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.ruc = ruc
        self.empresa = empresa

    def a_diccionario(self):
        datos = super().a_diccionario()      # id + nombre + apellido + email
        datos["ruc"] = self.ruc
        datos["empresa"] = self.empresa
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.empresa or 'sin empresa'} · RUC {self.ruc}"


# Y desde_diccionario() ya funciona sin escribir nada:
p = Proveedor.desde_diccionario({"id": 1, "nombre": "Luis", "apellido": "Mora",
                                 "email": "luis@x.com", "ruc": "0912345678001",
                                 "empresa": "Importadora Sur"})
print(p)     # usa __str__ de ModeloBase -> etiqueta() de Proveedor

#Ejercico 9   Polimorfismo sin if
#Esta función tiene el olor a “falta polimorfismo”. Reescríbela sin ningún if de tipo.
def describir(objeto, tipo):
    if tipo == "cliente":
        return f"{objeto.nombre} {objeto.apellido} de {objeto.ciudad}"
    elif tipo == "producto":
        return f"{objeto.nombre} a ${objeto.precio}"
    elif tipo == "venta":
        return f"venta de {objeto.cantidad} unidades"

#Ejercicio 10   Atributo estático nuevo
#Agrega a Producto el atributo estático DESCUENTO_MAYORISTA = 0.10 y el método estático precio_mayorista(precio, cantidad), que aplica el descuento solo si la cantidad es 12 o más. Úsalo en el comprobante.
class Producto(ModeloBase):
    DESCUENTO_MAYORISTA = 0.10
    CANTIDAD_MAYORISTA = 12

    @staticmethod
    def precio_mayorista(precio, cantidad):
        if cantidad >= Producto.CANTIDAD_MAYORISTA:
            return round(precio * (1 - Producto.DESCUENTO_MAYORISTA), 2)
        return round(precio, 2)


# En views.crear_venta(), al armar la venta:
precio = Producto.precio_mayorista(producto.precio, int(datos["cantidad"]))
venta = Venta(siguiente_id(gestor_ventas), int(datos["cliente_id"]),
              producto.id, int(datos["cantidad"]), precio)