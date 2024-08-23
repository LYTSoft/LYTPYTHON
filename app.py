# Incluir el Framework Flask
import os
from flask import Flask

# Importar la plantilla HTML. Para guardar datos desde el formulario importamos request, redirect y session (variable de sesión).
from flask import render_template, request, redirect, session, url_for, g, flash

# Importar el enlace a base de datos MySQL
from flaskext.mysql import MySQL

# Importar controlador del tiempo
from datetime import datetime

# Importar para obtener información de la imagen
from flask import send_from_directory

# 'mysql.connector' es un módulo que proporciona una interfaz para conectarse a una base de datos MySQL.
import mysql.connector

# 'secure_filename' se utiliza para asegurar que un nombre de archivo sea seguro para  usar en un sistema de archivos.
from werkzeug.utils import secure_filename

# 'wraps' se utiliza para preservar la identidad de la función original cuando se usa un decorador.
from functools import wraps



# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la aplicación
app.secret_key = 'lytpython'  # Clave secreta para sesiones

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'petvet'



# HECHO POR TIARA
# Función para obtener una conexión a la base de datos MySQL
def get_db_connection():
    # Devuelve una nueva conexión a la base de datos MySQL usando el conector de MySQL
    return mysql.connector.connect(
        host='localhost',  # Dirección del servidor de la base de datos (en este caso, se encuentra en el mismo equipo que la aplicación)
        user='root',  # Nombre de usuario para autenticarse en la base de datos
        password='',  # Contraseña asociada con el usuario de la base de datos (vacía en este ejemplo, pero debe ser segura en producción)
        database='petvet',  # Nombre de la base de datos a la que se desea conectar
        charset='utf8mb4'  # Codificación de caracteres que soporta un amplio rango de caracteres Unicode, incluyendo emojis
    )  

# HECHO POR TIARA
# Este código se ejecuta antes de cada solicitud
@app.before_request
def load_logged_in_user():
    # Obtiene el ID del usuario almacenado en la sesión
    user_id = session.get('id')
    
    # Verifica si el ID del usuario no está en la sesión
    if user_id is None:
        # Si no hay ID de usuario en la sesión, establece 'g.user' como None
        g.user = None
    else:
        # Si hay un ID de usuario, se conecta a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Ejecuta una consulta para obtener la información del usuario basado en el ID
        cursor.execute('SELECT * FROM usuario WHERE id_usuario = %s', (user_id,))
        
        # Obtiene el primer resultado de la consulta, que es un diccionario con la información del usuario
        g.user = cursor.fetchone()
        
        # Cierra la conexión con la base de datos
        connection.close()

# HECHO POR TIARA
# Función para obtener el tipo de mascota basado en el ID de la mascota
def get_mascota_tipo(id_mascota):
    # Establece una conexión con la base de datos
    connection = get_db_connection()
    
    # Crea un cursor para ejecutar consultas en la base de datos
    cursor = connection.cursor(dictionary=True)
    
    # Ejecuta una consulta SQL para obtener el tipo de mascota con el ID proporcionado
    cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [id_mascota])
    
    # Obtiene el primer resultado de la consulta como un diccionario
    mascota = cursor.fetchone()
    
    # Cierra la conexión con la base de datos
    connection.close()
    
    # Retorna el tipo de mascota si se encontró un resultado, de lo contrario retorna None
    return mascota['tipoMascota'] if mascota else None

# HECHO POR TIARA
def login_required(f):
    # Decorador que se utiliza para proteger vistas que requieren que el usuario esté autenticado

    @wraps(f)
    # El decorador @wraps ayuda a conservar la metadata original de la función f
    def decorated_function(*args, **kwargs):
        # Función interna que envuelve la función original para verificar la autenticación del usuario
        
        if 'loggedin' not in session:
            # Verifica si la clave 'loggedin' está en la sesión del usuario
            return redirect(url_for('login'))
            # Si 'loggedin' no está en la sesión, redirige al usuario a la página de inicio de sesión

        return f(*args, **kwargs)
        # Si 'loggedin' está en la sesión, ejecuta la función original con los argumentos proporcionados

    return decorated_function
    # Devuelve la función envuelta que realizará la verificación de autenticación


# HECHO POR TIARA
# Decorador para restringir el acceso a vistas solo para administradores
def admin_required(f):
    # 'wraps' se utiliza para preservar la información de la función original (nombre, docstring) cuando se usa un decorador
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si el usuario está autenticado y si es administrador
        if 'loggedin' not in session or not session.get('is_admin'):
            # Si no está autenticado o no es administrador, redirige a la página de inicio de sesión
            return redirect(url_for('login'))
        # Si el usuario está autenticado y es administrador, ejecuta la vista original
        return f(*args, **kwargs)
    
    # Retorna la función decorada
    return decorated_function


# HECHO POR TIARA
# Ruta para la página de inicio, redirige a la página de inicio de sesión
@app.route('/')
def Index():
    # Redirige a la vista de inicio de sesión cuando se accede a la página de inicio
    return redirect(url_for('login'))

# Ruta para la página de inicio de sesión, maneja tanto las solicitudes GET como POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtiene los datos del formulario de inicio de sesión enviados por POST
        nombre = request.form['nombre-sesion']
        password = request.form['pass-sesion']

        # Verifica si las credenciales corresponden a un administrador predefinido
        if nombre == 'Admin' and password == '12345':
            # Si el usuario es un administrador, establece las variables de sesión correspondientes
            session['loggedin'] = True
            session['is_admin'] = True
            session['user_id'] = 'admin'  # ID especial para el administrador
            # Redirige al administrador a la página principal del administrador
            return redirect(url_for('indexAdmin'))

        # Conecta a la base de datos para verificar las credenciales del usuario
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        # Ejecuta una consulta para verificar si el usuario existe con las credenciales proporcionadas
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))
        account = cursor.fetchone()
        connection.close()

        # Si se encuentra una cuenta con las credenciales correctas
        if account:
            # Actualiza la sesión con la información del usuario autenticado
            session.update({
                'loggedin': True,
                'is_admin': False,
                'user_id': account['id_usuario'],  # Usamos 'user_id' para referirse al usuario
                'id': account['id_usuario'],
                'nombre': account['nombre'],
                'apellido': account['apellido'],
                'telefono': account['telefono'],
                'correo': account['correo'],
                'id_mascota': account['id_mascota']
            })
            
            # Redirige al usuario a su página principal
            return redirect(url_for('indexUsuario'))

    # Renderiza el formulario de inicio de sesión si la solicitud es GET o las credenciales son incorrectas
    return render_template('usuario/login.html')

# Ruta para el registro de un nuevo usuario
@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    # Verifica si la solicitud es POST y si todos los campos requeridos están presentes
    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):
        # Obtiene los valores del formulario de registro
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        sexo = request.form['sexo']
        id_mascota = request.form['mascota']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        verificar_contraseña = request.form['verificar_contraseña']

        # Verifica si las contraseñas coinciden
        if contraseña != verificar_contraseña:
            # Si las contraseñas no coinciden, renderiza el formulario con un mensaje de error
            return render_template('usuario/u_registrousuario.html', error="Las contraseñas no coinciden")
        
        # Conecta a la base de datos para insertar el nuevo usuario
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verifica si ya existe una cuenta con el mismo correo electrónico
        cursor.execute('SELECT * FROM usuario WHERE correo = %s', (correo,))
        account = cursor.fetchone()
        
        if account:
            # Si el correo ya está registrado, cierra la conexión y renderiza el formulario con un mensaje de error
            connection.close()
            return render_template('usuario/u_registrousuario.html', error="El correo ya está registrado")
        else:
            # Si el correo no está registrado, inserta el nuevo usuario en la base de datos
            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            # Guarda los cambios y cierra la conexión con la base de datos
            connection.commit()
            connection.close()
            # Redirige al usuario a la página de inicio de sesión
            return redirect(url_for('login'))
    
    # Si la solicitud es GET o si el formulario no tiene todos los campos requeridos, renderiza el formulario
    return render_template('usuario/u_registrousuario.html')


# Ruta para agendar citas para el usuario, maneja tanto solicitudes GET como POST
# Ruta para agendar citas para el usuario, maneja tanto solicitudes GET como POST
@app.route('/agendarcitas/usuario/', methods=['GET', 'POST'])
@login_required
def agendar_cita():
    if request.method == 'POST':
        # Si la solicitud es POST (es decir, se envió un formulario), procesa los datos recibidos
        print("Datos recibidos:", request.form)
        
        # Verifica que todos los campos necesarios estén presentes en los datos del formulario
        if all(k in request.form for k in ['fecha', 'tanda', 'mascota', 'servicios', 'descripcion']):
            # Extrae los datos del formulario
            id_usuario = session['user_id']  # Obtiene el ID del usuario desde la sesión
            fecha = request.form['fecha']
            tanda = request.form['tanda']
            id_mascota = request.form['mascota']
            id_servicios = request.form['servicios']
            descripcion = request.form['descripcion']

            
            
            # Obtiene la conexión a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Consulta para verificar si ya existe una cita para el usuario en la misma fecha
            cursor.execute('SELECT * FROM citas WHERE fecha = %s AND id_usuario = %s', (fecha, id_usuario))
            existing_cita = cursor.fetchone()
            print("Citas encontradas:", existing_cita)
            
            if existing_cita:
                # Si ya existe una cita para esa fecha y usuario, muestra un mensaje y no inserta la nueva cita
                cursor.close()
                connection.close()
                return render_template('usuario/u_agendarCita.html', message='Ya tienes una cita agendada para esa fecha.')
            
            # Si no existe una cita para la misma fecha, inserta la nueva cita en la base de datos
            cursor.execute(''' INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion) VALUES (%s, %s, %s, %s, %s, %s)''', 
                           (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion))

            
             # Obtener el ID de la nueva cita
            id_citas = cursor.lastrowid
            
            if id_citas:
                cursor.execute('INSERT INTO admin (id_citas) VALUES (%s)', (id_citas,))
                # Insertar el ID de la cita en la tabla `admin`

             # Realiza la confirmación de la transacción.
            connection.commit()
            cursor.close()
            connection.close()
            # Redirige al usuario a la misma página para mostrar la nueva cita o para limpiar el formulario
            return redirect(url_for('agendar_cita'))

    # Si la solicitud es GET o si no se ha enviado un formulario, renderiza el formulario de agendar cita
    return render_template('usuario/u_agendarCita.html')


# Ruta para mostrar las citas agendadas del usuario
@app.route('/citas/agendadas/usuario/')
@login_required
def u_citasAgendada():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    id_usuario = session['user_id']

    cursor.execute('''
        SELECT c.fecha, c.tanda, m.tipoMascota, s.servicio, c.descripcion
        FROM citas c
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        WHERE c.id_usuario = %s
        ORDER BY c.fecha DESC
    ''', (id_usuario,))
    
    citas_agendadas = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('usuario/u_citasAgendadas.html', citas=citas_agendadas)


@app.route('/guarderia/usuario/', methods=['GET', 'POST'])
@login_required
def u_guarderia():
    # Esta vista maneja las solicitudes GET y POST para la ruta '/guarderia/usuario/'.
    # Requiere que el usuario esté autenticado (decorador @login_required).
    
    if request.method == 'POST':
        # Si la solicitud es de tipo POST (es decir, se envió un formulario),
        # se procesan los datos del formulario.

        print("Datos recibidos:", request.form)
        # Imprime los datos recibidos del formulario en la consola para depuración.

        # Lista de campos que deben estar presentes en el formulario.
        required_fields = ['id_usuario', 'desde', 'hasta', 'mascota', 'descripcion', 'id_servicios']
        
        # Verifica que todos los campos requeridos estén presentes en los datos del formulario.
        if all(k in request.form for k in required_fields):
            # Si todos los campos requeridos están presentes, extrae los valores.
            id_usuario = request.form['id_usuario']
            desde = request.form['desde']
            hasta = request.form['hasta']
            mascota = request.form['mascota']
            descripcion = request.form['descripcion']
            id_servicios = request.form['id_servicios']

            # Obtiene una conexión a la base de datos utilizando la función 'get_db_connection'.
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verifica si ya existe un registro con los mismos valores para evitar duplicados.
            cursor.execute('SELECT * FROM guarderia WHERE desde = %s AND hasta = %s AND id_usuario = %s AND id_servicios = %s',
                           (desde, hasta, id_usuario, id_servicios))
            existing_record = cursor.fetchone()

            if existing_record:
                # Si se encuentra un registro existente, cierra el cursor y la conexión
                # y devuelve una plantilla con un mensaje indicando que el registro ya existe.
                cursor.close()
                connection.close()
                return render_template('usuario/u_guarderia.html', message='El registro ya existe.')

            # Si no se encuentra un registro existente, inserta el nuevo registro en la base de datos.
            cursor.execute('INSERT INTO guarderia (id_usuario, id_servicios, desde, hasta, id_mascota, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, id_servicios, desde, hasta, mascota, descripcion))
            
             # Obtener el ID de la nueva cita
            id_guarderia = cursor.lastrowid
            
            if id_guarderia:
                # Insertar el ID de la cita en la tabla `admin`
                cursor.execute('INSERT INTO admin (id_guarderia) VALUES (%s)', (id_guarderia,))

             # Realiza la confirmación de la transacción.
            connection.commit()
            cursor.close()
            connection.close()

            # Redirige al usuario de vuelta a la misma página para limpiar el formulario o mostrar el estado actualizado.
            return redirect(url_for('u_guarderia'))

    # Si la solicitud es de tipo GET, o si se completa el procesamiento del formulario,
    # renderiza la plantilla 'usuario/u_guarderia.html' para mostrar el formulario.
    return render_template('usuario/u_guarderia.html')


# HECHO POR TIARA
# Ruta para mostrar las citas de guardería del usuario
@app.route('/guarderia/cita/usuario/')
@login_required
def u_guarderia_cita():
    # Conecta a la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtén el ID del usuario desde la sesión
    id_usuario = session['user_id']

    # Ejecuta la consulta SQL para obtener las citas de guardería del usuario
    cursor.execute('''
        SELECT c.desde, c.hasta, m.tipoMascota, s.servicio, c.descripcion
        FROM guarderia c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        WHERE c.id_usuario = %s
        ORDER BY c.desde DESC
    ''', (id_usuario,))

    # Obtiene todos los resultados de la consulta
    guarderia_citas = cursor.fetchall()

    # Cierra el cursor y la conexión a la base de datos
    cursor.close()
    connection.close()

    # Renderiza la plantilla con los datos de las citas de guardería
    return render_template('usuario/u_guarderiaCita.html', guarderia=guarderia_citas)


@app.route('/home/usuario/')
@login_required
def indexUsuario():
     return render_template('usuario/index.html')

@app.route('/adopcion/usuario/')
@login_required
def u_adopcion():
     return render_template('usuario/u_adopcion.html')

@app.route('/citasAdomicilio/', methods=['GET', 'POST'])
@login_required
def u_citasAdomicialio():
    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            # Obtener datos del formulario
            fecha = request.form.get('fecha')
            direccion = request.form.get('direccion')
            tanda = request.form.get('tanda')
            mascota = request.form.get('mascota')
            vacunas = request.form.getlist('vacunas[]')
            servicios = request.form.getlist('servicios[]')

            # Validar campos requeridos
            if not all([fecha, direccion, tanda, mascota, vacunas, servicios]):
                flash('Por favor, complete todos los campos requeridos y seleccione al menos una vacuna y un servicio.', 'error')
                return redirect(url_for('u_citasAdomicialio'))

            # Validar fecha
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                flash('Formato de fecha inválido.', 'error')
                return redirect(url_for('u_citasAdomicialio'))

            # Validar que mascota, vacuna y servicio sean números
            if not mascota.isdigit() or not all(v.isdigit() for v in vacunas) or not all(s.isdigit() for s in servicios):
                flash('ID de mascota, vacuna o servicio inválido.', 'error')
                return redirect(url_for('u_citasAdomicialio'))

            # Conectar a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()

            # Preparar datos para inserción
            vacunas_str = ','.join(vacunas)
            servicios_str = ','.join(servicios)

            # Insertar en la tabla adomicilio
            cursor.execute('''
                INSERT INTO adomicilio (id_usuario, fecha, direccion, tanda, id_mascota, id_vacuna, id_servicio) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (g.user['id_usuario'], fecha, direccion, tanda, int(mascota), vacunas_str, servicios_str))

            # Confirmar la transacción
            connection.commit()
            flash('Cita a domicilio registrada exitosamente.', 'success')
            return redirect(url_for('u_citasAdomicialio'))

        except mysql.connector.Error as err:
            if connection:
                connection.rollback()
            app.logger.error(f"Error de base de datos: {err}")
            flash('Ocurrió un error al procesar su solicitud. Por favor, inténtelo de nuevo.', 'error')
            return redirect(url_for('u_citasAdomicialio'))

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # Si es GET, simplemente renderizar la plantilla
    return render_template('usuario/u_servicioAdomicilio.html')



@app.route('/servicios/solicitados/usuario/')
@login_required
def u_servicio_solicitados():
     return render_template('usuario/u_Servicios-solicitud.html')

@app.route('/admin/')
@admin_required
def indexAdmin():
    return render_template('admin/index.html')


# Hecho por yohan adopcion
@app.route('/admin/adopcion/', methods=['GET', 'POST'])
@admin_required
def a_adopcion():
    if request.method == 'POST':
        # Manejo de formulario
        foto_mascota = request.form['foto_mascota']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        edad = request.form['edad']
        sexo = request.form['sexo']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo) VALUES (%s, %s, %s, %s, %s)',
                       (foto_mascota, nombre, descripcion, edad, sexo))
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('a_adopcion'))

    # GET Request: Muestra el formulario y la tabla con los datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id_adopcion, foto_mascota, nombre, descripcion, edad, sexo FROM adopcion')
    adopciones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin/a_adopcion.html', adopciones=adopciones)

@app.route('/admin/adopcion/eliminar/<int:id_adopcion>', methods=['POST'])
def eliminar_adopcion(id_adopcion):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Eliminar el registro por ID
    cursor.execute('DELETE FROM adopcion WHERE id_adopcion = %s', (id_adopcion,))
    connection.commit()
    connection.close()
    
    return redirect(url_for('a_adopcion'))  # Redirigir después de la eliminación


# HECHO POR TIARA
        
@app.route('/admin/citas/')
@admin_required
def a_servicios():
    # Este decorador asegura que solo los usuarios con privilegios de administrador puedan acceder a esta ruta.
    connection = get_db_connection()  # Establece una conexión con la base de datos usando una función que debe devolver un objeto de conexión de MySQL.
    cursor = connection.cursor(dictionary=True)  # Crea un objeto cursor para ejecutar consultas SQL. 'dictionary=True' hace que el cursor devuelva las filas como diccionarios.

    # Ejecuta una consulta SQL para seleccionar datos de varias tablas y unirlas para obtener información sobre las citas.
    cursor.execute('''
        SELECT c.id_citas, c.fecha, c.tanda, c.descripcion, u.nombre as usuario, m.tipoMascota as mascota, s.servicio
        FROM citas c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        ORDER BY c.fecha DESC
    ''')

    # Obtiene todas las filas del resultado de la consulta. El resultado será una lista de diccionarios (debido a dictionary=True).
    citas_pendientes = cursor.fetchall()
    cursor.close()  # Cierra el cursor para liberar los recursos de la base de datos.
    connection.close()  # Cierra la conexión a la base de datos para liberar los recursos.

    # Renderiza una plantilla HTML, pasando las citas pendientes como una variable al archivo 'admin/a_citas.html'.
    return render_template('admin/a_citas.html', citas=citas_pendientes)


@app.route('/admin/servicios/')
@admin_required
def a_servicio():
    return render_template('admin/a_sevicio.html')

@app.route('/admin/guarderia/')
@admin_required
def a_guarderia():
    # Este decorador asegura que solo los usuarios con privilegios de administrador puedan acceder a esta ruta.
    # Conecta a la base de datos usando una función que debe devolver un objeto de conexión de MySQL.
    connection = get_db_connection()
    # Crea un objeto cursor para ejecutar consultas SQL. 'dictionary=True' hace que el cursor devuelva las filas como diccionarios.
    cursor = connection.cursor(dictionary=True)

    # Ejecuta una consulta SQL para seleccionar datos de la tabla de guardería y unirlos con información de usuario, mascota y servicio.
    cursor.execute('''
        SELECT c.id_guarderia, c.desde, c.hasta,  m.tipoMascota as mascota, s.servicio, c.descripcion, u.nombre as usuario
        FROM guarderia c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        ORDER BY c.desde DESC
    ''')

    # Obtiene todas las filas del resultado de la consulta. El resultado será una lista de diccionarios (debido a dictionary=True).
    citas_guarderia = cursor.fetchall()

    # Cierra el cursor para liberar los recursos de la base de datos.
    cursor.close()
    # Cierra la conexión a la base de datos para liberar los recursos.
    connection.close()

    # Renderiza la plantilla HTML 'admin/a_AgendadasGuarderia.html', pasando los datos de las citas de guardería como una variable.
    return render_template('admin/a_AgendadasGuarderia.html', guarderia=citas_guarderia)

if __name__ == "__main__":
    app.run(port=3307, debug=True)