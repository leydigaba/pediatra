import web

class Logout:
    def GET(self):
        session = web.ctx.session  # Accede a la sesión
        session.kill()  # Elimina todos los datos de la sesión
        raise web.seeother('/iniciosesion')  # Redirige al inicio de sesión