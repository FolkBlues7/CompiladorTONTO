import ply.lex as lex

tokens = [

    #Estereótipos de classe:
    'EVENT', 'SITUATION', 'PROCESS', 'CATEGORY', 'MIXIN',
    'PHASEMIXIN', 'ROLEMIXIN', 'HISTORICALROLEMIXIN', 'KIND', 'COLLECTIVE',
    'QUANTITY', 'QUALITY', 'MODE', 'INTRISICMODE', 'EXTRINSICMODE', 'SUBKIND',
    'PHASE', 'ROLE', 'HISTORICALROLE',

    #Estereótipos de relações:
    'MATERIAL', 'DERIVATION', 'COMPARATIVE', 'MEDIATION',
    'CHARACTERIZATION', 'EXTERNALDEPENDENCE', 'COMPONENTOF', 'MEMBEROF',
    'SUBCOLLECTIONOF', 'SUBQUALITYOF', 'INSTANTIATION', 'TERMINATION',
    'PARTICIPATIONAL', 'PARTICIPATION', 'HISTORICALDEPENDENCE', 'CREATION',
    'MANIFESTATION', 'BRINGSABOUT', 'TRIGGERS', 'COMPOSITION', 'AGGREGATION',
    'INHERENCE', 'VALUE', 'FORMAL', 'CONSTITUTION',

    #Palavras reservadas:
    'GENSET', 'DISJOINT', 'COMPLETE', 'GENERAL', 'SPECIFICS', 'WHERE', 'PACKAGE',

    #Símbolos especiais:
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
    'DOTDOT', 'ARROW_RL', 'ARROW_LR', 'ASTERISK', 'AT', 'COLON',

    #Nomes de classes: Aqui precisaremos fazer uma função específica para compreender corretamente o que é o nome de uma classe.
    'CLASS_NAME',

    #Convenção para nomes de relações: Também há uma função para especificar corretamente, como definido pelo professor.
    'RELATION_NAME',

    #Convenção para instâncias: Também há uma função para especificar corretamente.
    'INSTANCE_NAME',

    # --- TOKENS PARA OS NOMES DOS TIPOS (PALAVRAS-CHAVE) --- NÃO DEVEM PRECISAR DE FUNÇÕES ESPECÍFICAS
    'NUMBER_TYPE',       # Para a palavra 'number'
    'STRING_TYPE',       # Para a palavra 'string'
    'BOOLEAN_TYPE',      # Para a palavra 'boolean'
    'DATE_TYPE',         # Para a palavra 'date'
    'TIME_TYPE',         # Para a palavra 'time'
    'DATETIME_TYPE',     # Para a palavra 'datetime'

    # --- TOKENS PARA OS VALORES LITERAIS --- NÃO PRECISA DE FUNÇÃO
    'NUMBER',            # Para um valor como 123, 42, etc.
    'STRING',            # Para um valor como "Olá Mundo"
    'BOOLEAN_VALUE',     # Para as palavras 'true' e 'false'
    # Tokens para literais de data/hora --- TODOS ABAIXO PRECISAM DE FUNÇÃO ESPECÍFICAS
    'DATE_LITERAL',      # Para um valor como '2025-10-13'
    'TIME_LITERAL',      # Para um valor como '15:30:00'
    'DATETIME_LITERAL',  # Para um valor como '2025-10-13T15:30:00'
    
    #Token específico para tipos de dados personalisados. Exemplo: CPFDataType, PhoneNumberDataType. Aqui temos outra função específica.
    'NEW_DATATYPE'

    #Meta-atributos: Aqui não há regras específicas, apenas nomes.
    'ORDERED', 'CONST', 'DERIVED', 'SUBSETS', 'REDEFINES',
]

reserved = {
    #Estereótipos de classe:
    'event'     : 'EVENT',
    'situtation': 'SITUATION',
    'process'   : 'PROCESS',
    'category'  : 'CATEGORY',
    'mixin'     : 'MIXIN',
    'phasemixin': 'PHASEMIXIN',
    'rolemixin' : 'ROLEMIXIN',
    'historicalrolemixin' : 'HISTORICALROLEMIXIN',
    'kind'      : 'KIND',
    'COLLECTIVE': 'COLLECTIVE',
    'quantity'  : 'QUANTITY',
    'mode'      : 'MODE',
    'intrisicmode' : 'INTRISICMODE',
    'extrinsicmode'  : 'EXTRINSICMODE',
    'SUBKIND' : 'SUBKIND',
    'phase'     : 'PHASE',
    'role'      : 'ROLE',
    'historicalrole'  : 'HISTORICALROLE',

    #Estereótipos de relações:
    'material'  : 'MATERIAL',
    'derivation': 'DERIVATION',
    'comparative' : 'COMPARATIVE',
    'mediation' : 'MEDIATION',
    'characterization'  : 'CHARACTERIZATION',
    'externaldependence' : 'EXTERNALDEPENDENCE',
    'componentof'  : 'COMPONENTOF',
    'memberof'  : 'MEMBEROF',
    'subcollectionof' : 'SUBCOLLECTIONOF',
    'subqualityof' : 'SUBQUALITYOF',
    'instantiation': 'INSTANTIATION',
    'termination' : 'TERMINATION',
    'participational'  : 'PARTICIPATIONAL',
    'participation'    : 'PARTICIPATION',
    'historicaldependence'  : 'HISTORICALDEPENDENCE',
    'creation' : 'CREATION',
    'manifestation' : 'MANIFESTATION',
    'bringsabout' : 'BRINGSABOUT',
    'triggers' : 'TRIGGERS',
    'composition' : 'COMPOSITION',
    'aggregatopm' : 'AGGREGATION',
    'inherence' : 'INHERENCE',
    'value ': 'VALUE',
    'formal' : 'FORMAL',
    'constitution' : 'CONSTITUTION',

    #Palavras reservadas: genset, disjoint, complete, general, specifics, where, package:
    'package'   : 'PACKAGE',
    'class'     : 'CLASS',
    'genset'    : 'GENSET',
    'disjoint'  : 'DISJOINT',
    'complete'  : 'COMPLETE',
    'general'   : 'GENERAL',
    'specifics' : 'SPECIFICS',
    'where'     : 'WHERE',

    #Símbolos especiais: “{“, “}”, “(“, “)”, “[“, “]”, “..”, “<>--” , “--<>”, “*”, “@”, “:”.
    #São especificados usando expressões regulares

    #Tipos de dados primitivos
    'number'    : 'NUMBER_TYPE',
    'string'    : 'STRING_TYPE',
    'boolean'   : 'BOOLEAN_TYPE',
    'date'      : 'DATE_TYPE',
    'time'      : 'TIME_TYPE',
    'datetime'  : 'DATETIME_TYPE',

    #Valores booleanos 'true' e 'false':
    'true'      : 'BOOLEAN_VALUE',
    'false'     : 'BOOLEAN_VALUE',

    #Meta atributos:
    'ordered'   : 'ORDERED',
    'const'     : 'CONST',
    'derived'   : 'DERIVED',
    'subsets'   : 'SUBSETS',
    'redefines' : 'REDEFINES',
}

#Símbolos especiais:
t_LBRACE      = r'\{'
t_RBRACE      = r'\}'
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_LBRACKET    = r'\['
t_RBRACKET    = r'\]'

# Outros Símbolos
t_DOTDOT      = r'\.\.'  # O ponto também precisa ser escapado
t_ASTERISK    = r'\*'
t_AT          = r'@'
t_COLON       = r':'

# Símbolos Compostos
t_ARROW_RL    = r'<>--'
t_ARROW_LR    = r'--<>'

#-----------------------------------------------------------------------------------------------------------------------------
# Grupo 1: Aqui começamos as funções mais específicas. No PLY, a ordem de precedências das funções define quais serão testadas primeiro
#-----------------------------------------------------------------------------------------------------------------------------

# Regra para Datetime: é a mais longa e específica do grupo de datas, então vem primeiro.
def t_DATETIME_LITERAL(t):
    r"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'"
    t.value = t.value[1:-1]
    return t

# Regra para Date: é menos específica que Datetime.
def t_DATE_LITERAL(t):
    r"'\d{4}-\d{2}-\d{2}'"
    t.value = t.value[1:-1]
    return t

# Regra para Time: também é menos específica que Datetime.
def t_TIME_LITERAL(t):
    r"'\d{2}:\d{2}:\d{2}'"
    t.value = t.value[1:-1]
    return t

# Regra para Números: um padrão único (só dígitos) que não conflita com os outros.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\"]|\\.)*\"'
    # Esta linha é importante: ela remove as aspas do início e do fim
    # do valor do token, deixando apenas o conteúdo limpo da string.
    t.value = t.value[1:-1]
    return t


# =============================================================================
# GRUPO 2: IDENTIFICADORES COM REGRAS DE NOMENCLATURA
# =============================================================================
# Dentro deste grupo, também vamos do mais específico para o mais genérico.

def t_NEW_DATATYPE(t):
    r'[a-zA-Z]+DataType'
    return t

# Regra para Nomes de Instâncias: é a mais específica deste grupo
# porque OBRIGATORIAMENTE termina com um número.
def t_INSTANCE_NAME(t):
    r'[a-zA-Z][a-zA-Z_]*[0-9]+'
    return t

# Regra para Nomes de Classes: captura palavras que começam com
# letra maiúscula. É menos específica que a anterior.
def t_CLASS_NAME(t):
    r'[A-Z][a-zA-Z_]*'
    return t

# Regra para Nomes de Relações e Palavras-Chave: esta é a regra
# "pega-tudo" para palavras que começam com minúscula. DEVE ser a
# ÚLTIMA deste grupo para não capturar os outros por engano.
def t_RELATION_NAME(t):
    r'[a-z_][a-zA-Z_]*'
    # Consulta a "lista VIP" para ver se é uma palavra reservada.
    # Se não for, o padrão é ser um RELATION_NAME.
    t.type = reserved.get(t.value, 'RELATION_NAME')
    return t

    # =============================================================================
# GRUPO 3: FUNÇÕES DE CONTROLE E TRATAMENTO DE ERROS
# =============================================================================

# ADICIONADO: Função para calcular a coluna, melhorando os relatórios de erro
def find_column(input_data, token):
    line_start = input_data.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Regra para contar os números das linhas. É essencial para reportar erros.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Uma string contendo caracteres a serem ignorados (espaços e tabs).
# O lexer simplesmente pulará esses caracteres.
t_ignore  = ' \t'

# Regra para tratamento de erros. É chamada quando o lexer encontra
# um caractere que não corresponde a nenhuma outra regra.
def t_error(t):
    # Usa a função find_column para dar uma localização exata do erro.
    col = find_column(t.lexer.lexdata, t)
    print(f"Erro Léxico: Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}, coluna {col}")
    # Pula o caractere ilegal e continua a análise.
    t.lexer.skip(1)


#Parte da execução prática
lexer = lex.lex()

# Este bloco só é executado quando você roda o script diretamente (ex: python seu_arquivo.py)
if __name__ == '__main__':

    # Um exemplo de código na linguagem TONTO para testar nosso analisador.
    # Ele contém palavras-chave, nomes, símbolos, literais e comentários.
    data = """
    import alergiaalimentar

package alergiaalimentar

kind Paciente

kind Alimento

subkind Proteina of functional-complexes  specializes Componente_Alimentar 
    """

    # 1. Fornece a string de dados para o analisador léxico.
    lexer.input(data)

    # 2. Inicia um loop infinito para processar os tokens um por um.
    print("--- INÍCIO DA ANÁLISE LÉXICA (TABELA DE SÍMBOLOS) ---")
    while True:
        # Pega o próximo token encontrado no texto.
        tok = lexer.token()

        # Se não houver mais tokens (chegou ao fim do arquivo), o loop é interrompido.
        if not tok:
            break

        # Imprime o token encontrado, mostrando seu tipo, valor, linha e coluna.
        print(f"Tipo: {tok.type:<20} | Lexema: '{str(tok.value):<20}' | Linha: {tok.lineno:<4} | Coluna: {find_column(data, tok)}")

    print("--- FIM DA ANÁLISE LÉXICA ---")


