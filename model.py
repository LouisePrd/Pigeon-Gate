from flask import Flask,request,render_template, session
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()
db_port = os.getenv('DB_PORT')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')


mydb = mysql.connector.connect(
    port = db_port,
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

## User

def getUserbyPseudo(pseudo):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM User WHERE pseudo = %s", (pseudo,))
    userData = mycursor.fetchall()
    if not userData:
        return None
    user = {
        "idUser": userData[0][0],
        "pseudo": userData[0][1],
        "bio": userData[0][3],
        "typeProfilePicture": userData[0][4],
        "sommePigeons": sumAllPigeonsByUser(userData[0][0])
    }
    return user

def getUserbyId(idUser):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM User WHERE idUser = %s", (idUser,))
    userData = mycursor.fetchall()
    user = {
        "idUser": userData[0][0],
        "pseudo": userData[0][1],
        "bio": userData[0][3],
        "typeProfilePicture": userData[0][4],
        "sommePigeons": sumAllPigeonsByUser(userData[0][0])
    }
    return user

def checkLogin(pseudo, password):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM User WHERE pseudo = %s", (pseudo,))
    user = mycursor.fetchone()
    if user == None:
        return False
    hashed_password = user[2]
    if Bcrypt().check_password_hash(hashed_password, password):
        return True
    return False

def newUser(pseudo, password, typeProfilePicture):
    if not pseudo or not password or not typeProfilePicture:
        return False
    if getUserbyPseudo(pseudo):
        return False
    mycursor = mydb.cursor()
    mycursor.execute("INSERT INTO User (pseudo, password, typeProfilePicture) VALUES (%s, %s, %s)", (pseudo, password, typeProfilePicture))
    mydb.commit()
    return True

def changeBio(idUser, newBio):
    mycursor = mydb.cursor()
    mycursor.execute("UPDATE User SET bio = %s WHERE idUser = %s", (newBio, idUser))
    mydb.commit()

def changeProfilePicture(idUser, newTypeProfilePicture):
    mycursor = mydb.cursor()
    mycursor.execute("UPDATE User SET typeProfilePicture = %s WHERE idUser = %s", (newTypeProfilePicture, idUser))
    mydb.commit()

def changePseudo(idUser, newPseudo):
    mycursor = mydb.cursor()
    mycursor.execute("UPDATE User SET pseudo = %s WHERE idUser = %s", (newPseudo, idUser))
    mydb.commit()


## Pigeon

def sumAllPigeonsByUser(idUser):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM Pigeon WHERE idUser = %s", (idUser,))
    sumPigeons = mycursor.fetchone()
    if not sumPigeons:
        return 0
    return sumPigeons[0]

def getAllPigeons():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Pigeon")
    allPigeons = mycursor.fetchall()
    return dataToPigeon(allPigeons)

def dataToPigeon(datas):
    pigeons = []
    for pigeon in datas:
        pigeon = {
            "idPigeon": pigeon[0],
            "prenomPigeon": pigeon[1],
            "color": pigeon[2],
            "rateWalk": pigeon[3],
            "rateVibe": pigeon[4],
            "rateOriginality": pigeon[5],
            "place": pigeon[6],
            "urlPhoto": pigeon[7],
            "idUser": pigeon[8]
        }    
        pigeons.append(pigeon)
    return pigeons


def addPigeon(prenomPigeon, color, rateWalk, rateVibe, rateOriginality, place, urlPhoto, idUser):
    mycursor = mydb.cursor()
    mycursor.execute("INSERT INTO Pigeon (prenomPigeon, color, rateWalk, rateVibe, rateOriginality, place, urlPhoto, idUser) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (prenomPigeon, color, rateWalk, rateVibe, rateOriginality, place, urlPhoto, idUser))
    mydb.commit()

def getLastPigeonsByUser(idUser, page):
    limit = 4
    offset = page * limit
    mycursor = mydb.cursor()
    query = "SELECT * FROM Pigeon INNER JOIN User ON Pigeon.idUser = User.idUser WHERE Pigeon.idUser = %s ORDER BY Pigeon.idPigeon DESC LIMIT %s OFFSET %s"
    mycursor.execute(query, (idUser, limit, offset))
    lastPigeons = mycursor.fetchall()
    return dataToPigeon(lastPigeons)

def getCardPigeonsById(idPigeon):
    mycursor = mydb.cursor()
    query = "SELECT * FROM Pigeon WHERE idPigeon = %s";
    mycursor.execute(query, (idPigeon,))
    cardPigeons = mycursor.fetchone()
    pigeon = {
        "idPigeon": cardPigeons[0],
        "prenomPigeon": cardPigeons[1],
        "color": cardPigeons[2],
        "rateWalk": cardPigeons[3],
        "rateVibe": cardPigeons[4],
        "rateOriginality": cardPigeons[5],
        "place": cardPigeons[6],
        "urlPhoto": cardPigeons[7],
        "idUser": cardPigeons[8]
    }
    return pigeon


# Comment

def dataToComment(datas, pseudoUser):
    comments = []
    for comment in datas:
        comment = {
            "idComment": comment[0],
            "textCom": comment[1],
            "nbLike": comment[2],
            "idUser": comment[3],
            "idPigeon": comment[4],
            "pseudoUser": pseudoUser,
        }
        comments.append(comment)
    return comments

def getCommentsByIdPigeon(idPigeon, idUser):
    mycursor = mydb.cursor()
    query = "SELECT * FROM commentaire WHERE idPigeon = %s";
    mycursor.execute(query, (idPigeon,))
    comments = mycursor.fetchall()
    user = getUserbyId(idUser)
    return dataToComment(comments, user['pseudo'])

def addComment(textCom, idUser, idPigeon):
    mycursor = mydb.cursor()
    mycursor.execute("INSERT INTO commentaire (textCom, nbLike, idUser, idPigeon) VALUES (%s, %s, %s, %s)", (textCom, 0, idUser, idPigeon))
    mydb.commit()

def getFourRandomPigeons(currentIdPigeon):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Pigeon WHERE idPigeon != %s ORDER BY RAND() LIMIT 4", (currentIdPigeon,))
    fourRandomPigeons = mycursor.fetchall()
    return dataToPigeon(fourRandomPigeons)

def addRatePigeon(idPigeon, rateWalk, rateVibe, rateOriginality):
    mycursor = mydb.cursor()
    pigeon = getCardPigeonsById(idPigeon)
    rateWalk = (pigeon['rateWalk'] + rateWalk) / 2
    rateVibe = (pigeon['rateVibe'] + rateVibe) / 2
    rateOriginality = (pigeon['rateOriginality'] + rateOriginality) / 2
    mycursor.execute("UPDATE Pigeon SET rateWalk = %s, rateVibe = %s, rateOriginality = %s WHERE idPigeon = %s", (rateWalk, rateVibe, rateOriginality, idPigeon))
    mydb.commit()
