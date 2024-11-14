import os
from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,Integer,String,Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

app = Flask(__name__)
base = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'  #change this in production
# Looking to send emails in production? Check out our Email API/SMTP product!
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '820bc56b0aded2'
app.config['MAIL_PASSWORD'] = '7eddaf9bc1866c'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database is created!!")

@app.cli.command('db_drop_database')
def db_drop():
    db.drop_all()
    print('Database dropped')

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',planet_type='Class D', home_star='Sol', mass=3.258e23, radius=1516, distance=35)
    venus = Planet(planet_name='Venus',planet_type='Class K', home_star='Sol', mass=8.259e23, radius=1316, distance=37)
    earth = Planet(planet_name='Earth',planet_type='Class M', home_star='Sol', mass=5.978e23, radius=3959, distance=92)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    user1 = User(first_name='sophie', last_name= 'muchiri', email='soph@gmail', password='pass@word')

    db.session.add(user1)
    db.session.commit()
    print('database seeded and committed!')


#getting planets using http get from the api
@app.route('/planets',methods=['GET'])
def planets():
    planet_list = Planet.query.all()
    result = planets_schema.dump(planet_list)
    return jsonify(result)

@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'),409
    
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"),201

    
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']


    else:
        email = request.form['email']
        password = request.form['password']

    
    test = User.query.filter_by(email=email, password=password).first()

    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login successed", access_token=access_token)
    
    else:
        return jsonify(message="Bad email or password"),401


@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email:str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Your PLanetary API password is " + user.password, sender="admin@planetary-api.com", recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to" + email)
    
    else:
        return jsonify("email doesn't exist"),401




#DATABASE MODELS
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String,unique=True)
    password = db.Column(db.String)

    def __repr__(self):
        return f"User {self.first_name} {self.last_name}"

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = db.Column(db.Integer,primary_key=True)
    planet_name = db.Column(db.String)
    planet_type = db.Column(db.String)
    home_star = db.Column(db.String)
    mass = db.Column(db.Float)
    radius = db.Column(db.Float)
    distance = db.Column(db.Float)


    def __repr__(self):
        return f"Planet {self.planet_name} pf planet type{self.planet_type}"


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name','planet_type','home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)


    





@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Planetary API'),200


@app.route('/not_found')
def not_found():
    return jsonify(message='Resource not found'),400


# using request objects
@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message='Sorry' + name +'you are not old enough'),401
    else:
        return jsonify(message=f"Welcome {name} you are old enough"),200


# using parameter rules
@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name:str, age:int):
    if age < 18:
        return jsonify(message='Sorry' + name +'you are not old enough'),401
    else:
        return jsonify(message=f"Welcome {name} you are old enough"),200



if __name__ == '__main__':
    app.run()