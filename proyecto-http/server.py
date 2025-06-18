import sys  # Añadido claramente para argumentos de línea de comandos
import socket
import threading
import json
from datetime import datetime  # Añadido para registro de logs

API_KEY = "123456"  # Clave API claramente definida aquí

HOST = 'localhost'

# Configurar claramente el puerto desde la terminal
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        print("El puerto debe ser un número entero. Usando puerto predeterminado 8080.")
        PORT = 8080
else:
    PORT = 8080

resources = {}
next_id = 1
users = {}  # Guarda claramente usuarios y contraseñas
tokens = {}  # Guarda claramente tokens de sesión activos

def handle_client(conn, addr):
    global next_id
    method, path = "UNKNOWN", "UNKNOWN"  # Evita errores claramente
    try:
        request = conn.recv(4096).decode()
        lines = request.splitlines()

        if not lines:
            response = b'HTTP/1.1 400 Bad Request\r\n\r\nEmpty request.'
            conn.sendall(response)
            conn.close()
            return

        # Verificación clara de API Key
        valid_key = False
        for line in lines[1:]:
            if line.startswith("X-API-Key:"):
                provided_key = line.split(":")[1].strip()
                if provided_key == API_KEY:
                    valid_key = True
                    break

        if not valid_key:
            response = b'HTTP/1.1 401 Unauthorized\r\n\r\nClave API incorrecta o no proporcionada.'

            # Logging peticiones no autorizadas
            log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {addr[0]} - Unauthorized request - {response.decode().splitlines()[0]}\n"
            with open("server.log", "a") as log_file:
                log_file.write(log_entry)
                print(" Log escrito correctamente (no autorizado).")

            conn.sendall(response)
            conn.close()
            return

        parts = lines[0].split()
        if len(parts) == 3:
            method, path, _ = parts
        else:
            response = b'HTTP/1.1 400 Bad Request\r\n\r\nInvalid request format.'
            conn.sendall(response)
            conn.close()
            return

        body = lines[-1] if lines[-1] else ''

        response = ''

        # Registro claramente de usuarios
        if method == 'POST' and path == '/register':
            user_data = json.loads(body)
            username = user_data.get("username")
            password = user_data.get("password")

            if username in users:
                response = b'HTTP/1.1 400 Bad Request\r\n\r\nUsuario ya existe.'
            else:
                users[username] = password
                response = b'HTTP/1.1 201 Created\r\n\r\nUsuario registrado correctamente.'

            conn.sendall(response)
            conn.close()
            return

        # Inicio de sesión claramente
        elif method == 'POST' and path == '/login':
            user_data = json.loads(body)
            username = user_data.get("username")
            password = user_data.get("password")

            if users.get(username) == password:
                token = f"token-{username}"
                tokens[token] = username
                response_body = json.dumps({"token": token})
                response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_body}'.encode()
            else:
                response = b'HTTP/1.1 401 Unauthorized\r\n\r\nCredenciales incorrectas.'

            conn.sendall(response)
            conn.close()
            return

        if method == 'GET' and path == '/':
            try:
                with open('static/index.html', 'rb') as f:
                    content = f.read()
                response = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + content
            except FileNotFoundError:
                response = b'HTTP/1.1 404 Not Found\r\n\r\nResource not found.'

        elif method == 'GET' and path == '/resources':
            response_body = json.dumps(resources)
            response = f'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_body}'.encode()

        elif method == 'POST' and path == '/resources':
            resources[next_id] = body
            response = f'HTTP/1.1 201 Created\r\n\r\nResource added with ID {next_id}.'.encode()
            next_id += 1

        elif method == 'PUT' and path.startswith('/resources/'):
            resource_id = int(path.split('/')[-1])
            if resource_id in resources:
                resources[resource_id] = body
                response = f'HTTP/1.1 200 OK\r\n\r\nResource {resource_id} updated.'.encode()
            else:
                response = f'HTTP/1.1 404 Not Found\r\n\r\nResource {resource_id} not found.'.encode()

        elif method == 'DELETE' and path.startswith('/resources/'):
            resource_id = int(path.split('/')[-1])
            if resource_id in resources:
                del resources[resource_id]
                response = f'HTTP/1.1 200 OK\r\n\r\nResource {resource_id} deleted.'.encode()
            else:
                response = f'HTTP/1.1 404 Not Found\r\n\r\nResource {resource_id} not found.'.encode()

        else:
            response = b'HTTP/1.1 400 Bad Request\r\n\r\nInvalid request method or path.'

    except Exception as e:
        response = f'HTTP/1.1 500 Internal Server Error\r\n\r\nServer error: {str(e)}'.encode()

    # Logging actividad del servidor
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - {addr[0]} - {method} {path} - {response.decode().splitlines()[0]}\n"
    with open("server.log", "a") as log_file:
        log_file.write(log_entry)
        print("Log escrito correctamente.")

    conn.sendall(response)
    conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor HTTP en http://{HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    run_server()
