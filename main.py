import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, Style, init
from datetime import datetime
import os
import re
import time

init(autoreset=True)

SITES_CONFIG = {
    'Amazon': {
        'url': "https://www.amazon.com.br/s?k=",
        'item': ["h2 a span", "span.a-size-base-plus", ".s-line-clamp-2"],
        'preco_inteiro': [".a-price-whole"],
        'preco_fracao': [".a-price-fraction"]
    },
    'Kalunga': {
        'url': "https://www.kalunga.com.br/",
        'search_box': "input#search-input, input.search-input",
        'item': [".produc-item__title", "h2.produc-item__title", ".product-item__title"],
        'preco_completo': [".produc-item__price", ".product-item__price"]
    },
    'Mercado Livre': {
        'url': "https://lista.mercadolivre.com.br/",
        'item': [".poly-component__title", ".ui-search-item__title", "h2.ui-search-item__title"],
        'preco_inteiro': [".poly-price__current .andes-money-amount__fraction", ".andes-money-amount__fraction"],
        'preco_fracao': [".poly-price__current .andes-money-amount__cents", ".andes-money-amount__cents"]
    }
}

class RastreadorPrecos:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.execute_script("document.title = 'Material Escolar'")
        self.wait = WebDriverWait(self.driver, 10)
        self.resultados = []

    def limpar_valor(self, texto):
        if not texto: return 99999.0
        try:
            limpo = texto.replace('.', '').replace(',', '.')
            res = re.findall(r"\d+\.\d+|\d+", limpo)
            return float(res[0]) if res else 99999.0
        except: return 99999.0

    def tentar_elementos(self, seletores):
        for seletor in seletores:
            try:
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                if elemento.is_displayed(): return elemento
            except: continue
        return None

    def buscar_kalunga_manual(self, termo):
        try:
            self.driver.get(SITES_CONFIG['Kalunga']['url'])
            busca = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SITES_CONFIG['Kalunga']['search_box'])))
            busca.clear()
            busca.send_keys(termo)
            busca.send_keys(Keys.ENTER)
            time.sleep(3.5)
            el_nome = self.tentar_elementos(SITES_CONFIG['Kalunga']['item'])
            el_preco = self.tentar_elementos(SITES_CONFIG['Kalunga']['preco_completo'])
            if el_nome and el_preco:
                return self.limpar_valor(el_preco.text), self.driver.current_url, el_nome.text
            return 99999.0, "", "Não encontrado"
        except: return 99999.0, "", "Erro Kalunga"

    def buscar_loja(self, loja, termo):
        if loja == 'Kalunga': return self.buscar_kalunga_manual(termo)
        config = SITES_CONFIG[loja]
        self.driver.get(f"{config['url']}{termo.replace(' ', '+')}")
        try:
            time.sleep(2.5)
            self.driver.execute_script("window.scrollTo(0, 500);")
            el_nome = self.tentar_elementos(config['item'])
            if not el_nome: return 99999.0, "", "Não encontrado"
            valor = 99999.0
            if 'preco_completo' in config:
                el_preco = self.tentar_elementos(config['preco_completo'])
                if el_preco: valor = self.limpar_valor(el_preco.text)
            else:
                el_int = self.tentar_elementos(config['preco_inteiro'])
                if el_int:
                    frac = "00"
                    el_frac = self.tentar_elementos(config['preco_fracao'])
                    if el_frac: frac = el_frac.text
                    valor = self.limpar_valor(f"{el_int.text}.{frac}")
            return valor, self.driver.current_url, el_nome.text
        except: return 99999.0, "", "Erro na leitura"

    def processar_lista(self, arquivo_entrada):
        df = pd.read_excel(arquivo_entrada)
        print(f"{Fore.MAGENTA}🚀 BUSCA INICIADA - Janela: Material Escolar")
        for _, row in df.iterrows():
            item_nome = str(row['Item']).strip()
            espec = str(row['Especificação']) if pd.notna(row['Especificação']) else ""
            termo_busca = f"{item_nome} {espec}".strip()
            print(f"\n🔎 Analisando: {Fore.YELLOW}{termo_busca}")
            ofertas = {}
            for loja in SITES_CONFIG.keys():
                val, link, nome_site = self.buscar_loja(loja, termo_busca)
                if 1.00 < val < 80000:
                    ofertas[loja] = (val, link, nome_site)
                    print(f"  ∟ {loja}: R$ {val:.2f}")
            if ofertas:
                venc = min(ofertas, key=lambda k: ofertas[k][0])
                v, l, n = ofertas[venc]
                self.resultados.append({
                    'Item': item_nome,
                    'Qtd': row['Quantidade Sugerida'],
                    'Melhor Preço': f"R$ {v:.2f}",
                    'Total': f"R$ {v * int(row['Quantidade Sugerida']):.2f}",
                    'Loja': venc,
                    'Link': l,
                    'Nome no Site': n
                })
        self.finalizar()

    def finalizar(self):
        self.driver.quit()
        if self.resultados:
            # Nome do arquivo atualizado conforme solicitado
            path = "Relatório Material Escolar.xlsx"
            pd.DataFrame(self.resultados).to_excel(path, index=False)
            print(f"\n{Fore.GREEN}✨ Relatório salvo em: {path}")

if __name__ == "__main__":
    bot = RastreadorPrecos()
    bot.processar_lista("lista_consolidada.xlsx")