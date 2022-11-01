import re
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
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

    id_alumno = fields.Number(dump_only = True)
    matricula = fields.String(required = True)
    ap_paterno = fields.String(required = True)
    ap_materno = fields.String(required = True)
    nombre = fields.String(required = True)


class Materias(db.Model):
   __tablename__ = "materias"
   id_materia = db.Column(db.Integer, primary_key=True)
   clave_materia = db.Column(db.String(6))
   nombre = db.Column(db.String(30))
   creditos = db.Column(db.SmallInteger)

   def create(self):
     db.session.add(self)
     db.session.commit()
     return self
 
   def __init__(self, clave_materia, nombre, creditos):
       self.clave_materia  = clave_materia
       self.nombre = nombre
       self.creditos = creditos
 
   def __repr__(self):
       return '' % self.id_materia


class MateriasSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Materias
        sqla_session = db.session

    id_materia = fields.Number(dump_only = True)
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
 
   def __init__(self, nombre, ap_paterno, ap_materno, num_empleado, password, correo):
        self.nombre = nombre
        self.ap_paterno = ap_paterno
        self.ap_materno = ap_materno
        self.num_empleado = num_empleado
        self.password = password
        self.correo = correo

   def __repr__(self):
       return '' % self.id_profesor


class ProfesoresSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Profesores
        sqla_session = db.session

    id_profesor = fields.Number(dump_only = True)
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
        materias_schema = AlumnosSchema(many=True)
        materias = materias_schema.dump(get_materias)
        return make_response(jsonify({"materia": materias}))
    elif request.method == 'POST':
        data = request.get_json()
        schema = MateriasSchema()
        materia = schema.load(data)
        result = schema.dump(materia.create())
        return make_response(jsonify({"materia": result}),200)

@app.route('/materias/<id>', methods = ['PUT', 'DELETE'])
def materias_2(id):
    if request.method == 'PUT':
        materia = Materias.query.get(id)

        materia.clave_materia = request.json('clave_materia')
        materia.nombre = request.json('nombre')
        materia.creditos = request.json('creditos')

        db.session.commit()
        return make_response(jsonify({"materia": materia}))
    elif request.method == 'DELETE':
        materia = Materias.query.get(id)
        db.session.delete(materia)
        db.session.commit()
        return MateriasSchema.jsonify(materia)

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

@app.route('/profesores/<id>', methods = ['PUT', 'DELETE'])
def profesor_2(id):
    if request.method == 'PUT':
        profesor = Profesores.query.get(id)

        profesor.nombre = request.json('nombre')
        profesor.ap_paterno = request.json('ap_paterno')
        profesor.num_empleado = request.json('num_empleado')
        profesor.password = request.json('password')
        profesor.correo = request.json('correo')

        if request.json('ap_materno'): 
            profesor.ap_materno = request.json('ap_materno')

        db.session.commit()
        return make_response(jsonify({"profesor": profesor}))
    elif request.method == 'DELETE':
        profesor = Profesores.query.get(id)
        db.session.delete(profesor)
        db.session.commit()
        return ProfesoresSchema.jsonify(profesor)
