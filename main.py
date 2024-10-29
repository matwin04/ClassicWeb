from flask import *
import sqlite3
import os
#FLASK CONFIG
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files'
app.config['DATABASE'] = 'classicweb.db'
app.config['SCHEMA'] = 'init.sql'
app.secret_key = 'supersecretkey'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#initalize DB
def init_db():
    if not os.path.exists(app.config['DATABASE']):
        print("Database does not exist. Creating and initializing...")
        with sqlite3.connect(app.config['DATABASE']) as conn:
            with open(app.config['SCHEMA'], 'r') as f:
                conn.executescript(f.read())  # Execute all SQL commands from init.sql
            print("Database created and initialized successfully.")
    else:
        print("Database already exists.") 
def getDB():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
    return conn

# PAGES
@app.route('/')
def index():
    conn = getDB()
    files = conn.execute("SELECT * FROM files").fetchall()
    conn.close()
    return render_template(
        "index.html",
        files=files,
    )

#UPLOAD
@app.route('/upload',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("NO FILE PART")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("NO SELECTED FILE")
            return redirect(request.url)
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            conn = getDB()
            conn.execute("INSERT INTO files (filename,filepath) VALUES (?,?)",(filename,filepath))
            conn.commit()
            conn.close()
            
            flash("File Successfully Uploaded")
            return redirect(url_for('index'))
    return render_template("upload.html")

#DOWNLOAD
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
if __name__ == '__main__':
    init_db()
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
    )