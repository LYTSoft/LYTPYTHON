import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for, flash
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
    
# Función para obtener el tipo de mascota basado en el ID de la mascota
def get_mascota_tipo(id_mascota):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [id_mascota])
    mascota = cursor.fetchone()
    connection.close()
    return mascota['tipoMascota'] if mascota else None

# Decorador para verificar si el usuario está logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para verificar si el usuario es un administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session.get('is_admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def Index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre-sesion']
        password = request.form['pass-sesion']

        if nombre == 'Admin' and password == '12345':
            session['loggedin'] = True
            session['is_admin'] = True
            return redirect(url_for('indexAdmin'))

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))
        account = cursor.fetchone()
        connection.close()

        if account:
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
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('usuario/login.html')

@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        sexo = request.form['sexo']
        id_mascota = request.form['mascota']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        verificar_contraseña = request.form['verificar_contraseña']

        if contraseña != verificar_contraseña:
            return render_template('usuario/u_registrousuario.html', error="Las contraseñas no coinciden")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM usuario WHERE correo = %s', (correo,))
        account = cursor.fetchone()
        
        if account:
            connection.close()
            return render_template('usuario/u_registrousuario.html', error="El correo ya está registrado")
        else:
            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            connection.commit()
            connection.close()
            return redirect(url_for('login'))
    
    return render_template('usuario/u_registrousuario.html')

@app.route('/citas/agendadas/usuario/')
@login_required
def u_citasAgendadas():
    return render_template('usuario/u_citasAgendadas.html')

@app.route('/agendarcitas/usuario/')
@login_required
def u_agendarCitaPerfil():
     return render_template('usuario/u_agendarCita.html')

@app.route('/usuario/u_agendarCita', methods=['GET', 'POST'])
@login_required
def agendar_cita():
    if request.method == 'POST':
        print("Datos recibidos:", request.form)
        
        if all(k in request.form for k in ['id_usuario', 'fecha', 'tanda', 'mascota', 'servicios', 'descripcion']):
            id_usuario = request.form['id_usuario']
            fecha = request.form['fecha']
            tanda = request.form['tanda']
            id_mascota = request.form['mascota']
            id_servicios = request.form['servicios']
            descripcion = request.form['descripcion']

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM citas WHERE fecha = %s', (fecha,))
            account = cursor.fetchone()

            if account:
                cursor.close()
                connection.close()
                return render_template('usuario/u_agendarCita.html', message='El registro ya existe.')

            cursor.execute('INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicio, descripcion) VALUES (%s, %s, %s, %s, %s, %s)',
                           (id_usuario, fecha, tanda, id_mascota, id_servicios, descripcion))

            connection.commit()
            cursor.close()
            connection.close()

            flash('Cita agendada con éxito', 'success')
            return redirect(url_for('u_citasAgendadas'))

    return render_template('usuario/u_agendarCita.html')

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

@app.route('/admin/')
@admin_required
def indexAdmin():
    return render_template('admin/index.html')

@app.route('/admin/adopcion/', methods=['GET', 'POST'])
@admin_required
def a_adopcion():
  if request.method == 'POST' and all(k in request.form for k in ['foto_mascota', 'nombre', 'descripcion', 'edad', 'sexo']):
        foto_mascota = request.files['foto_mascota']
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        edad = request.form['edad']
        sexo = request.form['sexo']
        peso = request.form['peso']

        # Guardar la foto de la mascota
        filename = secure_filename(foto_mascota.filename)
        foto_mascota.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM adopcion WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()
        if account:
            connection.close()
            return render_template('admin/a_adopcion.html', message='El registro ya existe.')
        else:
            cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo, peso) VALUES (%s, %s, %s, %s, %s, %s)',
                           (filename, nombre, descripcion, edad, sexo, peso))
            connection.commit()
            connection.close()
            return redirect(url_for('a_adopcion'))

        return render_template('admin/a_adopcion.html')

@app.route('/admin/citas/')
@admin_required
def a_citas():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT c.fecha, c.tanda, u.nombre AS usuario_nombre, u.apellido AS usuario_apellido, m.tipoMascota AS mascota_tipo, s.nombre_servicio, c.descripcion FROM citas c JOIN usuario u ON c.id_usuario = u.id_usuario JOIN mascota m ON c.id_mascota = m.id_mascota JOIN servicios s ON c.id_servicio = s.id_servicio WHERE DATE(c.fecha) = CURDATE()")
    citas = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('admin/a_citas.html', citas=citas)

@app.route('/admin/adopcion/<int:id>', methods=['GET', 'POST'])
@admin_required
def eliminar_adopcion(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM adopcion WHERE id = %s', (id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('a_adopcion'))

@app.route('/admin/servicios/')
@admin_required
def a_servicios():
    return render_template('admin/a_servicios.html')

@app.route('/admin/guarderia/')
@admin_required
def a_guarderia():
    return render_template('admin/a_guarderia.html')



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