# Incluir el Framework Flask
import os
from flask import Flask

# Importar la plantilla HTML. Para guardar datos desde el formulario importamos request, redirect y session (variable de sesión).
from flask import render_template, request, redirect, session, url_for, g

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
    return mysql.connector.connect(
        host='localhost',  # Dirección del servidor de la base de datos
        user='root',  # Usuario de la base de datos
        password='',  # Contraseña del usuario
        database='petvet',  # Nombre de la base de datos
        charset='utf8mb4'  # Codificación de caracteres
    )
    
    # HECHO POR TIARA

# Este código se ejecuta antes de cada solicitud
@app.before_request
def load_logged_in_user():
    # Obtiene el ID del usuario almacenado en la sesión
    user_id = session.get('id')
    
    # Verifica si el ID del usuario no está en la sesión
    if user_id is None:
        # Si no hay ID de usuario en la sesión, establece g.user como None
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


def login_required(f):# Decorador que se utiliza para proteger vistas que requieren que el 
    # usuario esté autenticado

    @wraps(f)# El decorador @wraps ayuda a conservar la metadata original de la función f
    
    def decorated_function(*args, **kwargs): # Verifica si la clave 'loggedin' está en la sesión del usuario

        if 'loggedin' not in session:
            return redirect(url_for('login')) # Si no está en la sesión, redirige al usuario a la 
        # página de inicio de sesión

        return f(*args, **kwargs)# Si 'loggedin' está en la sesión, ejecuta la función original 
        # con los argumentos proporcionados
    return decorated_function # Devuelve la función envuelta que realizará la verificación de autenticación

# HECHO POR TIARA


# Decorador para restringir el acceso a vistas solo para administradores
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si el usuario está autenticado y si es administrador
        if 'loggedin' not in session or not session.get('is_admin'):
            # Si no está autenticado o no es administrador, redirige a la página de inicio de sesión
            return redirect(url_for('login'))
        # Si el usuario está autenticado y es administrador, ejecuta la vista original
        return f(*args, **kwargs)
    return decorated_function


# HECHO POR TIARA
# Ruta para la página de inicio, redirige a la página de inicio de sesión
@app.route('/')
def Index():
    return redirect(url_for('login'))

# Ruta para la página de inicio de sesión, maneja tanto las solicitudes GET como POST
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtiene los datos del formulario de inicio de sesión
        nombre = request.form['nombre-sesion']
        password = request.form['pass-sesion']

        # Verifica si el nombre de usuario y la contraseña corresponden a un administrador predefinido
        if nombre == 'Admin' and password == '12345':
            # Si es un administrador, establece las variables de sesión correspondientes
            session['loggedin'] = True
            session['is_admin'] = True
            session['user_id'] = 'admin'  # Añadimos un ID de usuario para el admin
            # Redirige a la página principal del administrador
            return redirect(url_for('indexAdmin'))

        # Conecta a la base de datos para verificar las credenciales del usuario
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        # Ejecuta una consulta para encontrar un usuario con las credenciales proporcionadas
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))
        account = cursor.fetchone()
        connection.close()

        # Si se encuentra un usuario con las credenciales correctas
        if account:
            # Actualiza la sesión con la información del usuario
            session.update({
                'loggedin': True,
                'is_admin': False,
                'user_id': account['id_usuario'],  # Usamos 'user_id' para consistencia
                'id': account['id_usuario'],
                'nombre': account['nombre'],
                'apellido': account['apellido'],
                'telefono': account['telefono'],
                'correo': account['correo'],
                'id_mascota': account['id_mascota']
            })
            
            # Redirige a la página principal del usuario
            return redirect(url_for('indexUsuario'))

    # Renderiza la plantilla de inicio de sesión si la solicitud es GET o si las credenciales son incorrectas
    return render_template('usuario/login.html')


# HECHO POR TIARA
@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    # Verifica si la solicitud es de tipo POST y que todos los campos requeridos están presentes en el formulario
    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):
        # Obtiene los valores del formulario
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
        
        # Conecta a la base de datos
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
            # Si el correo no está registrado, inserta un nuevo usuario en la base de datos
            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            connection.commit()  # Guarda los cambios en la base de datos
            connection.close()  # Cierra la conexión con la base de datos
            # Redirige al usuario a la página de inicio de sesión
            return redirect(url_for('login'))
    
    # Si la solicitud es GET o si el formulario no tiene todos los campos requeridos, renderiza el formulario
    return render_template('usuario/u_registrousuario.html')




@app.route('/agendarcitas/usuario/', methods=['GET', 'POST'])
@login_required
def agendar_cita():
    if request.method == 'POST':
        # Código para manejar la solicitud POST
        print("Datos recibidos:", request.form)
        # Verifica que todos los campos necesarios estén presentes en el formulario.
        if all(k in request.form for k in ['fecha', 'tanda', 'mascota', 'servicios', 'descripcion']):
            # Extrae los datos del formulario.
            id_usuario = session['user_id']  # Obtén el ID del usuario de la sesión
            fecha = request.form['fecha']
            tanda = request.form['tanda']
            id_mascota = request.form['mascota']
            id_servicios = request.form['servicios']
            descripcion = request.form['descripcion']
            
            # Obtiene la conexión a la base de datos.
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Consulta para verificar si ya existe una cita para el usuario en la misma fecha.
            cursor.execute('SELECT * FROM citas WHERE fecha = %s AND id_usuario = %s', (fecha, id_usuario))
            account = cursor.fetchone()
            print("Citas encontradas:", account)
            
            if account:
                # Si ya existe una cita para la fecha y usuario, muestra un mensaje.
                cursor.close()
                connection.close()
                return render_template('usuario/u_agendarCita.html', message='Ya tienes una cita agendada para esa fecha.')
            
            # Si no existe una cita, inserta la nueva cita en la base de datos.
            cursor.execute('INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion))
            
            # Confirma los cambios en la base de datos.
            connection.commit()
            cursor.close()
            connection.close()
            
            # Redirige al usuario a la página de perfil de citas agendadas.
        return redirect(url_for('agendar_cita'))

    
    # Renderiza el formulario de agendar cita si la solicitud es GET o si no se ha enviado una cita.
    return render_template('usuario/u_agendarCita.html')


# HECHO POR TIARA
@app.route('/citas/agendadas/usuario/')
@login_required
def u_citasAgendada():
    # Conecta a la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtén el ID del usuario desde la sesión
    id_usuario = session['user_id']

    # Ejecuta la consulta SQL para obtener las citas agendadas del usuario
    cursor.execute('''
        SELECT c.fecha, c.tanda, m.tipoMascota, s.servicio, c.descripcion
        FROM citas c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON u.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        WHERE c.id_usuario = %s
        ORDER BY c.fecha DESC
    ''', (id_usuario,))
    
    # Obtiene todos los resultados de la consulta
    citas_agendadas = cursor.fetchall()

    # Cierra el cursor y la conexión
    cursor.close()
    connection.close()

    # Renderiza la plantilla con los datos de las citas agendadas
    return render_template('usuario/u_citasAgendadas.html', citas=citas_agendadas)


@app.route('/guarderia/usuario/', methods=['GET', 'POST'])
@login_required
def u_guarderia():
    if request.method == 'POST':
        print("Datos recibidos:", request.form)
        
        required_fields = ['id_usuario', 'desde', 'hasta', 'mascota', 'descripcion', 'id_servicios']
        if all(k in request.form for k in required_fields):
            id_usuario = request.form['id_usuario']
            desde = request.form['desde']
            hasta = request.form['hasta']
            mascota = request.form['mascota']
            descripcion = request.form['descripcion']
            id_servicios = request.form['id_servicios']

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM guarderia WHERE desde = %s AND hasta = %s AND id_usuario = %s AND id_servicios = %s',
            (desde, hasta, id_usuario, id_servicios))
            existing_record = cursor.fetchone()

            if existing_record:
                cursor.close()
                connection.close()
                return render_template('usuario/u_guarderia.html', message='El registro ya existe.')

            cursor.execute('INSERT INTO guarderia (id_usuario, id_servicios, desde, hasta, id_mascota, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, id_servicios, desde, hasta, mascota, descripcion))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('u_guarderia'))

    return render_template('usuario/u_guarderia.html')

# HECHO POR TIARA
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

    # Cierra el cursor y la conexión
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
        print("Datos recibidos:", request.form)

        required_fields = ['id_adomicilio', 'id_usuario', 'fecha', 'direccion', 'tanda', 'mascota']

        if all(k in request.form for k in required_fields):
            id_adomicilio = request.form.get('id_adomicilio')
            id_usuario = request.form.get('id_usuario')
            fecha = request.form.get('fecha')
            direccion = request.form.get('direccion')
            tanda = request.form.get('tanda')
            mascota = request.form.get('mascota')
            vacunas = request.form.getlist('vacunas[]')
            servicios = request.form.getlist('servicios[]')

            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute('SELECT * FROM domicilio WHERE id_adomicilio = %s AND id_usuario = %s AND fecha = %s AND direccion = %s AND tanda = %s AND id_mascota = %s',
                               (id_adomicilio, id_usuario, fecha, direccion, tanda, mascota))
                existing_record = cursor.fetchone()

                if existing_record:
                    return render_template('usuario/u_servicioAdomicilio.html', message='El registro ya existe.')

                for vacuna in vacunas:
                    for servicio in servicios:
                        cursor.execute('INSERT INTO domicilio (id_adomicilio, id_usuario, fecha, direccion, tanda, id_mascota, id_vacuna, id_servicio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                       (id_adomicilio, id_usuario, fecha, direccion, tanda, mascota, vacuna, servicio))

                connection.commit()

            except Exception as e:
                print("Error:", e)
                connection.rollback()
            
            finally:
                cursor.close()
                connection.close()

            return redirect(url_for('u_servicioAdomicilio'))

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
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Consulta para obtener todas las citas pendientes
    cursor.execute('''
        SELECT c.id_citas, c.fecha, c.tanda, c.descripcion, u.nombre as usuario, m.tipoMascota as mascota, s.servicio
        FROM citas c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        ORDER BY c.fecha DESC
    ''')
    
    citas_pendientes = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('admin/a_citas.html', citas=citas_pendientes)

@app.route('/admin/servicios/')
@admin_required
def a_servicio():
    return render_template('admin/a_sevicio.html')

@app.route('/admin/guarderia/')
@admin_required
def a_guarderia():
    # Conecta a la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Ejecuta la consulta SQL para obtener todas las citas de guardería
    cursor.execute('''
        SELECT c.id_guarderia, c.desde, c.hasta,  m.tipoMascota as mascota, s.servicio, c.descripcion, u.nombre as usuario
        FROM guarderia c
        JOIN usuario u ON c.id_usuario = u.id_usuario
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        ORDER BY c.desde DESC
    ''')

    # Obtiene todos los resultados de la consulta
    citas_guarderia = cursor.fetchall()

    # Cierra el cursor y la conexión
    cursor.close()
    connection.close()

    # Renderiza la plantilla con los datos de las citas de guardería
    return render_template('admin/a_AgendadasGuarderia.html', guarderia=citas_guarderia)

if __name__ == "__main__":
    app.run(port=3307, debug=True)