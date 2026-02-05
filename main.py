import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

class RastreadorPrecos:
    def __init__(self):
        # Configuração do Navegador (Chrome)
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') # Descomente para rodar sem abrir a janela
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.resultados = []

    def pesquisar_amazon(self, item):
        print(f"Buscando {item} na Amazon...")
        self.driver.get(f"https://www.amazon.com.br/s?k={item}")
        time.sleep(2)
        try:
            # Captura o preço e a URL do primeiro produto
            preco_inteiro = self.driver.find_element(By.CLASS_NAME, "a-price-whole").text
            preco_fracao = self.driver.find_element(By.CLASS_NAME, "a-price-fraction").text
            valor = float(f"{preco_inteiro}.{preco_fracao}".replace('.', '').replace(',', '.'))
            link = self.driver.current_url
            return valor, link
        except:
            return 99999.0, ""

    def pesquisar_kalunga(self, item):
        print(f"Buscando {item} na Kalunga...")
        self.driver.get(f"https://www.kalunga.com.br/busca/{item}")
        time.sleep(2)
        try:
            preco_texto = self.driver.find_element(By.CSS_SELECTOR, ".produc-item__price").text
            valor = float(preco_texto.replace('R$', '').replace('.', '').replace(',', '.').strip())
            return valor, self.driver.current_url
        except:
            return 99999.0, ""

    def pesquisar_lepok(self, item):
        print(f"Buscando {item} na Lepok...")
        self.driver.get(f"https://www.lepok.com.br/busca?t={item}")
        time.sleep(2)
        try:
            preco_texto = self.driver.find_element(By.CLASS_NAME, "price").text
            valor = float(preco_texto.replace('R$', '').replace('.', '').replace(',', '.').strip())
            return valor, self.driver.current_url
        except:
            return 99999.0, ""

    def processar_lista(self, arquivo_entrada):
        # Lê o arquivo que você subiu (materiais-escolares)
        df = pd.read_excel(arquivo_entrada)
        
        for index, row in df.iterrows():
            item = row['Item']
            
            # Pesquisa nos 3 sites
            p_ama, l_ama = self.pesquisar_amazon(item)
            p_kal, l_kal = self.pesquisar_kalunga(item)
            p_lep, l_lep = self.pesquisar_lepok(item)
            
            # Compara quem é o mais barato
            ofertas = {
                'Amazon': (p_ama, l_ama),
                'Kalunga': (p_kal, l_kal),
                'Lepok': (p_lep, l_lep)
            }
            
            loja_barata = min(ofertas, key=lambda k: ofertas[k][0])
            preco_final, link_final = ofertas[loja_barata]
            
            self.resultados.append({
                'Item': item,
                'Especificação': row['Especificação'],
                'Qtd': row['Quantidade Sugerida'],
                'Menor Preço': preco_final if preco_final != 99999.0 else "Não encontrado",
                'Loja': loja_barata,
                'URL': link_final
            })

        self.driver.quit()
        
        # Gera o NOVO arquivo Excel
        df_final = pd.DataFrame(self.resultados)
        df_final.to_excel("lista_com_melhores_precos.xlsx", index=False)
        print("\n✅ Projeto concluído! Arquivo 'lista_com_melhores_precos.xlsx' gerado.")

# Início do Projeto
if __name__ == "__main__":
    bot = RastreadorPrecos()
    bot.processar_lista("lista_consolidada.xlsx")