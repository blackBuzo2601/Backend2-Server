import socket
import threading
import sqlite3
#192.168.0.119 server ite
HOST = "172.23.189.64"
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

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    try:
        # Recibimos datos iniciales: esperamos "usuario:contraseña"
        data = conn.recv(1024).decode("utf-8").strip()
        if not data:
            conn.close()
            return

        if ":" not in data:
            conn.sendall("Formato inválido. Use usuario:contraseña\n".encode("utf-8"))
            conn.close()
            return

        username, password = data.split(":", 1)

        if authenticate(username, password):
            conn.sendall(f"Login exitoso. Bienvenido {username}!\n".encode("utf-8"))
            # Aquí podrías agregar más lógica para comandos posteriores
            while True:
                msg = conn.recv(1024)
                if not msg:
                    break
                conn.sendall(msg)  # eco simple
        else:
            conn.sendall("Usuario o contraseña incorrectos. Cerrando conexión.\n".encode("utf-8"))
            conn.close()
    except Exception as e:
        print(f"Error con {addr}: {e}")
        conn.close()
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
