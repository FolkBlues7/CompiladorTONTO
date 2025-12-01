import ply.yacc as yacc
import json
import os

# =============================================================================
# 1. IMPORTAÇÃO DOS TOKENS E LEXER
# =============================================================================
try:
    from lexer.lexer import tokens, lexer
except ImportError:
    print(
        "[ERRO FATAL] Não foi possível importar a lista de tokens do seu lexer. Por favor, verifique o caminho."
    )
    exit(1)

# =============================================================================
# 2. REGRAS DE GRAMÁTICA (TONTO)
# =============================================================================


# ----------------------------------
# A. REGRA PRINCIPAL
# ----------------------------------
def p_programa(p):
    """programa : pre_package_decls declaracao_package declaracoes_pos_package"""
    p[0] = {
        "type": "OntologyModel",
        "imports": p[1],
        "package": p[2],
        "declarations": p[3],
    }


def p_pre_package_decls(p):
    """pre_package_decls : declaracao_import pre_package_decls
    | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_declaracao_import(p):
    """declaracao_import : IMPORT nome_identificador"""
    p[0] = {"type": "Import", "target": p[2]}


# ----------------------------------
# B. DECLARAÇÃO DE PACOTE
# ----------------------------------
def p_declaracao_package(p):
    """declaracao_package : PACKAGE nome_identificador"""
    p[0] = {"type": "Package", "name": p[2]}


def p_nome_identificador(p):
    """nome_identificador : CLASS_NAME
    | RELATION_NAME
    | INSTANCE_NAME"""
    p[0] = p[1]


# (NOVO) Regra flexível para nomes de Classes
# Aceita 'Person' (CLASS_NAME) e 'Criterion_A1' (INSTANCE_NAME)
def p_class_identifier(p):
    """class_identifier : CLASS_NAME
    | INSTANCE_NAME
    | RELATION_NAME"""
    p[0] = p[1]


# ----------------------------------
# C. LISTA DE DECLARAÇÕES
# ----------------------------------
def p_declaracoes_pos_package(p):
    """declaracoes_pos_package : declaracao declaracoes_pos_package
    | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


# ----------------------------------
# D. HUB DE DECLARAÇÕES
# ----------------------------------
def p_declaracao(p):
    """declaracao : declaracao_classe
    | declaracao_enum
    | declaracao_datatype
    | declaracao_genset
    | declaracao_relacao_externa
    | declaracao_relacao_inline
    | declaracao_association"""
    p[0] = p[1]


# ----------------------------------
# E. DECLARAÇÃO DE CLASSE (CONSTRUTO 2)
# ----------------------------------
# (MODIFICADO) Usa class_identifier
def p_declaracao_classe(p):
    """declaracao_classe : estereotipo_classe class_identifier classe_natureza_opcional classe_specialization classe_body"""
    p[0] = {
        "type": "ClassDeclaration",
        "stereotype": p[1],
        "name": p[2],
        "nature": p[3],
        "specializes": p[4],
        "body": p[5],
    }


def p_classe_natureza_opcional(p):
    """classe_natureza_opcional : OF natureza_classe
    | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None


def p_natureza_classe(p):
    """natureza_classe : FUNCTIONALCOMPLEXES
    | RELATOR
    | RELATION_NAME
    | INTRINSICMODE
    | EXTRINSICMODE
    | QUALITY
    | MODE
    | EVENT
    | SITUATION"""
    p[0] = p[1]


def p_classe_specialization(p):
    """classe_specialization : SPECIALIZES lista_nomes_classe
    | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []


def p_classe_body(p):
    """classe_body : LBRACE lista_membros_classe RBRACE
    | empty"""
    if len(p) == 4:
        p[0] = {"type": "ClassBody", "members": p[2]}
    else:
        p[0] = None


def p_lista_membros_classe(p):
    """lista_membros_classe : membro_classe lista_membros_classe
    | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_membro_classe(p):
    """membro_classe : atributo_datatype
    | declaracao_relacao_interna
    | classe_relation_internal"""
    p[0] = p[1]


def p_classe_relation_internal(p):
    """classe_relation_internal : AT estereotipo_relacao cardinalidade_opcional seta cardinalidade_opcional class_identifier"""
    p[0] = {
        "type": "InternalRelation",
        "stereotype": p[2],
        "left_cardinality": p[3],
        "arrow": p[4],
        "right_cardinality": p[5],
        "target_class": p[6],
    }


# (MODIFICADO) Usa class_identifier para listas de especialização
def p_lista_nomes_classe(p):
    """lista_nomes_classe : class_identifier COMMA lista_nomes_classe
    | class_identifier"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


# --- ESTEREÓTIPOS DE CLASSE ---
def p_estereotipo_classe_1(p):
    """estereotipo_classe : EVENT"""
    p[0] = p[1]


def p_estereotipo_classe_2(p):
    """estereotipo_classe : SITUATION"""
    p[0] = p[1]


def p_estereotipo_classe_3(p):
    """estereotipo_classe : PROCESS"""
    p[0] = p[1]


def p_estereotipo_classe_4(p):
    """estereotipo_classe : CATEGORY"""
    p[0] = p[1]


def p_estereotipo_classe_5(p):
    """estereotipo_classe : MIXIN"""
    p[0] = p[1]


def p_estereotipo_classe_6(p):
    """estereotipo_classe : PHASEMIXIN"""
    p[0] = p[1]


def p_estereotipo_classe_7(p):
    """estereotipo_classe : ROLEMIXIN"""
    p[0] = p[1]


def p_estereotipo_classe_8(p):
    """estereotipo_classe : HISTORICALROLEMIXIN"""
    p[0] = p[1]


def p_estereotipo_classe_9(p):
    """estereotipo_classe : KIND"""
    p[0] = p[1]


def p_estereotipo_classe_10(p):
    """estereotipo_classe : COLLECTIVE"""
    p[0] = p[1]


def p_estereotipo_classe_11(p):
    """estereotipo_classe : QUANTITY"""
    p[0] = p[1]


def p_estereotipo_classe_12(p):
    """estereotipo_classe : QUALITY"""
    p[0] = p[1]


def p_estereotipo_classe_13(p):
    """estereotipo_classe : MODE"""
    p[0] = p[1]


def p_estereotipo_classe_14(p):
    """estereotipo_classe : INTRINSICMODE"""
    p[0] = p[1]


def p_estereotipo_classe_15(p):
    """estereotipo_classe : EXTRINSICMODE"""
    p[0] = p[1]


def p_estereotipo_classe_16(p):
    """estereotipo_classe : SUBKIND"""
    p[0] = p[1]


def p_estereotipo_classe_17(p):
    """estereotipo_classe : PHASE"""
    p[0] = p[1]


def p_estereotipo_classe_18(p):
    """estereotipo_classe : ROLE"""
    p[0] = p[1]


def p_estereotipo_classe_19(p):
    """estereotipo_classe : HISTORICALROLE"""
    p[0] = p[1]


# ----------------------------------
# F. DECLARAÇÃO DE ENUM (CONSTRUTO 4)
# ----------------------------------
# (MODIFICADO) Usa class_identifier
def p_declaracao_enum(p):
    """declaracao_enum : ENUM class_identifier LBRACE lista_individuos RBRACE"""
    p[0] = {"type": "EnumDeclaration", "name": p[2], "members": p[4]}


# (MODIFICADO) Usa class_identifier para membros do enum
def p_lista_individuos(p):
    """lista_individuos : class_identifier COMMA lista_individuos
    | class_identifier"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]


# ----------------------------------
# G. DECLARAÇÃO DE DATATYPE (CONSTRUTO 3)
# ----------------------------------
# (MODIFICADO) Usa class_identifier
def p_declaracao_datatype(p):
    """declaracao_datatype : DATATYPE class_identifier LBRACE lista_atributos_datatype RBRACE"""
    p[0] = {"type": "DataTypeDeclaration", "name": p[2], "attributes": p[4]}


def p_lista_atributos_datatype(p):
    """lista_atributos_datatype : atributo_datatype COMMA lista_atributos_datatype
    | atributo_datatype
    | empty"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []


def p_atributo_datatype(p):
    """atributo_datatype : RELATION_NAME COLON tipo_atributo cardinalidade_opcional"""

    p[0] = {
        "type": "Attribute",
        "name": p[1],
        "datatype": p[3],
        "cardinality": p[4],
    }


# (MODIFICADO) Usa class_identifier como tipo possível
def p_tipo_atributo(p):
    """tipo_atributo : tipo_primitivo
    | class_identifier"""
    p[0] = p[1]


# --- TIPOS PRIMITIVOS ---
def p_tipo_primitivo_1(p):
    """tipo_primitivo : NUMBER_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_2(p):
    """tipo_primitivo : STRING_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_3(p):
    """tipo_primitivo : BOOLEAN_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_4(p):
    """tipo_primitivo : DATE_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_5(p):
    """tipo_primitivo : TIME_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_6(p):
    """tipo_primitivo : DATETIME_TYPE"""
    p[0] = p[1]


def p_tipo_primitivo_7(p):
    """tipo_primitivo : INT_TYPE"""
    p[0] = p[1]


# ----------------------------------
# H. DECLARAÇÃO DE GENSET (CONSTRUTO 5)
# ----------------------------------
# Nota: genset aceita nome_identificador (maiúscula ou minúscula)
def p_declaracao_genset(p):
    """declaracao_genset : genset_modifiers GENSET nome_identificador genset_form"""
    p[0] = {"type": "GeneralizationSet", "name": p[3], "modifiers": p[1], **p[4]}


def p_genset_modifiers(p):
    """genset_modifiers : genset_modifier genset_modifiers
    | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_genset_modifier(p):
    """genset_modifier : DISJOINT
    | COMPLETE"""
    p[0] = p[1]


def p_genset_form(p):
    """genset_form : genset_form_where
    | genset_form_block"""
    p[0] = p[1]


# (MODIFICADO) Usa class_identifier para 'general' e lista 'specifics'
def p_genset_form_where(p):
    """genset_form_where : WHERE lista_nomes_classe SPECIALIZES class_identifier"""
    p[0] = {"form": "where", "general": p[4], "specifics": p[2]}


# (MODIFICADO) Usa class_identifier
def p_genset_form_block(p):
    """
    genset_form_block : LBRACE GENERAL class_identifier maybe_comma SPECIFICS lista_nomes_classe RBRACE
    """
    # p[3] = geral, p[5] = lista de específicos
    p[0] = {"form": "block", "general": p[3], "specifics": p[6]}


def p_maybe_comma(p):
    """maybe_comma : COMMA
    | empty"""
    if len(p) == 2 and p[1] is not None:
        p[0] = ","
    else:
        p[0] = None


# ----------------------------------
# I. DECLARAÇÃO DE RELAÇÃO (CONSTRUTO 6)
# ----------------------------------


# 1. Forma Externa (relator/relation)
# (MODIFICADO) Usa class_identifier
def p_declaracao_relacao_externa(p):
    """declaracao_relacao_externa : tipo_relacao_externa class_identifier classe_specialization relation_body"""
    p[0] = {
        "type": "RelationDeclaration",
        "relation_type": p[1],
        "name": p[2],
        "specializes": p[3],
        "body": p[4],
    }


def p_relation_body(p):
    """relation_body : LBRACE relation_members RBRACE
    | empty"""
    if len(p) == 4:
        p[0] = {"members": p[2]}
    else:
        p[0] = {"members": []}


def p_relation_members(p):
    """relation_members : relation_member relation_members
    | empty"""
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_relation_member(p):
    """relation_member : declaracao_relacao_interna
    | atributo_datatype
    | relacao_interna_relator"""
    p[0] = p[1]


def p_tipo_relacao_externa(p):
    """tipo_relacao_externa : RELATOR
    | RELATION"""
    p[0] = p[1]


def p_declaracao_relacao_inline_com_estereotipo(p):
    """declaracao_relacao_inline : AT estereotipo_relacao RELATION class_identifier cardinalidade_opcional seta RELATION_NAME seta cardinalidade_opcional class_identifier"""

    p[0] = {
        "type": "InlineRelation",
        "stereotype": p[2],
        "source_class": p[4],
        "source_cardinality": p[5],
        "left_arrow": p[6],
        "relation_name": p[7],
        "right_arrow": p[8],
        "target_cardinality": p[9],
        "target_class": p[10],
    }


# 2. Forma Interna (dentro de uma classe)
def p_relacao_interna_relator(p):
    """relacao_interna_relator : AT estereotipo_relacao cardinalidade_opcional seta cardinalidade_opcional class_identifier"""
    p[0] = {
        "type": "InternalRelationPole",
        "stereotype": p[2],
        "left_cardinality": p[3],
        "arrow": p[4],
        "right_cardinality": p[5],
        "target_class": p[6],
    }


# (MODIFICADO) Usa class_identifier para 'target_class'
def p_declaracao_relacao_interna(p):
    """declaracao_relacao_interna : estereotipo_relacao_opcional seta RELATION_NAME seta cardinalidade_opcional class_identifier"""
    p[0] = {
        "type": "RelationPole",
        "stereotype": p[1],
        "name": p[3],
        "cardinality": p[5],
        "target_class": p[6],
    }


def p_seta(p):
    """seta : DOUBLE_HYPHEN
    | ARROW_RL
    | ARROW_LR
    | ARROW_RL_COMPOSITION
    | ARROW_RL_AGGREGATION"""
    p[0] = p[1]


# 3. Auxiliares de Relação
def p_estereotipo_relacao_opcional(p):
    """estereotipo_relacao_opcional : AT estereotipo_relacao
    | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None


def p_cardinalidade_opcional(p):
    """cardinalidade_opcional : LBRACKET cardinalidade_valor RBRACKET
    | empty"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = None


def p_cardinalidade_valor(p):
    """cardinalidade_valor : NUMBER
    | ASTERISK
    | NUMBER DOTDOT NUMBER
    | NUMBER DOTDOT ASTERISK"""
    if len(p) == 2:
        p[0] = str(p[1])
    elif p[3] == "*":
        p[0] = f"{p[1]}..*"
    else:
        p[0] = f"{p[1]}..{p[3]}"


def p_declaracao_association(p):
    """declaracao_association : ASSOCIATION_NAME class_identifier classe_body"""
    p[0] = {"type": "AssociationDeclaration", "name": p[2], "body": p[3]}


# --- ESTEREÓTIPOS DE RELAÇÃO ---
def p_estereotipo_relacao_1(p):
    """estereotipo_relacao : MATERIAL"""
    p[0] = p[1]


def p_estereotipo_relacao_2(p):
    """estereotipo_relacao : DERIVATION"""
    p[0] = p[1]


def p_estereotipo_relacao_3(p):
    """estereotipo_relacao : COMPARATIVE"""
    p[0] = p[1]


def p_estereotipo_relacao_4(p):
    """estereotipo_relacao : MEDIATION"""
    p[0] = p[1]


def p_estereotipo_relacao_5(p):
    """estereotipo_relacao : CHARACTERIZATION"""
    p[0] = p[1]


def p_estereotipo_relacao_6(p):
    """estereotipo_relacao : EXTERNALDEPENDENCE"""
    p[0] = p[1]


def p_estereotipo_relacao_7(p):
    """estereotipo_relacao : COMPONENTOF"""
    p[0] = p[1]


def p_estereotipo_relacao_8(p):
    """estereotipo_relacao : MEMBEROF"""
    p[0] = p[1]


def p_estereotipo_relacao_9(p):
    """estereotipo_relacao : SUBCOLLECTIONOF"""
    p[0] = p[1]


def p_estereotipo_relacao_10(p):
    """estereotipo_relacao : SUBQUALITYOF"""
    p[0] = p[1]


def p_estereotipo_relacao_11(p):
    """estereotipo_relacao : INSTANTIATION"""
    p[0] = p[1]


def p_estereotipo_relacao_12(p):
    """estereotipo_relacao : TERMINATION"""
    p[0] = p[1]


def p_estereotipo_relacao_13(p):
    """estereotipo_relacao : PARTICIPATIONAL"""
    p[0] = p[1]


def p_estereotipo_relacao_14(p):
    """estereotipo_relacao : PARTICIPATION"""
    p[0] = p[1]


def p_estereotipo_relacao_15(p):
    """estereotipo_relacao : HISTORICALDEPENDENCE"""
    p[0] = p[1]


def p_estereotipo_relacao_16(p):
    """estereotipo_relacao : CREATION"""
    p[0] = p[1]


def p_estereotipo_relacao_17(p):
    """estereotipo_relacao : MANIFESTATION"""
    p[0] = p[1]


def p_estereotipo_relacao_18(p):
    """estereotipo_relacao : BRINGSABOUT"""
    p[0] = p[1]


def p_estereotipo_relacao_19(p):
    """estereotipo_relacao : TRIGGERS"""
    p[0] = p[1]


def p_estereotipo_relacao_20(p):
    """estereotipo_relacao : COMPOSITION"""
    p[0] = p[1]


def p_estereotipo_relacao_21(p):
    """estereotipo_relacao : AGGREGATION"""
    p[0] = p[1]


def p_estereotipo_relacao_22(p):
    """estereotipo_relacao : INHERENCE"""
    p[0] = p[1]


def p_estereotipo_relacao_23(p):
    """estereotipo_relacao : VALUE"""
    p[0] = p[1]


def p_estereotipo_relacao_24(p):
    """estereotipo_relacao : FORMAL"""
    p[0] = p[1]


def p_estereotipo_relacao_25(p):
    """estereotipo_relacao : CONSTITUTION"""
    p[0] = p[1]


# =============================================================================
# 3. FUNÇÃO VAZIA E TRATAMENTO DE ERROS
# =============================================================================
def p_empty(p):
    """empty :"""
    pass


global has_error
has_error = False


def p_error(p):
    """Tratamento de erro sintático."""
    global has_error
    has_error = True
    if p:
        print(
            f"\n[ERRO SINTÁTICO] Token inesperado: {p.type} ('{p.value}') na linha {p.lineno}"
        )
    else:
        print(
            "\n[ERRO SINTÁTICO] Fim de arquivo inesperado (EOF). O código está incompleto."
        )


# =============================================================================
# 4. CONSTRUÇÃO DO PARSER
# =============================================================================
parser = yacc.yacc(
    write_tables=True,  # gera (e depois reutiliza) parsetab.py
    debug=False,
    tabmodule="parsetab",  # nome do arquivo de tabelas
)


def parse_tonto_code(code_string):
    """
    Função principal para analisar o código TONTO.
    """
    global has_error
    has_error = False
    lexer.lineno = 1
    ast_result = parser.parse(code_string, lexer=lexer)
    if has_error:
        return None
    return ast_result
