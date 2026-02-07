# 📚 School Price Hunter (2026 Edition)

Este projeto automatiza a pesquisa de preços de materiais escolares em três grandes varejistas brasileiros (**Amazon**, **Kalunga** e **Lepok**), consolidando os menores valores encontrados em um arquivo Excel (.xlsx).

## 🚀 Tecnologias e Ferramentas
Este projeto foi desenvolvido utilizando o que há de mais moderno no ecossistema de desenvolvimento:

* **Linguagem:** Python 3.x
* **Automação:** Selenium & WebDriver Manager
* **Manipulação de Dados:** Pandas & Openpyxl
* **Editor:** [Visual Studio Code](https://code.visualstudio.com/) **v1.109 (January 2026 Release)**
    * *Nota: O projeto aproveita as novas capacidades de Agentic Development e o Integrated Browser da versão 1.109 para testes de scraping em tempo real.*

## 📋 Funcionalidades
- [x] Leitura de lista de materiais via arquivo Excel (.xlsx).
- [x] Web Scraping automatizado na Amazon, Kalunga e Lepok.
- [x] Comparação inteligente de preços (busca o menor valor).
- [x] Geração de relatório final: `lista_com_melhores_precos.xlsx`.

## 🛠️ Como Instalar e Rodar

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Mac-Toni/rastreador-precos-escolar.git](https://github.com/Mac-Toni/rastreador-precos-escolar.git)
   
Instale as dependências:

Bash
pip install -r requirements.txt
Prepare sua lista: Certifique-se de que o arquivo lista_consolidada.xlsx está na raiz do projeto.

Execute o script:

Bash
python main.py
💡 Dica de Execução (Modo Silencioso)
O projeto está configurado para abrir o navegador e mostrar as buscas em tempo real. Se você desejar que o robô trabalhe em segundo plano (sem abrir janelas):

No arquivo main.py, localize a linha 13: options.add_argument('--headless').

Remova o símbolo # do início da linha para ativá-la.

Salve e execute. O robô será muito mais rápido!

🤖 Desenvolvimento com Agentes
Seguindo a evolução do VS Code como um Home for Multi-Agent Development, este código foi estruturado de forma modular para que agentes de IA possam estender as classes de busca para novos sites através de extensibilidade simples.

![Pesquisa de material escolar](images/Ilustração escolar.png)

Desenvolvido por Mac-Toni 🚀