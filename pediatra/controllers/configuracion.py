import web
import os
import uuid
from models.pediatras import Personas
import json

# Configuración de plantillas
render = web.template.render("views/")

# Variable global para el mensaje
mensaje = None

class Configuracion:
    def GET(self):
        global mensaje
        try:
            # Verificar sesión de manera segura
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
            
            # Obtener correo del pediatra desde la sesión
            correo_pediatra = web.ctx.session.usuario.get('correo')
            print(f"📧 Correo del pediatra en sesión: {correo_pediatra}")
            
            # Crear instancia de Personas y obtener datos completos desde Firebase
            p = Personas()
            datos_pediatra = p.obtener_pediatra(correo_pediatra)
            
            if not datos_pediatra:
                print(f"⚠️ No se encontraron datos para el pediatra con correo: {correo_pediatra}")
                # Si no hay datos, usar al menos el correo que tenemos en la sesión
                datos_pediatra = {"correo": correo_pediatra}
            
            # Convertir OrderedDict a diccionario estándar para evitar problemas
            if hasattr(datos_pediatra, 'items'):  # Comprobar si tiene método items() (diccionario u OrderedDict)
                datos_pediatra = dict(datos_pediatra)
            
            print(f"🔍 Datos completos del pediatra (para la vista): {datos_pediatra}")
            print(f"🔍 Tipo de datos: {type(datos_pediatra)}")
            
            # Comprobar si podemos acceder a cada campo específico para debug
            print(f"Nombre: {datos_pediatra.get('nombre', 'NO DISPONIBLE')}")
            print(f"Apellido1: {datos_pediatra.get('apellido1', 'NO DISPONIBLE')}")
            print(f"Correo: {datos_pediatra.get('correo', 'NO DISPONIBLE')}")
            
            # Pasar el mensaje a la plantilla y luego limpiarlo
            mensaje_actual = mensaje
            mensaje = None  # Limpiar el mensaje después de usarlo
            
            # Renderizar la plantilla con los datos completos (diccionario estándar)
            return render.configuracion(datos_pediatra, mensaje=mensaje_actual)
            
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR en GET /configuracion: {str(error)}")
            return "Ocurrió un error: " + str(error)

class ActualizarConfiguracion:
    def POST(self):
        global mensaje
        try:
            # Verificar sesión de manera segura
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
            
            # Obtener datos del formulario
            formulario = web.input()
            
            # Validar campos obligatorios
            if not formulario.get('nombre') or not formulario.get('apellido1') or not formulario.get('correo'):
                mensaje = "Error: Faltan campos obligatorios."
                raise web.seeother('/configuracion')
            
            # Preparar datos para actualizar
            datos_actualizar = {
                'nombre': formulario.get('nombre'),
                'apellido1': formulario.get('apellido1'),
                'apellido2': formulario.get('apellido2', ''),
                'fecha_nacimiento': formulario.get('fecha_nacimiento', ''),
                'licencia': formulario.get('licencia', '')
                # Mantenemos 'rol' y 'uid' sin cambios
            }
            
            # Obtener correo del pediatra (identificador único)
            correo_pediatra = web.ctx.session.usuario.get('correo')
            
            # Actualizar datos en Firebase
            p = Personas()
            resultado = p.actualizar_pediatra(correo_pediatra, datos_actualizar)
            
            if resultado:
                # Obtener datos actualizados desde Firebase
                datos_actualizados = p.obtener_pediatra(correo_pediatra)
                
                # Convertir a diccionario estándar si es necesario
                if datos_actualizados and hasattr(datos_actualizados, 'items'):
                    datos_actualizados = dict(datos_actualizados)
                
                # Actualizar la sesión con TODOS los datos del usuario
                if datos_actualizados:
                    web.ctx.session.usuario = datos_actualizados
                else:
                    # Si fallamos al recuperar los datos actualizados, al menos actualizamos los campos locales
                    for key, value in datos_actualizar.items():
                        web.ctx.session.usuario[key] = value
                
                mensaje = "¡Información actualizada correctamente!"
            else:
                mensaje = "No se pudo actualizar la información. Intente nuevamente."
            
            # Redireccionar de vuelta a configuración
            raise web.seeother('/configuracion')
            
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR al actualizar configuración: {str(error)}")
            mensaje = f"Ocurrió un error: {str(error)}"
            raise web.seeother('/configuracion')
            
class ActualizarFoto:
    def POST(self):
        global mensaje
        try:
            # Verificar sesión
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                raise web.seeother('/iniciosesion')
            
            # Obtener datos del formulario
            formulario = web.input(foto={})
            
            # Verificar si se subió un archivo
            if 'foto' not in formulario or not formulario['foto'].filename:
                mensaje = "Error: No se seleccionó ninguna imagen."
                raise web.seeother('/configuracion')
            
            # Obtener correo del pediatra
            correo_pediatra = web.ctx.session.usuario.get('correo')
            
            # Subir foto
            p = Personas()
            url_foto = p.subir_foto_perfil(correo_pediatra, formulario['foto'])
            
            if url_foto:
                # Actualizar sesión con la nueva URL de foto
                web.ctx.session.usuario['foto_perfil'] = url_foto
                mensaje = "¡Foto de perfil actualizada correctamente!"
            else:
                mensaje = "No se pudo actualizar la foto de perfil."
            
            raise web.seeother('/configuracion')
        
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR al actualizar foto: {str(error)}")
            mensaje = f"Ocurrió un error: {str(error)}"
            raise web.seeother('/configuracion')


class ActualizarFotoBebe:
    def POST(self, paciente_id):
        try:
            # Get the uploaded file
            archivo = web.input(foto_paciente={})
            
            if 'foto_paciente' in archivo:
                # Generate a unique filename
                extension = os.path.splitext(archivo.foto_paciente.filename)[1]
                nombre_archivo = f"paciente_{paciente_id}_{uuid.uuid4()}{extension}"
                
                # Define local storage path
                ruta_local = os.path.join('static', 'uploads', 'pacientes', nombre_archivo)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
                
                # Save file locally
                with open(ruta_local, 'wb') as f:
                    f.write(archivo.foto_paciente.file.read())
                
                # Create URL path
                url_foto = f"/static/uploads/pacientes/{nombre_archivo}"
                
                # Update photo in database
                personas = Personas()
                resultado = personas.actualizar_foto_paciente(paciente_id, url_foto)
                
                if resultado:
                    return web.json.dumps({"success": True, "url": url_foto})
                else:
                    return web.json.dumps({"success": False, "error": "No se pudo actualizar la foto"})
            
            return web.json.dumps({"success": False, "error": "No se recibió ningún archivo"})
        
        except Exception as e:
            print(f"Error en ActualizarFotoBebe: {str(e)}")
            return web.json.dumps({"success": False, "error": str(e)})