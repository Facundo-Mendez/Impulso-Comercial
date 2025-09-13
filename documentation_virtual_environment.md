## 🚀 Uso de entornos virtuales en Python
Los entornos virtuales son una herramienta esencial en Python para gestionar dependencias y evitar conflictos entre proyectos. Nosotros para evitar conflixtos entre librerías e importaciones, 
vamos a usar .venv en vez de venvs, ya que es el estándar que reconoce VSCode y muchas herramientas. Pasos a seguir para desinstalar venvs y usar .venv:

**🔄 Paso 1: Detectar cuál entorno usas realmente(Terminal)**
- where python

Con el entorno activado (venv o .venv), eso te va a mostrar qué intérprete está usando.
Ejemplo:
- E:\Works\Pasantías AVIV\Impulso Comercial\venv\Scripts\python.exe

Ese es el entorno que Flask va a usar cuando hacés python run.py.

**🔄 Paso 2: unificar(Terminal)**
1. Salir de cualquier entorno activado:
- deactivate
2. Borrar el que no quieras (ejemplo, borrar venv):
- rmdir /s /q venv
3. Entrar al bueno (.venv):
- .\.venv\Scripts\activate
4. Instalar dependencias ahí:
- pip install -r requirements.txt
5. Probar que docx funciona:
- python -c "import docx; print(docx.__version__)"

**🔄 Paso 3: confirmación(Terminal)**
- python run.py

Y ya con eso qudaría bien configurado.