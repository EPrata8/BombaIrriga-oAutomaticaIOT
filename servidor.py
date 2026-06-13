import serial
import json
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

PORTA_SERIAL = 'COM4'
BAUD_RATE = 9600

dados_atuais = {"umidade": 0, "bomba": False, "status": "Conectando..."}
lock = threading.Lock()
conexao_serial = None


def ler_serial():
    global dados_atuais, conexao_serial
    try:
        conexao_serial = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=2)
        print(f"Conectado ao Arduino em {PORTA_SERIAL}")
        
        while True:
            linha = conexao_serial.readline().decode('utf-8', errors='ignore').strip()
            if linha:
                try:
                    dados = json.loads(linha)
                    with lock:
                        dados_atuais["umidade"] = dados.get("umidade", 0)
                        dados_atuais["bomba"] = dados.get("bomba", False)
                        dados_atuais["status"] = "Conectado"
                except json.JSONDecodeError:
                    pass  
    except serial.SerialException as e:
        print(f"Erro na porta serial: {e}")
        with lock:
            dados_atuais["status"] = "Desconectado"


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/dados':
            with lock:
                resposta = json.dumps(dados_atuais).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resposta)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global conexao_serial
        url_cortada = urlparse(self.path)
        
        if url_cortada.path == '/bomba':
            parametros = parse_qs(url_cortada.query)
            comando = parametros.get('comando', [None])[0]
            
            sucesso_envio = False
            if conexao_serial and conexao_serial.is_open:
                if comando == 'ligar':
                    conexao_serial.write(b"L")
                    sucesso_envio = True
                elif comando == 'desligar':
                    conexao_serial.write(b"D")
                    sucesso_envio = True
            
            resposta = json.dumps({"sucesso": sucesso_envio, "comando_recebido": comando}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resposta)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    t = threading.Thread(target=ler_serial, daemon=True)
    t.start()

    servidor = HTTPServer(('', 8765), Handler)
    print("Servidor ativo em http://127.0.0.1:8765")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")