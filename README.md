# AgroControl — Sistema de Irrigação Inteligente

Um sistema de irrigação automática feito com Arduino, Python e uma interface web. O sensor de umidade monitora o solo em tempo real e a bomba d'água é acionada automaticamente quando necessário — mas você também pode assumir o controle manualmente pelo painel.

---

## Como funciona

O Arduino lê o sensor de umidade a cada 500ms e envia os dados via serial para o Python em formato JSON. O Python sobe um servidor HTTP local que serve esses dados para a interface web. O painel atualiza sozinho a cada segundo e exibe o estado do solo, da bomba e permite alternar entre modo automático e manual.

```
[Sensor de Umidade] → [Arduino] → [Serial USB] → [Python] → [Interface Web]
```

**Lógica automática:**
- Umidade abaixo de 30% → bomba liga
- Umidade acima de 50% → bomba desliga

---

## O que você vai precisar

**Hardware:**
- Arduino (Uno ou similar)
- Sensor de umidade de solo capacitivo
- Módulo relé 5V
- Bomba d'água
- Cabo USB

**Software:**
- Python 3.x
- Biblioteca `pyserial` → `pip install pyserial`
- Arduino IDE (para gravar o sketch)

---

## Como rodar

**1. Grave o sketch no Arduino**

Abra o arquivo `BombaIrrigacaoArd.ino` na Arduino IDE e faça o upload para a placa.

**2. Verifique a porta serial**

No arquivo `servidor.py`, ajuste a variável `PORTA_SERIAL` para a porta onde o Arduino está conectado:

```python
PORTA_SERIAL = 'COM4'  # Windows
# PORTA_SERIAL = '/dev/ttyUSB0'  # Linux/Mac
```

**3. Suba o servidor Python**

```bash
python servidor.py
```

Você vai ver no terminal:
```
Conectado ao Arduino em COM4
Servidor ativo em http://127.0.0.1:8765
```

**4. Abra o painel**

Abra o arquivo `index.html` diretamente no navegador. O painel vai começar a receber os dados automaticamente.

---

## Modos de operação

| Modo | Comportamento |
|------|--------------|
| **AUTO** | O Arduino decide quando ligar/desligar a bomba com base na umidade |
| **MANUAL** | Você controla a bomba pelos botões "FORÇAR LIGAR" e "DESLIGAR" |

Ao voltar para o modo AUTO com o solo já úmido (acima de 30%), a bomba é desligada automaticamente como medida de segurança.

---

## Conexões do hardware

| Componente | Pino Arduino |
|------------|-------------|
| Sensor de umidade (sinal) | A0 |
| Módulo relé | 7 |

---

## Estrutura do projeto

```
├── BombaIrrigacaoArd.ino   # Sketch do Arduino
├── servidor.py             # Servidor HTTP + leitura serial
└── index.html              # Painel de controle web
```
O que cada integrante do grupo fez para o projeto:

Erick Prata e Daniel Tozato: Montagem e Código e HTML
Emanuel Domingos: Montagem
Gabriel Andrade: HTML
Lucas Lago: Trello