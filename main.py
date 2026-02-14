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
import os
import time

init(autoreset=True)

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
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        options.add_argument("--headless")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 15)  # espera maior para ML
        self.resultados = []

    def limpar_valor(self, texto):
        if not texto: return 99999.0
        try:
            limpo = texto.strip().replace("R$", "").replace(" ", "")
            limpo = limpo.replace(".", "").replace(",", ".")
            return float(limpo)
        except Exception as e:
            print("Erro limpar_valor:", e, texto)
            return 99999.0

    def tentar_elementos(self, seletores):
        for seletor in seletores:
            elementos = self.driver.find_elements(By.CSS_SELECTOR, seletor)
            if elementos:
                for el in elementos:
                    if el.is_displayed():
                        return el
        return None

    def buscar_loja(self, loja, termo):
        config = SITES_CONFIG[loja]
        self.driver.get(config['url'])
        try:
            busca = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['search_box'])))
            busca.clear()
            busca.send_keys(termo)
            busca.send_keys(Keys.ENTER)

            if loja == 'Kalunga':
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['item'][0])))
                time.sleep(2.5)
                el_nome = self.tentar_elementos(config['item'])
                el_preco = self.tentar_elementos(config['preco_completo'])
                if el_nome and el_preco:
                    return self.limpar_valor(el_preco.text), self.driver.current_url, el_nome.text

            elif loja == 'Amazon':
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['item'][0])))
                time.sleep(2.5)
                el_nome = self.tentar_elementos(config['item'])
                el_int = self.tentar_elementos(config['preco_inteiro'])
                el_frac = self.tentar_elementos(config['preco_fracao'])
                if el_nome and el_int:
                    frac = el_frac.text if el_frac else "00"
                    return self.limpar_valor(f"{el_int.text},{frac}"), self.driver.current_url, el_nome.text

            elif loja == 'Mercado Livre':
                # espera explícita pelo primeiro produto
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['item'][0])))
                time.sleep(5)  # dá mais tempo para carregar
                el_nome = self.tentar_elementos(config['item'])
                el_int = self.tentar_elementos(config['preco_inteiro'])
                el_frac = self.tentar_elementos(config['preco_fracao'])
                if el_nome and el_int:
                    frac = el_frac.text if el_frac else "00"
                    return self.limpar_valor(f"{el_int.text},{frac}"), self.driver.current_url, el_nome.text

            return 99999.0, "", "Não encontrado"

        except Exception as e:
            print(f"Erro {loja}:", e)
            return 99999.0, "", f"Erro {loja}"

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
