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

                option_bytes = conn.recv(1024)
                if not option_bytes:
                    break
                option = option_bytes.decode("utf-8").strip()

                if option == "1":
                    # --- LOGIN ---
                    conn.sendall("Ingresa usuario: ".encode("utf-8"))
                    user_input_bytes = conn.recv(1024)
                    if not user_input_bytes:
                        break
                    user = user_input_bytes.decode("utf-8").strip()

                    conn.sendall("Ingresa contraseña: ".encode("utf-8"))
                    password_input_bytes = conn.recv(1024)
                    if not password_input_bytes:
                        break
                    password = password_input_bytes.decode("utf-8").strip()

                    cursor.execute("SELECT * FROM users WHERE user=? AND password=?", (user, password))
                    result = cursor.fetchone()

                    if result:
                        conn.sendall(f"Login exitoso. Bienvenido {user}!\n".encode("utf-8"))
                        print(f"[LOGIN] Usuario {user} conectado desde {addr}")
                        logged_in = True
                    else:
                        conn.sendall("\nUsuario o contraseña incorrectos.\n".encode("utf-8"))

                elif option == "2":
                    # --- REGISTER ---
                    while True:
                        conn.sendall("Ingresa tu nombre de usuario: ".encode("utf-8"))
                        username_bytes = conn.recv(1024)
                        if not username_bytes:
                            break
                        new_username = username_bytes.decode("utf-8").strip()

                        if new_username == "":
                            conn.sendall("Usuario vacío, regresando al menú principal.\n".encode("utf-8"))
                            break

                        # Verificar que no exista
                        cursor.execute("SELECT 1 FROM users WHERE user = ?", (new_username,))
                        exists = cursor.fetchone()
                        if exists:
                            conn.sendall("Ese nombre de usuario ya existe, por favor introduce otro.\n".encode("utf-8"))
                            continue

                        while True:
                            conn.sendall("Ingresa la contraseña para tu usuario: ".encode("utf-8"))
                            p1_bytes = conn.recv(1024)
                            if not p1_bytes:
                                break
                            p1 = p1_bytes.decode("utf-8").strip()

                            if p1 == "":
                                conn.sendall("Contraseña vacía, regresando al menú principal.\n".encode("utf-8"))
                                break

                            conn.sendall("Repite la contraseña para guardar cambios: ".encode("utf-8"))
                            p2_bytes = conn.recv(1024)
                            if not p2_bytes:
                                break
                            p2 = p2_bytes.decode("utf-8").strip()

                            if p1 == p2:
                                try:
                                    cursor.execute("INSERT INTO users (user, password) VALUES (?, ?)", (new_username, p1))
                                    conn_db.commit()
                                    conn.sendall(f"Registro exitoso. Usuario '{new_username}' creado.\n".encode("utf-8"))
                                    print(f"[REGISTER] Usuario {new_username} creado desde {addr}")
                                    break
                                except sqlite3.IntegrityError:
                                    conn.sendall("Error al registrar. Ese nombre podría existir. Intenta otro.\n".encode("utf-8"))
                                    break
                                except Exception as e:
                                    conn.sendall(f"Error interno al registrar: {e}\n".encode("utf-8"))
                                    break
                            else:
                                conn.sendall("Las contraseñas no coinciden, vuelva a intentarlo.\n".encode("utf-8"))
                                conn.sendall("Teclea ENTER para regresar al menu principal (o escribe cualquier otra cosa para reintentar): ".encode("utf-8"))
                                decide_bytes = conn.recv(1024)
                                if not decide_bytes:
                                    break
                                decide = decide_bytes.decode("utf-8").strip()
                                if decide == "":
                                    break
                                else:
                                    continue
                        break  # volver al menú principal

                else:
                    conn.sendall("Opción inválida.\n".encode("utf-8"))

            else:
                # Ya logueado: escuchar mensajes del cliente
                msg_bytes = conn.recv(1024)
                if not msg_bytes:
                    break
                mensaje = msg_bytes.decode("utf-8").strip()
                print(f"{addr} {mensaje}")  # Mostrar mensaje con IP del cliente

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
