import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, init
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import os

init(autoreset=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SITES_CONFIG = {
    'Amazon': {
        'url': "https://www.amazon.com.br/",
        'search_box': "input#twotabsearchtextbox",
        'item': ["h2.a-size-base-plus.a-spacing-none.a-color-base.a-text-normal"],
        'preco_inteiro': [".a-price-whole"],
        'preco_fracao': [".a-price-fraction"]
    },
    'Kalunga': {
        'url': "https://www.kalunga.com.br/",
        'search_box': "input#txtBuscaProdMobile",
        'item': ["h2.blocoproduto__title"],
        'preco_completo': ["span.blocoproduto__price"]
    },
    'Mercado Livre': {
        'url': "https://lista.mercadolivre.com.br/",
        'search_box': "input#cb1-edit",
        'item': ["a.poly-component__title"],
        'preco_inteiro': [".andes-money-amount__fraction"],
        'preco_fracao': [".andes-money-amount__cents"]
    }
}

class RastreadorPrecos:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        options.add_argument("--headless")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.resultados = []

    def limpar_valor(self, texto):
        if not texto:
            return 99999.0
        try:
            limpo = texto.strip().replace("R$", "").replace(" ", "")
            # Corrige vírgulas e pontos duplicados
            while ".." in limpo:
                limpo = limpo.replace("..", ".")
            while ",," in limpo:
                limpo = limpo.replace(",,", ",")
            # Normaliza separadores
            limpo = limpo.replace(".", "").replace(",", ".")
            return float(limpo)
        except Exception as e:
            logging.warning(f"Erro limpar_valor: {e} | Texto original: {texto} | Texto limpo: {limpo}")
            return 99999.0

    def buscar_loja(self, loja, termo):
        config = SITES_CONFIG[loja]
        self.driver.get(config['url'])
        try:
            busca = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['search_box'])))
            busca.clear()
            busca.send_keys(termo)
            busca.send_keys(Keys.ENTER)

            # Espera pelo carregamento dos resultados
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['item'][0])))

            # Coleta múltiplos resultados com BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            nomes = [el.get_text(strip=True) for sel in config['item'] for el in soup.select(sel)]
            precos = []

            if 'preco_completo' in config:
                precos = [self.limpar_valor(el.get_text(strip=True)) for sel in config['preco_completo'] for el in soup.select(sel)]
            else:
                inteiros = [el.get_text(strip=True) for sel in config.get('preco_inteiro', []) for el in soup.select(sel)]
                fracs = [el.get_text(strip=True) for sel in config.get('preco_fracao', []) for el in soup.select(sel)]
                precos = [self.limpar_valor(f"{i},{fracs[idx] if idx < len(fracs) else '00'}") for idx, i in enumerate(inteiros)]

            resultados = []
            for nome, preco in zip(nomes, precos):
                if 1.00 < preco < 80000:
                    resultados.append((preco, self.driver.current_url, nome))

            logging.info(f"{loja} retornou {len(resultados)} resultados para '{termo}'")
            return resultados if resultados else [(99999.0, "", "Não encontrado")]

        except Exception as e:
            logging.error(f"Erro {loja}: {e}")
            return [(99999.0, "", f"Erro {loja}")]

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
                resultados = self.buscar_loja(loja, termo_busca)
                for val, link, nome_site in resultados:
                    if 1.00 < val < 80000:
                        ofertas[loja] = (val, link, nome_site)
                        print(f"  ∟ {loja}: R$ {val:.2f}")
                        break  # mantém apenas o primeiro válido
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
            if not os.path.exists("relatorios_precos"):
                os.makedirs("relatorios_precos")
            path = f"relatorios_precos/Relatório_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            pd.DataFrame(self.resultados).to_excel(path, index=False)
            print(f"\n{Fore.GREEN}✨ Relatório salvo em: {path}")

            # Faxina: manter apenas os 3 mais recentes
            arquivos = sorted(
                [os.path.join("relatorios_precos", f) for f in os.listdir("relatorios_precos")],
                key=os.path.getmtime,
                reverse=True
            )
            for velho in arquivos[3:]:
                os.remove(velho)
                print(f"{Fore.RED}🗑️ Relatório removido: {velho}")

if __name__ == "__main__":
    bot = RastreadorPrecos()
    bot.processar_lista("lista_consolidada.xlsx")