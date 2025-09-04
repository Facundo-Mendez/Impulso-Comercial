from app import create_app

app = create_app()

#DONDE SE INICIA LA APLICACION
if __name__=="__main__":
    app.run(port=5000, debug=True)