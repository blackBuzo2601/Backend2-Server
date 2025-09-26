from auth import login_user, register_user

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    try:
        logged_in = False
        user = None

        while True:
            if not logged_in:
                menu = "Elige una opción:\n1. Login\n2. Register\n"
                conn.sendall(menu.encode("utf-8"))

                option_bytes = conn.recv(1024)
                if not option_bytes:
                    break
                option = option_bytes.decode("utf-8").strip()

                if option == "1":
                    # --- LOGIN ---
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

                    if login_user(user, password):
                        conn.sendall(f"Login exitoso. Bienvenido {user}!\n".encode("utf-8"))
                        logged_in = True
                    else:
                        conn.sendall("Usuario o contraseña incorrectos.\n".encode("utf-8"))

                elif option == "2":
                    # --- REGISTER ---
                    while True:
                        conn.sendall("Ingresa tu nombre de usuario: ".encode("utf-8"))
                        username_bytes = conn.recv(1024)
                        if not username_bytes:
                            break
                        new_username = username_bytes.decode("utf-8").strip()
                        if new_username == "":
                            break

                        if user_exists(new_username):
                            conn.sendall("Ese nombre de usuario ya existe, por favor introduce otro.\n".encode("utf-8"))
                            continue

                        conn.sendall("Ingresa la contraseña para tu usuario: ".encode("utf-8"))
                        password1_bytes = conn.recv(1024)
                        if not password1_bytes:
                            break
                        password1 = password1_bytes.decode("utf-8").strip()
                        if password1 == "":
                            break

                        conn.sendall("Repite la contraseña para guardar cambios: ".encode("utf-8"))
                        password2_bytes = conn.recv(1024)
                        if not password2_bytes:
                            break
                        password2 = password2_bytes.decode("utf-8").strip()

                        if password1 != password2:
                            conn.sendall("Las contraseñas no coinciden. Teclea ENTER para regresar al menu principal.\n".encode("utf-8"))
                            decide_bytes = conn.recv(1024)
                            if not decide_bytes or decide_bytes.decode("utf-8").strip() == "":
                                break
                        else:
                            success, msg = register_user(new_username, password1)
                            conn.sendall(f"{msg}\n".encode("utf-8"))
                            break

                else:
                    conn.sendall("Opción inválida.\n".encode("utf-8"))

            else:
                msg_bytes = conn.recv(1024)
                if not msg_bytes:
                    break
                mensaje = msg_bytes.decode("utf-8").strip()
                print(f"{addr} {mensaje}")

    except Exception as e:
        print(f"Error con {addr}: {e}")
    finally:
        conn.close()
        print(f"Cliente {addr} desconectado")
