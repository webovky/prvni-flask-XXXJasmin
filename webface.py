from distutils.log import error
from flask import Flask, render_template, request, redirect, url_for, session, flash
import functools
import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string


from mysqlite import SQLite

# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b"totoj e zceLa n@@@hodny retezec nejlep os.urandom(24)"
app.secret_key = b"x6\x87j@\xd3\x88\x0e8\xe8pM\x13\r\xafa\x8b\xdbp\x8a\x1f\xd41\xb8"



slova = ("Super", "Perfekt", "Úža", "Flask")

def prihlasit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("login", url=request.path))

    return wrapper


@app.route("/", methods=["GET"])
def index():
    return render_template("base.html")


@app.route("/info/")
def info():
    return render_template("info.html")

@app.route("/zkracovac/")
def zkracovac():
    return render_template("Zkracovac.html")

@app.route("/zkracovac/" ,methods=["POST"])
def zkracovac_post():
    url=request.form.get("url")
    zkratka= ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=5))
    with SQLite('data.db') as cur:
            cur.execute("INSERT INTO adresy (zkratka,adresa) VALUES (?,?)", [zkratka, url])
    return redirect(url_for("zkracovac"))

@app.route("/abc/")
def abc():
    return render_template("abc.html", slova=slova)




@app.route("/malina/", methods=['GET', 'POST'])
def malina():
    if 'uzivatel' not in session:
        flash('Nejsi přihlášen, tato stránka vyžaduje přihlášení.', 'error')
        return redirect(url_for('login', page = request.full_path))

    hmotnost = request.args.get('hmotnost')
    vyska = request.args.get('vyska')

    print(hmotnost, vyska)    
    if hmotnost and vyska:
        try:
            hmotnost = float(hmotnost)
            vyska=float(vyska)
            bmi = hmotnost/(0.01*vyska)**2
        except (ZeroDivisionError, ValueError):
            bmi=None
            err="Je třba zadat dvě nenulová čísla"
    else:
        bmi = None

    return render_template('malina.html', bmi=bmi)

@app.route("/login/", methods=["GET"])
def login():
    jméno=request.args.get("jméno")
    heslo=request.args.get("heslo")
    print(jméno,heslo)
    return render_template('login.html')

@app.route("/login/", methods=["POST"])
def login_post():
    jmeno=request.form.get("jméno")
    heslo=request.form.get("heslo")
    page = request.args.get('page')

    with SQLite('data.db') as cur:
        cur.execute('SELECT passwd FROM user WHERE login = ?', [jmeno])
        ans= cur.fetchall()[0][0]
        print(ans)

    if ans and ans[0][0] ==heslo:
        flash('Jsi přihlášen!', 'message')
        session["uzivatel"] = jmeno
        if page:
            return redirect(page)
    else:
        flash('Nesprávné přihlašovací údaje', 'error')
    if page:
        return redirect(url_for("login", page=page))
    return redirect(url_for('login'))

@app.route("/logout/", methods=["GET", "POST"])
def logout():
    session.pop("uživatel", None)
    return redirect(url_for('index'))



@app.route("/registrace/", methods=['GET'])
def registrace():
    return render_template("registrace.html")

@app.route("/registrace/", methods=['POST'])
def registrace_post():
    jmeno=request.args.get("jméno")
    heslo=request.args.get("heslo")
    heslo2=request.args.get("heslo_znovu")
    
    if not (jmeno and heslo and heslo2):
        flash('Je nutné vyplnit všechna políčka', 'error')
        return redirect(url_for("registrace"))

    if heslo != heslo2:
        flash('Obě hesla musí být stejná', 'error')
        return redirect(url_for("registrace"))
    heslo_hash =generate_password_hash(heslo)
    try:    
        with SQLite('data.db') as cur:
            cur.execute("INSERT INTO user (login,passwd) VALUES (?,?)", [jmeno,heslo_hash])
        flash('Právě jsi se zaregistroval.', 'message')
        flash('Jsi přihlášen....', 'message')
        session['u6ivatel'] = jmeno
        return redirect(url_for("index"))
    except sqlite3.InstegrityError:
        flash(f"Jméno {jmeno} již existuje. Vyberte jiné.", "error")

    return redirect(url_for("registrace"))
