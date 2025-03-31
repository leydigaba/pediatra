import web
import json
import os
import uuid
from models.pediatras import Personas

# Renderizar las vistas desde la carpeta "views"
render = web.template.render("views/")

class DetalleUsuario:
    def GET(self, persona_id):
            session = web.ctx.session
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')

            usuario = session.get('usuario')
            if usuario.get('rol') != 'pedia':
                    print("🚫 Acceso denegado. Solo los pediatras pueden ver esta lista.")
                    raise web.seeother('/')
                
            correo_pediatra = usuario.get('correo')
            #print("🌟 ID recibido en la URL: ", persona_id)  # <-- Verificamos si el ID llega bien
            #print(f"🔍 Correo pediatra: {correo_pediatra}")
            if not persona_id:
                return "⚠️ Error: No se recibió un ID válido."


            try:
                p = Personas()
                datos_persona = p.obtener_bebe_por_id(persona_id, correo_pediatra)
                #web.debug(f"🔍 Datos obtenidos: {datos_persona}")  # Para verificar estructura
                #print("🔍 Datos obtenidos: ", datos_persona)  # Para verificar estructura
                # Extraemos el paciente del diccionario
                paciente = datos_persona.get(persona_id, None)
                #web.debug(f"✅ Paciente seleccionado: {paciente}")  # Para verificar
                #print(f"✅ Paciente seleccionado: {paciente}")  # Para verificar
                
                if paciente:
                    return render.detallepersonas(datos_persona)
                else:
                    return "❌ Persona no encontrada."

            except Exception as e:
                #web.debug(f"💥 Error en DetallePersonas: {str(e)}")  # <-- Esto muestra cualquier error
                return f"⚠️ Error interno del servidor: {str(e)}"

    def POST(self, paciente_id):
        print(f"POST iniciado con paciente_id: '{paciente_id}'")
        try:
            # Verificar si la sesión está iniciada
            session = web.ctx.session
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                return json.dumps({"error": "No hay sesión iniciada"})

            datos = web.input(
                carnet_vacunacion={}, 
                resultados_laboratorio={}, 
                recetas_medicas={}, 
                otros_documentos={}
            )
            correo_pediatra = session.get('usuario').get('correo')
            personas = Personas()
            print(f"Correo pediatra: {correo_pediatra}")
            paciente = personas.obtener_bebe_por_id(paciente_id, correo_pediatra)
            if not paciente or not paciente.get(paciente_id):
                return json.dumps({"error": "No tienes acceso a este paciente"})
            print(f"Paciente encontrado: {paciente}")

            # Separar la actualización de datos y documentos
            datos_actualizar = {
                    'nombre': datos.get('nombre'),
                    'primer_apellido': datos.get('primer_apellido'),
                    'segundo_apellido': datos.get('segundo_apellido'),
                    'fecha_nacimiento': datos.get('fecha_nacimiento'),
                    'edad': datos.get('edad'),
                    'curp': datos.get('curp'),
                    'genero': datos.get('genero'),
                    'nombre_madre': datos.get('nombre_madre'),
                    'nombre_padre': datos.get('nombre_padre'),
                    'telefono': datos.get('telefono'),
                    'direccion': datos.get('direccion'),
                    'peso': datos.get('peso'),
                    'talla': datos.get('talla'),
                    'perimetro_cefalico': datos.get('perimetro_cefalico'),
                    'grupo_sanguineo': datos.get('grupo_sanguineo'),
                    'antecedente_neonatal': datos.get('antecedente_neonatal'),
                    
                    'edad_neonatal_semanas': datos.get('edad_neonatal_semanas'),
                    'edad_neonatal_dias': datos.get('edad_neonatal_dias'),
                    'peso_datos': datos.get('peso_datos'),
                    'talla_datos': datos.get('talla_datos'),
                    'patologias': datos.get('patologias'),
            
                    'gestas': datos.get('gestas'),
                    'abortos': datos.get('abortos'),
                    'partos': datos.get('partos'),
                    'cesareas': datos.get('cesareas'),
                    'normal': datos.get('normal'),
                    'riesgo': datos.get('riesgo'), 
                    'terminacion': datos.get('terminacion')
            }
            
            # Remover claves vacías
            datos_actualizar = {k: v for k, v in datos_actualizar.items() if v}
            print(f"Datos a actualizar: {datos_actualizar}")
            # Actualizar datos del paciente
            if datos_actualizar:
                resultado = personas.actualizar_paciente(paciente_id, datos_actualizar)
            
            # Manejar subida de documentos
            documentos_guardados = personas.subir_documentos_paciente(paciente_id, datos)
            
            response = {
                "success": True,
                "mensaje": "Datos actualizados correctamente"
            }
            
            if documentos_guardados:
                response["documentos"] = documentos_guardados
                
            raise web.seeother(f'/usuario/{paciente_id}')
            return json.dumps(response)
            
            
        except Exception as e:
            print("Error en POST de DetalleUsuario:", str(e))
            return json.dumps({"success": False, "error": str(e)})


class ActualizarFotoBebe:
    def POST(self):
        global mensaje
        try:
            # Verificar sesión
            if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
                raise web.seeother('/iniciosesion')
            
            # Obtener datos del formulario
            formulario = web.input(foto={})
            
            id_paciente = web.input().get('paciente_id')
            print(f"Received paciente_id: {id_paciente}")
            
            # Verificar si se subió un archivo
            if 'foto' not in formulario or not formulario['foto'].filename:
                mensaje = "Error: No se seleccionó ninguna imagen."
                raise web.seeother(f'/usuario/{id_paciente}')
            
            # Obtener correo del pediatra
            correo_pediatra = web.ctx.session.usuario.get('correo')
            
            # Subir foto
            p = Personas()
            url_foto = p.actualizar_foto_bebe(id_paciente, formulario['foto'])
            
            if url_foto:
                # Actualizar sesión con la nueva URL de foto
                web.ctx.session.usuario['foto_perfil'] = url_foto
                mensaje = "¡Foto de perfil actualizada correctamente!"
            else:
                mensaje = "No se pudo actualizar la foto de perfil."
            
            raise web.seeother(f'/usuario/{id_paciente}')
        
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR al actualizar foto: {str(error)}")
            mensaje = f"Ocurrió un error: {str(error)}"
            raise web.seeother(f'/usuario/{id_paciente}')