import mysql.connector  # Importa el conector de MySQL para interactuar con la base de datos
from flask import Flask, render_template, request, redirect, session, url_for  # Importa los módulos necesarios de Flask
from functools import wraps  # Importa wraps para preservar la metadata de las funciones decoradas

app = Flask(__name__)  # Crea una instancia de la aplicación Flask
app.secret_key = 'lytpython'  # Configura una clave secreta para la sesión de Flask
UPLOAD_FOLDER = 'static/uploads'  # Configura la carpeta para subir archivos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Asigna la carpeta de subida a la configuración de Flask
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limita el tamaño máximo de archivo subido a 16 MB

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # Dirección del servidor de base de datos
        user='root',  # Usuario de la base de datos
        password='',  # Contraseña del usuario de la base de datos
        database='petvet',  # Nombre de la base de datos
        charset='utf8mb4'  # Conjunto de caracteres para manejar caracteres especiales
    )

# Función para obtener el tipo de mascota basado en el ID de la mascota
def get_mascota_tipo(id_mascota):
    connection = get_db_connection()  # Establece una conexión con la base de datos
    cursor = connection.cursor(dictionary=True)  # Crea un cursor para ejecutar consultas SQL
    cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [id_mascota])  # Ejecuta una consulta SQL para seleccionar el tipo de mascota dado un ID de mascota
    mascota = cursor.fetchone()  # Recupera una fila de resultados de la consulta
    connection.close()  # Cierra la conexión con la base de datos
    return mascota['tipoMascota'] if mascota else None  # Devuelve el tipo de mascota si se encontró una fila, de lo contrario, devuelve None

# Decorador para verificar si el usuario está logueado
def login_required(f):
    @wraps(f)  # Preserva la información de la función original (nombre, docstring, etc.)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:  # Verifica si 'loggedin' está en la sesión, lo que indica que el usuario está logueado
            return redirect(url_for('login'))  # Si no está logueado, redirige a la página de login
        return f(*args, **kwargs)  # Si está logueado, ejecuta la función original
    return decorated_function

# Decorador para verificar si el usuario es un administrador
def admin_required(f):
    @wraps(f)  # Preserva la información de la función original (nombre, docstring, etc.)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session.get('is_admin'):  # Verifica si 'loggedin' está en la sesión y si el usuario tiene permisos de administrador
            return redirect(url_for('login'))  # Si no está logueado o no es administrador, redirige a la página de login
        return f(*args, **kwargs)  # Si está logueado y es administrador, ejecuta la función original
    return decorated_function


@app.route('/')
def Index():

    return redirect(url_for('login'))  # Redirige a la función 'login' usando la URL generada para la ruta '/login'

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Ruta para manejar el inicio de sesión de los usuarios. Soporta los métodos GET y POST.
    if request.method == 'POST':  # Verifica si el método de la solicitud es POST (cuando el formulario es enviado)
        nombre = request.form['nombre-sesion']  # Obtiene el valor del campo 'nombre-sesion' del formulario de inicio de sesión
        password = request.form['pass-sesion']  # Obtiene el valor del campo 'pass-sesion' del formulario de inicio de sesión

        # Verifica si el nombre de usuario y la contraseña son correctos para el usuario administrador
        if nombre == 'Admin' and password == '12345':
            session['loggedin'] = True  # Marca la sesión como iniciada
            session['is_admin'] = True  # Marca la sesión como perteneciente a un administrador
            return redirect(url_for('indexAdmin'))  # Redirige a la página principal del administrador

        # Si no es el administrador, se verifica el usuario en la base de datos
        connection = get_db_connection()  # Obtiene una conexión a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crea un cursor para ejecutar consultas SQL, configurado para devolver resultados en forma de diccionario
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))  # Ejecuta una consulta SQL para verificar el nombre de usuario y contraseña
        account = cursor.fetchone()  # Obtiene la primera fila del resultado de la consulta
        connection.close()  # Cierra la conexión con la base de datos

        # Si se encuentra una cuenta que coincide con el nombre de usuario y la contraseña proporcionados
        if account:
            # Actualiza la sesión con la información del usuario
            session.update({
                'loggedin': True,
                'is_admin': False,  # Marca al usuario como no administrador
                'id': account['id_usuario'],  # Almacena el ID del usuario en la sesión
                'nombre': account['nombre'],  # Almacena el nombre del usuario en la sesión
                'apellido': account['apellido'],  # Almacena el apellido del usuario en la sesión
                'telefono': account['telefono'],  # Almacena el teléfono del usuario en la sesión
                'correo': account['correo'],  # Almacena el correo del usuario en la sesión
                'id_mascota': account['id_mascota'],  # Almacena el ID de la mascota del usuario en la sesión
                'foto_perfil': account.get('foto_perfil', '')  # Almacena la foto de perfil del usuario si existe, de lo contrario, asigna una cadena vacía
            })
            return redirect(url_for('indexUsuario'))  # Redirige a la página principal del usuario
    return render_template('usuario/login.html')  # Renderiza la plantilla de login si el método no es POST

@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    # Ruta para manejar el registro de nuevos usuarios. Soporta los métodos GET y POST.

    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):  # Verifica que el método sea POST y que todos los campos necesarios estén presentes
        nombre = request.form['nombre']  # Obtiene el nombre del formulario
        apellido = request.form['apellido']  # Obtiene el apellido del formulario
        fecha_nacimiento = request.form['fecha_nacimiento']  # Obtiene la fecha de nacimiento del formulario
        telefono = request.form['telefono']  # Obtiene el teléfono del formulario
        sexo = request.form['sexo']  # Obtiene el sexo del formulario
        id_mascota = request.form['mascota']  # Obtiene el ID de la mascota del formulario
        correo = request.form['correo']  # Obtiene el correo del formulario
        contraseña = request.form['contraseña']  # Obtiene la contraseña del formulario
        verificar_contraseña = request.form['verificar_contraseña']  # Obtiene la contraseña de verificación del formulario

        # Verifica si las contraseñas coinciden
        if contraseña != verificar_contraseña:
            return render_template('usuario/u_registrousuario.html', error="Las contraseñas no coinciden")  # Renderiza la página de registro con un mensaje de error si las contraseñas no coinciden
        
        connection = get_db_connection()  # Obtiene una conexión a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crea un cursor para ejecutar consultas SQL, configurado para devolver resultados en forma de diccionario
        
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s', (nombre,))  # Verifica si el nombre ya está registrado en la base de datos
        account = cursor.fetchone()  # Obtiene la primera fila del resultado de la consulta
        
        # Si ya existe una cuenta con el mismo nombre
        if account:
            connection.close()  # Cierra la conexión con la base de datos
            return render_template('usuario/u_registrousuario.html', error="El correo ya está registrado")  # Renderiza la página de registro con un mensaje de error si el correo ya está registrado
        else:
            # Inserta la nueva cuenta de usuario en la base de datos
            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            connection.commit()  # Confirma la transacción en la base de datos
            connection.close()  # Cierra la conexión con la base de datos
            return redirect(url_for('login'))  # Redirige a la página de inicio de sesión
    
    return render_template('usuario/u_registrousuario.html')  # Renderiza la página de registro de usuario si el método no es POST o faltan campos en el formulario


# Ruta para mostrar las citas agendadas del usuario (requiere login)
@app.route('/citas/agendadas/usuario/')
@login_required
def u_citasAgendadas():
    return render_template('usuario/u_citasAgendadas.html')

# Ruta para mostrar el formulario de agendar cita (requiere login)
@app.route('/agendarcitas/usuario/')
@login_required
def u_agendarCitaPerfil():
     return render_template('usuario/u_agendarCita.html')

# Ruta para procesar la agenda de citas (GET y POST)
@app.route('/usuario/u_agendarCita', methods=['GET', 'POST'])
def agendar_cita():
    if request.method == 'POST':
        print("Datos recibidos:", request.form)
        
        # Verifica si todos los campos necesarios están en el formulario
        if all(k in request.form for k in ['id_usuario', 'fecha', 'tanda', 'mascota', 'servicios', 'descripcion']):
            # Extrae los datos del formulario
            id_usuario = request.form['id_usuario']
            fecha = request.form['fecha']
            tanda = request.form['tanda']
            id_mascota = request.form['mascota']
            id_servicios = request.form['servicios']
            descripcion = request.form['descripcion']

            # Conecta a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verifica si ya existe una cita en esa fecha
            cursor.execute('SELECT * FROM CITAS WHERE FECHA = %s', (fecha,))
            account = cursor.fetchone()

            if account:
                # Si ya existe, cierra la conexión y muestra un mensaje
                cursor.close()
                connection.close()
                return render_template('usuario/u_agendarCita.html', message='El registro ya existe.')

            # Si no existe, inserta la nueva cita
            cursor.execute('INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicio, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion))

            # Confirma la transacción y cierra la conexión
            connection.commit()
            cursor.close()
            connection.close()

            # Redirige a la misma página (probablemente debería mostrar un mensaje de éxito)
            return redirect(url_for('agendar_cita'))

    # Si es GET o si falla el POST, muestra el formulario de agendar cita
    return render_template('usuario/u_agendarCita.html')

# Rutas para diferentes páginas de usuario (todas requieren login)
@app.route('/home/usuario/')
@login_required
def indexUsuario():
     return render_template('usuario/index.html')

@app.route('/adopcion/usuario/')
@login_required
def u_adopcion():
     return render_template('usuario/u_adopcion.html')

@app.route('/guarderia/usuario/')
@login_required
def u_guarderia():
     return render_template('usuario/u_guarderia.html')

@app.route('/citasAgendadas/guarderia/usuario/')
@login_required
def u_citasAgendadasGuarderia():
    return render_template('usuario/u_citasAgendadasGuarderia.html')

@app.route('/guarderia/cita/usuario/')
@login_required
def u_guarderia_cita():
     return render_template('usuario/u_guarderiaCita.html')

@app.route('/servicios/solicitados/usuario/')
@login_required
def u_servicio_solicitados():
     return render_template('usuario/u_Servicios-solicitud.html')

# Rutas para el administrador (requieren ser admin)
@app.route('/admin/')
@admin_required
def indexAdmin():
    return render_template('admin/index.html')

# Ruta para la página de adopción del admin (GET y POST)
@app.route('/admin/adopcion/', methods=['GET', 'POST'])
@admin_required
def a_adopcion():
  if request.method == 'POST' and all(k in request.form for k in ['foto_mascota', 'nombre', 'descripcion', 'edad', 'sexo']):
        # Extrae los datos del formulario
        foto_mascota = request.form['foto_mascota']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        edad = request.form['edad']
        sexo = request.form['sexo']
        peso = request.form['peso']

        # Conecta a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verifica si ya existe una mascota con ese nombre
        cursor.execute('SELECT * FROM adopcion WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()
        if account:
            connection.close()
            return render_template('admin/a_adopcion.html', message='El registro ya existe.')
        else:
            # Si no existe, inserta el nuevo registro
            cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo, peso) VALUES (%s, %s, %s, %s, %s, %s)',
                           (foto_mascota, nombre, descripcion, edad, sexo, peso))
            connection.commit()
            connection.close()
            return redirect(url_for('a_adopcion'))

# Más rutas para el administrador
@app.route('/admin/citas/agendada/')
@admin_required
def a_agendada_citas():
    return render_template('admin/a_citas.html')

@app.route('/admin/servicios/')
@admin_required
def a_servicios():
    return render_template('admin/a_sevicio.html')

@app.route('/admin/agenda/citas/')
@admin_required
def a_agenda_citas():
    return render_template('admin/a_AgendadasGuarderia.html')

@app.route('/admin/despliegue/guarderia/')
@admin_required
def a_despliegueGuarderia():
    return render_template('admin/a_despliegue-Guarderia.html')

@app.route('/admin/despliegue/citas/')
@admin_required
def a_despliegueCitas():
     return render_template('admin/a_despliegue-Citas.html')

# Inicia la aplicación
if __name__ == "__main__":
    app.run(port=3307, debug=True)