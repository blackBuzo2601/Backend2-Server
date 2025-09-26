import socket

HOST = "172.23.189.64"  # Cambia a la IP del servidor
PORT = 65432

def recv_until_prompt(s):
    """Recibe datos hasta encontrar '\n' o ': ' y los devuelve."""
    buf = ""
    while True:
        chunk = s.recv(1024)
        if not chunk:
            return None
        buf += chunk.decode("utf-8")
        if "\n" in buf or buf.endswith(": "):
            return buf

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Conectado al servidor en {HOST}:{PORT}")

    try:
        while True:
            # Recibir mensaje del servidor
            msg = recv_until_prompt(s)
            if msg is None:
                print("Conexión cerrada por el servidor.")
                break
            print(msg, end='')

            # Enviar respuesta si el servidor espera input
            user_input = input()
            s.sendall((user_input + "\n").encode("utf-8"))

    except KeyboardInterrupt:
        print("\nCerrando cliente.")
