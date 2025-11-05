import paho.mqtt.client as mqtt
import json
import time
import threading
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# A linha abaixo é específica para ambientes como Jupyter Notebook
# from IPython.display import display, clear_output

# =========== Configurações do MQTT =============
# Devem ser EXATAMENTE as mesmas do código do ESP32
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
# Tópico para o sensor de GÁS MQ-2
MQTT_TOPIC = "br/com/meuprojeto/esp32c3/mq2"

# =========== Configurações de Plotagem =============
READ_INTERVAL = 5   # Intervalo de atualização do gráfico (em segundos)
MAX_POINTS = 100    # Quantidade máxima de pontos a manter no gráfico

# --- Variáveis globais para buffer de dados ---
data_buffer = {
    "timestamp": [],
    "valorAnalogico": [],
    "statusDigital": [] # Usaremos 1 para GÁS_DETECTADO e 0 para NORMAL
}
# Lock para garantir que a escrita e leitura do buffer não aconteçam ao mesmo tempo
buffer_lock = threading.Lock()

# --- Funções MQTT ---

# Esta função será chamada toda vez que uma nova mensagem chegar no tópico
def on_message(client, userdata, msg):
    """
    Processa as mensagens MQTT recebidas do sensor MQ-2.
    """
    try:
        # Decodifica a mensagem (payload) de bytes para string
        payload_str = msg.payload.decode()
        print(f"Mensagem recebida: {payload_str}")
        
        # Converte a string JSON para um dicionário Python
        data = json.loads(payload_str)
        
        analog_value = data.get("valorAnalogico")
        status_str = data.get("status")
        
        if analog_value is not None and status_str is not None:
            # Converte o status de texto para um valor numérico para o gráfico
            digital_status = 1 if status_str == "GAS_DETECTADO" else 0
            
            # Trava o buffer para adicionar os novos dados com segurança
            with buffer_lock:
                data_buffer["timestamp"].append(datetime.now())
                data_buffer["valorAnalogico"].append(analog_value)
                data_buffer["statusDigital"].append(digital_status)
                
                # Mantém o buffer com no máximo MAX_POINTS para não sobrecarregar a memória
                if len(data_buffer["timestamp"]) > MAX_POINTS:
                    for key in data_buffer:
                        data_buffer[key].pop(0)
                        
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Função para plotar os dados do buffer
def plot_buffer():
    """
    Cria e exibe um gráfico em tempo real com os dados do sensor.
    """
    with buffer_lock:
        # Cria uma cópia para evitar problemas de concorrência durante a plotagem
        df = pd.DataFrame(data_buffer.copy())
        
    if df.empty:
        print("Aguardando os primeiros dados do sensor MQ-2...")
        return

    # Cria uma figura com um eixo Y secundário para o status digital
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Adiciona a linha da leitura analógica
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["valorAnalogico"], mode="lines+markers", name="Leitura Analógica (Gás)"),
        secondary_y=False
    )
    
    # Adiciona a linha do status digital (Detectado/Normal)
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["statusDigital"], mode="lines+markers", name="Detecção de Gás", line=dict(shape='hv')), # 'hv' cria uma linha em degraus
        secondary_y=True
    )
    
    fig.update_layout(
        title_text="Monitoramento de Gás (MQ-2) em Tempo Real via MQTT",
        xaxis_title="Horário"
    )
    
    # Configura o eixo Y primário (analógico)
    fig.update_yaxes(title_text="<b>Valor Analógico</b>", secondary_y=False)
    
    # Configura o eixo Y secundário (digital)
    fig.update_yaxes(
        title_text="<b>Status</b>", 
        secondary_y=True,
        tickvals=[0, 1], # Define as posições dos ticks
        ticktext=["Normal", "Gás Detectado"] # Define os rótulos dos ticks
    )
    
    # # Limpa a saída anterior e exibe o novo gráfico (funciona em Jupyter)
    # clear_output(wait=True)
    # display(fig)

# --- Programa Principal ---
if __name__ == "__main__":
    # Cria um cliente MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    # Associa a função on_message ao cliente
    client.on_message = on_message

    print(f"Conectando ao Broker MQTT em {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    print(f"Inscrevendo-se no tópico: {MQTT_TOPIC}")
    client.subscribe(MQTT_TOPIC)

    # Inicia o loop de rede do MQTT em uma thread separada.
    # Isso permite que o programa continue rodando enquanto escuta as mensagens.
    client.loop_start()

    print("Setup completo. O gráfico será atualizado abaixo a cada 5 segundos.")
    print("Pressione CTRL+C para parar.")

    # Loop principal para plotar o gráfico
    try:
        while True:
            # Em um ambiente como o Jupyter, a função plot_buffer será chamada
            # para atualizar o gráfico. Em um terminal, você pode querer apenas
            # imprimir os dados ou salvar em um arquivo.
            plot_buffer()
            time.sleep(READ_INTERVAL)
    except KeyboardInterrupt:
        print("\nParando o cliente MQTT...")
        client.loop_stop()
        print("Programa finalizado.")