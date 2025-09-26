import socket

#192.168.0.119 server ite
HOST = "172.23.189.64"
PORT = 65432

def recv_until_prompt(s, prompt_suffix=": "):
    """
    Lee del socket hasta ver un prompt finalizado (p.ej. "user: " o "password: "),
    o hasta recibir una línea completa terminada en '\n'.
    Devuelve la cadena recibida (sin el newline).
    """
    buf = ""
    while True:
        chunk = s.recv(1024)
        if not chunk:
            return None
        try:
            decoded = chunk.decode("utf-8")
        except UnicodeDecodeError:
            decoded = chunk.decode("latin-1", errors="ignore")
        buf += decoded
        # si encontramos newline -> devolver hasta newline
        if "\n" in buf:
            line, _, rest = buf.partition("\n")
            return line
        # si encontramos el prompt (ej. "user: " o "password: "), devolver el buffer completo
        if buf.endswith(prompt_suffix):
            return buf

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Conectado al servidor en {HOST}:{PORT}")

    # Esperar prompt de usuario
    prompt = recv_until_prompt(s, prompt_suffix=": ")
    if prompt is None:
        print("Conexión cerrada por el servidor.")
    else:
        # Mostrar prompt tal cual vino (por ejemplo "user: ")
        print(prompt, end="", flush=True)
        user = input()
        s.sendall((user + "\n").encode("utf-8"))

        # Esperar prompt de password
        prompt = recv_until_prompt(s, prompt_suffix=": ")
        if prompt is None:
            print("Conexión cerrada por el servidor.")
        else:
            print(prompt, end="", flush=True)
            password = input()
            s.sendall((password + "\n").encode("utf-8"))

            # Recibir respuesta del servidor (login ok / fail)
            data = s.recv(1024)
            if not data:
                print("Sin respuesta. Conexión cerrada.")
            else:
                print(data.decode("utf-8"))

                # Si login fue exitoso, servidor hace eco por líneas
                if b"Login exitoso" in data:
                    try:
                        while True:
                            msg = input("Mensaje (deja el prompt vacio para salir): ")
                            if not msg:
                                break
                            s.sendall((msg + "\n").encode("utf-8"))
                            response = s.recv(1024)
                            if not response:
                                print("Servidor cerró la conexión.")
                                break
                            print(f"Servidor: {response.decode('utf-8').rstrip()}")
                    except KeyboardInterrupt:
                        print("\nCerrando cliente.")
