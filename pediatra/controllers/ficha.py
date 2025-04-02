import web
from models.pediatras import Personas

render = web.template.render("views/", globals())

class DetallePersonas:
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
        print("🌟 ID recibido en la URL: ", persona_id)  # <-- Verificamos si el ID llega bien
        print(f"🔍 Correo pediatra: {correo_pediatra}")
        if not persona_id:
            return "⚠️ Error: No se recibió un ID válido."

        try:
            p = Personas()
            datos_persona = p.obtener_bebe_por_id(persona_id, correo_pediatra)
            #web.debug(f"🔍 Datos obtenidos: {datos_persona}")  # Para verificar estructura
            print("🔍 Datos obtenidos: ", datos_persona)  # Para verificar estructura
            paciente = datos_persona.get(persona_id, None)
           
            print(f"✅ Paciente seleccionado: {paciente}")  # Para verificar
            
            if paciente:
                return render.ficha(paciente=paciente)
            else:
                return "❌ Persona no encontrada."

        except Exception as e:
            #web.debug(f"💥 Error en DetallePersonas: {str(e)}")  # <-- Esto muestra cualquier error
            return f"⚠️ Error interno del servidor: {str(e)}"