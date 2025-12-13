# Analisador Léxico para a Linguagem TONTO

## 🧩 Fase 1 — Análise Léxica (Lexer)

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

## 🧩 Fase 2 — Análise Sintática (Parser)

Além da análise léxica, o projeto agora implementa a segunda fase do compilador, responsável por verificar se a estrutura da ontologia TONTO está sintaticamente correta.
A interação foi ampliada para permitir escolher entre análise léxica, sintática e (futuramente) semântica.

Ao executar python main.py, o menu inicial é:
```
============================================================
                ANALISADOR DE LINGUAGEM TONTO
============================================================
Selecione o TIPO de análise que deseja executar:
  1. Análise Léxica (Fase 1)
  2. Análise Sintática (Fase 2)
  3. Análise Semântica (Fase 3)
  Q. Sair
Digite sua escolha:


Escolhendo a opção 2, o menu de testes sintáticos é apresentado:

------------------------------------------------------------
Executando: Análise Sintática (Fase 2)
Selecione uma opção para analisar:
  1. CarOwnershipExample
  2. CarRentalExample
  3. FoodAllergyExample
  4. TDAHExample
  6. Analisar um arquivo externo (.tonto)
  V. Voltar ao menu anterior
Digite sua escolha:


Ao selecionar um dos exemplos (por exemplo, o CarOwnershipExample), o parser executa as validações sintáticas e gera um relatório estrutural:

--- Iniciando Análise SINTÁTICA para: CarOwnershipExample ---

[SUCESSO] A estrutura sintática está CORRETA. Gerando relatório...

============================================================
               RESUMO ESTRUTURAL DA ONTOLOGIA
============================================================

📦 PACOTE: CarOwnership
   │
   ├── 📄 CLASSE: Organization
   │   ├── Estereótipo: <<kind>>
   │   └── (Sem atributos ou relações internas)
   ├── 📄 CLASSE: CarAgency
   │   ├── Estereótipo: <<subkind>> ➡️ Specializes: Organization
   │   └── (Sem atributos ou relações internas)
   ├── 📄 CLASSE: Car
   │   ├── Estereótipo: <<kind>>
   │   └── (Sem atributos ou relações internas)
   └── 🔗 RELAÇÃO EXTERNA: CarOwnership
       ├── Tipo: <<relator>>
       ├── Conecta: -- involvesOwner [1] ➝ CarAgency
       └── Conecta: -- involvesProperty [1] ➝ Car

============================================================

Pressione ENTER para continuar...
```

A estrutura acima é gerada dinamicamente com base nos nós sintáticos identificados pelo parser.

## 🧠 Fase 3 — Análise Semântica

A terceira e última fase do compilador implementa a **Análise Semântica**, focada na validação de **Padrões de Projeto de Ontologias (ODPs - Ontology Design Patterns)**.

Nesta etapa, o compilador não verifica apenas se o código está "gramaticalmente correto", mas se ele faz "sentido ontológico", respeitando as regras da linguagem UFO/TONTO.

### 🛡️ Funcionalidades Semânticas

O analisador utiliza uma **Tabela de Símbolos** centralizada para cruzar informações entre Classes, Relações e Conjuntos de Generalização (Gensets).

Ele é capaz de identificar e validar os seguintes padrões:

1.  **Subkind Pattern**: Verifica se o *Genset* é disjunto (`disjoint`) e rígido.
2.  **Role Pattern**: Verifica a regra de anti-rigidez (o *Genset* **não** pode ser `disjoint`).
3.  **Phase Pattern**: Verifica a regra temporal (o *Genset* **deve** ser `disjoint`).
4.  **Relator Pattern**: Garante que o Relator conecte pelo menos duas entidades e possua uma relação material derivada.
5.  **Mode Pattern**: Verifica se o Modo possui relações de caracterização (`@characterization`) e dependência externa.
6.  **RoleMixin Pattern**: Valida abstrações de papéis através de *Gensets* disjuntos.

### 🚨 Tratamento de Erros e Coerção

O sistema implementa **Coerção de Erros**, identificando violações de restrições ontológicas e apontando inconsistências lógicas:

* **Detecção de Padrões Incompletos**: Se o usuário declara um Relator mas esquece a relação material, o sistema avisa exatamente o que está faltando.
* **Violação de Rigidez**: Alerta se uma *Role* (anti-rígida) for declarada dentro de um conjunto disjunto, o que é logicamente proibido.

### 💻 Exemplo de Saída Semântica

Ao analisar um arquivo com inconsistências, o compilador gera um relatório detalhado:

```text
============================================================
      RELATÓRIO DE ANÁLISE SEMÂNTICA & PADRÕES (ODPs)
============================================================

✅ PADRÕES ONTOLÓGICOS IDENTIFICADOS:
   [Linha 12] Subkind Pattern
     └─ Kind 'Person' particionada em ['Man', 'Woman']

❌ VIOLAÇÕES E AVISOS SEMÂNTICOS:
   [Linha 45] ERRO SEMÂNTICO (Violação Anti-Rigidez)
     └─ O Genset 'RolesGenset' (Kind 'Person') com Roles NÃO deve ser 'disjoint'.
   
   [Linha 88] PADRÃO INCOMPLETO (Relator)
     └─ Entre as Roles 'Employee' e 'Employer' falta: Relação @material.