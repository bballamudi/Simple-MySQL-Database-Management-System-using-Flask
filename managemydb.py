from flask import Flask, render_template, request, jsonify, url_for, redirect, session
import MySQLdb
app = Flask(__name__)

app.secret_key="mykey";
@app.route('/ManageMyDB',methods=['GET'])
def ManageMyDB():
	if 'login' in session:
		return redirect(url_for("displayDatabases"))
	if 'loginError' in session:
		e=session['loginError']
	else:
		e=""
	return render_template("home.html",error=e)
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		form = request.form
		try:
			db = MySQLdb.connect(host="localhost",user=form['username'],passwd=form['password'])
			db.close()
			session['login']=True
			session['dbUsername']=form['username']
			session['dbPassword']=form['password']
			if 'loginError' in session:
				session.pop('loginError',None)
			return redirect(url_for("displayDatabases"))
		except:
			session['loginError']="Wrong username or password"
			return redirect(url_for("ManageMyDB"))
	else:
		return redirect(url_for("ManageMyDB"))
@app.route('/ManageMyDB/logout')
def logout():
	session.clear()
	return redirect(url_for("ManageMyDB"))
@app.route('/execute',methods=['POST'])
def executeSQL():
	if request.method=="POST":
		form=request.form
		try:
			if form['database']=="None":
				db = MySQLdb.connect(host="localhost",user=session['dbUsername'],passwd=session['dbPassword'])
			else:
				db = MySQLdb.connect(host="localhost",user=session['dbUsername'],passwd=session['dbPassword'],db=form['database'])
			cursor=db.cursor()
			cursor.execute(form['sqlStatement'])
			data = cursor.fetchall()
			db.commit()
			db.close()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			data=e
			db.close()
		return str(data)
			
@app.route('/databases')
def displayDatabases():
	if 'login' not in session:
		return redirect(url_for("ManageMyDB"))
	db = MySQLdb.connect(host="localhost",user=session['dbUsername'],passwd=session['dbPassword'])
	cursor = db.cursor()
	cursor.execute("Show databases")
	databases = cursor.fetchall()
	cursor.close()
	db.close()
	return render_template("displayDatabases.html",databases=databases)
@app.route('/databases/<database>')
def displayTables(database):
	if 'login' not in session:
		return redirect(url_for("ManageMyDB"))
	db = MySQLdb.connect(host="localhost",user=session['dbUsername'],passwd=session['dbPassword'])
	cursor = db.cursor()
	cursor.execute("Show databases")
	databases = cursor.fetchall()
	if not (database,) in databases:
		return redirect(url_for("displayDatabases"))
	cursor.execute("use "+database)
	cursor.execute("show tables")
	tables = cursor.fetchall()
	cursor.close()
	db.close()
	return render_template("displayTables.html",database=database,tables=tables)
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
@app.route('/databases/<database>/<table>')
def displayRows(database,table):
	if 'login' not in session:
		return redirect(url_for("ManageMyDB"))
	db = MySQLdb.connect(host="localhost",user=session['dbUsername'],passwd=session['dbPassword'])
	cursor = db.cursor()
	cursor.execute("Show databases")
	databases = cursor.fetchall()
	if not (database,) in databases:
		return redirect(url_for("displayDatabases"))
	cursor.execute("use "+database)
	cursor.execute("show tables")
	tables = cursor.fetchall()
	if not (table,) in tables:
		return redirect(url_for("displayDatabases")+"/"+database)
	cursor.execute("desc "+table);
	rows=cursor.fetchall()
	l=[]
	for row in rows:
		l.append(row[0])
	rows1=[]
	rows1.append(l)
	cursor.execute("select * from "+table);
	l=cursor.fetchall()
	rows1=rows1+list(l)
	cursor.close()
	db.close()
	return render_template("displayRows.html",database=database,rows=rows,rows1=rows1)
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
app.after_request(add_cors_headers)
app.run()
