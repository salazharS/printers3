
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
import sys

def get_app_path():
    if getattr(sys, 'frozen', False): 
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    """Carrega a configuração dos IDs de coleta de dados"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuração padrão para HP, se o arquivo não existir
        return {
            "hp_ids": {
                "toner_percentage_prefix": "SupplyPLR",
                "toner_name_prefix": "SupplyName",
            }
        }

def load_printer_data(filename="printer_data.json"):
    """Carrega os dados das impressoras do arquivo JSON"""
    try:
        with open(os.path.join(get_app_path(), filename), "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado!")
        return []
    except json.JSONDecodeError:
        print(f"Erro ao ler o arquivo {filename}!")
        return []

def save_collected_data(data, filename="collected_data.json"):
    """Salva os dados coletados no arquivo JSON especificado"""
    try:
        with open(os.path.join(get_app_path(), filename), "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados em {filename}: {e}")
        return False

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

class TerminalProgressBar:
    """Barra de progresso para o terminal"""
    def __init__(self, total, width=50):
        self.total = total
        self.width = width
        self.current = 0
        self.success_count = 0
        self.error_count = 0

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def update(self, current, status_text="", printer_name=""):
        self.current = current
        percentage = (current / self.total) * 100 if self.total > 0 else 0
        filled = int(self.width * current / self.total) if self.total > 0 else 0
        bar = '█' * filled + '░' * (self.width - filled)
        
        self.clear_screen()
        
        print("╔" + "═" * 70 + "╗")
        print(f"║{'COLETANDO DADOS DAS IMPRESSORAS':^70}║")
        print("╠" + "═" * 70 + "╣")
        print(f"║ Progresso: [{bar}] {percentage:6.1f}%{' ' * (70 - len(f'Progresso: [{bar}] {percentage:6.1f}%') - 1)}║")
        print(f"║ Processando: {current:3d} de {self.total:3d} impressoras{' ' * (70 - len(f' Processando: {current:3d} de {self.total:3d} impressoras') - 1)}║")
        print("╠" + "═" * 70 + "╣")
        print(f"║ Total: {self.total:3d} | Processadas: {current:3d} | Sucesso: {self.success_count:3d} | Erros: {self.error_count:3d}{' ' * (70 - len(f' Total: {self.total:3d} | Processadas: {current:3d} | Sucesso: {self.success_count:3d} | Erros: {self.error_count:3d}') - 1)}║")
        print("╠" + "═" * 70 + "╣")
        
        if status_text:
            status_text = status_text[:66] + "..." if len(status_text) > 66 else status_text
            print(f"║ Status: {status_text:<62} ║")
        
        if printer_name:
            printer_name = printer_name[:60] + "..." if len(printer_name) > 60 else printer_name
            print(f"║ Atual: {printer_name:<63} ║")
            
        print("╚" + "═" * 70 + "╝")
        sys.stdout.flush()

    def increment_success(self):
        self.success_count += 1
        
    def increment_error(self):
        self.error_count += 1
        
    def finish(self):
        self.clear_screen()
        print("╔" + "═" * 70 + "╗")
        print(f"║{'PROCESSAMENTO CONCLUÍDO!':^70}║")
        print("╠" + "═" * 70 + "╣")
        print(f"║ Total de impressoras processadas: {self.total:3d}{' ' * (70 - len(f' Total de impressoras processadas: {self.total:3d}') - 1)}║")
        print(f"║ Sucessos: {self.success_count:3d}{' ' * (70 - len(f' Sucessos: {self.success_count:3d}') - 1)}║")
        print(f"║ Erros: {self.error_count:3d}{' ' * (70 - len(f' Erros: {self.error_count:3d}') - 1)}║")
        print("╠" + "═" * 70 + "╣")
        print(f"║{'Salvando dados coletados...':^70}║")
        print("╚" + "═" * 70 + "╝")
        time.sleep(2)

def get_toner_color(toner_name):
    """Retorna a cor correspondente ao tipo de toner"""
    name_lower = toner_name.lower()
    if "amarelo" in name_lower or "yellow" in name_lower:
        return "#FFD700"  # Amarelo
    elif "magenta" in name_lower:
        return "#FF1493"  # Magenta
    elif "ciano" in name_lower or "cyan" in name_lower:
        return "#00BFFF"  # Ciano
    elif "preto" in name_lower or "black" in name_lower:
        return "#000000"  # Preto
    elif "fusor" in name_lower or "fuser" in name_lower:
        return "#808080"  # Cinza para fusor
    elif "alimentador" in name_lower or "feeder" in name_lower:
        return "#A0A0A0"  # Cinza para alimentador
    return "#808080" # Cor padrão

def collect_printer_data(printers_list, config, progress_bar=None):
    """Coleta dados das impressoras e retorna uma lista de dicionários."""
    collected_data = []
    hp_ids = config.get("hp_ids", {})
    
    for index, printer in enumerate(printers_list):
        current_printer_num = index + 1
        ip = printer["ip"]
        printer_name = printer["name"]
        url = f"http://{ip}"
        
        if progress_bar:
            progress_bar.update(current_printer_num, f"Conectando a {ip}...", printer_name)
        
        printer_info = {
            **printer, # Inclui todos os dados originais de printer_data.json
            "id": index + 1,
            "status": "error",
            "toners": [],
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "errorMessage": "Não foi possível conectar à impressora."
        }

        try:
            response = requests.get(url, verify=False, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            toners = []
            toner_percentage_prefix = hp_ids.get("toner_percentage_prefix", "SupplyPLR")
            toner_name_prefix = hp_ids.get("toner_name_prefix", "SupplyName")

            for i in range(6): # Tenta IDs de 0 a 5 para toners
                supply_id = f"{toner_percentage_prefix}{i}"
                supply_name_id = f"{toner_name_prefix}{i}"
                
                toner_percentage_tag = soup.find("span", id=supply_id)
                toner_name_tag = soup.find("h2", id=supply_name_id)

                if toner_percentage_tag and toner_name_tag:
                    percentage_text = toner_percentage_tag.text.strip()
                    name = toner_name_tag.text.strip()
                    percentage_num_str = re.sub(r'[^0-9]', '', percentage_text)
                    percentage_num = int(percentage_num_str) if percentage_num_str else 0
                    
                    toners.append({
                        "name": name,
                        "color": get_toner_color(name),
                        "level": percentage_num
                    })
            
            # Define o status geral da impressora
            printer_info["status"] = "online"
            if any(t["level"] <= 10 for t in toners if "kit" not in t["name"].lower()):
                 printer_info["status"] = "alerta"

            printer_info["toners"] = toners
            printer_info["errorMessage"] = None
            
            if progress_bar:
                progress_bar.increment_success()

        except requests.exceptions.RequestException as e:
            printer_info["errorMessage"] = f"Erro de conexão: {str(e)}"
            if progress_bar:
                progress_bar.increment_error()
        except Exception as e:
            printer_info["errorMessage"] = f"Erro inesperado: {str(e)}"
            if progress_bar:
                progress_bar.increment_error()
        
        collected_data.append(printer_info)
        time.sleep(0.1) # Pequeno delay para evitar sobrecarga

    return collected_data

def main():
    """Função principal do programa que inicia a coleta automaticamente"""
    clear_screen()
    print("Iniciando coleta de dados das impressoras...")
    
    printers = load_printer_data()
    
    if not printers:
        print("Nenhuma impressora cadastrada em printer_data.json. Abortando coleta.")
        sys.exit(1)
    
    config = load_config()
    progress_bar = TerminalProgressBar(len(printers))
    
    collected_data = collect_printer_data(printers, config, progress_bar)
    
    progress_bar.finish()
    
    output_filename = "collected_data.json"
    if save_collected_data(collected_data, filename=output_filename):
        clear_screen()
        print("╔" + "═" * 70 + "╗")
        print(f"║{'PROCESSO FINALIZADO!':^70}║")
        print("╠" + "═" * 70 + "╣")
        print(f"║ ✅ Dados coletados com sucesso!{' ' * (70 - len(' ✅ Dados coletados com sucesso!') - 1)}║")
        print(f"║ Arquivo salvo como: {output_filename}{' ' * (70 - len(f' Arquivo salvo como: {output_filename}') - 1)}║")
        print("╚" + "═" * 70 + "╝")
    else:
        print("Erro ao salvar os dados coletados.")
    
    print("Coleta de dados concluída.")

if __name__ == "__main__":
    main()