# client_handler.py
from protocol import recv_line, send_str
from auth import login_user, register_user

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    try:
        logged_in = False
        user = None

        while True:
            if not logged_in:
                send_str(conn, "Elige una opción:\n1. Login\n2. Register\n")

                option = recv_line(conn)
                if option is None:
                    break
                option = option.strip()

                if option == "1":
                    # LOGIN
                    send_str(conn, "Ingresa usuario: ")
                    user_input = recv_line(conn)
                    if user_input is None:
                        break
                    user = user_input.strip()
                    send_str(conn, "Ingresa contraseña: ")
                    pw_input = recv_line(conn)
                    if pw_input is None:
                        break
                    password = pw_input.strip()

                    ok = login_user(user, password)
                    if ok:
                        send_str(conn, f"Login exitoso. Bienvenido {user}!\n")
                        print(f"[LOGIN] Usuario {user} conectado desde {addr}")
                        logged_in = True
                    else:
                        send_str(conn, "\nUsuario o contraseña incorrectos.\n")

                elif option == "2":
                    # REGISTER
                    while True:
                        send_str(conn, "Ingresa tu nombre de usuario: ")
                        username_line = recv_line(conn)
                        if username_line is None:
                            # desconexión del cliente
                            break
                        new_username = username_line.strip()
                        # si vacío -> volver al menú
                        if new_username == "":
                            send_str(conn, "Usuario vacío, regresando al menú principal.\n")
                            break

                        # si ya existe
                        if login_user(new_username, ""):  # hack: check existence via user_exists not available here, but better use register_user's logic
                            # avoid using login_user for existence; but to keep modules lean, we'll call register_user and handle
                            pass

                        # check existence via register attempt will detect duplicates, but better call register helper
                        from database import user_exists
                        if user_exists(new_username):
                            send_str(conn, "Ese nombre de usuario ya existe, por favor introduce otro.\n")
                            continue

                        # pedir contraseña
                        while True:
                            send_str(conn, "Ingresa la contraseña para tu usuario: ")
                            p1 = recv_line(conn)
                            if p1 is None:
                                break
                            p1 = p1.strip()
                            if p1 == "":
                                send_str(conn, "Contraseña vacía, regresando al menú principal.\n")
                                break

                            send_str(conn, "Repite la contraseña para guardar cambios: ")
                            p2 = recv_line(conn)
                            if p2 is None:
                                break
                            p2 = p2.strip()

                            if p1 == p2:
                                ok, msg = register_user(new_username, p1)
                                send_str(conn, msg + "\n")
                                if ok:
                                    print(f"[REGISTER] Usuario {new_username} creado desde {addr}")
                                    # registro completado: volver al menú principal
                                    break
                                else:
                                    # si no se pudo registrar, mostrar msg y volver a pedir username
                                    # (msg ya enviado)
                                    break
                            else:
                                send_str(conn, "Las contraseñas no coinciden, vuelva a intentarlo.\n")
                                send_str(conn, "Teclea ENTER para regresar al menu principal (o escribe cualquier otra cosa para reintentar): ")
                                decide = recv_line(conn)
                                if decide is None:
                                    break
                                if decide.strip() == "":
                                    # volver al menú principal
                                    break
                                else:
                                    # reintentar pedir contraseñas
                                    continue
                        # salir del bucle de registro y volver al menu
                        break

                else:
                    send_str(conn, "Opción inválida.\n")
            else:
                # Cliente ya autenticado: recibir mensajes y mostrarlos en servidor
                msg = recv_line(conn)
                if msg is None:
                    break
                mensaje = msg.strip()
                print(f"[{user} - {addr}] dice: {mensaje}")

    except Exception as e:
        # enviar mensaje de error al cliente si es posible antes de cerrar
        try:
            send_str(conn, f"Error interno: {e}\n")
        except Exception:
            pass
        print(f"Error con {addr}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        print(f"Cliente {addr} desconectado")
