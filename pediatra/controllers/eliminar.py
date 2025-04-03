import web
from models.pediatras import Personas
render = web.template.render("views/", globals())

class EliminarPaciente:
    def GET(self, persona_id):
        """Muestra una página de confirmación antes de eliminar al paciente"""
        session = web.ctx.session
        if not session.get('usuario'):
            print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
            return web.seeother('/iniciosesion')
        
        usuario = session.get('usuario')
        if usuario.get('rol') != 'pedia':
            print("🚫 Acceso denegado. Solo los pediatras pueden eliminar pacientes.")
            return web.seeother('/')
        
        print("🌟 ID recibido para eliminar: ", persona_id)
        
        if not persona_id:
            return "⚠️ Error: No se recibió un ID válido."
        
        # Solo pasamos el ID a la plantilla
        return render.eliminar(bebe_id=persona_id)

    def POST(self, persona_id):
        """Procesa la eliminación del paciente"""
        session = web.ctx.session
        if not session.get('usuario'):
            print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
            return web.seeother('/iniciosesion')
        
        usuario = session.get('usuario')
        if usuario.get('rol') != 'pedia':
            print("🚫 Acceso denegado. Solo los pediatras pueden eliminar pacientes.")
            return web.seeother('/')
            
        correo_pediatra = usuario.get('correo')
        
        try:
            p = Personas()
            resultado = p.eliminar_paciente(persona_id, correo_pediatra)
            
            if resultado:
                print(f"✅ Paciente {persona_id} eliminado correctamente")
                # Usar return en lugar de raise para evitar el error 303
                return web.seeother('/listaspersonas?mensaje=Paciente eliminado con éxito')
            else:
                print(f"❌ Error al eliminar paciente {persona_id}")
                return web.seeother('/listaspersonas?mensaje=Error al eliminar paciente')
        except Exception as e:
            print(f"💥 Error en eliminar_paciente: {str(e)}")
            return web.seeother(f'/listaspersonas?mensaje=Error: {str(e)}')