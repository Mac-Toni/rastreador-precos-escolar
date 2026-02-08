# 📚 School Price Hunter (2026 Edition)

Este projeto automatiza a pesquisa de preços de materiais escolares em três gigantes do varejo brasileiro (**Amazon**, **Kalunga** e **Mercado Livre**), consolidando os menores valores encontrados em um relatório inteligente e autolimpante.

## 🚀 Tecnologias e Ferramentas
Desenvolvido com foco em performance e escalabilidade:

* **Linguagem:** Python 3.12+
* **Automação:** Selenium & WebDriver Manager (Chrome)
* **Manipulação de Dados:** Pandas & Openpyxl
* **Interface de Terminal:** Colorama (Status em cores)
* **Editor:** [Visual Studio Code](https://code.visualstudio.com/) **v1.109+**
    * *Nota: Otimizado para Agentic Development e inspeção via Integrated Browser.*

## 📋 Funcionalidades de Elite
- [x] **Busca Multi-Varejista:** Scrape sincronizado na Amazon, Kalunga e Mercado Livre.
- [x] **Teste de Mesa Virtual:** O relatório captura a **descrição real encontrada no site** para conferência de precisão.
- [x] **Gestão de Armazenamento:** Função "Faxina" que mantém apenas os **3 últimos relatórios** na pasta, evitando acúmulo de arquivos.
- [x] **Cálculo de Economia:** Identifica a diferença entre o menor e o maior preço encontrado para cada item.
- [x] **Relatórios Inteligentes:** Arquivos gerados via Pandas com timestamp para histórico organizado.

## 🛠️ Como Instalar e Rodar

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Mac-Toni/rastreador-precos-escolar.git](https://github.com/Mac-Toni/rastreador-precos-escolar.git)
   cd rastreador-precos-escolar
Instale as dependências:

Bash
pip install -r requirements.txt
Prepare sua lista: Certifique-se de que o arquivo lista_consolidada.xlsx está na raiz do projeto com as colunas: Item, Especificação e Quantidade Sugerida.

Execute o script:

Bash
python main.py
📁 Estrutura de Saída
O bot organiza os resultados automaticamente:

Os relatórios são salvos na pasta /relatorios_precos.

Regra de Retenção: Apenas os 3 arquivos mais recentes são preservados para economizar espaço.

💡 Dica de Execução (Modo Silencioso)
Se você desejar que o robô trabalhe em segundo plano (sem abrir janelas):

No arquivo main.py, localize a linha: options.add_argument('--headless').

Remova o símbolo # do início da linha para ativá-la.

Desenvolvido por Mac-Toni 🚀