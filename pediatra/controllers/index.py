import web
render = web.template.render("views/")  

class Index:
    def GET(self):
        try:
            return render.index() 
        except Exception as error:
            message = {
                "Error": str(error)
            }
            print(f"ERROR: {message}")  
            return str(message)  