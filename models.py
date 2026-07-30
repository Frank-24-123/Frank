from extensions import db

class Upload_System(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    Note_sharing = db.Column(db.String(200), nullable=True)
    Note_writing = db.Column(db.String(500), nullable=True)
    Assignment_Sharing = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(100), nullable=True)
    Comments = db.Column(db.String(500), nullable=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    First_Name = db.Column(db.String(20), nullable=False)
    Last_Name =db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    Confirm_password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Student('{self.First_Name}', '{self.Last_Name}', '{self.Email}')"
    

class feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(20), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Message = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return f"feedback('{self.Name}', '{self.Email}', '{self.Message}')"