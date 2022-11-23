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
        "Email" : user.Email,
        "Head" : user.Committee_Head_id
    }
    return jsonify(ans)

def getComplaint(complaint):
    comments = Section_Comments.query.filter_by(Complaint_id = complaint.Complaint_id).all()
    comment_list = []
    for comment in comments:
        section = Section.query.filter_by(Section_id = comment.Section_id).first()
        ans = {
            "user" : section.Name,
            "designation" : section.Designation,
            "comment" : comment.Comment,
            "email" : section.Email

        }
        comment_list.append(ans)
    ans={
        'id' : complaint.Complaint_id,
        "title" : complaint.Title,
        "description" : complaint.Description,
        "status" : complaint.Status,
        "date" : complaint.Date_posted,
        "type" : "Test",
        "remarks" : complaint.Remarks,
        "comments" : comment_list
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

@app.route('/authorize/<int:id>', methods=["PUT"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def authorize(current_user,role,id):
    if role == "committee head":
        section = Section.query.filter_by(User_id = id).first()
        section.is_Authorized =True
        db.session.commit()
        return jsonify({"Response" : "User Authorized Successfully"}),200

        
@app.route('/rmUser/<int:id>', methods=["DELETE"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def removeUser(current_user,role,id):
     if role == "committee head":
        section = Section.query.filter_by(User_id = id).first()
        db.session.delete(section)
        db.session.commit()
        return jsonify({"Response" : "User Removed"}),200

@app.route('/changeStatus/<int:id>', methods=["PUT"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def changeStatus(current_user,role,id):
    data = request.json
    if role == "committee head":
        complaint = Complaints.query.filter_by(Complaint_id = id).first()
        complaint.Status = data.status
        db.session.commit()
        return jsonify({"Response" : "Complaint Status Updated"}),200

@app.route('/complaint', methods=["POST"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def post_complaint(current_user,role):
    data = request.json
    now =datetime.now()
    date = now.strftime("%d/%m/%Y")
    new_complaint = Complaints(
        Title = data.title,
        Description = data.description,
        Date_posted = time,
        Remarks = "",
        Status = "Open",
        Location = data.location,
        User_id = current_user.id,
        Committee_Head_id = 1
        )
    db.session.add(new_complaint)
    db.session.commit()
    return jsonify({"Response" : "Complaint Added Successfully"}),200

@app.route('/complaints', methods=["GET"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def get_complaints(current_user,role):
    if role == "section head":
        complaints = Complaints.query.filter_by(Committee_Head_id = current_user.Head).all()
    elif role == "committee head":
        complaints = Complaints.query.filter_by(Committee_Head_id = current_user.id).all()
    else:
        complaints = Complaints.query.filter_by(User_id = current_user.id).all()
    ans = []
    for complaint in complaints:
        ans.append(getComplaint(complaint))
    return jsonify({"Response" : "Success", "Complaints" : ans}),200

@app.route('/complaint/<int:id>', methods=["GET","PUT","DELETE"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def get_complaint(current_user,role,id):
    if request.method=="GET":
        complaint = Complaints.query.filter_by(Complaint_id = id).first()
        return getComplaint(complaint)

    if request.method=="PUT":
        data = request.json
        complaint=Complaints.query.filter_by(Complaint_id = id).first()
        complaint.Title = data.title
        complaint.Description = data.description
        complaint.Location = data.location
        db.session.commit()
        return jsonify({"Response" : "Complaint Updated"}),200

    if request.method=="DELETE":
        complaint=Complaints.query.filter_by(Complaint_id = id).first()
        db.session.delete(complaint)
        db.session.commit()
        return jsonify({"Response" : "Complaint Deleted"}),200

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
            return jsonify({"token": token}),200
        else:
            return jsonify({"Response" : "Incorrect Password"}),403

    except:
        return jsonify({"Response" : "Login Failed"}),400

@app.route('/comment/<int:id>', methods=["POST"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def comment(current_user,role,id):
    data = request.json
    if role == "section head":
        new_comment = Section_Comments(
            Section_id=current_user.id,
            Complaint_id=id,
            Comment=data.comment
        )
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"Response" : "New Comment Added"}),200

@app.route('/resolve/<int:id>', methods=["PUT"])
@cross_origin(supports_credentials=True,headers=['Content-Type'])
@token_required
def resolve(current_user,role,id):
    data = request.json
    if role == "committee head":
        complaint = Complaints.query.filter_by(Complaint_id = id).first()
        complaint.Status = "Resolved"
        complaint.Remarks = data.remarks
        db.session.commit()
        return jsonify({"Response" : "Complaint Resolved"}),200

@app.route("/test")
@cross_origin(supports_credentials=True,headers=['Content-Type'])
def test():
    user = Committee_Head.query.filter_by(Email = "Test@gmail.com").first()
    return getCommitteeHead(user)