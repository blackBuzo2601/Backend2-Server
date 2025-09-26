import socket
import threading
import sqlite3

#192.168.0.119 server ite
HOST = "172.23.189.64"  #
PORT = 65432
DB_PATH = "usuarios.sqlite"

def authenticate(username, password):
    """Verifica si el usuario existe y la contraseña coincide."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == password:
        return True
    return False

def recv_line(conn):
    """
    Recibe datos del socket hasta encontrar '\n'.
    Devuelve la línea sin el salto de línea final (strip de \r\n).
    Si se cierra la conexión, devuelve None.
    """
    buf = ""
    while True:
        try:
            chunk = conn.recv(1024)
        except Exception:
            return None
        if not chunk:
            return None
        try:
            decoded = chunk.decode("utf-8")
        except UnicodeDecodeError:
            decoded = chunk.decode("latin-1", errors="ignore")
        buf += decoded
        if "\n" in buf:
            line, _, rest = buf.partition("\n")
            return line.rstrip("\r")
        # si no hay '\n', seguir recibiendo

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    try:
        # Enviar prompts para usuario y contraseña (el cliente puede ser telnet o tu script)
        try:
            conn.sendall(b"user: ")
        except Exception:
            conn.close()
            return

        username = recv_line(conn)
        if username is None:
            conn.close()
            return
        username = username.strip()

        try:
            conn.sendall(b"password: ")
        except Exception:
            conn.close()
            return

        password = recv_line(conn)
        if password is None:
            conn.close()
            return
        password = password.strip()

        # Validación (igual que antes)
        if authenticate(username, password):
            conn.sendall(f"Login exitoso. Bienvenido {username}!\n".encode("utf-8"))
            # ciclo de ejemplo: eco simple
            while True:
                msg = recv_line(conn)
                if msg is None:
                    break
                # reenviamos el mensaje recibido (añadimos salto de línea para que telnet muestre en nueva línea)
                try:
                    conn.sendall((msg + "\n").encode("utf-8"))
                except Exception:
                    break
        else:
            conn.sendall("Usuario o contraseña incorrectos. Cerrando conexión.\n".encode("utf-8"))
            conn.close()
    except Exception as e:
        print(f"Error con {addr}: {e}")
        try:
            conn.close()
        except Exception:
            pass
    finally:
        print(f"Cliente {addr} desconectado")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
