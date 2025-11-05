# Projeto IoT: Monitor de Gás com ESP32-C3 e Dashboard Python

Este repositório contém o código-fonte para um projeto de Internet das Coisas (IoT) que utiliza um microcontrolador ESP32-C3 e um sensor de gás MQ-2 para monitorar a qualidade do ar em tempo real. Os dados coletados são enviados via protocolo MQTT para um dashboard interativo desenvolvido em Python com as bibliotecas Plotly e Pandas.

![GIF do Dashboard em Funcionamento](https://i.imgur.com/placeholder.gif)  
*(Sugestão: grave um GIF do seu dashboard funcionando e substitua o link acima)*

## ✨ Funcionalidades

*   Leitura contínua dos níveis de gás com o sensor MQ-2 (saídas analógica e digital).
*   Conexão do microcontrolador à internet via Wi-Fi.
*   Comunicação leve e em tempo real utilizando o protocolo MQTT.
*   Dashboard interativo que exibe os dados em um gráfico atualizado automaticamente.
*   Visualização com fuso horário ajustado para Brasília (UTC-3).
*   Código modular e comentado para fácil entendimento.

## 🔧 Como Funciona

A arquitetura do projeto é dividida em duas partes principais: o **Hardware Embarcado (ESP32)** e o **Dashboard (Python)**, que se comunicam através de um **Broker MQTT** na internet.

`[ESP32 + Sensor MQ-2] --(WiFi)--> [Broker MQTT HiveMQ] --(Internet)--> [Script Python] --> [Dashboard Interativo]`

1.  O **ESP32** lê os dados do sensor MQ-2.
2.  Ele se conecta à rede Wi-Fi local.
3.  Os dados são formatados em JSON e publicados em um tópico MQTT no broker público do HiveMQ.
4.  O **Script Python** (Jupyter Notebook) está inscrito no mesmo tópico, recebendo os dados assim que são publicados.
5.  Os dados recebidos são processados e armazenados em um buffer.
6.  A cada 5 segundos, o gráfico na tela é atualizado com os novos dados, criando uma visualização em tempo real.

## 📂 Estrutura dos Arquivos

O projeto está organizado nos seguintes arquivos:

### 1. `ESP32_MQ2_MQTT/ESP32_MQ2_MQTT.ino`

Este é o código que deve ser carregado no ESP32-C3. Suas principais responsabilidades são:
*   Inicializar o sensor MQ-2.
*   Conectar-se à rede Wi-Fi.
*   Conectar-se ao broker MQTT.
*   Ler os valores analógico e digital do sensor a cada 5 segundos.
*   Formatar os dados em um pacote JSON (ex: `{"valorAnalogico": 350, "status": "NORMAL"}`).
*   Publicar o JSON no tópico MQTT `br/com/meuprojeto/esp32c3/mq2`.
*   Manter a conexão com o broker estável.

### 2. `Dashboard_Python/Dashboard_MQ2.ipynb`

Este é o Jupyter Notebook que funciona como nosso cliente e interface de visualização. Suas funções são:
*   Conectar-se ao mesmo broker MQTT.
*   Inscrever-se no tópico `br/com/meuprojeto/esp32c3/mq2` para ouvir as mensagens.
*   Receber os pacotes JSON, decodificá-los e processar os dados.
*   Armazenar os dados em um buffer em memória com timestamp ajustado.
*   Utilizar Plotly para gerar e atualizar um gráfico interativo em tempo real, mostrando o nível de gás e o status da detecção.

## 🚀 Como Executar

Siga os passos abaixo para colocar o projeto em funcionamento.

### Pré-requisitos

#### Hardware
*   ESP32-C3 Super Mini (ou similar)
*   Sensor de Gás MQ-2
*   Jumper wires (fios de conexão)

#### Software (ESP32)
*   [Arduino IDE](https://www.arduino.cc/en/software)
*   Placas ESP32 instaladas na Arduino IDE.
*   Bibliotecas Arduino:
    *   `WiFi` (geralmente já incluída)
    *   `PubSubClient` (por Nick O'Leary)
    *   `ArduinoJson` (por Benoît Blanchon)

#### Software (Python)
*   Python 3.7+
*   Jupyter Notebook ou JupyterLab
*   Bibliotecas Python (instale via pip):
    ```sh
    pip install paho-mqtt pandas plotly notebook
    ```

### Passo 1: Montagem do Hardware

Conecte o sensor MQ-2 ao ESP32 da seguinte forma:
*   **VCC** do sensor -> **5V** ou **3.3V** do ESP32
*   **GND** do sensor -> **GND** do ESP32
*   **A0** (saída analógica) do sensor -> **GPIO3** (ou pino ADC de sua preferência) do ESP32
*   **D0** (saída digital) do sensor -> **GPIO4** (ou pino digital de sua preferência) do ESP32

### Passo 2: Configuração do ESP32

1.  Abra o arquivo `ESP32_MQ2_MQTT.ino` na Arduino IDE.
2.  **Altere as credenciais de Wi-Fi** nas linhas abaixo com os dados da sua rede:
    ```cpp
    const char* ssid = "[Nome da Rede WI-Fi]";
    const char* password = "[Senha do seu Wi-fi]";
    ```
3.  Instale as bibliotecas `PubSubClient` e `ArduinoJson` através do *Library Manager* da IDE.
4.  Selecione a placa correta (ex: "XIAO_ESP32C3") e a porta COM correspondente.
5.  Compile e carregue o código no ESP32.
6.  Abra o Serial Monitor para verificar se ele conectou ao Wi-Fi e ao MQTT com sucesso.

### Passo 3: Executando o Dashboard

1.  Abra um terminal ou prompt de comando.
2.  Navegue até a pasta do projeto.
3.  Inicie o Jupyter Notebook com o comando:
    ```sh
    jupyter notebook
    ```
4.  No seu navegador, abra o arquivo `Dashboard_MQ2.ipynb`.
5.  Execute todas as células do notebook (no menu, *Cell -> Run All*).
6.  Um gráfico aparecerá na saída da última célula. Ele começará a ser preenchido e atualizado automaticamente assim que o ESP32 enviar a primeira mensagem.

Pronto! Agora você tem um sistema de monitoramento de gás completo e funcional.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
*Este README foi gerado com base nos códigos do projeto.*
