import pyrebase
import bcrypt  # Importar bcrypt para el hashing de contraseñas
import os
import json
import uuid
import web 
import json


config = {
    "apiKey": "AIzaSyB-jKmhqOEX7H3p22MxQs_A7MdqTN-ei70",
    "authDomain": "bbchat-2a2af.firebaseapp.com",
    "databaseURL": "https://bbchat-2a2af-default-rtdb.firebaseio.com",
    "storageBucket": "bbchat-2a2af.firebasestorage.app"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

    
def registrar_usuario(nombre, apellido1, apellido2, fecha_nacimiento, correo, licencia, password, rol):
    try:
        user = auth.create_user_with_email_and_password(correo, password)  # ¡Firebase maneja la seguridad!
        
        datos_usuario = {
            "nombres": nombre,
            "primer_apellido": apellido1,
            "segundo_apellido": apellido2,
            "fecha_nacimiento": fecha_nacimiento,
            "correo": correo,
            "licencia": licencia if rol == "pedia" else None,  # Solo se asigna licencia si es pediatra
            "rol": rol,
            "uid": user["localId"],
            "fotoperfil": "link-to-fotoperfil-placeholder.foto"  # Puedes asignar un link placeholder o vacío
        }
        
        # Para padres o cuidadores, agregamos la sección de bebés
        if rol == "padre":
            datos_usuario["bebes"] = {}

        # Guardamos los datos del usuario en Firebase
        db.child("usuarios").child(user["localId"]).set(datos_usuario)
        print("Usuario registrado correctamente.")
        return True

    except Exception as e:
        print(f"Error al registrar usuario: {str(e)}")
        return False  



def iniciar_sesion(correo, password):
    try:
        user = auth.sign_in_with_email_and_password(correo, password)
        uid = user["localId"]
        
        usuarios = db.child("usuarios").get().val()
        
        usuario_encontrado = None
        for user_id, datos in usuarios.items():
            if datos.get("correo") == correo:  # ✅ Corrección aquí
                usuario_encontrado = datos
                break
        
        if usuario_encontrado:
            print("Inicio de sesión exitoso.")
            return usuario_encontrado  
        else:
            print("No se encontraron datos del usuario.")
            return None
    
    except Exception as e:
        print(f"Error en el inicio de sesión: {str(e)}")
        return None



class Personas:
    def __init__(self):
        self.db = db 

    def lista_pacientes(self, correo_pediatra):
        try:
            usuarios = self.db.child("usuarios").get().val()
            print("📂 Datos crudos desde Firebase:", json.dumps(usuarios, indent=2))

            # Verificar si el pediatra está en la base de datos
            pediatra_id = None
            for user_id, datos in usuarios.items():
                if datos.get("correo", "").strip().lower() == correo_pediatra.strip().lower() and datos.get("rol") == "pedia":
                    print(f"✅ Pediatra encontrado: {user_id}")
                    pediatra_id = user_id
                    break  
            
            if not pediatra_id:
                print("❌ Error: No se encontró el pediatra en la base de datos.")
                return "Error: No se encontró el pediatra en la base de datos."

            # Buscar bebés vinculados a este pediatra
            pacientes = {}
            for padre_id, datos in usuarios.items():
                if datos.get("rol") == "padre" and "bebes" in datos:
                    bebes = datos["bebes"]
                    for bebe_id, bebe_info in bebes.items():
                        # Comprobamos si el pediatra está vinculado al bebé
                        if pediatra_id in usuarios and "bebesvinculados" in usuarios[pediatra_id]:
                            if bebe_id in usuarios[pediatra_id]["bebesvinculados"]:
                                paciente = {
                                    "id": bebe_id,
                                    "nombres": bebe_info.get("nombres", "Desconocido"),
                                    "apodo": bebe_info.get("apodo", ""),
                                    "edad": bebe_info.get("nacimiento", "Fecha no registrada"),
                                    "alergias": bebe_info.get("alergias", "Ninguna"),
                                    "fotoperfil": bebe_info.get("fotoperfil", ""),
                                    "padre": {
                                        "id": padre_id,
                                        "nombre": datos.get("nombres", "Desconocido"),
                                        "correo": datos.get("email", ""),
                                        "fotoperfil": datos.get("fotoperfil", ""),
                                    }
                                }
                                pacientes[bebe_id] = paciente

            if not pacientes:
                print("⚠️ No hay bebés vinculados a este pediatra.")
                return "No hay bebés vinculados a este pediatra."

            return pacientes
        except Exception as e:
            print(f"❌ Error en lista_pacientes: {str(e)}")
            return f"Error en lista_pacientes: {str(e)}"


    
    def agregar_persona(self, nombre, edad, rol, email, bebe_id=None):
        """Método para agregar personas (padres, pediatras, etc.) con relación a un bebé"""
        try:
            persona = {
                "nombre": nombre,
                "edad": edad,
                "rol": rol,
                "email": email
            }

            # Si es un pediatra o un padre/madre, podemos agregar bebés vinculados
            if rol == "padre" or rol == "pediatra":
                persona["bebesvinculados"] = {}  # Solo si es relevante para el rol

            if bebe_id:  # Si se incluye un bebé, agregarlo al pediatra o al padre
                if rol == "padre" or rol == "pediatra":
                    persona["bebesvinculados"][bebe_id] = ""  # Añadir bebé vinculado
            
            # Subir la persona a Firebase
            self.db.child("usuarios").push(persona)
            return True
        except Exception as e:
            print(f"Error al agregar persona: {str(e)}")
            return False


    def lista_pacientes(self, pediatra_email=None):
        """Método para listar pacientes (bebés), filtrando por pediatra si es necesario"""
        try:
            datos = self.db.child("usuarios").get()
            todos_usuarios = datos.val() if datos.val() else {}

            pacientes_filtrados = {}

            for id_usuario, usuario in todos_usuarios.items():
                if usuario.get("rol") == "pediatra" and pediatra_email == usuario.get("email"):
                    # Obtener los bebés vinculados al pediatra
                    bebes_vinculados = usuario.get("bebesvinculados", {})
                    for bebe_id in bebes_vinculados:
                        # Buscar bebé en la base de datos
                        bebe = self.db.child("usuarios").child(bebe_id).get()
                        if bebe.val():
                            pacientes_filtrados[bebe_id] = bebe.val()

            return pacientes_filtrados
        except Exception as e:
            print(f"Error al listar pacientes: {str(e)}")
            return {}


    def lista_pacientes_por_id_y_pediatra(self, paciente_id=None, pediatra_email=None):

        try:
            datos = self.db.child("usuarios").get()
            todos_usuarios = datos.val() if datos.val() else {}

            pacientes_filtrados = {}

            for id_usuario, usuario in todos_usuarios.items():
                if usuario.get("rol") == "pediatra" and pediatra_email == usuario.get("email"):
                    bebes_vinculados = usuario.get("bebesvinculados", {})
                    for bebe_id, _ in bebes_vinculados.items():
                        bebe = self.db.child("usuarios").child(bebe_id).get()
                        if bebe.val():
                            # Filtrar por paciente_id si se proporciona
                            if paciente_id and paciente_id == bebe_id:
                                pacientes_filtrados[bebe_id] = bebe.val()

            return pacientes_filtrados
        except Exception as e:
            print(f"Error al listar pacientes: {str(e)}")
            return {}


    def agregar_paciente(self, datos_paciente, pediatra_email=None):
        """Método para agregar un paciente (bebé) con datos completos y asociarlo a un pediatra"""
        try:
            # Subir bebé a la base de datos
            resultado = self.db.child("usuarios").push(datos_paciente)
            
            if pediatra_email:
                # Vincular bebé con el pediatra correspondiente
                usuario_pediatra = self.db.child("usuarios").order_by_child("email").equal_to(pediatra_email).get()
                if usuario_pediatra.val():
                    pediatra_id = list(usuario_pediatra.val().keys())[0]
                    # Añadir bebé al pediatra
                    self.db.child("usuarios").child(pediatra_id).child("bebesvinculados").push(datos_paciente["email"])

            return True
        except Exception as e:
            print(f"Error al agregar paciente: {str(e)}")
            return False


    def obtener_pediatra(self, correo):

        try:
            correo_key = correo.replace(".", ",")
            datos = self.db.child("usuarios").child(correo_key).get()

            if datos.val() and datos.val().get("rol") == "pediatra":
                return datos.val()
            return None
        except Exception as e:
            print(f"Error al obtener pediatra: {str(e)}")
            return None


    def actualizar_pediatra(self, correo, datos):
        try:
            # En Firebase, el punto (.) no está permitido en las claves, así que lo reemplazamos por coma (,)
            correo_key = correo.replace(".", ",")
            
            # En Firebase, podemos actualizar solo los campos específicos
            self.db.child("usuarios").child(correo_key).update(datos)
            
            return True
        except Exception as e:
            print(f"Error al actualizar pediatra: {str(e)}")
            return False

    def actualizar_paciente(self, paciente_id, datos_actualizar):
        try:
            self.db.child("pacientes").child(paciente_id).update(datos_actualizar)
            print(f"Datos actualizados para el paciente {paciente_id}: {datos_actualizar}")
            return True
        except Exception as e:
            print(f"Error al actualizar paciente: {str(e)}")
            return False


    def actualizar_foto_paciente(self, paciente_id, ruta_foto):
        try:
            self.db.child("pacientes").child(paciente_id).update({"foto_perfil": ruta_foto})
            print(f"Foto actualizada para el paciente {paciente_id}")
            return True
        except Exception as e:
            print(f"Error al actualizar foto de paciente: {str(e)}")
            return False
    
    def subir_foto_perfil(self, correo, archivo):
        try:
            # Generar un nombre de archivo único
            extension = os.path.splitext(archivo.filename)[1]
            nombre_archivo = f"{correo.replace('.', '')}{uuid.uuid4()}{extension}"
            
            # Ruta donde se guardará la foto
            ruta_local = os.path.join('static', 'uploads', 'perfiles', nombre_archivo)
            ruta_storage = f"perfiles/{nombre_archivo}"
            
            # Asegurar que el directorio exista
            os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
            
            # Guardar archivo localmente
            with open(ruta_local, 'wb') as f:
                f.write(archivo.file.read())
            
            # Verificar si el archivo existe antes de subirlo
            if not os.path.exists(ruta_local):
                print(f"Error: El archivo {ruta_local} no existe")
                return None
            
            # Subir a Firebase Storage
            try:
                self.storage.child(ruta_storage).put(ruta_local)
            except Exception as e:
                print(f"Error al subir a Firebase Storage: {str(e)}")
                # Continuar con la ruta local si la subida falla
            
            # Construir URL de la foto (usar ruta local si la subida falla)
            url_foto = f"/static/uploads/perfiles/{nombre_archivo}"
            
            # Actualizar datos del usuario con la URL de la foto
            correo_key = correo.replace(".", ",")
            self.db.child("usuarios").child(correo_key).update({
                "foto_perfil": url_foto
            })
            
            return url_foto
        except Exception as e:
            print(f"Error al subir foto: {str(e)}")
            return None
        
    def actualizar_foto_bebe(self, paciente_id, archivo):
        try:
            # Generar un nombre de archivo único
            extension = os.path.splitext(archivo.filename)[1]
            nombre_archivo = f"{paciente_id}{uuid.uuid4()}{extension}"
            
            # Ruta donde se guardará la foto
            ruta_local = os.path.join('static', 'uploads', 'bebes', nombre_archivo)
            ruta_storage = f"bebes/{nombre_archivo}"
            
            # Asegurar que el directorio exista
            os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
            
            # Guardar archivo localmente
            with open(ruta_local, 'wb') as f:
                f.write(archivo.file.read())
            
            # Verificar si el archivo existe antes de subirlo
            if not os.path.exists(ruta_local):
                print(f"Error: El archivo {ruta_local} no existe")
                return None
            
            # Subir a Firebase Storage
            try:
                self.storage.child(ruta_storage).put(ruta_local)
            except Exception as e:
                print(f"Error al subir a Firebase Storage: {str(e)}")
                # Continuar con la ruta local si la subida falla
            
            # Construir URL de la foto (usar ruta local si la subida falla)
            url_foto = f"/static/uploads/bebes/{nombre_archivo}"
            
            # Actualizar datos del paciente con la URL de la foto
            self.db.child("pacientes").child(paciente_id).update({
                "foto_perfil": url_foto
            })
            
            print(f"Foto actualizada para el bebé {paciente_id}")
            return url_foto
        except Exception as e:
            print(f"Error al actualizar foto del bebé: {str(e)}")
            return None
    def subir_documentos_paciente(self, paciente_id, datos):
        try:
            documentos_guardados = {}
            
            # Tipos de documentos a guardar
            tipos_documentos = [
                'carnet_vacunacion', 
                'resultados_laboratorio', 
                'recetas_medicas', 
                'otros_documentos'
            ]
            
            for tipo_documento in tipos_documentos:
                archivo = datos.get(tipo_documento, {})
                
                # Check if the file is actually present and has a filename
                if hasattr(archivo, 'filename') and archivo.filename:
                    # Generar un nombre de archivo único
                    extension = os.path.splitext(archivo.filename)[1]
                    nombre_archivo = f"{paciente_id}_{tipo_documento}_{uuid.uuid4()}{extension}"
                    
                    # Ruta donde se guardará el documento
                    ruta_local = os.path.join('static', 'uploads', 'documentos', nombre_archivo)
                    ruta_storage = f"documentos/{nombre_archivo}"
                    
                    # Asegurar que el directorio exista
                    os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
                    
                    # Guardar archivo localmente
                    with open(ruta_local, 'wb') as f:
                        f.write(archivo.file.read())
                    
                    # Verificar si el archivo existe
                    if not os.path.exists(ruta_local):
                        print(f"Error: El archivo {ruta_local} no existe")
                        continue
                    
                    # Construir URL del documento
                    url_documento = f"/static/uploads/documentos/{nombre_archivo}"
                    
                    # Almacenar la URL del documento
                    documentos_guardados[tipo_documento] = url_documento
            
            # Actualizar los documentos en la base de datos
            if documentos_guardados:
                self.db.child("pacientes").child(paciente_id).child("documentos").update(documentos_guardados)
                print(f"Documentos actualizados para el paciente {paciente_id}")
                return documentos_guardados
            
            return None
        
        except Exception as e:
            print(f"Error al subir documentos: {str(e)}")
            return None