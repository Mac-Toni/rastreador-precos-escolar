import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from colorama import Fore, Style, init
from datetime import datetime
import time
import os

init(autoreset=True)

class RastreadorPrecos:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        # options.add_argument('--headless') 
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.resultados = []

    def formatar_brl(self, valor):
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def extrair_valor(self, texto):
        try:
            limpo = texto.replace('R$', '').replace('.', '').replace(',', '.').strip()
            return float(limpo)
        except:
            return 99999.0

    def limpar_relatorios_antigos(self, pasta, limite=3):
        arquivos = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.xlsx')]
        arquivos.sort(key=os.path.getmtime)
        if len(arquivos) > limite:
            for arquivo in arquivos[:-limite]:
                try:
                    os.remove(arquivo)
                    print(f"{Fore.YELLOW}🗑️ Faxina: Removendo antigo: {os.path.basename(arquivo)}")
                except: pass

    def buscar_amazon(self, termo):
        self.driver.get(f"https://www.amazon.com.br/s?k={termo}")
        time.sleep(2)
        try:
            nome_site = self.driver.find_element(By.CSS_SELECTOR, "h2 a span").text
            inteiro = self.driver.find_element(By.CLASS_NAME, "a-price-whole").text
            fracao = self.driver.find_element(By.CLASS_NAME, "a-price-fraction").text
            return self.extrair_valor(f"{inteiro},{fracao}"), self.driver.current_url, nome_site
        except:
            return 99999.0, "", "Não encontrado"

    def buscar_kalunga(self, termo):
        self.driver.get(f"https://www.kalunga.com.br/busca/{termo}")
        time.sleep(2)
        try:
            nome_site = self.driver.find_element(By.CSS_SELECTOR, ".produc-item__title").text
            preco_texto = self.driver.find_element(By.CSS_SELECTOR, ".produc-item__price").text
            return self.extrair_valor(preco_texto), self.driver.current_url, nome_site
        except:
            return 99999.0, "", "Não encontrado"

    def buscar_mercadolivre(self, termo):
        """Nova loja substituindo a Gimba"""
        try:
            self.driver.get(f"https://lista.mercadolivre.com.br/{termo}")
            time.sleep(2)
            # Pega o primeiro título e preço da lista
            nome_site = self.driver.find_element(By.CLASS_NAME, "ui-search-item__title").text
            preco_texto = self.driver.find_element(By.CLASS_NAME, "andes-money-amount__fraction").text
            # Se houver centavos, o ML usa uma estrutura diferente, mas para busca rápida o inteiro resolve ou pegamos o container
            return self.extrair_valor(preco_texto), self.driver.current_url, nome_site
        except:
            return 99999.0, "", "Não encontrado"

    def processar_lista(self, arquivo_entrada):
        if not os.path.exists(arquivo_entrada):
            print(f"{Fore.RED}❌ Erro: '{arquivo_entrada}' não encontrado!")
            return

        df = pd.read_excel(arquivo_entrada)
        print(f"{Fore.MAGENTA}{Style.BRIGHT}🚀 Iniciando Busca Refinada (Sem Gimba, Com ML)")

        for index, row in df.iterrows():
            item_nome = str(row['Item'])
            espec = str(row['Especificação']) if pd.notna(row['Especificação']) else ""
            qtd = int(row['Quantidade Sugerida']) if pd.notna(row['Quantidade Sugerida']) else 1
            termo_final = f"{item_nome} {espec}".strip()

            print(f"\n{Fore.CYAN}🔎 Pesquisando: {termo_final}")

            v_ama, l_ama, n_ama = self.buscar_amazon(termo_final)
            v_kal, l_kal, n_kal = self.buscar_kalunga(termo_final)
            v_ml, l_ml, n_ml = self.buscar_mercadolivre(termo_final)

            ofertas = {
                'Amazon': (v_ama, l_ama, n_ama),
                'Kalunga': (v_kal, l_kal, n_kal),
                'Mercado Livre': (v_ml, l_ml, n_ml)
            }

            validos = {loja: dados for loja, dados in ofertas.items() if 0.50 < dados[0] < 90000}

            if validos:
                loja_venc = min(validos, key=lambda k: validos[k][0])
                preco_unit, link_venc, nome_venc = validos[loja_venc]
                
                precos_encontrados = [v[0] for v in validos.values()]
                economia = max(precos_encontrados) - preco_unit

                print(f"{Fore.GREEN}✅ Vencedor: {loja_venc} | {self.formatar_brl(preco_unit)}")
                
                self.resultados.append({
                    'Item Original': item_nome,
                    'Especificação Enviada': espec,
                    'Descrição no Site (Vencedor)': nome_venc,
                    'Qtd': qtd,
                    'Menor Preço Unitário': self.formatar_brl(preco_unit),
                    'Preço Total': self.formatar_brl(preco_unit * qtd),
                    'Loja': loja_venc,
                    'Economia Unitária': self.formatar_brl(economia),
                    'Link': link_venc,
                    'Data': datetime.now().strftime("%d/%m/%Y %H:%M")
                })
            else:
                print(f"{Fore.RED}❌ Nenhum resultado confiável.")

        self.driver.quit()

        if self.resultados:
            pasta = "relatorios_precos"
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
            pd.DataFrame(self.resultados).to_excel(caminho, index=False)
            print(f"\n{Fore.GREEN}✅ Relatório salvo com sucesso!")
            self.limpar_relatorios_antigos(pasta, limite=3)
        else:
            print(f"\n{Fore.RED}❌ Nenhum dado coletado.")

if __name__ == "__main__":
    bot = RastreadorPrecos()
    bot.processar_lista("lista_consolidada.xlsx")