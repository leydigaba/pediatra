import web
from models.pediatras import Personas
render = web.template.render("views/")

class EstadisticaUsuario: 
    def GET(self):
        try:
            # Verificamos si la sesión está iniciada
            session = web.ctx.session  # Asegurarse de que la sesión está configurada
            if not session.get('usuario'):  # Si no hay usuario en sesión
                print("🚫 No hay usuario en sesión. Redirigiendo a /iniciosesion...")
                raise web.seeother('/iniciosesion')  # Redirige a la página de inicio de sesión
            
            print(f"🔍 Sesión actual: {session.get('usuario')}")
 
            p = Personas()  
            correo_pediatra = session.get('usuario').get('correo')
            # Filtrar pacientes por el pediatra
            pacientes = p.lista_pacientes(correo_pediatra) 

            # Procesamos los datos para asegurarnos de que tengan las propiedades necesarias
            for id, paciente in pacientes.items():
                paciente.setdefault('estado', 'pendiente')
                if 'edad' in paciente and isinstance(paciente['edad'], (int, float)):
                    paciente['edad'] = f"{paciente['edad']} años"
                paciente.setdefault('ultima_visita', 'Sin registro')

            return render.estadistica_personas(pacientes)
        except web.seeother as redireccion:
            raise redireccion  # Redirige correctamente sin capturar como error
        except Exception as error:
            print(f"❌ ERROR: {str(error)}")
            return "Ocurrió un error, revisa la consola."