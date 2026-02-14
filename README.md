# 📚 School Price Hunter (2026 Edition)

Este projeto automatiza a pesquisa de preços de materiais escolares em três gigantes do varejo brasileiro (**Amazon**, **Kalunga** e **Mercado Livre**), consolidando os menores valores encontrados em um relatório inteligente e autolimpante.

## 1. 🚀 Tecnologias e Ferramentas
- Linguagem: Python 3.12+
- Automação: Selenium & WebDriver Manager (Chrome)
- Manipulação de Dados: Pandas & Openpyxl
- Interface de Terminal: Colorama (status em cores)
- Editor recomendado: Visual Studio Code v1.109+

## 2. 📋 Funcionalidades
- [x] Busca Multi-Varejista: Amazon, Kalunga e Mercado Livre.
- [x] Captura Real: O relatório traz a descrição exata encontrada no site.
- [x] Gestão de Relatórios: Apenas os 3 últimos relatórios são mantidos.
- [x] Cálculo de Economia: Mostra a diferença entre menor e maior preço por item.
- [x] Relatórios Inteligentes: Arquivos Excel com timestamp para histórico organizado.

## 3. 🛠️ Instalação e Execução

### 3.1 Clone o repositório
git clone https://github.com/Mac-Toni/rastreador-precos-escolar.git
cd rastreador-precos-escolar

### 3.2 Instale as dependências
pip install -r requirements.txt

### 3.3 Prepare sua lista
Certifique-se de que o arquivo lista_consolidada.xlsx está na raiz do projeto com as colunas:
- Item
- Especificação
- Quantidade Sugerida

### 3.4 Execute o rastreador principal
python main.py

### 3.5 Teste os seletores manualmente (opcional)
python teste_lojas.py

## 4. 📁 Estrutura de Saída
- Relatórios salvos em /relatorios_precos.
- Nome do arquivo: Relatório_YYYYMMDD_HHMMSS.xlsx.
- Apenas os 3 mais recentes são preservados.

## 5. 💡 Dica de Execução (Modo Silencioso)
Se quiser rodar sem abrir janelas do navegador:
- No main.py, mantenha a linha:
options.add_argument("--headless")

---

## 6. 📂 Estrutura do Projeto

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        07/02/2026     14:34                relatorios_precos
-a----        12/02/2026     20:34           7796 lista_consolidada.xlsx
-a----        13/02/2026     22:30           7271 main.py
-a----        13/02/2026     22:41           2564 README.md
-a----        13/02/2026     21:07           7296 Relatório Material Escolar.xlsx
-a----        07/02/2026     14:51             55 requirements.txt
-a----        13/02/2026     22:30           2922 teste_lojas.py

---

Desenvolvido por Mac-Toni 🚀
