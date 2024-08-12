# Importar los módulos necesarios
import mysql.connector  # Para conectar con la base de datos MySQL
from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory  # Módulos de Flask
from werkzeug.utils import secure_filename  # Para asegurar los nombres de archivos
import os  # Módulos de operaciones del sistema operativo

# Crear la aplicación Flask
app = Flask(__name__)

# Configurar la aplicación
app.secret_key = 'lytpython'  # Clave secreta para manejar sesiones
UPLOAD_FOLDER = 'static/uploads'  # Carpeta para almacenar archivos subidos
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Comentado, no se usa en este código
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar el tamaño de los archivos subidos a 16 MB

# Función para obtener una conexión a la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  # Dirección del servidor de la base de datos
        user='root',  # Usuario de la base de datos
        password='',  # Contraseña del usuario
        database='petvet',  # Nombre de la base de datos
        charset='utf8mb4'  # Codificación de caracteres
    )

# Ruta principal redirige a la página de inicio de sesión
@app.route('/')
def Index():
    return redirect(url_for('login'))  # Redirige a la ruta de inicio de sesión

# Ruta para el inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'nombre-sesion' in request.form and 'pass-sesion' in request.form:
        nombre = request.form['nombre-sesion']  # Obtener nombre del formulario
        password = request.form['pass-sesion']  # Obtener contraseña del formulario

        # Autenticación de administrador
        if nombre == 'Admin' and password == '12345':
            session['loggedin'] = True  # Establecer sesión como iniciada
            session['is_admin'] = True  # Establecer que es un administrador
            return redirect(url_for('indexAdmin'))  # Redirige al panel de administración

        # Autenticación de usuario normal
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND contraseña = %s', (nombre, password))  # Consultar usuario
        account = cursor.fetchone()  # Obtener el primer registro encontrado
        connection.close()  # Cerrar la conexión a la base de datos

        if account:
            # Guardar información del usuario en la sesión
            session.update({
                'loggedin': True,  # Establecer sesión como iniciada
                'is_admin': False,  # Establecer que no es un administrador
                'id': account['id_usuario'],  # ID del usuario
                'nombre': account['nombre'],  # Nombre del usuario
                'apellido': account['apellido'],  # Apellido del usuario
                'telefono': account['telefono'],  # Teléfono del usuario
                'correo': account['correo'],  # Correo del usuario
                'id_mascota': account['id_mascota'],  # ID de la mascota del usuario
                'foto_perfil': account.get('foto_perfil', '')  # Foto de perfil del usuario (opcional)
            })
            return redirect(url_for('indexUsuario'))  # Redirige a la página de inicio del usuario
        else:
            return render_template('usuario/login.html')  # Renderiza la página de login si no hay coincidencia
    return render_template('usuario/login.html')  # Renderiza la página de login si es un GET

# Ruta para el registro de usuario
@app.route('/index/registro_usuario/', methods=['GET', 'POST'])
def u_registrousuario():
    if request.method == 'POST' and all(k in request.form for k in ['nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'sexo', 'mascota', 'correo', 'contraseña', 'verificar_contraseña']):
        nombre = request.form['nombre']  # Obtener nombre del formulario
        apellido = request.form['apellido']  # Obtener apellido del formulario
        fecha_nacimiento = request.form['fecha_nacimiento']  # Obtener fecha de nacimiento del formulario
        telefono = request.form['telefono']  # Obtener teléfono del formulario
        sexo = request.form['sexo']  # Obtener sexo del formulario
        mascota = request.form['mascota']  # Obtener tipo de mascota del formulario
        correo = request.form['correo']  # Obtener correo del formulario
        contraseña = request.form['contraseña']  # Obtener contraseña del formulario
        verificar_contraseña = request.form['verificar_contraseña']  # Obtener verificación de contraseña del formulario

        if contraseña != verificar_contraseña:
            return redirect(url_for('u_registrousuario'))  # Redirige si las contraseñas no coinciden

        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT * FROM usuario WHERE nombre = %s', (nombre,))  # Consultar si el usuario ya existe
        account = cursor.fetchone()  # Obtener el primer registro encontrado

        if account:
            connection.close()  # Cerrar la conexión a la base de datos
            return render_template('usuario/u_registrousuario.html')  # Renderiza la página de registro si el usuario ya existe
        else:
            # Insertar una nueva mascota en la base de datos
            cursor.execute('INSERT INTO mascota (tipoMascota) VALUES (%s)', (mascota,))
            id_mascota = cursor.lastrowid  # Obtener el ID de la última fila insertada
            connection.commit()  # Confirmar los cambios

            # Insertar un nuevo usuario en la base de datos
            cursor.execute('INSERT INTO usuario (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (nombre, apellido, fecha_nacimiento, telefono, sexo, id_mascota, correo, contraseña))
            connection.commit()  # Confirmar los cambios
            connection.close()  # Cerrar la conexión a la base de datos
            return redirect(url_for('login'))  # Redirige a la página de login
    return render_template('usuario/u_registrousuario.html')  # Renderiza la página de registro si es un GET

# Ruta para ver citas agendadas del usuario
@app.route('/citas/agendadas/usuario/')
def u_citasAgendadasPerfil():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_citasAgendadas.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de citas agendadas
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para ver citas agendadas del usuario
@app.route('/citas/agendadas/usuario/')
def u_citasAgendadas():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        
        # Obtener las citas del usuario
        cursor.execute('''
            SELECT c.fecha, c.tanda, m.tipoMascota, s.servicio, c.descripcion 
            FROM citas c
            JOIN mascota m ON c.id_mascota = m.id_mascota
            JOIN servicio s ON c.id_servicio = s.id_servicio
            WHERE c.id_usuario = %s
        ''', (session['id'],))  # Consultar citas del usuario
        citas = cursor.fetchall()  # Obtener todas las citas
        
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        
        return render_template('usuario/u_citasAgendadas.html', 
                               nombre=session['nombre'], 
                               apellido=session['apellido'], 
                               telefono=session['telefono'], 
                               correo=session['correo'], 
                               mascota=mascota['tipoMascota'],
                               citas=citas)  # Renderiza la página de citas agendadas con la información
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para agendar citas del usuario
@app.route('/agendarcitas/usuario/')
def u_agendarCita():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_agendarCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página para agendar citas
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para procesar la solicitud de agendar una cita
@app.route('/u_agendarCita', methods=['POST'])
def agendar_cita():
    if 'loggedin' in session:
        id_usuario = request.form['id_usuario']  # Obtener ID del usuario del formulario
        fecha = request.form['fecha']  # Obtener fecha de la cita del formulario
        tanda = request.form['tanda']  # Obtener tanda de la cita del formulario
        mascota = request.form['mascota']  # Obtener ID de la mascota del formulario
        servicios = request.form['servicios']  # Obtener ID del servicio del formulario
        descripcion = request.form['descripcion']  # Obtener descripción de la cita del formulario

        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor()  # Crear un cursor para ejecutar consultas
        
        # Insertar datos en la tabla citas
        query = "INSERT INTO citas (id_usuario, fecha, tanda, id_mascota, id_servicio, descripcion) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (id_usuario, fecha, tanda, mascota, servicios, descripcion))  # Ejecutar consulta
        connection.commit()  # Confirmar los cambios
        cursor.close()  # Cerrar el cursor
        connection.close()  # Cerrar la conexión a la base de datos
        
        return redirect(url_for('u_citasAgendadas'))  # Redirige a la página de citas agendadas
    return redirect(url_for('login'))  # Redirige a la página de login si no está logueado

# Ruta para la página de inicio del usuario
@app.route('/home/usuario/')
def indexUsuario():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/index.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de inicio del usuario
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para la adopción de mascotas por parte del usuario
@app.route('/adopcion/usuario/')
def u_adopcion():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_adopcion.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de adopción
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para la guardería de mascotas por parte del usuario
@app.route('/guarderia/usuario/')
def u_guarderia():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_guarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de guardería
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para ver citas agendadas en la guardería del usuario
@app.route('/citasAgendadas/guarderia/usuario/')
def u_citasAgendadasGuarderia():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_citasAgendadasGuarderia.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de citas agendadas en la guardería
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para la cita en la guardería del usuario
@app.route('/guarderia/cita/usuario/')
def u_guarderia_cita():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_guarderiaCita.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de cita en la guardería
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Ruta para ver los servicios solicitados por el usuario
@app.route('/servicios/solicitados/usuario/')
def u_servicio_solicitados():
    if 'loggedin' in session:
        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor(dictionary=True)  # Crear un cursor para ejecutar consultas
        cursor.execute('SELECT tipoMascota FROM mascota WHERE id_mascota = %s', [session['id_mascota']])  # Consultar tipo de mascota
        mascota = cursor.fetchone()  # Obtener el registro de la mascota
        connection.close()  # Cerrar la conexión a la base de datos
        return render_template('usuario/u_Servicios-solicitud.html', nombre=session['nombre'], apellido=session['apellido'], telefono=session['telefono'], correo=session['correo'], mascota=mascota['tipoMascota'])  # Renderiza la página de servicios solicitados
    return redirect(url_for('Index'))  # Redirige a la página principal si no está logueado

# Rutas para administradores
@app.route('/admin/')
def indexAdmin():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/index.html')  # Renderiza la página principal del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

# Ruta para solicitar servicios a domicilio
@app.route('/admin/adopcion/', methods=['GET', 'POST'])
def a_adopcion():
    if request.method == 'POST' and all(k in request.form for k in ['foto_mascota', 'nombre', 'descripcion', 'edad', 'sexo']):
        foto_mascota = request.form['foto_mascota']  # Obtener foto de la mascota del formulario
        nombre = request.form['nombre']  # Obtener nombre de la mascota del formulario
        descripcion = request.form['descripcion']  # Obtener descripción de la mascota del formulario
        edad = request.form['edad']  # Obtener edad de la mascota del formulario
        sexo = request.form['sexo']  # Obtener sexo de la mascota del formulario
        peso = request.form['peso']  # Obtener peso de la mascota del formulario

        connection = get_db_connection()  # Conectar a la base de datos
        cursor = connection.cursor()  # Crear un cursor para ejecutar consultas

        # Verificar si el registro ya existe
        cursor.execute('SELECT * FROM adopcion WHERE nombre = %s', (nombre,))
        account = cursor.fetchone()  # Obtener el registro de adopción
        if account:
            connection.close()  # Cerrar la conexión a la base de datos
            return render_template('admin/a_adopcion.html', message='El registro ya existe.')  # Mensaje de error si el registro ya existe
        else:
            # Insertar datos en la base de datos
            cursor.execute('INSERT INTO adopcion (foto_mascota, nombre, descripcion, edad, sexo, peso) VALUES (%s, %s, %s, %s, %s, %s)',
                           (foto_mascota, nombre, descripcion, edad, sexo, peso))  # Ejecutar consulta
            connection.commit()  # Confirmar los cambios
            connection.close()  # Cerrar la conexión a la base de datos
            return redirect(url_for('a_adopcion'))  # Redirigir después de la inserción

    return render_template('admin/a_adopcion.html')  # Renderiza la página de adopción del administrador


@app.route('/admin/citas/agendada/')
def a_agendada_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_citas.html')  # Renderiza la página de citas agendadas del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

@app.route('/admin/servicios/')
def a_servicios():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_sevicio.html')  # Renderiza la página de servicios del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

@app.route('/admin/agenda/citas/')
def a_agenda_citas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_AgendadasGuarderia.html')  # Renderiza la página de agenda de citas del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

@app.route('/admin/despliegue/guarderia/')
def a_despliegueGuarderia():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Guarderia.html')  # Renderiza la página de despliegue de guardería del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

@app.route('/admin/despliegue/citas/')
def a_despliegueCitas():
    if 'loggedin' in session and session.get('is_admin'):
        return render_template('admin/a_despliegue-Citas.html')  # Renderiza la página de despliegue de citas del administrador
    return redirect(url_for('login'))  # Redirige a la página de login si no es administrador

# Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(port=3307, debug=True)  # Ejecuta la aplicación Flask en el puerto 3307 y con modo debug activado
