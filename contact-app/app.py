from flask import Flask,render_template,redirect,flash,request,url_for
from flask_login import login_required,LoginManager,login_user,logout_user,UserMixin
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/contact'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy()
db.init_app(app)


login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key = True,autoincrement = True)
    username = db.Column(db.String(265),nullable = False)
    password = db.Column(db.String(265),nullable = False)

    def __repr__(self):
        return f'<User {self.id}'

class Contact(db.Model):
    contact_id = db.Column(db.Integer(),primary_key = True,autoincrement = True)
    name = db.Column(db.String(265),nullable = False)
    phone_no = db.Column(db.Integer(),nullable = False)
    address = db.Column(db.String(),)

    def __repr__(self):
        return f'<Contact {self.contact_id}'

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']

        existing_user = User.query.filter(User.username==username).first()
        if existing_user:
            flash('Username in use')
            return redirect(url_for('register'))
        new_user = User(username=username,password=password)
        
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registration Successful','success')
        return redirect(url_for('contact'))
    return render_template('register.html')

@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        current_user = User.query.filter_by(username=username,password=password).first()
        if current_user:
            login_user(current_user)
            flash('Login Successful','success')
            return redirect(url_for('contact'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/contact',methods = ['POST','GET'])
@login_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        phone_no = request.form['phone_no']
        address = request.form['address']

        new_contact = Contact(name=name,phone_no=phone_no,address=address)
        db.session.add(new_contact)
        db.session.commit()
    contacts = Contact.query.all()
    return render_template('contact.html',contacts=contacts)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/delete_contact/<int:contact_id>',methods = ['GET','POST'])
def delete_contact(contact_id):
    contact_to_delete = Contact.query.get(contact_id)
    if contact_to_delete:
        db.session.delete(contact_to_delete)
        db.session.commit()
    return redirect(url_for('contact'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
