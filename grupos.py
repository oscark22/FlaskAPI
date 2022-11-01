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

class Grupos(db.Model):
    __tablename__ = "grupos"
    id_grupo = db.Column(db.Integer, primary_key=True)
    numero_grupo = db.Column(db.String(30))
    id_profesor = db.Column(db.Integer, db.ForeignKey('profesores.id_profesor'))
    id_materia = db.Column(db.Integer, db.ForeignKey('materia.id_materia'))
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
        model = Grupos
        sqla_session = db.session
    id_grupo = fields.Number(dump_only = True)
    numero_grupo = fields.String(required = True)
    id_profesor = fields.Number(required = True)
    id_periodo = fields.Number(required = True)
    id_materia = fields.Number(required = True)

@app.route('/grupos', methods = ['GET'])
def index():
	get_Grupos = Grupos.query.all()
	Grupos_schema = GruposSchema(many=True)
	Grupos = Grupos_schema.dump(get_Grupos)
	return make_response(jsonify({"grupos": Grupos}))

@app.route('/grupos', methods = ['POST'])
def create_grupo():
   data = request.get_json()
   Grupos_schema = GruposSchema()
   grupo = Grupos_schema.load(data)
   result = Grupos_schema.dump(grupo.create())
   return make_response(jsonify({"grupo": result}),200)

@app.route('/grupos/' + id, methods = ['PUT'])
def update_grupo_by_id(id):
   data = request.get_json()
   get_grupo = Grupos.query.get(id)
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