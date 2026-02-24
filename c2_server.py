from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import json
import base64

class C2Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        # 1) Ler o tamanho do corpo
        content_length = int(self.headers.get('Content-Length', 0))

        # 2) Ler o corpo (bytes -> string)
        raw_body = self.rfile.read(content_length).decode()

        # 3) Tentar parsear JSON
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # 4) Extrair campos esperados
        host = data.get("host", "unknown")
        user = data.get("user", "unknown")
        os_name = data.get("os", "unknown")
        encoded_payload = data.get("data", "")

        # 5) Decodificar Base64 (se existir)
        try:
            decoded_payload = base64.b64decode(encoded_payload).decode()
        except Exception:
            decoded_payload = "<erro ao decodificar>"

        # 6) Log do operador (atacante)
        print("\n==============================")
        print(f"[+] Beacon recebido em {datetime.datetime.now()}")
        print(f"[+] Origem IP: {self.client_address[0]}")
        print(f"[+] Host: {host}")
        print(f"[+] Usuário: {user}")
        print(f"[+] SO: {os_name}")
        print(f"[+] User-Agent: {self.headers.get('User-Agent')}")
        print(f"[+] DADO (decodificado): {decoded_payload}")
        print("==============================\n")

        # 7) Resposta do C2 (comando FAKE / inofensivo)
        response = {
            "action": "noop",        # nenhuma ação
            "sleep": 10,             # sugestão de intervalo
            "message": "ok"
        }

        response_bytes = json.dumps(response).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)


server = HTTPServer(("127.0.0.1", 8080), C2Handler)

print("[*] C2 HTTP inteligente ativo em http://127.0.0.1:8080")
print("[*] Aguardando beacons...\n")

server.serve_forever()