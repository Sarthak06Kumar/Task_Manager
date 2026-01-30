from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

# ===============================
# Flask App Setup
# ===============================

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

# ===============================
# Home Route
# ===============================

@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ===============================
# Register
# ===============================

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not username or not email or not password:
            msg = 'Please fill all fields!'
        else:
            cursor.execute(
                'INSERT INTO users VALUES (NULL, %s, %s, %s)',
                (username, email, password)
            )
            mysql.connection.commit()
            return redirect(url_for('login'))

    return render_template('register.html', msg=msg)

# ===============================
# Login
# ===============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE email = %s AND password = %s',
            (email, password)
        )
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect email or password!'

    return render_template('login.html', msg=msg)

# ===============================
# Logout
# ===============================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===============================
# Dashboard (Read Tasks)
# ===============================

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        'SELECT * FROM tasks WHERE user_id = %s',
        (session['id'],)
    )
    tasks = cursor.fetchall()

    return render_template('dashboard.html', tasks=tasks)

# ===============================
# Add Task
# ===============================

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        'INSERT INTO tasks VALUES (NULL, %s, %s, %s)',
        (session['id'], title, description)
    )
    mysql.connection.commit()

    return redirect(url_for('dashboard'))

# ===============================
# Edit Task
# ===============================

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        cursor.execute(
            'UPDATE tasks SET title=%s, description=%s WHERE id=%s AND user_id=%s',
            (title, description, id, session['id'])
        )
        mysql.connection.commit()
        return redirect(url_for('dashboard'))

    cursor.execute(
        'SELECT * FROM tasks WHERE id=%s AND user_id=%s',
        (id, session['id'])
    )
    task = cursor.fetchone()

    return render_template('edit_task.html', task=task)

# ===============================
# Delete Task
# ===============================

@app.route('/delete_task/<int:id>')
def delete_task(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        'DELETE FROM tasks WHERE id=%s AND user_id=%s',
        (id, session['id'])
    )
    mysql.connection.commit()

    return redirect(url_for('dashboard'))

# ===============================
# Run Server
# ===============================

if __name__ == '__main__':
    app.run(debug=True)
