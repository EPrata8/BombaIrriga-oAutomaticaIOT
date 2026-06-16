import serial
import json
import threading
import time
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

PORTA_SERIAL = 'COM4'
BAUD_RATE = 9600

# O Python inicia vazio e vai assumir o que o Arduino ditar
dados_atuais = {"umidade": 0, "bomba": False, "status": "Conectando...", "modo": "auto"}
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
                    # Resolve o problema das aspas simples do Arduino
                    linha_corrigida = linha.replace("'", '"')
                    dados = json.loads(linha_corrigida)
                    
                    with lock:
                        dados_atuais["status"] = "Conectado"
                        dados_atuais["umidade"] = dados.get("umidade", 0)
                        dados_atuais["bomba"] = dados.get("bomba", False)
                        
                        # Agora o Python confia 100% no modo que o Arduino relatar
                        if "modo" in dados:
                            dados_atuais["modo"] = dados["modo"]
                                
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
        parametros = parse_qs(url_cortada.query)
        sucesso = False
        
        # ROTA: Altera entre Automático e Manual
        if url_cortada.path == '/modo':
            novo_modo = parametros.get('tipo', ['auto'])[0]
            with lock:
                if conexao_serial and conexao_serial.is_open:
                    # Envia A ou M com o \n (quebra de linha) para o Arduino ler imediatamente
                    if novo_modo == "auto":
                        conexao_serial.write(b"A\n")
                    else:
                        conexao_serial.write(b"M\n")
                sucesso = True
                
        # ROTA: Controla a bomba
        elif url_cortada.path == '/bomba':
            comando = parametros.get('comando', [None])[0]
            with lock:
                if dados_atuais["modo"] == "manual":
                    if conexao_serial and conexao_serial.is_open:
                        # Envia L ou D com o \n
                        if comando == 'ligar':
                            conexao_serial.write(b"L\n")
                        elif comando == 'desligar':
                            conexao_serial.write(b"D\n")
                    sucesso = True
                else:
                    sucesso = False
            
        resposta = json.dumps({"sucesso": sucesso}).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(resposta)

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