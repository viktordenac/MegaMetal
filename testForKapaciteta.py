from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Define the Data model
class Data(db.Model):
    position = db.Column(db.String(100), primary_key=True)
    month = db.Column(db.String(20), primary_key=True)
    num_of_working_days = db.Column(db.Integer, nullable=False)
    num_of_working_hours = db.Column(db.Integer, nullable=False)
    num_of_employees = db.Column(db.Integer, nullable=False)
    available_hours = db.Column(db.Integer)
    needed_hours = db.Column(db.Integer, nullable=False)
    capacity_at = db.Column(db.Float)

    def __init__(self, position, month, num_of_working_days, num_of_working_hours, num_of_employees, needed_hours):
        self.position = position
        self.month = month
        self.num_of_working_days = num_of_working_days
        self.num_of_working_hours = num_of_working_hours
        self.num_of_employees = num_of_employees
        self.needed_hours = needed_hours
        self.calculate_available_hours()
        self.calculate_capacity_at()

    def calculate_available_hours(self):
        self.available_hours = self.num_of_employees * self.num_of_working_hours * self.num_of_working_days

    def calculate_capacity_at(self):
        if self.available_hours != 0:
            self.capacity_at = round((self.needed_hours / self.available_hours) * 100, 1)
        else:
            self.capacity_at = 0

# Initialize database tables
with app.app_context():
    db.create_all()

# Route to handle the index page
@app.route('/')
def index():
    datas = get_sample_data()  # Retrieve data from the database
    return render_template('kapaciteta.html', datas=datas)

# Route to handle the edited data submission
@app.route('/update', methods=['POST'])
def update_data():
    position = request.form['position']
    month = request.form['month']
    print(position, month)
    # Retrieve data from the database based on position and month
    data = Data.query.all()
    print(data)
    for d in data:
        if d.position == position and d.month == month:
            data = d
            break
    print(data)
    # Update data with form inputs
    data.num_of_working_days = request.form['num_of_working_days']
    data.num_of_working_hours = request.form['num_of_working_hours']
    data.num_of_employees = request.form['num_of_employees']
    data.needed_hours = request.form['needed_hours']
    # Recalculate dependent fields
    data.calculate_available_hours()
    data.calculate_capacity_at()
    # Commit changes to the database
    db.session.commit()
    return redirect(url_for('index'))

# Sample function to generate and retrieve sample data from the database
def get_sample_data():
    # Sample data for the entire year
    positions = ['Manager', 'Developer', 'Designer']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    sample_data = []

    for position in positions:
        for month in months:
            num_of_working_days = 22
            num_of_working_hours = 8
            num_of_employees = 10
            needed_hours = 300

            data = Data(position=position, month=month, num_of_working_days=num_of_working_days,
                        num_of_working_hours=num_of_working_hours, num_of_employees=num_of_employees,
                        needed_hours=needed_hours)
            sample_data.append(data)

    # Initialize a dictionary to hold data for each position
    position_data = {}

    # Populate the dictionary
    for data in sample_data:
        position = data.position
        if position not in position_data:
            position_data[position] = []
        position_data[position].append(data)

    return position_data

if __name__ == "__main__":
    app.run(debug=True)
