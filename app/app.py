import os
import pdfkit
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, Blueprint, make_response
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required

from Models.ModelUser import ModuleUser
from Models.entities.user import User
#importamos Blueprint para crear una etiqueta

#Creamos una tag con la ayuda de Blueprint y la iniciamos en nuestro proyecti (al crear nuestra applicación)
custom_tags = Blueprint('custom_tags', __name__)

app = Flask(__name__)
csrf=CSRFProtect()

# Conexión MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'tiard'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ruta=app.config['UPLOAD_FOLDER']='./app/static/img/uploads/profesores'

db = MySQL(app)

Login_manager_app=LoginManager(app)

@Login_manager_app.user_loader
def load_user(idusuarios):
    return ModuleUser.get_by_id(db,idusuarios)

@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html')


app.secret_key='mysecretkey'

#Usamos el nuevo tag que creamos y le asignamos una función
@custom_tags.app_template_global()
def listar_materias():
    cur=db.connection.cursor()
    sql="SELECT * FROM materias order by nombre asc"
    cur.execute(sql)
    materias=cur.fetchall()
    cur.close()
    return materias

@login_required
def listar_profesores():
    cur=db.connection.cursor()
    sql="SELECT * FROM profesores order by nombre asc"
    cur.execute(sql)
    profesores=cur.fetchall()
    cur.close()
    return profesores

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Ruta al Inicio
@app.route('/')
def index():
    materias = listar_materias()
    data = {
        'titulo': 'Inicio',
        'bienvenida': 'Proyecto TIAIRD',
        'materias': materias,
        'numero_materias': len(materias)
    }
    print(materias)
    
    return render_template('index.html', data=data)

# ---------------------------------------------- Apartado CRUD de Alumnos ---------------------------------------------
#Read (Leer)
@app.route('/alumnos')
@login_required
def alumnos_Ver():
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos order by matricula asc"
    cur.execute(sql)
    alumnos=cur.fetchall()
    print(alumnos) 
    cur.close()

    return render_template('alumnos.html', alumnos=alumnos)

@app.route('/alumno/<string:id>')
@login_required
def ver_alumno(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    alumno=cur.fetchall()
    print(alumno[0])
    cur.close()
    
    return render_template('alumnoVer.html', alumno=alumno[0])

#Generar PDF de Alumno en otra ventana
@app.route('/alumno/<string:id>/PDF')
@login_required
def ver_alumno_PDF(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    alumno=cur.fetchall()
    print(alumno[0])
    cur.close()
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    # Renderizar el template HTML con los datos obtenidos
    options  ={
        'page-size' : 'Letter',
        'margin-top' : '0px',
        'margin-right' : '0px',
        'margin-bottom' : '0px',
        'margin-left' : '0px',
        'encoding': "UTF-8",
    }
    html = render_template('alumnosPDF.html', alumno=alumno[0])
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=AlumnoPDF.pdf"
    return response
    # Generar el PDF a partir del HTML renderizado
    #pdfkit.from_string(html, 'alumnoVer.pdf', configuration=config, options=options)

    #return 'Reporte generado correctamente'

    #return render_template('alumnoVer.html', alumno=alumno[0])

#Create (Crear)
@app.route('/alumno/nuevo')
@login_required
def alumno_Crear():
    return render_template('alumnoCrear.html',)

@app.route('/alumno/agregar', methods=['POST'])
@login_required
def alumno_Agregar():
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Matricula=request.form['Matricula']

        cur=db.connection.cursor()
        sql="INSERT INTO alumnos (nombre, matricula) VALUES (%s, %s)"
        valores=(Nombre, Matricula.upper())
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        #flash('¡Alumno "{}" agregado exitosamente!'.format(Nombre))
        flash('¡Alumno agregado exitosamente!')

        return redirect(url_for('alumno_Crear'))

#Update (Actualizar)
@app.route('/alumno/editar/<string:id>')
@login_required
def editar_alumno(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    alumno=cur.fetchall()
    print(alumno[0])
    cur.close()
    return render_template('alumnoEditar.html', alumno=alumno[0])

@app.route('/alumno/actualizar/<string:id>', methods=['POST'])
@login_required
def alumno_actualizar(id):
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Matricula=request.form['Matricula']

        cur=db.connection.cursor()
        sql="UPDATE alumnos SET nombre=%s, Matricula=%s WHERE idalumnos=%s"        
        valores=(Nombre, Matricula.upper(), id)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Alumno modificado exitosamente!')
    return redirect(url_for('alumnos_Ver'))

#Delete (Borrar)
@app.route('/alumno/eliminar/<string:id>')
@login_required
def eliminar_alumno(id):
    print(id)
    cur=db.connection.cursor()
    sql="DELETE FROM alumnos WHERE idalumnos={0}".format(id)
    cur.execute(sql)
    db.connection.commit()
    cur.close()
    flash('¡Alumno  eliminado correctamente!')
    return redirect(url_for('alumnos_Ver'))


# ---------------------------------------------- Apartado CRUD de Profesores ----------------------------------------------
#Read (Leer)
@app.route('/profesores')
@login_required
def profesores_Ver():
    cur=db.connection.cursor()
    sql="SELECT * FROM profesores ORDER BY idprofesores desc"
    cur.execute(sql)
    profesores=cur.fetchall()
    print(profesores) 
    cur.close()
    return render_template('profesores.html', profesores=profesores)

@app.route('/profesor/<string:id>')
@login_required
def ver_profesor(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM profesores WHERE idprofesores={0}".format(id)
    cur.execute(sql)
    profesor=cur.fetchall()
    print(profesor[0])
    cur.close()
    return render_template('profesorVer.html', profesor=profesor[0])

#Create (Crear)
@app.route('/profesor/nuevo')
@login_required
def profesor_Crear():
    return render_template('profesorCrear.html',)

@app.route('/profesor/agregar', methods=['POST'])
@login_required
def profesor_Agregar():
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Empleado=request.form['Empleado']
        Creado=datetime.now()
        Activo=1
        
        file=request.files['Foto']

        if file and allowed_file(file.filename):
            # Verificar si el archivo con el mismo nombre ya existe
            # Creamos un nombre dinamico para la foto de perfil con el nombre y el numero de empleado
            filename = "FotoPerfil_" + Nombre + "_" + Empleado + "_" + secure_filename(file.filename)
            file_path = os.path.join(ruta, filename)
            if os.path.exists(file_path):
                flash('Advertencia: ¡Un archivo con el mismo nombre ya existe!')
            
            # Guardar el archivo y registrar en la base de datos
            file.save(file_path)
        else:
            flash('Error: ¡Extensión de archivo invalida!')

            return redirect(url_for('profesores_Ver'))

        cur=db.connection.cursor()
        sql="INSERT INTO profesores (nombre, numero_empleado, creado, activo, file_url) VALUES (%s, %s, %s, %s, %s)"
        valores=(Nombre, Empleado, Creado, Activo, filename)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Profesor agregado exitosamente!')

        return redirect(url_for('profesores_Ver'))

#Update (Actualizar)
@app.route('/profesor/editar/<string:id>')
@login_required
def editar_profesor(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM profesores WHERE idprofesores={0}".format(id)
    cur.execute(sql)
    profesor=cur.fetchall()
    print(profesor[0])
    cur.close()
    return render_template('profesorEditar.html', profesor=profesor[0])

@app.route('/profesor/actualizar/<string:id>', methods=['POST'])
@login_required
def profesor_actualizar(id):
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Empleado=request.form['Empleado']

        cur=db.connection.cursor()
        sql="UPDATE profesores SET nombre=%s, numero_empleado=%s WHERE idprofesores=%s"        
        valores=(Nombre, Empleado, id)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()
        flash('¡Profesores modificado exitosamente!')
    return redirect(url_for('profesores_Ver'))

#Delete (Borrar)
@app.route('/profesor/eliminar/<string:id>')
@login_required
def eliminar_profesor(id):
    print(id)
    cur=db.connection.cursor()
    sql="DELETE FROM profesores WHERE idprofesores={0}".format(id)
    cur.execute(sql)
    db.connection.commit()
    cur.close()
    flash('¡Profesores eliminado correctamente!')
    return redirect(url_for('profesores_Ver'))

# ---------------------------------------------- Apartado CRUD de Materias ----------------------------------------------
#Read (Leer)
@app.route('/materias')
@login_required
def materias_Ver():
    cur=db.connection.cursor()
    #sql="SELECT m.idmaterias, m.nombre, m.idprofesor, p.numero_empleado, p.nombre FROM materias as m INNER JOIN profesores as p ON m.idprofesor = p.idprofesores ORDER BY idmaterias desc"
    sql="SELECT m.idmaterias, m.nombre , p.numero_empleado, p.nombre FROM materias as m INNER JOIN profesores as p ON m.idprofesor = p.idprofesores ORDER BY m.idmaterias desc"
    cur.execute(sql)
    materias=cur.fetchall()
    print(materias) 
    cur.close()
    return render_template('materias.html', materias=materias)

@app.route('/materia/<string:id>')
@login_required
def ver_materia(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM materias WHERE idmaterias={0}".format(id)
    cur.execute(sql)
    materia=cur.fetchall()
    print(materia[0])
    cur.close()
    return render_template('materiaVer.html', materia=materia[0])

#Create (Crear)
@app.route('/materia/nuevo')
@login_required
def materia_Crear():
    return render_template('materiaCrear.html',profesores=listar_profesores())

@app.route('/materia/agregar', methods=['POST'])
@login_required
def materia_Agregar():
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Profesor=request.form['Profesor']

        cur=db.connection.cursor()
        sql="INSERT INTO materias (nombre, idprofesor) VALUES (%s, %s)"
        valores=(Nombre, Profesor)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Materia agregada exitosamente!')

        return redirect(url_for('materias_Ver'))

#Update (Actualizar)
@app.route('/materia/editar/<string:id>')
@login_required
def editar_materia(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM materias WHERE idmaterias={0}".format(id)
    cur.execute(sql)
    materia=cur.fetchall()
    print(materia[0])
    cur.close()
    return render_template('materiaEditar.html', materia=materia[0])

@app.route('/materia/actualizar/<string:id>', methods=['POST'])
@login_required
def materia_actualizar(id):
    if request.method == 'POST':
        Nombre=request.form['Nombre']
        Profesor=request.form['Profesor']

        cur=db.connection.cursor()
        sql="UPDATE materias SET nombre=%s, idprofesor=%s WHERE idmaterias=%s"        
        valores=(Nombre, Profesor, id)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Materia modificada exitosamente!')
    return redirect(url_for('materias_Ver'))

#Delete (Borrar)
@app.route('/materia/eliminar/<string:id>')
@login_required
def eliminar_materia(id):
    print(id)
    cur=db.connection.cursor()
    sql="DELETE FROM materias WHERE idmaterias={0}".format(id)
    cur.execute(sql)
    db.connection.commit()
    cur.close()
    flash('¡Materia eliminada correctamente!')
    return redirect(url_for('materias_Ver'))


# ---------------------------------------------- Apartado CRUD de Usuarios ----------------------------------------------
#Read (Leer)
@app.route('/usuarios')
@login_required
def usuarios_Ver():
    cur=db.connection.cursor()
    sql="SELECT * FROM usuarios ORDER BY idusuarios desc"
    cur.execute(sql)
    usuarios=cur.fetchall()
    print(usuarios) 
    cur.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuario/<string:id>')
@login_required
def ver_usuario(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM usuarios WHERE idusuarios={0}".format(id)
    cur.execute(sql)
    usuario=cur.fetchall()
    print(usuario[0])
    cur.close()
    return render_template('usuarioVer.html', usuario=usuario[0])

#Create (Crear)
@app.route('/usuario/nuevo')
@login_required
def usuario_Crear():
    return render_template('usuarioCrear.html',)

@app.route('/usuario/agregar', methods=['POST'])
@login_required
def usuario_Agregar():
    if request.method == 'POST':
        Username=request.form['Username']
        Password=request.form['Password']
        Pass=generate_password_hash(Password)
        TipoUsuario=request.form['TipoUsuario']
        Creado=datetime.now()
        Activo=1

        cur=db.connection.cursor()
        sql="INSERT INTO usuarios (username, password, tipo, creado, activo) VALUES (%s, %s, %s,%s, %s)"
        valores=(Username, Pass, TipoUsuario, Creado, Activo)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Usuario agregado exitosamente!')

        return redirect(url_for('usuarios_Ver'))

#Update (Actualizar)
@app.route('/usuario/editar/<string:id>')
@login_required
def editar_usuario(id):
    print(id)
    cur=db.connection.cursor()
    sql="SELECT * FROM usuarios WHERE idusuarios={0}".format(id)
    cur.execute(sql)
    usuario=cur.fetchall()
    print(usuario[0])
    cur.close()
    return render_template('usuarioEditar.html', usuario=usuario[0])

@app.route('/usuario/actualizar/<string:id>', methods=['POST'])
@login_required
def usuario_actualizar(id):
    if request.method == 'POST':
        Username=request.form['Username']
        Password=request.form['Password']
        Pass=generate_password_hash(Password)
        TipoUsuario=request.form['TipoUsuario']
        Activo=1

        cur=db.connection.cursor()
        sql="UPDATE usuarios SET username=%s, password=%s, tipo=%s, activo=%s WHERE idusuarios=%s"        
        valores=(Username, Pass, TipoUsuario, Activo, id)
        cur.execute(sql,valores)
        db.connection.commit()
        cur.close()

        flash('¡Usuario modificado exitosamente!')
    return redirect(url_for('usuarios_Ver'))

#Delete (Borrar)
@app.route('/usuario/eliminar/<string:id>')
@login_required
def eliminar_usuario(id):
    print(id)
    cur=db.connection.cursor()
    sql="DELETE FROM usuarios WHERE idusuarios={0}".format(id)
    cur.execute(sql)
    db.connection.commit()
    cur.close()
    flash('¡Usuario eliminado correctamente!')
    return redirect(url_for('usuarios_Ver'))

### Apartado SingUp

@app.route('/signup')
def signup():
    return render_template('signup.html')

### Apartado Login

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loguear', methods=['POST'])
def loguear():
    if request.method == 'POST':
        Username=request.form['Username']
        Password=request.form['Password']
        user=User(0,Username,Password,None)
        loged_user=ModuleUser.login(db,user)

        if loged_user!= None:
            if loged_user.password:
                login_user(loged_user)
                return redirect(url_for('usuarios_Ver'))
            else:
                flash('Nombre de usuario y/o Contraseña incorrecta.')
                return render_template('login.html')
        else:
            flash('Nombre de usuario y/o Contraseña incorrecta.')
            return render_template('login.html')
    else:
            flash('Nombre de usuario y/o Contraseña incorrecta.')
            return render_template('login.html')


def pagina_no_encontrada(error):
    #return render_template('404.html'), 404
    return redirect(url_for('index'))
def acceso_no_autorizado(error):
    return redirect(url_for('login'))

if __name__ == '__main__':
    csrf.init_app(app)
    app.register_blueprint(custom_tags)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port=5000)