import web
from models.pediatras import Personas

render = web.template.render("views/", globals())

class ActualizarEstado:
    def POST(self):
        try:
            # Obtener los datos enviados desde el frontend
            data = json.loads(web.data())
            paciente_id = data.get('id')
            nuevo_estado = data.get('estado')
            pediatra_email = data.get('pediatra_email')  # Obtener el email del pediatra desde la solicitud
            
            # Validar datos
            if not paciente_id or not nuevo_estado or not pediatra_email:
                return json.dumps({'success': False, 'message': 'Datos incompletos'})
            
            # Validar que el estado sea válido
            estados_validos = ['activo', 'inactivo', 'pendiente']
            if nuevo_estado not in estados_validos:
                return json.dumps({'success': False, 'message': 'Estado no válido'})
            
            # Inicializar modelo de Personas
            personas = Personas()
            
            # Primero necesitamos encontrar al pediatra por su email
            usuarios = personas.db.child("usuarios").get().val()
            pediatra_uid = None
            
            # Buscar al pediatra que tiene este bebé vinculado
            for uid, datos in usuarios.items():
                if (datos.get("correo") == pediatra_email and 
                    datos.get("rol") == "pedia" and 
                    datos.get("bebesvinculados") and 
                    paciente_id in datos.get("bebesvinculados")):
                    pediatra_uid = uid
                    break
            
            if not pediatra_uid:
                return json.dumps({'success': False, 'message': 'No se encontró el pediatra con el paciente vinculado'})
            
            # Actualizar el estado del paciente en la ubicación correcta
            personas.db.child("usuarios").child(pediatra_uid).child("bebesvinculados").child(paciente_id).update({
                "estado": nuevo_estado
            })
            
            # Retornar respuesta exitosa
            web.header('Content-Type', 'application/json')
            return json.dumps({
                'success': True, 
                'message': f'Estado del paciente actualizado a "{nuevo_estado}" correctamente'
            })
            
        except Exception as e:
            # Manejar errores
            print(f"Error al actualizar estado del paciente: {str(e)}")
            web.header('Content-Type', 'application/json')
            return json.dumps({'success': False, 'message': str(e)})