import web
from models.pediatras import Personas, firebase

db = firebase.database()

render = web.template.render("views/")

class AgregarPaciente:
    def GET(self):
        try:
            # Verificamos si la sesión está iniciada
            session = web.ctx.session
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
                
            return render.agregar_personas()
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR: {str(error)}")
            return "Ocurrió un error, revisa la consola."
    
    def POST(self):
        try:
            # Verificamos si la sesión está iniciada
            session = web.ctx.session
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
                
            datos = web.input()
            
            campos_obligatorios = [
                "nombre", "primer_apellido", "segundo_apellido", 
                "edad", "genero", "telefono",
                "nombre_madre", "direccion"
            ]
            
            for campo in campos_obligatorios:
                if campo not in datos or datos[campo].strip() == "":
                    print(f"Campo faltante o vacío: {campo}")
                    return f"Error: El campo {campo} es obligatorio."
            
            # Obtenemos el correo del pediatra de la sesión
            correo_pediatra = session.get('usuario').get('correo')
            
            # Generamos un ID único para el bebé (con formato "bb" + números)
            bebe_id = "bb" + db.generate_key()[:5]  # Usamos solo los primeros 5 caracteres para mantenerlo corto
            
            paciente = {
                "nombre": datos.nombre,
                "primer_apellido": datos.primer_apellido,
                "segundo_apellido": datos.segundo_apellido,
                "edad": datos.edad,
                "genero": datos.genero,
                "telefono": datos.telefono,
                "nombre_madre": datos.nombre_madre,
                "nombre_padre": datos.get("nombre_padre", "No especificado"),
                "direccion": datos.direccion,
                "fecha_registro": db.generate_key(),
                "pediatra": correo_pediatra
            }
            
            print("Datos del paciente a guardar:", paciente)
            
            # Buscamos al pediatra por su correo electrónico
            usuarios = db.child("usuarios").get().val()
            pediatra_id = None
            
            # Corregido: Buscar por 'correo' en lugar de 'email'
            for user_id, datos_usuario in usuarios.items():
                # Imprimimos para debug
                print(f"Revisando usuario {user_id}: correo={datos_usuario.get('correo')}, rol={datos_usuario.get('rol')}")
                if datos_usuario.get("correo") == correo_pediatra and datos_usuario.get("rol") == "pedia":
                    pediatra_id = user_id
                    print(f"✅ Pediatra encontrado con ID: {pediatra_id}")
                    break
            
            if not pediatra_id:
                print(f"❌ Error: No se encontró el pediatra con correo {correo_pediatra}")
                return f"Error: No se encontró el pediatra con correo {correo_pediatra}"
            
            # Obtenemos los bebés vinculados actuales (o inicializamos si no existen)
            bebes_vinculados = db.child("usuarios").child(pediatra_id).child("bebesvinculados").get().val() or {}
            
            # Añadimos el nuevo bebé a los bebés vinculados del pediatra
            bebes_vinculados[bebe_id] = paciente
            
            # Actualizamos los datos del pediatra con el bebé vinculado
            db.child("usuarios").child(pediatra_id).update({
                "bebesvinculados": bebes_vinculados
            })
            
            print(f"✅ Bebé con ID {bebe_id} vinculado directamente al pediatra con ID {pediatra_id}")
            
            # Redirigimos a la lista de personas
            raise web.seeother('/listaspersonas')
            
        except web.seeother as redireccion:
            raise redireccion
        except Exception as e:
            print(f"❌ Error al agregar paciente: {str(e)}")
            return f"Error al agregar paciente: {str(e)}"