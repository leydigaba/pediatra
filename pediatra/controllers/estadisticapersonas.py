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
            
            #print(f"🔍 Sesión actual: {session.get('usuario')}")
 
            p = Personas()  
            correo_pediatra = session.get('usuario').get('correo')
            # Filtrar pacientes por el pediatra
            pacientes = p.lista_pacientes(correo_pediatra) 

            
            pacientes_formateados = []
            for p in pacientes:
                pacientes_formateados.append({
                    'id': p['ID'], 
                    'nombre': p['Nombre'],
                    'primer_apellido': p['Apellido(s)'].split()[0] if p['Apellido(s)'] and ' ' in p['Apellido(s)'] else p['Apellido(s)'],
                    'segundo_apellido': p['Apellido(s)'].split()[1] if p['Apellido(s)'] and ' ' in p['Apellido(s)'] else '',
                    'edad': p['Edad'],
                    'genero': p['Género'].lower(),
                    'estado': 'activo',  # Por defecto,
                    'oms': p['oms'] if 'oms' in p else '',  # Asegurarse de que la propiedad existe
                })
            print(f"👶 Pacientes encontrados: {pacientes_formateados}")
            pacientes_dict = {p['id']: p for p in pacientes_formateados}
            return render.estadisticapersonas(pacientes_dict)
            #print(f"👶 Pacientes encontrados: {pacientes_formateados}")
            #return render.estadisticapersonas(pacientes_formateados)
        except web.seeother as redireccion:
            raise redireccion  # Redirige correctamente sin capturar como error
        except Exception as error:
            print(f"❌ ERROR: {str(error)}")
            return "Ocurrió un error, revisa la consola."