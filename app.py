import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, g
from werkzeug.utils import secure_filename
import os
from functools import wraps

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la aplicación
app.secret_key = 'lytpython'  # Clave secreta para sesiones

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'petvet'


# Función para obtener una conexión a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # Dirección del servidor de la base de datos
        user='root',  # Usuario de la base de datos
        password='',  # Contraseña del usuario
        database='petvet',  # Nombre de la base de datos
        charset='utf8mb4'  # Codificación de caracteres
    )
    
    
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

@app.route('/usuario/u_agendarCita', methods=['GET', 'POST'])
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
            return redirect(url_for('u_citasAgendada'))
    
    # Renderiza el formulario de agendar cita si la solicitud es GET o si no se ha enviado una cita.
    return render_template('usuario/u_agendarCita.html')



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
     # Esta ruta maneja tanto solicitudes GET como POST.
    # Solo los usuarios autenticados pueden acceder a esta ruta.
    
    if request.method == 'POST':
        print("Datos recibidos:", request.form)  # Imprime los datos del formulario para depuración
        
        # Verifica si todos los campos requeridos están presentes en el formulario
        if all(k in request.form for k in ['id_usuario', 'telefono', 'desde', 'hasta', 'mascota', 'descripcion']):
            # Obtiene los valores del formulario
            id_usuario = request.form['id_usuario']
            telefono = request.form['telefono']
            desde = request.form['desde']
            hasta = request.form['hasta']
            mascota = request.form['mascota']
            descripcion = request.form['descripcion']
            id_servicio = request.form['id_servicio']

            # Conecta a la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()

            # Verifica si ya existe un registro con los mismos datos
            cursor.execute('SELECT * FROM guarderia WHERE telefono = %s AND desde = %s AND hasta = %s AND id_usuario = %s AND id_servicio = %s', 
                           (telefono, desde, hasta, id_usuario, id_servicio))
            existing_record = cursor.fetchone()

            if existing_record:
                # Si el registro ya existe, cierra el cursor y la conexión, y renderiza la plantilla con un mensaje
                cursor.close()
                connection.close()
                return render_template('usuario/u_guarderia.html', message='El registro ya existe.')

            # Si el registro no existe, inserta el nuevo registro en la base de datos
            cursor.execute('INSERT INTO guarderia (id_usuario, id_servicio, telefono, desde, hasta, id_mascota, descripcion) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                           (id_usuario, id_servicio, telefono, desde, hasta, mascota, descripcion))

            # Guarda los cambios en la base de datos
            connection.commit()
            # Cierra el cursor y la conexión con la base de datos
            cursor.close()
            connection.close()

            # Redirige al usuario a la página de guardería
            return redirect(url_for('u_guarderia'))

    # Si la solicitud es GET, renderiza la plantilla del formulario de guardería
    return render_template('usuario/u_guarderia.html')


@app.route('/citas/agendadas/usuario/')
@login_required
def u_citasAgendadas():
    return render_template('usuario/u_citasAgendadas.html')

@app.route('/agendarcitas/usuario/')
@login_required
def u_agendarCitaPerfil():
     return render_template('usuario/u_agendarCita.html')

@app.route('/home/usuario/')
@login_required
def indexUsuario():
     return render_template('usuario/index.html')

@app.route('/adopcion/usuario/')
@login_required
def u_adopcion():
     return render_template('usuario/u_adopcion.html')

@app.route('/citasAdomicilio/')
@login_required
def u_citasAdomicilio():
    return render_template('usuario/u_servicioAdomicialio.html')

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

# @app.route('/admin/adopcion/delete/<int:id_adopcion>', methods=['POST'])
# @admin_required
# def delete_adopcion(id_adopcion):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute('DELETE FROM adopcion WHERE id_adopcion = ?', (id_adopcion,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return redirect(url_for('a_adopcion'))

@app.route('/admin/adopcion/eliminar/<int:id_adopcion>', methods=['POST'])
def eliminar_adopcion(id_adopcion):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Eliminar el registro por ID
    cursor.execute('DELETE FROM adopcion WHERE id_adopcion = %s', (id_adopcion,))
    connection.commit()
    connection.close()
    
    return redirect(url_for('a_adopcion'))  # Redirigir después de la eliminación



















@app.route('/citas/agendadas/usuario/')

def tablaadopc():
    # Conecta a la base de datos
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtén el ID del usuario desde la sesión
 

    # Ejecuta la consulta SQL para obtener las citas agendadas del usuario
    cursor.execute('''
        SELECT * FROM adopcion ORDER BY
                
    ''')
    
    # Obtiene todos los resultados de la consulta
    citas_agendadas = cursor.fetchall()

    # Cierra el cursor y la conexión
    cursor.close()
    connection.close()

    # Renderiza la plantilla con los datos de las citas agendadas
    return render_template('admin/a_adopcion.html', citas=citas_agendadas)





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


# @app.route('/admin/adopcion/', methods=['GET', 'POST'])
# @admin_required
# def a_adopcion():
#   if request.method == 'POST' and all(k in request.form for k in ['foto_mascota', 'nombre', 'descripcion', 'edad', 'sexo']):
#         foto_mascota = request.files['foto_mascota']
#         nombre = request.form['nombre']
#         descripcion = request.form['descripcion']
#         edad = request.form['edad']
#         sexo = request.form['sexo']
#         peso = request.form['peso']

#         # Guardar la foto de la mascota
#         filename = secure_filename(foto_mascota.filename)
#         foto_mascota.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#         connection = get_db_connection()
#         cursor = connection.cursor()

#         cursor.execute('SELECT * FROM adopcion WHERE nombre = %s', (nombre,))
#         account = cursor.fetchone()
#         if account:
#             connection.close()
#             return render_template('admin/a_adopcion.html', message='El registro ya existe.')
#         else:
#             cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo, peso) VALUES (%s, %s, %s, %s, %s, %s)',
#                            (filename, nombre, descripcion, edad, sexo, peso))
#             connection.commit()
#             connection.close()
#             return redirect(url_for('admin/a_adopcion.html'))
        


# @app.route('/admin/citas/')
# @admin_required
# def a_citas():
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT c.fecha, c.tanda, u.nombre AS usuario_nombre, u.apellido AS usuario_apellido, m.tipoMascota AS mascota_tipo, s.nombre_servicio, c.descripcion FROM citas c JOIN usuario u ON c.id_usuario = u.id_usuario JOIN mascota m ON c.id_mascota = m.id_mascota JOIN servicios s ON c.id_servicio = s.id_servicio WHERE DATE(c.fecha) = CURDATE()")
#     citas = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return render_template('admin/a_citas.html', citas=citas)

# @app.route('/admin/adopcion/<int:id>', methods=['GET', 'POST'])
# @admin_required
# def eliminar_adopcion(id):
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute('DELETE FROM adopcion WHERE id = %s', (id,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return redirect(url_for('a_adopcion'))

@app.route('/admin/servicios/')
@admin_required
def a_servicio():
    return render_template('admin/a_sevicio.html')

@app.route('/admin/guarderia/')
@admin_required
def a_guarderia():
    return render_template('admin/a_AgendadasGuarderia.html')





# Inicia la aplicación
if __name__ == "__main__":
    app.run(port=3307, debug=True)