import os
from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import MySQLdb.cursors
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

# Crear la aplicación
app = Flask(__name__)

# Crear una llave secreta
app.secret_key = 'lytpython'

# Configurar la base de datos MySQL
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar el tamaño del archivo a 16 MB
app.config['MYSQL_CHARSET'] = 'utf8mb4'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'petvet'

# Inicializar MySQL
mysql = MySQL(app)

# Ruta principal (login)
@app.route('/')
def Index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'nombre-sesion' in request.form and 'pass-sesion' in request.form:
        nombre = request.form['nombre-sesion']
        password = request.form['pass-sesion']

        if nombre == 'Admin' and password == '12345':
            session['loggedin'] = True
            session['is_admin'] = True
            return redirect(url_for('indexAdmin'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['is_admin'] = False
            session['id'] = account['id_usuario']
            session['nombre'] = account['nombre']
            session['apellido'] = account['apellido']
            session['telefono'] = account['telefono']
            session['correo'] = account['correo']
            session['id_mascota'] = account['id_mascota']
            session['foto_perfil'] = account.get('foto_perfil', '')
            return redirect(url_for('indexUsuario'))
        else:
            return render_template('usuario/login.html')
    else:
        return render_template('usuario/login.html')

# Ruta de registro de usuario
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

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()

        if account:
            return render_template('usuario/u_registrousuario.html', error="¡El nombre ya está registrado!")
        else:
            cursor.execute('INSERT INTO mascota (tipoMascota) VALUES (%s)', (mascota,))
            id_mascota = cursor.lastrowid
            mysql.connection.commit()

            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            mysql.connection.commit()
            return redirect(url_for('login'))
    return render_template('usuario/u_registrousuario.html')

@app.route('/citas/agendadas/usuario/')
def u_citasAgendadas():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_citasAgendadas.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/agendarcitas/usuario/')
def u_agendarCita():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/agendarCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        update_user_profile_picture(filename)  # Asegúrate de que esta función actualiza la base de datos
        return redirect(url_for('indexUsuario'))  # Redirige a la página donde se muestra el perfil
    return redirect(request.url)


def update_user_profile_picture(filename):
    user_id = session.get('id')  # Suponiendo que el ID del usuario está en la sesión
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE usuario SET foto_perfil = %s WHERE id_usuario = %s', (filename, user_id))
    mysql.connection.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_file', filename=filename))

@app.route('/uploads/<filename>')
def archivo_subido(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/home/usuario/')
def indexUsuario():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/index.html', 
                               nombre=session['nombre'], 
                               apellido=session['apellido'], 
                               telefono=session['telefono'], 
                               correo=session['correo'], 
                               mascota=mascota['tipoMascota'],
                               foto_perfil=session['foto_perfil'])
    else:
        return redirect(url_for('Index'))

@app.route('/adopcion/usuario/')
def u_adopcion():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_adopcion.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/guarderia/usuario/')
def u_guarderia():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_guarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/citasAgendadas/guarderia/usuario/')
def u_citasAgendadasGuarderia():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_citasAgendadasGuarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/guarderia/cita/usuario/')
def u_guarderia_cita():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_guarderiaCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/servicios/solicitados/usuario/')
def u_servicio_solicitados():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_Servicios-solicitud.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/servicios/adomicilio/usuario/')
def u_servicio_adomicilio():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])
        mascota = cursor.fetchone()
        return render_template('usuario/u_servicioAdomicialio.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

# Rutas para administradores
@app.route('/admin/')
def indexAdmin():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/index.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/adopcion/')
def a_adopcion():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_adopcion.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/citas/agendada/')
def a_agendada_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_citas.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/servicios/')
def a_servicios():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_sevicio.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/agenda/citas/')
def a_agenda_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_AgendadasGuarderia.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/despliegue/guarderia/')
def a_despliegueGuarderia():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Guarderia.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/despliegue/citas/')
def a_despliegueCitas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Citas.html')
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(port=3307, debug=True)
