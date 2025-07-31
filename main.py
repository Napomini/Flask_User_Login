from flask import Flask, request
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host="dpg-d25oct63jp1c73a6775g-a",
        database="validate_user",
        user="root",
        password="n3Qi5ffvKEt7DaBPoiP7zWMcgo1EjF9x",
        port=5432
    )

# Create users table if not exists
def create_users_table():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        """)
    conn.commit()
    conn.close()

create_users_table()

@app.route('/')
def index():
    return '''
        <h2>User Login</h2>
        <form method="POST" action="/login">
            Username: <input type="text" name="username"><br><br>
            Password: <input type="password" name="password"><br><br>
            <input type="submit" value="Login">
        </form>
        <p>Don't have an account? <a href="/register">Register here</a></p>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password)
                )
            conn.commit()
            message = '<h3>Registration successful. <a href="/">Go to Login</a></h3>'
        except psycopg2.IntegrityError:
            conn.rollback()
            message = '<h3>Username already exists. <a href="/register">Try again</a></h3>'
        conn.close()
        return message
    else:
        return '''
            <h2>User Registration</h2>
            <form method="POST" action="/register">
                Username: <input type="text" name="username"><br><br>
                Password: <input type="password" name="password"><br><br>
                <input type="submit" value="Register">
            </form>
        '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
    conn.close()

    if user:
        return f"<h3>Welcome, {username}.</h3>"
    else:
        return "<h3>Invalid username or password. <a href='/'>Try again</a></h3>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
