# Import necessary libraries and modules
from flask import Flask, render_template, url_for, request, redirect  # Flask components for routing, templates, and handling requests
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for database ORM
from datetime import datetime  # For handling date and time

# Initialize SQLAlchemy without linking it to the app yet
db = SQLAlchemy()

# Create the Flask application instance
app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Define a database model for storing tasks
class Todo(db.Model):  # Inherit from SQLAlchemy's base model class
    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key column (unique ID for each task)
    content = db.Column(db.String(200), nullable=False)  # Task description, must not be null
    completed = db.Column(db.Integer, default=0)  # Status of task (0 = incomplete, 1 = complete)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of task creation, default to current time

    # String representation for debugging purposes
    def __repr__(self):
        return '<Task %r>' % self.id  # Returns the task ID for easier identification during debugging
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.id

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()

# Define the route and logic for the homepage
@app.route('/', methods=['POST', 'GET'])  # Allow POST (form submission) and GET (load page) methods
def index():
    if request.method == 'POST':  # If the request is a POST (user submits a form)
        task_content = request.form['content']  # Get the task content from the form input
        new_task = Todo(content=task_content)  # Create a new Todo object with the input content
        
        try:
            db.session.add(new_task)  # Add the new task to the database session
            db.session.commit()  # Commit the transaction to save the task
            return redirect('/')  # Redirect to the homepage to show the updated task list
        except:
            return "There was an issue adding your task."  # Error message if something goes wrong

    else:  # If the request is a GET (user loads the page)
        tasks = Todo.query.order_by(Todo.date_created).all()  # Query all tasks, ordered by creation date
        users = User.query.all()
        return render_template('index.html', tasks=tasks, users=users)  # Render the index.html template and pass tasks to it


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'there was a problem deleting'
    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'there was a problem updating'
    else:
        return render_template('update.html', task=task)
    
@app.route('/user/', methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)

        try:
            next_user = User.query.order_by(User.id.desc()).first()
            if next_user:
                db.session.delete(next_user)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/') 
        except:
            return "error adding new user"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()  # Query all tasks, ordered by creation date
        users = User.query.all()
        return render_template('index.html', tasks=tasks, users=users)  # Render the index.html template and pass tasks to it

# Run the application only if this script is executed directly
if __name__ == "__main__":
    init_db()
    app.run(debug=True)  # Start the Flask development server with debugging enabled
