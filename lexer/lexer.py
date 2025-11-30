import ply.lex as lex
import sys
import os

# -----------------------------------------------------------------------------
# IMPORTAÇÃO COM FALLBACK
# -----------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from tokens import tokens, reserved
except ImportError:
    # Fallback caso a execução seja feita de outro nível
    try:
        from .tokens import tokens, reserved
    except ImportError:
        print("[ERRO FATAL NO LEXER] Não foi possível importar 'tokens.py'.")
        sys.exit(1)

# -----------------------------------------------------------------------------
# SÍMBOLOS ESPECIAIS
# -----------------------------------------------------------------------------
# Atenção: ordem importa! Setas mais longas primeiro.

# COMPOSIÇÃO, AGREGAÇÃO ESPECIAL (EXTENSÃO TONTO)
t_ARROW_RL_COMPOSITION = r"<o>--"
t_ARROW_RL_AGGREGATION = r"<<>--"

# SETAS NORMAIS (PDF DO PROFESSOR)
t_ARROW_RL = r"<>--"
t_ARROW_LR = r"--<>"
t_DOUBLE_HYPHEN = r"--"

t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"

t_DOTDOT = r"\.\."
t_ASTERISK = r"\*"
t_AT = r"@"
t_COLON = r":"
t_COMMA = r","
t_DOT  = r"\."

# -----------------------------------------------------------------------------
# IGNORAR ESPAÇOS E COMENTÁRIOS
# -----------------------------------------------------------------------------
t_ignore = " \t"

# Comentário simples //
t_ignore_comment = r"//.*"


# Comentário multilinha /* ... */
def t_comment_block(t):
    r"/\*([^*]|\*+[^*/])*\*/"
    pass


# -----------------------------------------------------------------------------
# LITERAIS
# -----------------------------------------------------------------------------
def t_DATETIME_LITERAL(t):
    r"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'"
    t.value = t.value[1:-1]
    return t


def t_DATE_LITERAL(t):
    r"'\d{4}-\d{2}-\d{2}'"
    t.value = t.value[1:-1]
    return t


def t_TIME_LITERAL(t):
    r"'\d{2}:\d{2}:\d{2}'"
    t.value = t.value[1:-1]
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_STRING(t):
    r"(\"([^\"\\]|\\.)*\"|\'([^\'\\]|\\.)*\')"
    t.value = t.value[1:-1]
    return t


# -----------------------------------------------------------------------------
# IDENTIFICADORES (ID ÚNICO)
# -----------------------------------------------------------------------------
def t_ID(t):
    r"[a-zA-Z][a-zA-Z0-9_\-\.]*"

    # 1. Palavra reservada
    if t.value in reserved:
        t.type = reserved[t.value]
        return t

    # 2. NOVO DATATYPE
    if t.value.endswith("DataType"):
        t.type = "NEW_DATATYPE"
        return t

    # 3. INSTANCE
    if t.value[-1].isdigit():
        t.type = "INSTANCE_NAME"
        return t

    # 4. RELATION_NAME
    if t.value[0].islower():
        t.type = "RELATION_NAME"
        return t

    # 5. CLASS_NAME
    t.type = "CLASS_NAME"
    return t


# -----------------------------------------------------------------------------
# CONTROLE
# -----------------------------------------------------------------------------
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Erro Léxico: Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)


# -----------------------------------------------------------------------------
# CRIAR LEXER
# -----------------------------------------------------------------------------
lexer = lex.lex()


# -----------------------------------------------------------------------------
# FUNÇÃO TESTE
# -----------------------------------------------------------------------------
def run_lexer_test(code_example, test_name):
    output = []
    lexer.lineno = 1
    lexer.input(code_example)

    while True:
        tok = lexer.token()
        if not tok:
            break
        output.append(
            f"Tipo: {tok.type:<25} | Lexema: '{str(tok.value):<20}' | Linha: {tok.lineno}"
        )

    return output
