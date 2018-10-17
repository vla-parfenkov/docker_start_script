import docker
import json
import sqlite3

def deploy_wsgi_interface(environ, start_response):
	respone = "Invalid id"
	status = '404 Not Found'
	idApp = 0
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0

	if environ["REQUEST_METHOD"] == 'POST' and environ["wsgi.input"]:
		request_body = environ["wsgi.input"].read(request_body_size)
		data = json.loads(request_body)
		idApp = data["appName"]
		infoApp = getInfoApp(idApp)
		if infoApp == None:
			start_new_docker(idApp)
		else:
			restart_docker(idApp, infoApp[2])
		respone = str(idApp)
		status = '200 OK'

	response_headers = [('Content-type', 'aplication/json')]
	start_response(status, response_headers)
	return [respone]

def start_new_docker(idApp):
	client = docker.from_env()
	global lastport
	lastport = lastport + 1
	str_env = "APP_Name=" + str(idApp)
	container = client.containers.run('vktestapp', ports={'8080/tcp': lastport}, detach=True, environment=[str_env])
	setInfoApp(idApp, lastport, container.id)

def restart_docker(idApp, containerId):
	client = docker.from_env()
	try:
		container = client.containers.get(containerId)
		container.restart()
	#if container remove, but exist in datebase
	except Exception:
		global lastport
		lastport = lastport + 1
		str_env = "APP_Name=" + str(idApp)
		container = client.containers.run('vktestapp', ports={'8080/tcp': lastport}, detach=True, environment=[str_env])
		updateInfoApp(idApp, lastport, container.id)


def getInfoApp(idApp):
	cursor = conn.cursor()
	sql = "SELECT * FROM Apps WHERE id=?"
	cursor.execute(sql, [idApp])
	return cursor.fetchone()

def setInfoApp(idApp, port, container):
	cursor = conn.cursor()
	sql = "INSERT INTO Apps VALUES (?, ?, ?)"
	cursor.execute(sql, [idApp, port, container])
	conn.commit()

def updateInfoApp(idApp, port, container):
	cursor = conn.cursor()
	sql = "UPDATE Apps SET port = ? , container = ? WHERE id=?"
	cursor.execute(sql, [port, container, idApp])
	conn.commit()

def getLastPort():
	cursor = conn.cursor()
	sql = "SELECT port FROM Apps ORDER BY port DESC LIMIT 1"
	cursor.execute(sql)
	res = cursor.fetchone()
	if res == None:
		return 3999
	else:
		return res[0]

conn = sqlite3.connect("idApp.db")
lastport = getLastPort()
