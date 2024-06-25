from flask import Flask,request,render_template, jsonify,abort
import random
import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
    port = 8889,
    host="localhost",
    user="root",
    password="root",
    database="pigeon-gate",
)

pigeons = [];

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM Pigeon")
allPigeons = mycursor.fetchall()

@app.route("/", methods=['GET', 'POST'])
def welcome():
    if mydb.is_connected():
        return render_template("welcome.html", pigeons=allPigeons);

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        password = request.form['password']
        typeProfilePicture = request.form['typeProfilePicture']
        mycursor.execute("SELECT * FROM User WHERE pseudo = %s", (pseudo,))
        messageError = "Ce pseudo est déjà utilisé"
        if mycursor.fetchall():
            print(typeProfilePicture)
            return render_template("register.html", messageError=messageError);
        if not pseudo or not password or not typeProfilePicture:
            message_error = "Tous les champs sont obligatoires."
            return render_template('register.html', messageError=message_error)
        mycursor.execute("INSERT INTO User (pseudo, password, typeProfilePicture) VALUES (%s, %s, %s)", (pseudo, password, typeProfilePicture))
        mydb.commit()
        return render_template("welcome.html", pigeons=allPigeons, pseudo=pseudo);
    else:
        return render_template("register.html");

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        password = request.form['password']
        mycursor.execute("SELECT * FROM User WHERE pseudo = %s AND password = %s", (pseudo, password))
        testLogin = mycursor.fetchall()
        if testLogin:
            return render_template("welcome.html", pigeons=allPigeons, pseudo=pseudo);
        else:
            messageErrorLogin = "Pseudo ou mot de passe incorrect"
            return render_template("login.html", messageErrorLogin=messageErrorLogin);
    else:
        return render_template("login.html");



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)