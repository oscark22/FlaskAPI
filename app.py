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
    result = schema.dump(materia)
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
    result = schema.dump(profesor)
    return make_response(jsonify({"profesor": result}))


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
        get_alumno_grupo = AlumnoGrupo.query.get(id)
        Alumno_Grupo_Schema = AlumnoGrupoSchema()
        alumno_grupo = Alumno_Grupo_Schema.dump(get_alumno_grupo)
        return make_response(jsonify({"alumno_grupo": alumno_grupo}))
    elif request.method == 'PUT':
        data = request.get_json()
        alumno_grupo = AlumnoGrupo.query.get(id)
        if data.get('id_grupo'):
            alumno_grupo.id_grupo = data['id_grupo']
        if data.get('id_alumno'):
            alumno_grupo.id_alumno = data['id_alumno']
        db.session.add(alumno_grupo)
        db.session.commit()
        AlumnoGrupo_schema = AlumnoGrupoSchema(only=['id_alumno','id_grupo'])
        result = AlumnoGrupo_schema.dump(alumno_grupo)
        return make_response(jsonify({"asistencia": result}))
    elif request.method == 'DELETE':
        alumno_grupo = AlumnoGrupo.query.get(id)
        db.session.delete(alumno_grupo)
        db.session.commit()
        return make_response("",204)

@app.route('/alumno_grupo/<id>', methods = ['POST'])
def AlumnoGrupoMethods2(id):
    if request.method == 'POST':
        data = request.get_json()
        alumno_grupo = AlumnoGrupoSchema()
        AlumnoGrupo = alumno_grupo.load(data)
        result = alumno_grupo.dump(AlumnoGrupo.create())
        return make_response(jsonify({"alumno_grupo": result}),200)

class Asistencia(db.Model):
    _tablename_ = "asistencia"
    id_asistencia = db.Column(db.Integer, primary_key = True)
    fecha = db.Column(db.Date)
    id_tipo_asistencia = db.Column(db.Integer)
    id_alumno = db.Column(db.Integer)
    id_horario = db.Column(db.Integer)
    
    def create(self):
     db.session.add(self)
     db.session.commit()
     return self

    def _init_(self, id_asistencia, fecha, id_tipo_asistencia, id_alumno, id_horario):
     self.id_asistencia  = id_asistencia
     self.fecha = fecha
     self.id_tipo_asistencia = id_tipo_asistencia
     self.id_alumno = id_alumno
     self.id_horario = id_horario    

    def _repr_(self):
        return '' % self.id_alumno  
  
class AsistenciaSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
      model = Asistencia
      sqla_session = db.session
    
    id_asistencia = fields.Number(dump_only=True)
    fecha = fields.Date(required=True)
    id_tipo_asistencia = fields.Number(required=True)
    id_alumno = fields.Number(required=True)
    id_horario = fields.Number(required=True)

@app.route('/asistencia', methods = ['GET'])
def asistencia():
  get_asistencia = Asistencia.query.all()
  Asistencia_schema = AsistenciaSchema(many = True)
  asistencia = Asistencia_schema.dump(get_asistencia)
  return make_response(jsonify({"asistencia": asistencia}))

@app.route('/asistencia', methods = ['POST'])
def create_asistencia():
  data = request.get_json()
  Asistencia_schema = AsistenciaSchema()
  asistencia = Asistencia_schema.load(data)
  result = Asistencia_schema.dump(asistencia).create()
  return make_response(jsonify({"asistencia": result}),200)


@app.route('/asistencia/<id>', methods = ['PUT'])
def update_asistencia_by_id(id):
  data = request.get_json()
  get_asistencia = Asistencia.query.get(id)
  if data.get('id_asistencia'):
    get_asistencia.fecha = data['fecha']
  if data.get('fecha'):
    get_asistencia.id_tipo_asistencia = data['id_tipo_asistencia']
  if data.get('id_tipo_asistencia'):
    get_asistencia.id_alumno = data['id_alumno']
  if data.get('id_horario'):
    get_asistencia.price= data['id_horario']   
  db.session.add(get_asistencia)
  db.session.commit()
  Asistencia_schema = AsistenciaSchema(only=['id_asistencia', 'fecha', 'id_tipo_asistencia','id_alumno','id_horario'])
  asistencia = Asistencia_schema.dump(get_asistencia)
  return make_response(jsonify({"asistencia": asistencia}))

@app.route('/asistencia/<id>', methods = ['DELETE'])
def delete_asistencia_by_id(id):
  get_asistencia = Asistencia.query.get(id)
  db.session.delete(get_asistencia)
  db.session.commit()
  return make_response("",204)



class Periodo(db.Model):
    __tablename__ = "periodo"
    id_periodo = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(20))
    inicio = db.Column(db.Date())
    final = db.Column(db.Date())

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self,id_periodo,nombre,inicio,final):
        self.id_periodo = id_periodo
        self.nombre = nombre
        self.inicio = inicio
        self.final = final
    def __repr__(self):
        return '' % self.id_periodo

class PeriodoSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Periodo
        sqla_session = db.session

    id_periodo = fields.Number(dump_only=True)
    nombre = fields.String(required=True)
    inicio = fields.Date(required=True)
    final = fields.Date(required=True)

@app.route('/periodo', methods = ['GET'])
def periodo():
    get_periodo = Periodo.query.all()
    periodo_schema = PeriodoSchema(many = True)
    periodo = periodo_schema.dump(get_periodo)
    return make_response(jsonify({"periodo": periodo}))

@app.route('/periodo', methods = ['POST'])
def create_periodo():
    data = request.get_json()
    periodo_schema = PeriodoSchema()
    periodo = periodo_schema.load(data)
    result = periodo_schema.dump(periodo.create())
    return make_response(jsonify({"periodo": result}),200)

@app.route('/periodo/<id>', methods = ['PUT'])
def update_periodo_by_id(id):
    data = request.get_json()
    get_periodo = Periodo.query.get(id)
    if data.get('id_periodo'):
        get_periodo.id_periodo = data['id_periodo']
    if data.get('nombre'):
        get_periodo.nombre = data['nombre']
    if data.get('inicio'):
        get_periodo.inicio = data['inicio']
    if data.get('final'):
        get_periodo.final= data['final']   
    db.session.add(get_periodo)
    db.session.commit()
    periodo_schema = PeriodoSchema(only=['id_periodo', 'nombre', 'inicio','final'])
    periodo = periodo_schema.dump(get_periodo)
    return make_response(jsonify({"periodo": periodo}))

@app.route('/periodo/<id>', methods = ['DELETE'])
def delete_periodo_by_id(id):
  get_periodo = Periodo.query.get(id)
  db.session.delete(get_periodo)
  db.session.commit()
  return make_response("",204)


class Grupo(db.Model):
    __tablename__ = "grupos"
    id_grupo = db.Column(db.Integer, primary_key=True)
    numero_grupo = db.Column(db.String(30))
    id_profesor = db.Column(db.Integer, db.ForeignKey(Profesores.id_profesor))
    id_materia = db.Column(db.Integer, db.ForeignKey(Materias.id_materia))
    id_periodo = db.Column(db.Integer, db.ForeignKey(Periodo.id_periodo))
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
	Grupos_schema = GruposSchema(many = True)
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

@app.route('/grupos/<id>', methods = ['DELETE'])
def delete_grupos_by_id(id):
  get_grupo = Grupo.query.get(id)
  db.session.delete(get_grupo)
  db.session.commit()
  return make_response("", 204)


class Horarios(db.Model):
    tablename = "horarios"
    id_horario = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.Time)
    hora_final = db.Column(db.Time)
    dia = db.Column(db.Integer)
    id_grupo = db.Column(db.Integer, db.ForeignKey(Grupo.id_grupo))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    def init(self,id_horario,hora_inicio,hora_final,dia,id_grupo):
        self.id_horario = id_horario
        self.hora_inicio = hora_inicio
        self.hora_final = hora_final
        self.dia = dia
        self.id_grupo = id_grupo
    def repr(self):
        return '' % self.id_horario

class HorariosSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Horarios
        sqla_session = db.session
        include_relationships = True
        load_instance = True
    id_horario = auto_field(dump_only=True)
    hora_inicio = fields.Time(required=True)
    hora_final = fields.Time(required=True)
    dia = fields.Number(required = True)
    id_grupo = fields.Number(required = True)

@app.route('/horarios', methods = ['GET'])
def horarios():
    get_horarios = Horarios.query.all()
    horarios_schema = HorariosSchema(many=True)
    horarios = horarios_schema.dump(get_horarios)
    return make_response(jsonify({"horarios": horarios}))

@app.route('/horarios', methods = ['POST'])
def create_horarios():
    data = request.get_json()
    horarios_schema = HorariosSchema()
    horarios = horarios_schema.load(data)
    result = horarios_schema.dump(horarios.create())
    return make_response(jsonify({"horarios": result}),200)

@app.route('/horarios/<id>', methods = ['PUT'])
def update_horarios_by_id(id):
    data = request.get_json()
    get_horarios = Horarios.query.get(id)
    if data.get('id_horario'):
       get_horarios.id_horario = data['id_horario']
    if data.get('hora_inicio'):
       get_horarios.hora_inicio = data['hora_inicio']
    if data.get('hora_final'):
       get_horarios.hora_final= data['hora_final']
    if data.get('dia'):
       get_horarios.dia= data['dia']
    if data.get('id_grupo'):
       get_horarios.id_grupo= data['id_grupo']     
    db.session.add(get_horarios)
    db.session.commit()
    horarios_schema = HorariosSchema(only=['id_horario', 'hora_inicio','hora_final','dia','id_grupo'])
    horarios = horarios_schema.dump(get_horarios)
    return make_response(jsonify({"horarios": horarios}))

@app.route('/horarios/<id>', methods = ['DELETE'])
def delete_horarios_by_id(id):
   get_horarios = Horarios.query.get(id)
   db.session.delete(get_horarios)
   db.session.commit()
   return make_response("", 204)
