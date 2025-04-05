from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

# ✅ Get DATABASE_URL from Render environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

# ✅ Only initialize DB when running locally (not on Render)
@app.before_first_request
def init_db():
    if DATABASE_URL:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS names (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL
                    );
                """)
                conn.commit()
        except Exception as e:
            print("DB Initialization Error:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        if DATABASE_URL:
            try:
                with psycopg2.connect(DATABASE_URL) as conn:
                    cur = conn.cursor()
                    cur.execute("INSERT INTO names (name) VALUES (%s)", (name,))
                    conn.commit()
            except Exception as e:
                return f"Database error: {e}"
        return redirect('/view_names')
    return render_template('index.html')

@app.route('/view_names')
def view_names():
    names = []
    if DATABASE_URL:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM names")
                rows = cur.fetchall()
                names = [row[0] for row in rows]
        except Exception as e:
            return f"Database error: {e}"
    return render_template('view.html', names=names)

if __name__ == '__main__':
    app.run(debug=True)
