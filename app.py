# Incluir el Framework Flask
import os
from flask import Flask

# Importar la plantilla HTML. Para guardar datos desde el formulario importamos request, redirect y session (variable de sesión).
from flask import render_template, request, redirect, session, url_for

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



# Crear la aplicación Flask
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img/' 
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

@app.route('/cerrar-sesion', methods=['GET'])
def cerrar_sesion():
    session.clear()  # Borra todos los datos de la sesión
    return redirect(url_for('login'))  # Redirige a la página de inicio de sesión


# informacion del perfil mostrada en la pantalla 
@app.route('/citasAdomicilio/', methods=['GET', 'POST'])
def citaAdomicilio():
    # Verificar si el usuario está logueado
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener información del usuario
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono, id_mascota FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()

    return render_template('usuario/u_servicioAdomicilio.html', user=user)




# Ruta para agendar citas para el usuario, maneja tanto solicitudes GET como POST
@app.route('/agendarcitas/usuario/', methods=['GET', 'POST'])
def agendar_cita():
    # Verificar si el usuario está logueado
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener la información del usuario desde la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if request.method == 'POST':
        # Verificar que todos los campos requeridos están presentes
        if all(k in request.form for k in ['id_usuario', 'fecha', 'tanda', 'mascota', 'servicios', 'descripcion']):
            id_usuario = request.form['id_usuario']
            fecha = request.form['fecha']
            tanda = request.form['tanda']
            id_mascota = request.form['mascota']
            id_servicios = request.form['servicios']
            descripcion = request.form['descripcion']
            
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Verificar si ya existe una cita para esa fecha y usuario
            cursor.execute('SELECT * FROM citas WHERE fecha = %s AND id_usuario = %s', (fecha, user_id))
            existing_cita = cursor.fetchone()
            
            if existing_cita:
                cursor.close()
                connection.close()
                return render_template('usuario/u_agendarCita.html', user=user, message='Ya tienes una cita agendada para esa fecha.')

            # Insertar nueva cita
            cursor.execute('INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion) VALUES (%s, %s, %s, %s, %s, %s)', 
                           (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion))
            id_citas = cursor.lastrowid
            
            if id_citas:
                cursor.execute('INSERT INTO admin (id_citas) VALUES (%s)', (id_citas,))
            
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('agendar_cita'))

    return render_template('usuario/u_agendarCita.html', user=user)




@app.route('/citas/agendadas/usuario/')
def u_citasAgendada():
    # Verifica si el usuario está logueado. Si no está logueado, redirige a la página de login.
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Obtiene el ID del usuario desde la sesión.
    user_id = session.get('user_id')
    
    # Si no se encuentra el ID del usuario en la sesión, redirige a la página de login.
    if not user_id:
        return redirect(url_for('login'))
    
    # Establece una conexión a la base de datos y crea un cursor para ejecutar consultas SQL.
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Ejecuta una consulta SQL para obtener información del usuario (nombre, apellido, correo, teléfono, ID de mascota) basado en el ID del usuario.
    cursor.execute('SELECT nombre, apellido, correo, telefono, id_mascota FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    
    # Si no se encuentra el usuario en la base de datos, cierra el cursor y la conexión, y devuelve un error 404.
    if not user:
        cursor.close()
        connection.close()
        return "Usuario no encontrado", 404
    
    # Ejecuta una consulta SQL para obtener las citas agendadas del usuario, uniendo las tablas 'citas', 'mascota' y 'servicio' para obtener detalles completos.
    # Ordena los resultados por fecha en orden descendente.
    cursor.execute('''
        SELECT id_citas, c.fecha, c.tanda, m.tipoMascota, s.servicio, c.descripcion
        FROM citas c
        JOIN mascota m ON c.id_mascota = m.id_mascota
        JOIN servicio s ON c.id_servicios = s.id_servicios
        WHERE c.id_usuario = %s
        ORDER BY c.fecha DESC
    ''', (user_id,))
    
    # Obtiene todos los resultados de la consulta.
    citas_agendadas = cursor.fetchall()

    # Cierra el cursor y la conexión a la base de datos.
    cursor.close()
    connection.close()

    # Renderiza la plantilla 'u_citasAgendadas.html' con los datos del usuario y las citas agendadas.
    return render_template('usuario/u_citasAgendadas.html', user=user, citas=citas_agendadas)

@app.route('/eliminar_cita/<int:id_cita>/', methods=['POST'])
def eliminar_cita(id_cita):
    # Verifica si el usuario está logueado. Si no está logueado, redirige a la página de login.
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Obtiene el ID del usuario desde la sesión.
    user_id = session.get('user_id')
    
    # Si no se encuentra el ID del usuario en la sesión, redirige a la página de login.
    if not user_id:
        return redirect(url_for('login'))
    
    # Establece una conexión a la base de datos y crea un cursor para ejecutar consultas SQL.
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Verifica si la conexión y el cursor están disponibles antes de proceder.
    if connection and cursor:
        # Ejecuta la consulta SQL para eliminar la cita de la base de datos basada en el ID de la cita y el ID del usuario.
        cursor.execute('DELETE FROM citas WHERE id_citas = %s AND id_usuario = %s', (id_cita, user_id))
        
        # Verifica si se realizó alguna modificación en la base de datos.
        if cursor.rowcount > 0:
            # Confirma los cambios en la base de datos.
            connection.commit()
       
        
        # Cierra el cursor y la conexión a la base de datos.
        cursor.close()
        connection.close()
    
        # Redirige a la página de citas agendadas después de eliminar la cita.
        return redirect(url_for('u_citasAgendada'))
     



@app.route('/guarderia/usuario/', methods=['GET', 'POST'])
def u_guarderia():
    # Verificar si el usuario está logueado 
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener información del usuario
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono, id_mascota FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        connection.close()
        return render_template('usuario/u_guarderia.html', message='Usuario no encontrado.')

    if request.method == 'POST':
        required_fields = ['id_usuario', 'desde', 'hasta', 'mascota', 'descripcion', 'id_servicios']
        
        if all(k in request.form for k in required_fields):
            id_usuario = request.form['id_usuario']
            desde = request.form['desde']
            hasta = request.form['hasta']
            mascota = request.form['mascota']
            descripcion = request.form['descripcion']
            id_servicios = request.form['id_servicios']

            # Verificar si el id_usuario existe
            cursor.execute('SELECT id_usuario FROM usuario WHERE id_usuario = %s', (id_usuario,))
            existing_user = cursor.fetchone()

            if not existing_user:
                cursor.close()
                connection.close()
                return render_template('usuario/u_guarderia.html', user=user, message='El usuario no existe.')

            cursor.execute('SELECT * FROM guarderia WHERE desde = %s AND hasta = %s AND id_usuario = %s AND id_servicios = %s',
                           (desde, hasta, id_usuario, id_servicios))
            existing_record = cursor.fetchone()

            if existing_record:
                cursor.close()
                connection.close()
                return render_template('usuario/u_guarderia.html', user=user, message='El registro ya existe.')

            cursor.execute('INSERT INTO guarderia (id_usuario, id_servicios, desde, hasta, id_mascota, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, id_servicios, desde, hasta, mascota, descripcion))
            id_guarderia = cursor.lastrowid
            
            if id_guarderia:
                cursor.execute('INSERT INTO admin (id_guarderia) VALUES (%s)', (id_guarderia,))

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('u_guarderia'))

    return render_template('usuario/u_guarderia.html', user=user)








@app.route('/guarderia/cita/usuario/')
def u_guarderia_cita():
    # Verifica si el usuario está logueado. Si no está logueado, redirige a la página de login.
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Obtiene el ID del usuario desde la sesión.
    user_id = session.get('user_id')
    
    # Si no se encuentra el ID del usuario en la sesión, redirige a la página de login.
    if not user_id:
        return redirect(url_for('login'))
    
    # Establece una conexión a la base de datos y crea un cursor para ejecutar consultas SQL.
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Ejecuta una consulta SQL para obtener información del usuario (nombre, apellido, correo, teléfono, ID de mascota) basado en el ID del usuario.
    cursor.execute('SELECT nombre, apellido, correo, telefono, id_mascota FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    
    # Si no se encuentra el usuario en la base de datos, cierra el cursor y la conexión, y devuelve un error 404.
    if not user:
        cursor.close()
        connection.close()
        return "Usuario no encontrado", 404
    
    # Ejecuta una consulta SQL para obtener las citas agendadas del usuario, uniendo las tablas 'citas', 'mascota' y 'servicio' para obtener detalles completos.
    # Ordena los resultados por fecha en orden descendente.
    cursor.execute('''
        SELECT c.desde, c.hasta, m.tipoMascota, s.servicio, c.descripcion
         FROM guarderia c
         JOIN usuario u ON c.id_usuario = u.id_usuario
         JOIN mascota m ON c.id_mascota = m.id_mascota
         JOIN servicio s ON c.id_servicios = s.id_servicios
         WHERE c.id_usuario = %s
         ORDER BY c.desde DESC
    ''', (user_id,))
    
    # Obtiene todos los resultados de la consulta.
    guarderia_agendadas = cursor.fetchall()

    # Cierra el cursor y la conexión a la base de datos.
    cursor.close()
    connection.close()

    # Renderiza la plantilla 'u_citasAgendadas.html' con los datos del usuario y las citas agendadas.
    return render_template('usuario/u_guarderiaCita.html', user=user, guarderia=guarderia_agendadas)



#Funcion que muestra la informacion del usuario en el perfil
@app.route('/home/usuario/')
def indexUsuario():
   # Verificar si el usuario está logueado
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener la información del usuario desde la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()


        # Asegúrate de pasar `user` a la plantilla
    return render_template('usuario/index.html', user=user)
  


@app.route('/servicios/solicitados/usuario/')
def u_servicio_solicitados():
  # Verificar si el usuario está logueado
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener la información del usuario desde la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('usuario/u_Servicios-solicitud.html', user=user)

@app.route('/admin/')
def indexAdmin():
    return render_template('admin/index.html')



@app.route('/admin/adopcion/', methods=['GET', 'POST'])
def a_adopcion():
    if request.method == 'POST':
        # Manejo de formulario
        foto_mascota = request.files['foto_mascota']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        edad = request.form['edad']
        sexo = request.form['sexo']

        # Guardar la imagen
        # Verificar si se ha subido una foto de mascota y si el nombre del archivo no está vacío
        if foto_mascota and foto_mascota.filename != "":
            # Obtener la hora actual en formato 'AÑO-MES-DÍA-HORA-MINUTO-SEGUNDO'
            horaActual = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Generar un nuevo nombre para el archivo que incluye la hora actual y el nombre original del archivo
            nuevoNombre = f"{horaActual}_{foto_mascota.filename}"
            
            # Construir la ruta completa del archivo en el directorio de carga usando el nuevo nombre
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], nuevoNombre)
            
            # Guardar el archivo subido en el directorio especificado con el nuevo nombre
            foto_mascota.save(archivo_path)
            
            # Generar la URL para acceder al archivo guardado, usando la ruta de los archivos estáticos
            foto_mascota_url = url_for('static', filename=f'img/{nuevoNombre}')
        else:
            # Si no se ha subido una foto o el nombre del archivo está vacío, establecer la URL como None
            foto_mascota_url = None
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo) VALUES (%s, %s, %s, %s, %s)',
            (foto_mascota_url, nombre, descripcion, edad, sexo)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect(url_for('a_adopcion'))

#    Muestra el formulario y la tabla con los datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id_adopcion, foto_mascota, nombre, descripcion, edad, sexo FROM adopcion')
    adopciones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin/a_adopcion.html', adopciones=adopciones)




# Funcion que muestra las mascotas en adopcion en el usuario 
@app.route('/adopcion/usuario/')
def u_adopcion():
   # Verificar si el usuario está logueado
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Obtener la información del usuario desde la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT nombre, apellido, correo, telefono FROM usuario WHERE id_usuario = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
 

# Muestra las adopcion 
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT foto_mascota, nombre, descripcion, edad, sexo FROM adopcion')
    useradopciones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('usuario/u_adopcion.html', useradopciones=useradopciones, user=user)



# Permite eliminar las adopciones de la mascota al admin y asi no aparzcan al usuario 
@app.route('/admin/adopcion/eliminar/<int:id_adopcion>', methods=['POST'])
def eliminar_adopcion(id_adopcion):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Eliminar el registro por ID
    cursor.execute('DELETE FROM adopcion WHERE id_adopcion = %s', (id_adopcion,))
    connection.commit()
    connection.close()
    
    return redirect(url_for('a_adopcion'))  # Redirigir después de la eliminación


# Muestra la citas que tiene pendiente el admin.

@app.route('/admin/citas/')# Este decorador asegura que solo los usuarios con privilegios de administrador puedan acceder a esta ruta
def a_servicios():

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



# Muestra las citas de guarderia  que tiene pendiente el admin.


@app.route('/admin/guarderia/')
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