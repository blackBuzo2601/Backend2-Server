import socket
import threading
import sqlite3

HOST = "172.23.189.64"  # IP del servidor
PORT = 65432
DB_PATH = "users.sqlite"

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    conn_db = sqlite3.connect(DB_PATH)
    cursor = conn_db.cursor()

    try:
        logged_in = False
        user = None

        while True:
            if not logged_in:
                # Mostrar menú solo si no está logueado
                menu = "Elige una opción:\n1. Login\n2. Register\n"
                conn.sendall(menu.encode("utf-8"))

                option = conn.recv(1024)
                if not option:
                    break
                option = option.decode("utf-8").strip()

                if option == "1":
                    # Login
                    conn.sendall("Ingresa usuario: ".encode("utf-8"))
                    user_input = conn.recv(1024)
                    if not user_input:
                        break
                    user = user_input.decode("utf-8").strip()

                    conn.sendall("Ingresa contraseña: ".encode("utf-8"))
                    password_input = conn.recv(1024)
                    if not password_input:
                        break
                    password = password_input.decode("utf-8").strip()

                    cursor.execute("SELECT * FROM users WHERE user=? AND password=?", (user, password))
                    result = cursor.fetchone()

                    if result:
                        conn.sendall(f"Login exitoso. Bienvenido {user}!\n".encode("utf-8"))
                        print(f"[LOGIN] Usuario {user} conectado desde {addr}")
                        logged_in = True  # Cambia el estado
                    else:
                        conn.sendall("Usuario o contraseña incorrectos.\n".encode("utf-8"))
                        # Sigue el loop para intentar de nuevo

                elif option == "2":
                    conn.sendall("Intentando registrarse...\n".encode("utf-8"))
                else:
                    conn.sendall("Opción inválida.\n".encode("utf-8"))

            else:
                # Ya logueado: escuchar mensajes del cliente
                msg = conn.recv(1024)
                if not msg:
                    break
                mensaje = msg.decode("utf-8").strip()
                print(f"{mensaje} {addr}")  # Mostrar mensaje con IP del cliente

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
