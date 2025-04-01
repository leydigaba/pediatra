import web
from models.pediatras import Personas
render = web.template.render("views/")

class ListaPersonas: 
    def GET(self):
        try:
            session = web.ctx.session  
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
            
            # Transformar los datos para que coincidan con la plantilla
            pacientes_formateados = []
            for p in pacientes:
                pacientes_formateados.append({
                   
                    'nombre': p['Nombre'],
                    'primer_apellido': p['Apellido(s)'].split()[0] if p['Apellido(s)'] and ' ' in p['Apellido(s)'] else p['Apellido(s)'],
                    'segundo_apellido': p['Apellido(s)'].split()[1] if p['Apellido(s)'] and ' ' in p['Apellido(s)'] else '',
                    'edad': p['Edad'],
                    'genero': p['Género'].lower(),
                    'estado': 'activo'  # Por defecto
                })
                
            return render.lista_personas(pacientes_formateados)
            
        except web.seeother as redireccion:
            raise redireccion
        except Exception as error:
            print(f"❌ ERROR en ListaPersonas.GET: {(error)}")
            return render.lista_personas([])