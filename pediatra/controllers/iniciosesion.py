import web
from models.pediatras import iniciar_sesion 
render = web.template.render("views/")


class Iniciosesion:
    def GET(self):
        return render.iniciosesion(datos={})  

    def POST(self):
        try:
            datos = web.input()
            correo = datos.correo
            password = datos.password

            print(f"Intentando iniciar sesión con: {correo}")  

            usuario = iniciar_sesion(correo, password)

            print(f"Resultado de iniciar_sesion: {usuario}")  

            if usuario:
                session = web.ctx.session  # Acceder correctamente a la sesión
                session.usuario = usuario  # Guardar el usuario en sesión
                print("✅ Sesión iniciada correctamente.")
                return web.seeother("/listaspersonas")
            else:
                print("❌ Credenciales incorrectas")  
                return render.iniciosesion(datos={"error": "Correo o contraseña incorrectos."})

        except Exception as e:
            print(f"⚠️ Error en inicio de sesión: {str(e)}")  
            return render.iniciosesion(datos={"error": str(e)})