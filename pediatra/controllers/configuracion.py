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
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
            
            usuario_id = web.ctx.session.usuario.get('id')
            print(f"🆔 ID del usuario en sesión: {usuario_id}")
            
            p = Personas()
            datos_pediatra = p.obtener_pediatra(usuario_id)
            
            if not datos_pediatra:
                print(f"⚠️ No se encontraron datos para el usuario ID: {usuario_id}")
                datos_pediatra = {"id": usuario_id}
            
            if hasattr(datos_pediatra, 'items'):
                datos_pediatra = dict(datos_pediatra)
            
            mensaje_actual = mensaje
            mensaje = None
            
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
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                raise web.seeother('/iniciosesion')
            
            formulario = web.input()
            usuario_id = web.ctx.session.usuario.get('id')
            
            if not formulario.get('nombres') or not formulario.get('primer_apellido'):
                mensaje = "Error: Faltan campos obligatorios."
                raise web.seeother('/configuracion')
            
            datos_actualizar = {
                'nombres': formulario.get('nombres'),
                'primer_apellido': formulario.get('primer_apellido'),
                'segundo_apellido': formulario.get('segundo_apellido', ''),
                'nacimiento': formulario.get('nacimiento', ''),
                'licencia': formulario.get('licencia', '')
            }
            
            p = Personas()
            resultado = p.actualizar_pediatra(usuario_id, datos_actualizar)
            
            if resultado:
                datos_actualizados = p.obtener_pediatra(usuario_id)
                if datos_actualizados and hasattr(datos_actualizados, 'items'):
                    datos_actualizados = dict(datos_actualizados)
                
                if datos_actualizados:
                    web.ctx.session.usuario = datos_actualizados
                else:
                    for key, value in datos_actualizar.items():
                        web.ctx.session.usuario[key] = value
                
                mensaje = "¡Información actualizada correctamente!"
            else:
                mensaje = "No se pudo actualizar la información. Intente nuevamente."
            
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
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                raise web.seeother('/iniciosesion')
            
            formulario = web.input(foto={})
            if 'foto' not in formulario or not formulario['foto'].filename:
                mensaje = "Error: No se seleccionó ninguna imagen."
                raise web.seeother('/configuracion')
            
            usuario_id = web.ctx.session.usuario.get('id')
            
            p = Personas()
            url_foto = p.subir_foto_perfil(usuario_id, formulario['foto'])
            
            if url_foto:
                web.ctx.session.usuario['fotoperfil'] = url_foto
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
    def POST(self, usuario_id, bebe_id):
        try:
            archivo = web.input(foto_paciente={})
            
            if 'foto_paciente' in archivo:
                extension = os.path.splitext(archivo.foto_paciente.filename)[1]
                nombre_archivo = f"bebe_{bebe_id}_{uuid.uuid4()}{extension}"
                ruta_local = os.path.join('static', 'uploads', 'bebes', nombre_archivo)
                os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
                
                with open(ruta_local, 'wb') as f:
                    f.write(archivo.foto_paciente.file.read())
                
                url_foto = f"/static/uploads/bebes/{nombre_archivo}"
                
                personas = Personas()
                resultado = personas.actualizar_foto_bebe(usuario_id, bebe_id, url_foto)
                
                if resultado:
                    return web.json.dumps({"success": True, "url": url_foto})
                else:
                    return web.json.dumps({"success": False, "error": "No se pudo actualizar la foto"})
            
            return web.json.dumps({"success": False, "error": "No se recibió ningún archivo"})
        
        except Exception as e:
            print(f"Error en ActualizarFotoBebe: {str(e)}")
            return web.json.dumps({"success": False, "error": str(e)})