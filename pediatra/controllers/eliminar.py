import web
from models.pediatras import Personas

render = web.template.render("views/")
personas = Personas()

class EliminarPaciente:
    def GET(self, bebe_id):
        """Muestra una página de confirmación antes de eliminar al paciente"""
        return render.eliminar(bebe_id)

    def POST(self, bebe_id):
        pediatra_id = "id_del_pediatra_actual"
        
        resultado = personas.eliminar_paciente(bebe_id, pediatra_id)
        
        if resultado:
            raise web.seeother('/listaspersonas?mensaje=Paciente eliminado con éxito')
        else:
            raise web.seeother('/listaspersonas?mensaje=Error al eliminar paciente')