import os
from flask import Flask, render_template, request, redirect, session, url_for, flash
import MySQLdb.cursors
from flask_mysqldb import MySQL

# Crear la aplicación
app = Flask(__name__)

# Crear una llave secreta
app.secret_key = 'lytpython'

# Configurar la base de datos MySQL
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
            flash('¡Inicio de sesión exitoso como administrador!', 'success')
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
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('u_citasAgendadas'))  
        else:
            flash('¡Nombre o contraseña incorrectos!', 'danger')
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
            flash('¡Las contraseñas no coinciden!', 'danger')
            return redirect(url_for('u_registrousuario'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()

        if account:
            flash('¡El nombre ya está registrado!', 'danger')
        else:
            cursor.execute('INSERT INTO mascota (tipoMascota) VALUES (%s)', (mascota,))
            id_mascota = cursor.lastrowid
            mysql.connection.commit()

            cursor.execute('INSERT INTO usuario (nombre, apellido, `fecha-nacimiento`, telefono, sexo, id_mascota, correo, contraseña, verificar_contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña, verificar_contraseña))
            mysql.connection.commit()
            flash('¡Te has registrado exitosamente!', 'success')
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
        return render_template('usuario/u_agendarCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])
    else:
        return redirect(url_for('Index'))

@app.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    if 'loggedin' in session:
        id_usuario = session['id']
        fecha = request.form['fecha']
        tanda = request.form['tanda']
        id_mascota = request.form['mascota']
        id_servicio = request.form.get('servicio', 'valor_por_defecto')
        descripcion = request.form.get('descripcion', 'Valor por defecto')

        cursor = mysql.connection.cursor()
        sql = """
        INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicio, descripcion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (id_usuario, fecha, tanda, id_mascota, id_servicio, descripcion))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('u_citasAgendadas'))
    else:
        return redirect(url_for('Index'))

@app.route('/adopcion/usuario/')
def u_adopcion():
    return render_template('usuario/u_adopcion.html')

@app.route('/guarderia/usuario/')
def u_guarderia():
    return render_template('usuario/u_guarderia.html')

@app.route('/citasAgendadas/guarderia/usuario/')
def u_citasAgendadasGuarderia():
    return render_template('usuario/u_citasAgendadasGuarderia.html')

@app.route('/guarderia/cita/usuario/')
def u_guarderia_cita():
    return render_template('usuario/u_guarderiaCita.html')

@app.route('/servicios/solicitados/usuario/')
def u_servicio_solicitados():
    return render_template('usuario/u_Servicios-solicitud.html')

@app.route('/servicios/adomicilio/usuario/')
def u_servicio_adomicilio():
    return render_template('usuario/u_servicioAdomicialio.html')

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
