import re
import web
from models.pediatras import registrar_usuario

render = web.template.render("views/")

class Registro:
    def GET(self):
        return render.registro()  
    
    def POST(self):
        try:
            datos = web.input()
            
            # Validaciones
            if not self.validar_nombre(datos.nombre) or not self.validar_nombre(datos.apellido1) or not self.validar_nombre(datos.apellido2):
                return "Error: El nombre y apellidos solo pueden contener letras y espacios."
            
            if not self.validar_correo(datos.correo):
                return "Error: Formato de correo inválido."
            
            if not self.validar_fecha(datos.fecha_nacimiento):
                return "Error: La fecha de nacimiento debe ser en formato YYYY-MM-DD."
            
            if not self.validar_licencia(datos.licencia) and datos.rol == "pedia":
                return "Error: La licencia debe ser un número válido para pediatras."
            
            if not self.validar_password(datos.password):
                return "Error: La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números."
            
            if datos.password != datos.password_confirm:
                return "Error: Las contraseñas no coinciden."
            
            # Llamamos a la función de registrar usuario con el campo de rol
            resultado = registrar_usuario(
                datos.nombre.strip(),
                datos.apellido1.strip(),
                datos.apellido2.strip(),
                datos.fecha_nacimiento.strip(),
                datos.correo.strip(),
                datos.licencia.strip(),
                datos.password.strip(),
                datos.rol.strip()  # El rol puede ser 'padre', 'admin' o 'pedia'
            )
            
            if resultado:
                raise web.seeother('/iniciosesion')  
            else:
                return "Error: No se pudo registrar el usuario. Es posible que el correo ya esté en uso."
                
        except Exception as e:
            return f"Error inesperado: {str(e)}"
    
    def validar_nombre(self, texto):
        """Permite solo letras y espacios en nombres y apellidos"""
        return bool(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", texto))
    
    def validar_correo(self, correo):
        """Verifica que el correo tenga un formato válido"""
        return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo))
    
    def validar_fecha(self, fecha):
        """Verifica que la fecha esté en formato YYYY-MM-DD"""
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", fecha))
    
    def validar_licencia(self, licencia):
        """La licencia debe ser un número válido"""
        return licencia.isdigit()
    
    def validar_password(self, password):
        """Verifica que la contraseña tenga al menos 8 caracteres, una mayúscula, una minúscula y un número"""
        return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$", password))
