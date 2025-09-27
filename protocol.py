def send_str(conn, s):
    try:
        conn.sendall(s.encode("utf-8"))
    except Exception:
        # si falla enviar, no hacemos nada más (el hilo manejará cierre)
        pass

def recv_line(conn):
    """
    Lee del socket hasta encontrar '\n'. Devuelve la línea sin terminadores.
    Si el cliente cierra la conexión retorna None.
    Maneja CRLF (\r\n) y fragmentación.
    """
    buf = []
    while True:
        try:
            chunk = conn.recv(1024)
        except Exception:
            return None
        if not chunk:
            return None
        try:
            text = chunk.decode("utf-8")
        except UnicodeDecodeError:
            text = chunk.decode("latin-1", errors="ignore")
        buf.append(text)
        data = "".join(buf)
        if "\n" in data:
            line, _, rest = data.partition("\n")
            # Si quedó algo de 'rest' lo dejamos en una nota,
            # pero aquí no mantenemos buffer entre llamadas (simplifica el protocolo)
            return line.rstrip("\r")
        # si no hay newline, seguir recibiendo
