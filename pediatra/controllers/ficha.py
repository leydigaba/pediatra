import web
from models.pediatras import Personas

render = web.template.render("views/", globals())

class DetallePersonas:
    def GET(self, persona_id):  
        #web.debug(f"🌟 ID recibido en la URL: {persona_id}")  # <-- Verificamos si el ID llega bien
        
        if not persona_id:
            return "⚠️ Error: No se recibió un ID válido."

        try:
            p = Personas()
            datos_persona = p.lista_pacientes_por_id_y_pediatra(paciente_id=persona_id)
            #web.debug(f"🔍 Datos obtenidos: {datos_persona}")  # Para verificar estructura

            # Extraemos el paciente del diccionario
            paciente = datos_persona.get(persona_id, None)
            #web.debug(f"✅ Paciente seleccionado: {paciente}")  # Para verificar

            if paciente:
                return render.ficha(paciente=paciente)
            else:
                return "❌ Persona no encontrada."

        except Exception as e:
            #web.debug(f"💥 Error en DetallePersonas: {str(e)}")  # <-- Esto muestra cualquier error
            return f"⚠️ Error interno del servidor: {str(e)}"