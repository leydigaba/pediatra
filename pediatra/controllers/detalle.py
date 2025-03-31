import web
import json
import os
import uuid
from models.pediatras import Personas

# Renderizar las vistas desde la carpeta "views"
render = web.template.render("views/")

class DetalleUsuario:
    def GET(self, paciente_id):
        try:
            session = web.ctx.session
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')

            correo_pediatra = session.get('usuario').get('correo')
            personas = Personas()
            paciente = personas.lista_pacientes_por_id_y_pediatra(paciente_id,correo_pediatra)
            print("Paciente obtenido:", paciente)
            
            # Verificar si el paciente existe
            if paciente and paciente.get(paciente_id):
         
                return render.detalle_personas(paciente)  # Mostrar los detalles del paciente
            else:
                return "No tienes acceso a este paciente"
        except web.seeother as redireccion:
            raise redireccion

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
            
            paciente = personas.lista_pacientes_por_id_y_pediatra(paciente_id, correo_pediatra)
            if not paciente or not paciente.get(paciente_id):
                return json.dumps({"error": "No tienes acceso a este paciente"})
            
            # Separar la actualización de datos y documentos
            datos_actualizar = {
                      'nombre': datos.get('nombre'),
                    'primer_apellido': datos.get('apellido1'),
                    'segundo_apellido': datos.get('apellido2'),
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
                    'antecedente_neonatal_si': datos.get('antecedente_neonatal_si'),
                    'antecedente_neonatal_no': datos.get('antecedente_neonatal_no'),
                    'edad_neonatal_semanas': datos.get('edad_neonatal_semanas'),
                    'edad_neonatal_dias': datos.get('edad_neonatal_dias'),
                    'peso_datos': datos.get('peso_datos'),
                    'talla_datos': datos.get('talla_datos'),
                    'patologias_si': datos.get('patologias_si'),
                    'patologias_no': datos.get('patologias_no'),
                    'gestas': datos.get('gestas'),
                    'abortos': datos.get('abortos'),
                    'partos': datos.get('partos'),
                    'cesareas': datos.get('cesareas'),
                    'normal': datos.get('normal'),
                    'riesgo': datos.get('riesgo'), 
                    'alto_riesgo': datos.get('alto_riesgo'),
                    'terminacion': datos.get('terminacion')
            }
            
            # Remover claves vacías
            datos_actualizar = {k: v for k, v in datos_actualizar.items() if v}
            
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