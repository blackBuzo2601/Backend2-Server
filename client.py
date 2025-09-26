import socket
#192.168.0.119 server ite
HOST = "172.23.189.64"
PORT = 65432

#Estas dos variables almacenan lo que el usuario pone en el prompt al correr el script.
#Para saltar ese prompt, se pueden poner poner las credenciales directamente para hacer pruebas
user = ""
password = ""

#Si alguna de las variables esta vacía, solicitar por prompt credenciales
if not user:
    user = input("user: ")
if not password:
    password = input("password: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Conectado al servidor en {HOST}:{PORT}")

    #Enviamos usuario y contreaseña al server con formato "usuario:contraseña"
    s.sendall(f"{user}:{password}\n".encode("utf-8"))

    #Recibir respuesta del servidor
    data = s.recv(1024)
    print(data.decode("utf-8"))

    # Si login fue exitoso, podemos enviar mensajes de prueba
    if b"Login exitoso" in data:
        while True:
            msg = input("Mensaje (deja el prompt vacio para salir): ")
            if not msg:
                break
            s.sendall(msg.encode("utf-8"))
            response = s.recv(1024)
            print(f"Servidor: {response.decode('utf-8')}")
