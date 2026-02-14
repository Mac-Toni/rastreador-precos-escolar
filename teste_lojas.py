import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def testar_loja(loja, termo, driver, wait):
    print(f"\n--- Testando {loja} ---")
    driver.get(SITES_CONFIG[loja]['url'])
    try:
        busca = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SITES_CONFIG[loja]['search_box'])))
        busca.clear()
        busca.send_keys(termo)
        busca.send_keys(Keys.ENTER)

        if loja == "Mercado Livre":
            # espera explícita pelo primeiro produto
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SITES_CONFIG[loja]['item'][0])))
            time.sleep(5)  # dá mais tempo para carregar os preços
        else:
            time.sleep(3)

        nome = driver.find_element(By.CSS_SELECTOR, SITES_CONFIG[loja]['item'][0]).text
        if 'preco_completo' in SITES_CONFIG[loja]:
            preco = driver.find_element(By.CSS_SELECTOR, SITES_CONFIG[loja]['preco_completo'][0]).text
        else:
            inteiro = driver.find_element(By.CSS_SELECTOR, SITES_CONFIG[loja]['preco_inteiro'][0]).text
            fracao = driver.find_element(By.CSS_SELECTOR, SITES_CONFIG[loja]['preco_fracao'][0]).text
            preco = f"{inteiro},{fracao}"

        print(f"Produto: {nome}\nPreço: {preco}")
    except Exception as e:
        print("Erro ao capturar produto/preço:", e)

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)  # espera maior para ML

    termo = "caderno"
    for loja in SITES_CONFIG.keys():
        testar_loja(loja, termo, driver, wait)

    driver.quit()
