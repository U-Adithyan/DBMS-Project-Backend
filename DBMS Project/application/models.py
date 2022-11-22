from .database import db

class User(db.Model):
    __tablename__="User"
    User_id=db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    Name=db.Column(db.String,nullable=False)
    Department=db.Column(db.String,nullable=False)
    Email=db.Column(db.String,unique=True,nullable=False)
    Password=db.Column(db.String,nullable=False)
    Complaints=db.relationship("Complaints",cascade="all, delete-orphan")

class Complaints(db.Model):
    __tablename__="Complaints"
    Complaint_id=db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    Title=db.Column(db.String,nullable=False)
    Description=db.Column(db.String,nullable=False)
    Date_posted=db.Column(db.String,nullable=False)
    Remarks=db.Column(db.String)
    Status=db.Column(db.String,nullable=False)
    Location=db.Column(db.String)
    User_id=db.Column(db.Integer,db.ForeignKey("User.User_id"))
    Committee_Head_id=db.Column(db.Integer,db.ForeignKey("Committee_Head.Committee_Head_id"))
    Comments=db.relationship("Section_Comments",cascade="all, delete-orphan")

class Committee_Head(db.Model):
    __tablename__="Committee_Head"
    Committee_Head_id=db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    Name=db.Column(db.String,nullable=False)
    Type=db.Column(db.String,nullable=False)
    Email=db.Column(db.String,unique=True,nullable=False)
    Password=db.Column(db.String,nullable=False)
    Complaints=db.relationship("Complaints",cascade="all, delete-orphan")
    
class Section(db.Model):
    __tablename__="Section"
    Section_id=db.Column(db.Integer,autoincrement=True,unique=True,primary_key=True)
    Name=db.Column(db.String,nullable=False)
    is_Authorized=db.Column(db.Boolean,nullable=False)
    Designation=db.Column(db.String,nullable=False)
    Email=db.Column(db.String,unique=True,nullable=False)
    Password=db.Column(db.String,nullable=False)
    Committee_Head_id=db.Column(db.Integer,db.ForeignKey("Committee_Head.Committee_Head_id"))
    Comments=db.relationship("Section_Comments",cascade="all, delete-orphan")
    
class Section_Comments(db.Model):
    __tablename__="Section_Comments"
    Section_id=db.Column(db.Integer,db.ForeignKey("Section.Section_id"),primary_key=True)
    Complaint_id=db.Column(db.Integer,db.ForeignKey("Complaints.Complaint_id"),primary_key=True)
    Comment=db.Column(db.String,nullable=False)

