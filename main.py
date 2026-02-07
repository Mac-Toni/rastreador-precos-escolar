import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from colorama import Fore, Style, init
from datetime import datetime
import time
import os

# Inicializa as cores no terminal do VS Code
init(autoreset=True)

class RastreadorPrecos:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # User-Agent para evitar bloqueios da Lepok e Amazon
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        # options.add_argument('--headless') # Descomenta para rodar sem abrir a janela
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.resultados = []

    def formatar_brl(self, valor):
        """Converte float para o formato de moeda R$"""
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def extrair_valor(self, texto):
        """Limpa o texto do preço vindo do site e converte para float"""
        try:
            limpo = texto.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(limpo)
        except:
            return 99999.0

    # --- Métodos de Busca Individuais ---
    def buscar_amazon(self, termo):
        self.driver.get(f"https://www.amazon.com.br/s?k={termo}")
        time.sleep(2)
        try:
            inteiro = self.driver.find_element(By.CLASS_NAME, "a-price-whole").text
            fracao = self.driver.find_element(By.CLASS_NAME, "a-price-fraction").text
            return self.extrair_valor(f"{inteiro},{fracao}"), self.driver.current_url
        except:
            return 99999.0, ""

    def buscar_kalunga(self, termo):
        self.driver.get(f"https://www.kalunga.com.br/busca/{termo}")
        time.sleep(2)
        try:
            preco_texto = self.driver.find_element(By.CSS_SELECTOR, ".produc-item__price").text
            return self.extrair_valor(preco_texto), self.driver.current_url
        except:
            return 99999.0, ""

    def buscar_lepok(self, termo):
        termo_url = termo.replace(" ", "%20")
        self.driver.get(f"https://www.lepok.com.br/busca?t={termo_url}")
        time.sleep(3)
        try:
            preco_texto = self.driver.find_element(By.CSS_SELECTOR, ".price, .vtex-product-summary-2-x-currencyInteger").text
            return self.extrair_valor(preco_texto), self.driver.current_url
        except:
            return 99999.0, ""

    # --- Processamento da Lista ---
    def processar_lista(self, arquivo_entrada):
        # Carrega a planilha enviada
        df = pd.read_excel(arquivo_entrada)
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🚀 A iniciar procura REFINADA em {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        for index, row in df.iterrows():
            item_nome = str(row['Item'])
            espec = str(row['Especificação']) if pd.notna(row['Especificação']) else ""
            qtd = int(row['Quantidade Sugerida']) if pd.notna(row['Quantidade Sugerida']) else 1
            
            termo_final = f"{item_nome} {espec}".strip()
            print(f"\n{Fore.CYAN}🔎 Produto: {termo_final}")

            v_ama, l_ama = self.buscar_amazon(termo_final)
            v_kal, l_kal = self.buscar_kalunga(termo_final)
            v_lep, l_lep = self.buscar_lepok(termo_final)

            ofertas = {
                'Amazon': (v_ama, l_ama),
                'Kalunga': (v_kal, l_kal),
                'Lepok': (v_lep, l_lep)
            }

            validos = {loja: dados for loja, dados in ofertas.items() if 0.50 < dados[0] < 90000}

            if validos:
                loja_venc = min(validos, key=lambda k: validos[k][0])
                preco_unitario, link_venc = validos[loja_venc]

                precos_encontrados = [v[0] for v in validos.values()]
                economia_unitaria = max(precos_encontrados) - preco_unitario
                preco_total = preco_unitario * qtd

                print(f"{Fore.GREEN}✅ Melhor: {loja_venc} | Unit: {self.formatar_brl(preco_unitario)} | Total: {self.formatar_brl(preco_total)}")

                self.resultados.append({
                    'Item': item_nome,
                    'Busca Realizada': termo_final,
                    'Qtd': qtd,
                    'Menor Preço Unitário': self.formatar_brl(preco_unitario),
                    'Preço Total (Qtd)': self.formatar_brl(preco_total),
                    'Loja': loja_venc,
                    'Economia Unitária': self.formatar_brl(economia_unitaria),
                    'Link': link_venc,
                    'Atualizado em': datetime.now().strftime("%d/%m/%Y %H:%M")
                })
            else:
                print(f"{Fore.RED}❌ Sem resultados para: {termo_final}")

        self.driver.quit()

        # Guardar com carimbo de data/hora para o teu histórico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_ficheiro = f"relatorio_precos_{timestamp}.xlsx"

        # Cria a pasta "relatorios_precos" se não existir
        pasta_relatorios = "relatorios_precos"
        os.makedirs(pasta_relatorios, exist_ok=True)

        # Caminho completo do arquivo dentro da pasta
        caminho_final = os.path.join(pasta_relatorios, nome_ficheiro)

        df_final = pd.DataFrame(self.resultados)
        df_final.to_excel(caminho_final, index=False)

        print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ PROCESSO FINALIZADO!")
        print(f"{Fore.YELLOW}Relatório gerado com sucesso: {caminho_final}")

if __name__ == "__main__":
    bot = RastreadorPrecos()
    bot.processar_lista("lista_consolidada.xlsx")
