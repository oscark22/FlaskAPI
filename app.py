from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields
from dotenv import load_dotenv
import os


# Load environmental variables
load_dotenv()

DB_USERNAME = os.environ.get('DB_USERNAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')


db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db.init_app(app)


class Alumnos(db.Model):
   __tablename__ = "alumnos"
   id_alumno = db.Column(db.Integer, primary_key=True)
   matricula = db.Column(db.String(10))
   ap_paterno = db.Column(db.String(30))
   ap_materno = db.Column(db.String(30))
   nombre = db.Column(db.String(30))
 
   def create(self):
     db.session.add(self)
     db.session.commit()
     return self
 
   def __init__(self, matricula, ap_paterno, ap_materno, nombre):
       self.matricula  = matricula
       self.ap_paterno = ap_paterno
       self.ap_materno = ap_materno
       self.nombre = nombre
 
   def __repr__(self):
       return '' % self.id_alumno


class AlumnosSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Alumnos
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    id_alumno = auto_field(dump_only = True)
    matricula = fields.String(required = True)
    ap_paterno = fields.String(required = True)
    ap_materno = fields.String(required = True)
    nombre = fields.String(required = True)


class Materias(db.Model):
   __tablename__ = "materias"
   id_materia = db.Column(db.Integer, primary_key=True)
   clave_materia = db.Column(db.String(6))
   nombre = db.Column(db.String(30))
   creditos = db.Column(db.Integer)

   def create(self):
     db.session.add(self)
     db.session.commit()
     return self
 
   def __init__(self, clave_materia, nombre, creditos):
       self.clave_materia = clave_materia
       self.nombre = nombre
       self.creditos = creditos
 
   def __repr__(self):
       return '' % self.id_materia


class MateriasSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Materias
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    id_materia = auto_field(dump_only = True)
    clave_materia = fields.String(required = True)
    nombre = fields.String(required = True)
    creditos = fields.Number(required = True)


class Profesores(db.Model):
   __tablename__ = "profesores"
   id_profesor = db.Column(db.Integer, primary_key=True)
   nombre = db.Column(db.String(30))
   ap_paterno = db.Column(db.String(30))
   ap_materno = db.Column(db.String(30), nullable=True)
   num_empleado = db.Column(db.String(20))
   password = db.Column(db.String(20))
   correo = db.Column(db.String(50))

   def create(self):
     db.session.add(self)
     db.session.commit()
     return self
 
   def __init__(self, nombre, ap_paterno, num_empleado, password, correo, ap_materno='NA'):
        self.nombre = nombre
        self.ap_paterno = ap_paterno
        self.num_empleado = num_empleado
        self.password = password
        self.correo = correo

        if ap_materno != 'NA':
            self.ap_materno = ap_materno

   def __repr__(self):
       return '' % self.id_profesor


class ProfesoresSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Profesores
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    id_profesor = auto_field(dump_only = True)
    nombre = fields.String(required = True)
    ap_paterno = fields.String(required = True)
    ap_materno = fields.String(required = False)
    num_empleado = fields.String(required = True)
    password = fields.String(required = True)
    correo = fields.String(required = True)
    
@app.route('/alumnos', methods = ['GET'])
def alumnos():
    if request.method == 'GET':
        get_alumnos = Alumnos.query.all()
        alumnos_schema = AlumnosSchema(many=True)
        alumnos = alumnos_schema.dump(get_alumnos)
        return make_response(jsonify({"alumno": alumnos}))

@app.route('/materias', methods = ['GET', 'POST'])
def materias():
    if request.method == 'GET':
        get_materias= Materias.query.all()
        materias_schema = MateriasSchema(many=True)
        materias = materias_schema.dump(get_materias)
        return make_response(jsonify({"materia": materias}))
    elif request.method == 'POST':
        data = request.get_json()
        schema = MateriasSchema()
        materia = schema.load(data)
        materia = schema.dump(materia.create())
        return make_response(jsonify({"materia": materia}),200)

@app.route('/materias/<int:id>', methods = ['PUT'])
def materias_2(id):
    data = request.get_json()
    materia = Materias.query.get(id)

    if 'clave_materia' in data:   materia.clave_materia = data['clave_materia']
    if 'nombre' in data:          materia.nombre = data['nombre']
    if 'creditos' in data:        materia.creditos = data['creditos']
    
    db.session.add(materia)
    db.session.commit()
    schema = ProfesoresSchema()
    result = schema.dump(schema)
    return make_response(jsonify({"materia": result}),200)

@app.route('/profesores', methods = ['GET', 'POST'])
def profesor():
    if request.method == 'GET':
        get_profesores= Profesores.query.all()
        profesores_schema = ProfesoresSchema(many=True)
        profesores = profesores_schema.dump(get_profesores)
        return make_response(jsonify({"profesor": profesores}))
    elif request.method == 'POST':
        data = request.get_json()
        schema = ProfesoresSchema()
        profesor = schema.load(data)
        result = schema.dump(profesor.create())
        return make_response(jsonify({"profesor": result}),200)

@app.route('/profesores/<int:id>', methods = ['PUT'])
def profesor_2(id):
    data = request.get_json()
    profesor = Profesores.query.get(id)
    
    if 'nombre' in data:        profesor.nombre = data['nombre']
    if 'ap_paterno' in data:    profesor.ap_paterno = data['ap_paterno']
    if 'ap_materno' in data:    profesor.ap_materno = data['ap_materno']
    if 'num_empleado' in data:  profesor.num_empleado = data['num_empleado']
    if 'password' in data:      profesor.password = data['password']
    if 'correo' in data:        profesor.correo = data['correo']        

    db.session.add(profesor)
    db.session.commit()
    schema = ProfesoresSchema()
    result = schema.dump(schema)
    return make_response(jsonify({"profesor": result}))

class Grupo(db.Model):
    __tablename__ = "grupos"
    id_grupo = db.Column(db.Integer, primary_key=True)
    numero_grupo = db.Column(db.String(30))
    id_profesor = db.Column(db.Integer, db.ForeignKey('ProfesoresSchema.id_profesor'))
    id_materia = db.Column(db.Integer, db.ForeignKey('MateriasSchema.id_materia'))
    id_periodo = db.Column(db.Integer, db.ForeignKey('periodo.id_periodo'))
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    def __init__(self, numero_grupo, id_profesor, id_materia, id_periodo):
        self.id_periodo  = id_periodo
        self.numero_grupo = numero_grupo
        self.id_materia = id_materia
        self.id_profesor = id_profesor
    def __repr__(self):
        return '' % self.id_grupo
    #db.create_all()

class GruposSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Grupo
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    id_grupo = auto_field(dump_only = True)
    numero_grupo = fields.String(required = True)
    id_profesor = fields.Number(required = True)
    id_periodo = fields.Number(required = True)
    id_materia = fields.Number(required = True)

@app.route('/grupos', methods = ['GET'])
def index():
	get_Grupos = Grupo.query.all()
	Grupos_schema = GruposSchema(many=True)
	grupos = Grupos_schema.dump(get_Grupos)
	return make_response(jsonify({"grupos": grupos}))

@app.route('/grupos', methods = ['POST'])
def create_grupo():
   data = request.get_json()
   Grupos_schema = GruposSchema()
   grupo = Grupos_schema.load(data)
   result = Grupos_schema.dump(grupo.create())
   return make_response(jsonify({"grupo": result}),200)

@app.route('/grupos/<id>', methods = ['PUT'])
def update_grupo_by_id(id):
   data = request.get_json()
   get_grupo = Grupo.query.get(id)
   if data.get('numero_grupo'):
       get_grupo.numero_grupo = data['numero_grupo']

   if data.get('id_profesor'):
       get_grupo.id_profesor = data['id_profesor']

   if data.get('id_periodo'):
       get_grupo.id_periodo = data['id_periodo']

   if data.get('id_materia'):
       get_grupo.id_materia= data['id_materia']   
       
   db.session.add(get_grupo)
   db.session.commit()
   grupo_schema = GruposSchema(only=['id_grupo', 'numero_grupo', 'id_profesor','id_periodo','id_materia'])
   grupo = grupo_schema.dump(get_grupo)
   return make_response(jsonify({"grupo": grupo}))

class AlumnoGrupo(db.Model):
   __tablename__ = "alumno_grupo"
   id_alumno_grupo = db.Column(db.Integer, primary_key=True)
   id_alumno = db.Column(db.Integer, db.ForeignKey('alumnos.id_alumno'))
   id_grupo = db.Column(db.Integer, db.ForeignKey('grupos.id_grupo'))
 
   def create(self):
     db.session.add(self)
     db.session.commit()
     return self
 
   def __init__(self, id_alumno_grupo, id_alumno, id_grupo):
       self.id_alumno_grupo  = id_alumno_grupo
       self.id_alumno = id_alumno
       self.id_grupo = id_grupo
 
   def __repr__(self):
       return '' % self.id_alumno_grupo

class AlumnoGrupoSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = AlumnoGrupo
        sqla_session = db.session
        include_relationships = True
        load_instance = True

    id_alumno_grupo = auto_field(dump_only = True)
    id_alumno = fields.String(required = True)
    id_grupo = fields.String(required = True)

@app.route('/alumno_grupo/<id>', methods = ['GET', 'PUT', 'DELETE'])
def AlumnoGrupoMethods1(id):
    if request.method == 'GET':
        alumno_grupo = AlumnoGrupo.query.get(id)
        return make_response(jsonify({"alumno_grupo": alumno_grupo.id_grupo}),200)
    elif request.method == 'PUT':
        data = request.get_json()
        alumno_grupo = AlumnoGrupo.query.get(id)
        alumno_grupo.id_grupo = data['id_grupo']
    elif request.method == 'DELETE':
        alumno_grupo = AlumnoGrupo.query.get(id)
        db.session.delete(alumno_grupo)
        db.session.commit()
        return MateriasSchema.jsonify(alumno_grupo)

@app.route('/alumno_grupo/<id>', methods = ['POST'])
def AlumnoGrupoMethods2(id):
    if request.method == 'POST':
        data = request.get_json()
        alumno_grupo = AlumnoGrupoSchema()
        AlumGrupo = alumno_grupo.load(data)
        result = alumno_grupo.dump(AlumGrupo.create())
        return make_response(jsonify({"alumno_grupo": result}),200)