from flask import Flask,request,jsonify,make_response
from flask import current_app as app
import jwt
from  functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from datetime import datetime
from .database import *
from .models import *

def getUser(user):
    ans = {
        "role" : "User",
        "id" : user.User_id,
        "Name" : user.Name,
        "Department" : user.Department,
        "Email" : user.Email,
    }
    return jsonify(ans)

def getCommitteeHead(user):
    ans = {
        "role" : "CommitteeHead",
        "id" : user.Committee_Head_id,
        "Name" : user.Name,
        "Type" : user.Type,
        "Email" :user.Email,
    }
    return jsonify(ans)

def getSectionHead(user):
    ans = {
        "role" : "SectionHead",
        "id" : user.Section_id,
        "Name" : user.Name,
        "is_Authorized" : user.is_Authorized,
        "Designation" : user.Designation,
        "Email" : user.Email
    }
    return jsonify(ans)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token=None
        if 'x-access-token' in request.headers:
            token=request.headers['x-access-token']

        if not token:
            return make_response("Unauthorized access",401)

        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
            if data["role"] == "section head":
                current_user = Section.query.filter_by(User_id = data["ID"]).first()
            elif data["role"] == "committee head":
                current_user = Committee_Head.query.filter_by(Committee_Head_id = data["ID"]).first()
            else:
                current_user = User.query.filter_by(Section_id = data["ID"]).first()

            role = data ["role"]
        except:
            return make_response("Could not Verify",401,{"Auth_Status":"invalid"})

        return f(current_user,role,*args,**kwargs)
    return decorated

@app.route('/user/current', methods=["GET"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def get_current_user(current_user,role):
    if role == "section head":
        return getSectionHead(current_user)
    elif role == "committee head":
        return getCommitteeHead(current_user)
    else:
        return getUser(current_user)


@app.route("/signup",methods=["POST"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
def signUp():
    try:
        data = request.json
        pwd = generate_password_hash(data["password"],method='sha256')
        if data["role"] == "section head":
            new_user = Section(
                Name=data["name"],
                is_Authorized=False,
                Designation=data["designation"],
                Email=data["email"],
                Password=pwd,
                Committee_Head_id= 1)
        else:
            new_user = User(
                Name=data["name"],
                Department=data["department"],
                Email=data["email"],
                Password=pwd)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"Response" : "User Created Successfully"}),200
    except:
        return jsonify({"Response" : "User Creation Failed"}),400



@app.route("/login",methods=["POST"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
def login():
    try:
        data = request.json

        if data["role"] == "section head":
            user = Section.query.filter_by(Email = data["email"]).first()
        elif data["role"] == "committee head":
            user = Committee_Head.query.filter_by(Email = data["email"]).first()
        else:
            user = User.query.filter_by(Email = data["email"]).first()

        if data["role"] == "section head":
            id = user.Section_id
        elif data["role"] == "committee head":
            id = user.Committee_Head_id
        else:
            id = user.User_id

        if user is None:
            return jsonify({"Response" : "User does not exist"}),404
        
        if check_password_hash(user.Password, data["password"]):
            token=jwt.encode({"Role":data['role'],"ID":id},app.config['SECRET_KEY'])
            return jsonify({"Response" : "Login Success", "token":token.decode('UTF-8')}),200
        else:
            return jsonify({"Response" : "Incorrect Password"}),403

    except:
        return jsonify({"Response" : "Login Failed"}),400


@app.route("/test")
@cross_origin(supports_credentials=True,headers=['Content-Type'])
def test():
    user = Committee_Head.query.filter_by(Email = "Test@gmail.com").first()
    return getCommitteeHead(user)