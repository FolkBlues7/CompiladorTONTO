# Analisador Léxico para a Linguagem TONTO

Projeto da disciplina de Compiladores para a criação de um analisador léxico em Python para a "Textual Ontology Language" (TONTO).

## 📖 Sobre o Projeto

**TONTO** (Textual Ontology Language) é uma linguagem textual para a especificação de ontologias computacionais. Este projeto implementa a primeira fase de um compilador para a linguagem, o **analisador léxico**, responsável por ler o código-fonte `.tonto` e convertê-lo em uma sequência de tokens (as menores unidades lógicas da linguagem).

O analisador foi construído em Python utilizando a biblioteca [PLY (Python Lex-Yacc)](http://www.dabeaz.com/ply/).

## ✨ Funcionalidades

*   **Reconhecimento Completo**: Identifica todos os estereótipos, palavras-chave e símbolos especiais da linguagem TONTO.

*   **Identificadores Complexos**: Classifica corretamente os diferentes tipos de identificadores:
    *   `CLASS_NAME` (Ex: `Car`, `Criterion_A2i`)
    *   `INSTANCE_NAME` (Ex: `Planeta2`)
    *   `RELATION_NAME` (Ex: `involvesOwner`)
    *   `NEW_DATATYPE` (Ex: `CPFDataType`)

*   **Literais**: Analisa e extrai valores de `STRING`, `DATE_LITERAL`, `TIME_LITERAL` e `DATETIME_LITERAL`.

*   **Interface Interativa**: Um menu de linha de comando (CLI) amigável para testar exemplos internos ou analisar arquivos `.tonto` externos.

*   **Dupla Visualização de Saída**:
    *   **Visão Analítica**: Uma lista detalhada de cada token encontrado, seu lexema (valor) e a linha.
    *   **Tabela de Síntese**: Um resumo quantitativo com a contagem de cada tipo de token ao final da análise.

*   **Relatório de Erros**: Captura caracteres ilegais e informa a linha onde o erro léxico ocorreu.

## 🛠️ Tecnologias Utilizadas

*   Python 3.x
*   [PLY (Python Lex-Yacc)](http://www.dabeaz.com/ply/)

## 📁 Estrutura de Pastas

Para que o programa funcione corretamente, os arquivos devem estar organizados da seguinte forma:

```
seu-projeto/
├── lexer/
│   ├── __init__.py          (Arquivo vazio, necessário para o Python)
│   ├── lexer.py             (A lógica do analisador léxico)
│   └── tokens.py            (Definição dos tokens e palavras reservadas)
├── main.py                  (O script principal para executar o programa)
├── Trabalho_de_Anlise_...pdf (O PDF do trabalho)
└── README.md                (Este arquivo)
```

> **Importante**: A pasta `lexer` deve conter um arquivo chamado `__init__.py` (pode estar vazio) para que o Python a reconheça como um pacote.

## 🚀 Como Rodar

O projeto depende de uma biblioteca externa, a PLY. Siga os passos abaixo para instalar e executar.

### 1. Requisitos

*   Python 3 instalado.

### 2. Instalação da Dependência

Abra seu terminal ou prompt de comando e instale a biblioteca `ply`:

```bash
pip install ply
```

### 3. Execução

Com a dependência instalada, basta rodar o arquivo `main.py` a partir da pasta raiz do projeto:

```bash
python main.py
```

Um menu interativo aparecerá no seu terminal. Você pode escolher um dos exemplos internos (1-4) ou a opção 5 para fornecer o caminho de um arquivo `.tonto` local para análise.

## 📋 Exemplo de Saída

Ao selecionar uma opção no menu (como o Exemplo 2), a saída será parecida com esta:

```
==================================================
  SELECIONE O TESTE DE ANÁLISE LÉXICA
==================================================
 1. CarOwnershipExample
 2. CarRentalExample
 3. FoodAllergyExample
 4. TDAHExample
 5. Testar Arquivo Externo (.tonto)
 Q. Sair
--------------------------------------------------
Digite o número do teste (ou Q para sair): 2

##################################################
         Executando: CarRentalExample
##################################################

=== CÓDIGO FONTE ANALISADO ===
// Exemplo 2: Car Rental
package CarRental

kind Person
...
---------------------------------

=== VISÃO ANALÍTICA (LISTA DE TOKENS) ===
  [Tipo: PACKAGE              Lexema: 'package' Linha: 3]
  [Tipo: CLASS_NAME           Lexema: 'CarRental' Linha: 3]
  [Tipo: KIND                 Lexema: 'kind' Linha: 5]
  [Tipo: CLASS_NAME           Lexema: 'Person' Linha: 5]
  [Tipo: ROLE                 Lexema: 'role' Linha: 7]
  [Tipo: CLASS_NAME           Lexema: 'Employee' Linha: 7]
  [Tipo: SPECIALIZES          Lexema: 'specializes' Linha: 7]
  [Tipo: CLASS_NAME           Lexema: 'Person' Linha: 7]
  ...
  (e assim por diante)
  ...

==================================================
  === TABELA DE SÍNTESE (CONTAGEM DE TOKENS) ===
==================================================
  ADULT                      : 2
  AGEPHASE                   : 1
  ARROW_LR                   : 1
  AT                         : 3
  AVAILABLECAR               : 1
  CAR                        : 1
  CHARACTERIZATION           : 1
  CHILD                      : 2
  CLASS_NAME                 : 17
  COMMA                      : 2
  COMPLETE                   : 2
  CORPORATECUSTOMER          : 1
  CUSTOMER                   : 2
  DECEASEDPESON              : 2
  DISJOINT                   : 2
  EMPLOYEE                   : 2
  GENERAL                    : 2
  GENSET                     : 2
  KIND                       : 3
  LBRACE                     : 3
  LBRACKET                   : 3
  LIFESTATUS                 : 1
  LIVINGPERSON               : 5
  MEDIATION                  : 3
  ORGANIZATION               : 1
  PACKAGE                    : 1
  PERSON                     : 4
  PERSONALCUSTOMER           : 1
  PHASE                      : 5
  RBRACE                     : 3
  RBRACKET                   : 3
  RELATION_NAME              : 4
  RENTALCAR                  : 2
  RESPONSIBLEEMPLOYEE        : 2
  ROLE                       : 4
  ROLEMIXIN                  : 1
  SPECIFICS                  : 2
  SPECIALIZES                : 7
  TEENAGER                   : 2
  UNDERMAINTENANCECAR        : 1
```
