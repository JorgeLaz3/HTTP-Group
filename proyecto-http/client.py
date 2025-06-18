import socket

def send_request(method, path, host='localhost', port=9091, headers=None, body=''):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        request = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n"

        if headers:
            for header, value in headers.items():
                request += f"{header}: {value}\r\n"
        
        if body:
            request += f"Content-Length: {len(body)}\r\n"

        request += "\r\n" + body

        s.sendall(request.encode())
        response = s.recv(4096).decode()

        # Separar la respuesta
        header_part, _, body_part = response.partition('\r\n\r\n')
        status_line, *header_lines = header_part.splitlines()
        
        # Mostrar cada parte por separado
        print("\n🔸 Estado HTTP:")
        print(status_line)

        print("\n🔸 Encabezados de la respuesta:")
        for header in header_lines:
            print(header)

        print("\n🔸 Cuerpo de la respuesta:")
        print(body_part)

def main():
    while True:
        method = input("Método HTTP (GET, POST, PUT, DELETE): ").upper()
        path = input("Ruta (ejemplo '/', '/resources', '/resources/1'): ")
        headers = {}
        
        add_headers = input("¿Quieres añadir encabezados personalizados? (si/no): ").lower()
        while add_headers == 'si':
            header_name = input("Nombre del encabezado: ")
            header_value = input("Valor del encabezado: ")
            headers[header_name] = header_value
            add_headers = input("¿Añadir otro encabezado más? (si/no): ").lower()
        
        body = ''
        if method in ['POST', 'PUT']:
            body = input("Cuerpo de la solicitud: ")
        
        send_request(method, path, headers=headers, body=body)

if __name__ == '__main__':
    main()
