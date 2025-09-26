import socket
import threading
import sqlite3

HOST = "172.23.189.64"  # Escucha en todas las interfaces
PORT = 65432
DB_PATH = "users.sqlite"

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    conn_db = sqlite3.connect(DB_PATH)
    cursor = conn_db.cursor()

    try:
        while True:
            # Enviar menú
            menu = "Elige una opción:\n1. Login\n2. Register\n"
            conn.sendall(menu.encode("utf-8"))

            option = conn.recv(1024)
            if not option:
                break
            option = option.decode("utf-8").strip()

            if option == "1":
                # Login
                conn.sendall("Ingresa usuario: ".encode("utf-8"))
                user = conn.recv(1024).decode("utf-8").strip()

                conn.sendall("Ingresa contraseña: ".encode("utf-8"))
                password = conn.recv(1024).decode("utf-8").strip()

                cursor.execute("SELECT * FROM users WHERE user=? AND password=?", (user, password))
                result = cursor.fetchone()

                if result:
                    conn.sendall(f"Login exitoso. Bienvenido {user}!\n".encode("utf-8"))
                else:
                    conn.sendall("Usuario o contraseña incorrectos.\n".encode("utf-8"))

            elif option == "2":
                # Register temporal
                conn.sendall("Intentando registrarse...\n".encode("utf-8"))
            else:
                conn.sendall("Opción inválida.\n".encode("utf-8"))

            # Preguntar si quiere continuar
            conn.sendall("¿Quiere volverlo a intentar? (s/n): ".encode("utf-8"))
            cont = conn.recv(1024)
            if not cont or cont.decode("utf-8").strip().lower() != "s":
                conn.sendall("Cerrando conexión. ¡Hasta luego!\n".encode("utf-8"))
                break

    except Exception as e:
        print(f"Error con {addr}: {e}")

    finally:
        conn.close()
        conn_db.close()
        print(f"Cliente {addr} desconectado")


# Servidor principal
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
