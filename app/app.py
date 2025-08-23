from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # <- usar 'pages/' porque está dentro de templates

@app.route('/sobrenosotros')
def sobrenosotros():
    return render_template('pages/sobrenosotros.html')

@app.route('/contacto')
def contacto():
    return render_template('pages/contacto.html')

@app.route('/postulantes')
def postulantes():
    return render_template('pages/postulantes.html')

@app.route('/login')
def login():
    return render_template('pages/login.html')

@app.route('/admin',methods=['POST'] )
def admin():
    
    return render_template('pages/inicio_admin.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return {'success': True}, 200

if __name__=="__main__":
    app.run(port=5000)
