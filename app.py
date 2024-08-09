import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la aplicación
app.secret_key = 'lytpython'  # Clave secreta para sesiones
UPLOAD_FOLDER = 'static/uploads'  # Carpeta para almacenar archivos subidos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar el tamaño del archivo a 16 MB

# Función para obtener una conexión a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='petvet',
        charset='utf8mb4'
    )

# Función para verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta principal redirige a la página de inicio de sesión
@app.route('/')
def Index():
    return redirect(url_for('login'))

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'nombre-sesion' in request.form and 'pass-sesion' in request.form:
        nombre = request.form['nombre-sesion']
        password = request.form['pass-sesion']

        # Autenticación de administrador
        if nombre == 'Admin' and password == '12345':
            session['loggedin'] = True
            session['is_admin'] = True
            return redirect(url_for('indexAdmin'))

        # Autenticación de usuario normal
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))
        account = cursor.fetchone()
        connection.close()

        if account:
            # Guardar información del usuario en la sesión
            session.update({
                'loggedin': True,
                'is_admin': False,
                'id': account['id_usuario'],
                'nombre': account['nombre'],
                'apellido': account['apellido'],
                'telefono': account['telefono'],
                'correo': account['correo'],
                'id_mascota': account['id_mascota'],
                'foto_perfil': account.get('foto_perfil', '')
            })
            return redirect(url_for('indexUsuario'))
        else:
            return render_template('usuario/login.html')
    return render_template('usuario/login.html')

# Ruta para el registro de usuarios
@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        sexo = request.form['sexo']
        mascota = request.form['mascota']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        verificar_contraseña = request.form['verificar_contraseña']

        if contraseña != verificar_contraseña:
            return redirect(url_for('u_registrousuario'))

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()

        if account:
            connection.close()
            return render_template('usuario/u_registrousuario.html')
        else:
            cursor.execute('INSERT INTO mascota (tipoMascota) VALUES (%s)', (mascota,))
            id_mascota = cursor.lastrowid
            connection.commit()

            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            connection.commit()
            connection.close()
            return redirect(url_for('login'))
    return render_template('usuario/u_registrousuario.html')

# Ruta para ver citas agendadas del usuario
@app.route('/citas/agendadas/usuario/')
def u_citasAgendadas():
      if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_citasAgendadas.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
      return redirect(url_for('Index'))
        

# Ruta para agendar citas del usuario
@app.route('/agendarcitas/usuario/')
def u_agendarCita():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_agendarCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para cargar la foto de perfil
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'profile_picture' not in request.files:
        return redirect(request.url)
    file = request.files['profile_picture']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update_user_profile_picture(filename)
        return redirect(url_for('indexUsuario'))
    return redirect(request.url)

# Actualiza la foto de perfil del usuario en la base de datos
def update_user_profile_picture(filename):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('UPDATE usuario SET foto_perfil = %s WHERE id_usuario = %s', (filename, session['id']))
    connection.commit()
    connection.close()

# Ruta para servir archivos subidos
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rutas para usuarios
@app.route('/home/usuario/')
def indexUsuario():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/index.html', 
                               nombre=session['nombre'], 
                               apellido=session['apellido'], 
                               telefono=session['telefono'], 
                               correo=session['correo'], 
                               mascota=mascota['tipoMascota'],
                               foto_perfil=session['foto_perfil'])
    return redirect(url_for('Index'))

# Ruta para la adopción de mascotas por parte del usuario
@app.route('/adopcion/usuario/')
def u_adopcion():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_adopcion.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para la guardería de mascotas por parte del usuario
@app.route('/guarderia/usuario/')
def u_guarderia():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_guarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para ver citas agendadas en la guardería del usuario
@app.route('/citasAgendadas/guarderia/usuario/')
def u_citasAgendadasGuarderia():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_citasAgendadasGuarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para la cita en la guardería del usuario
@app.route('/guarderia/cita/usuario/')
def u_guarderia_cita():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_guarderiaCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para ver los servicios solicitados por el usuario
@app.route('/servicios/solicitados/usuario/')
def u_servicio_solicitados():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        connection.close()
        return render_template('usuario/u_Servicios-solicitud.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    return redirect(url_for('Index'))

# Ruta para solicitar servicios a domicilio
@app.route('/admin/adopcion/', methods=['GET', 'POST'])
def a_adopcion():
    if request.method == 'POST' and all(k in request.form for k in ['foto_mascota', 'nombre', 'descripcion', 'edad', 'sexo']):
        foto_mascota = request.form['foto_mascota']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        edad = request.form['edad']
        sexo = request.form['sexo']
        peso = request.form['peso']

        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si el registro ya existe
        cursor.execute('SELECT * FROM adopcion WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()

        if account:
            connection.close()
            return render_template('admin/a_adopcion.html', message='El registro ya existe.')
        else:
            # Insertar datos en la base de datos
            cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo, peso) VALUES (%s, %s, %s, %s, %s, %s)',
                           (foto_mascota, nombre, descripcion, edad, sexo, peso))
            connection.commit()
            connection.close()
            return redirect(url_for('a_adopcion'))  # Redirigir después de la inserción

    return render_template('admin/a_adopcion.html')

# Rutas para administradores
@app.route('/admin/')
def indexAdmin():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/index.html')
    return redirect(url_for('login'))

# @app.route('/admin/adopcion/')
# def a_adopcion():
#     if 'loggedin' in session and session.get('is_admin'):
#         return render_template('admin/a_adopcion.html')
#     return redirect(url_for('login'))

@app.route('/admin/citas/agendada/')
def a_agendada_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_citas.html')
    return redirect(url_for('login'))

@app.route('/admin/servicios/')
def a_servicios():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_sevicio.html')
    return redirect(url_for('login'))

@app.route('/admin/agenda/citas/')
def a_agenda_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_AgendadasGuarderia.html')
    return redirect(url_for('login'))

@app.route('/admin/despliegue/guarderia/')
def a_despliegueGuarderia():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Guarderia.html')
    return redirect(url_for('login'))

@app.route('/admin/despliegue/citas/')
def a_despliegueCitas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Citas.html')
    return redirect(url_for('login'))

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(port=3307, debug=True)
