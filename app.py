from flask import Flask, render_template, request, redirect, session, url_for
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root@1234',
        db='employee_management',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username=%s AND password=%s', (username, password))
            user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect('/employees')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/employees')
def employees():
    if 'username' not in session:
        return redirect('/')
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM employees')
        employees = cursor.fetchall()
    conn.close()
    return render_template('list.html', employees=employees)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        salary = request.form['salary']
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO employees (name, email, department, salary) VALUES (%s, %s, %s, %s)',
                           (name, email, department, salary))
            conn.commit()
        conn.close()
        return redirect('/employees')
    return render_template('add.html')

@app.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if 'username' not in session:
        return redirect('/')
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM employees WHERE id=%s', (id,))
        employee = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        salary = request.form['salary']
        with conn.cursor() as cursor:
            cursor.execute('UPDATE employees SET name=%s, email=%s, department=%s, salary=%s WHERE id=%s',
                           (name, email, department, salary, id))
            conn.commit()
        conn.close()
        return redirect('/employees')
    conn.close()
    return render_template('edit.html', employee=employee)

@app.route('/employee/delete/<int:id>')
def delete_employee(id):
    if 'username' not in session:
        return redirect('/')
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM employees WHERE id=%s', (id,))
        conn.commit()
    conn.close()
    return redirect('/employees')

if __name__ == '__main__':
    app.run(debug=True)
