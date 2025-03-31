import web
from models.pediatras import Personas
render = web.template.render("views/")

class ListaPersonas: 
    def GET(self):
        try:
            session = web.ctx.session  # Verificamos la sesión
            if not session.get('usuario'):
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')
            
            print(f"🔍 Sesión actual: {session.get('usuario')}")
            
            usuario = session.get('usuario')
            if usuario.get('rol') != 'pedia':
                print("🚫 Acceso denegado. Solo los pediatras pueden ver esta lista.")
                raise web.seeother('/')
            
            correo_pediatra = usuario.get('correo')
            p = Personas()
            pacientes = p.lista_pacientes(correo_pediatra)
            
            return render.lista_personas(pacientes)
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR: {str(error)}")
            return "Ocurrió un error, revisa la consola."