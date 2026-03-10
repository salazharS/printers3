# 🖨️ Printers3

Sistema local de **monitoramento de impressoras corporativas**, que coleta dados automaticamente (status, nível de toner, conectividade) e exibe tudo em um **painel web interativo**.

---

## 📋 Sumário

- [Visão Geral](#-visao-geral)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Instalação e Configuração](#-instalacao-e-configuracao)
- [Como Executar](#-como-executar)
- [Funcionamento Técnico e Ajustes Necessários](#-funcionamento-tecnico-e-ajustes-necessarios)
- [Funcionalidades do Painel Web](#-funcionalidades-do-painel-web)
- [Capturas de Tela](#-capturas-de-tela)
---

## 🚀 Visão Geral

Este projeto realiza a **coleta automatizada de informações das impressoras da rede** e gera relatórios visuais para facilitar o controle de insumos e status.  
É útil para equipes de **suporte técnico e infraestrutura** que precisam acompanhar múltiplas impressoras distribuídas em diferentes unidades.

---

## 🧱 Arquitetura do Projeto

```
📂 printer-dashboard/
 ├── printer_collector.py       # Script principal de coleta (Python)
 ├── printer_data.json          # Lista base de impressoras e IPs
 ├── collected_data.json        # Resultado consolidado da coleta
 ├── printer_dashboard.html     # Painel web interativo
 ├── leia-me.txt                # Guia rápido de instalação
 └── README.md                  # Este documento
```

### 🔹 Componentes principais

| Componente | Função |
|-------------|--------|
| **Collector (Python)** | Conecta às impressoras via HTTP, extrai níveis de toner e status, salva tudo em JSON. |
| **Dashboard (HTML/JS)** | Lê os dados coletados e exibe estatísticas, alertas e filtros interativos. |

---

## ⚙️ Instalação e Configuração

### 1. Instalar o Python (versão 3.9 ou superior)

No Windows:
```bash
winget install Python.Python.3.9
```

Verifique a instalação:
```bash
python --version
```

### 2. Instalar as dependências

No terminal (cmd ou PowerShell), execute:
```bash
pip install requests bs4
pip install requests request
```

### 3. Configurar as impressoras

Edite o arquivo `printer_data.json` e adicione suas impressoras conforme o modelo abaixo:
Não possui limites de equipamentos.

```json
[
  {
    "id": 1,
    "name": "Impressora do Escritorio",
    "assetTag": "7172",
    "serial": "ST7812",
    "model": "HP LaserJet Pro",
    "location": "São Paulo",
    "ip": "192.168.15.2",
    "status": "",
    "toners": [],
    "lastUpdate": "",
    "errorMessage": ""
  },
  {
    "id": 2,
    "name": "Impressora do CD",
    "assetTag": "8182",
    "serial": "ST7813",
    "model": "HP LaserJet Pro",
    "location": "Cajamar",
    "ip": "192.168.15.3",
    "status": "",
    "toners": [],
    "lastUpdate": "",
    "errorMessage": ""
  }
]
```

Cada IP deve ser acessível na rede (porta 80 habilitada).

---

## ▶️ Como Executar

### 1. Rodar o coletor

No terminal, dentro da pasta do projeto:

```bash
python printer_collector.py
```

Durante a execução:
- O script exibirá uma **barra de progresso animada** no terminal.
- Os dados serão salvos automaticamente em `collected_data.json`.

### 2. Visualizar o painel

Para hospede localmente:
```bash
python -m http.server 8080
```
E acesse:  
👉 [http://localhost:8080/printer_dashboard.html](http://localhost:8080/printer_dashboard.html)

---

## 🧠 Funcionamento Técnico

1. O script lê `printer_data.json`.
2. Para cada impressora:
   - Faz uma requisição HTTP ao IP (`http://192.168.1.X`).
   - Usa **BeautifulSoup** para extrair IDs do HTML (`SupplyName0`, `SupplyPLR0`, etc.).
   - Converte os dados em JSON estruturado.
3. Determina o **status**:
   - 🟢 `online` → Conexão e toner OK.  
   - 🟠 `alerta` → Algum toner ≤ 10%.  
   - 🔴 `error` → Impressora inacessível.
4. Atualiza o `collected_data.json` com data/hora e erros, se houver.
5. O painel web lê esse arquivo e mostra tudo em tempo real (sem precisar atualizar manualmente).
6. hp_ids são ids definidos na pagia http da propria impressora, para outros modelosm substitua o campo abaixo pelo id correto de cada fabricante 
6. `hp_ids` são IDs definidos na página HTTP da própria impressora. Para outros modelos, substitua os prefixos pelo ID correto de cada fabricante. Se a página não usar os mesmos elementos (por exemplo, `span` para o percentual e `h2` para o nome), além de trocar o ID pode ser necessário ajustar os seletores no código. 
 <img width="616" height="122" alt="image" src="https://github.com/user-attachments/assets/1037c2ce-e5c7-4b8c-a4f7-900b4aed1ad4" />


---

## 💻 Funcionalidades do Painel Web

✅ **Resumo geral**
- Total de impressoras
- Quantas estão online, em alerta ou com erro

✅ **Filtros e buscas**
- Por status, local, cor de toner e percentual
- Busca global por nome, IP, serial, ou asset tag

✅ **Alertas automáticos**
- Notificações (“toasts”) de toner baixo, esgotado ou impressora offline

✅ **Modais detalhados**
- Exibe informações completas e níveis de toner individuais

✅ **Exportação**
- Geração de relatórios em PDF (`html2pdf.js`)

✅ **Interface responsiva**
- Compatível com desktops, notebooks e tablets

---

## 🖼️ Capturas de Tela 

<img width="1898" height="925" alt="image" src="https://github.com/user-attachments/assets/ca5ab547-15a0-4480-83da-6a4b96280829" />
> - `printer_dashboard.html` — Dashboard do printers 3

---

🧠 **Resumo:**  
> Edite `printer_data.json`, execute o `printer_collector.py` (após customizar os ids) → ele gera o `collected_data.json` → hospede localmente: `python -m http.server 8080` → acesse [http://localhost:8080/printer_dashboard.html](http://localhost:8080/printer_dashboard.html) 
