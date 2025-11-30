# =============================================================================
# 1. LISTA DE TOKENS VÁLIDOS (TODOS EM MAIÚSCULO)
# =============================================================================

tokens = [
    # Estereótipos de classe:
    "EVENT", "SITUATION", "PROCESS", "CATEGORY", "MIXIN",
    "PHASEMIXIN", "ROLEMIXIN", "HISTORICALROLEMIXIN", "KIND", "COLLECTIVE",
    "QUANTITY", "QUALITY", "MODE", "INTRINSICMODE", "EXTRINSICMODE", "SUBKIND",
    "PHASE", "ROLE", "HISTORICALROLE", "TYPE", 

    # Estereótipos de relações:
    "MATERIAL", "DERIVATION", "COMPARATIVE", "MEDIATION",
    "CHARACTERIZATION", "EXTERNALDEPENDENCE", "COMPONENTOF", "MEMBEROF",
    "SUBCOLLECTIONOF", "SUBQUALITYOF", "INSTANTIATION", "TERMINATION",
    "PARTICIPATIONAL", "PARTICIPATION", "HISTORICALDEPENDENCE", "CREATION",
    "MANIFESTATION", "BRINGSABOUT", "TRIGGERS", "COMPOSITION", "AGGREGATION",
    "INHERENCE", "VALUE", "FORMAL", "CONSTITUTION", "SPECIALIZES",

    # Estruturas:
    "RELATOR", "DATATYPE", "OF", "ASSOCIATION_NAME", "ENUM", "RELATION",

    # Palavras reservadas:
    "GENSET", "DISJOINT", "COMPLETE", "GENERAL", "SPECIFICS", "CATEGORIZER", 
    "WHERE", "PACKAGE", "CLASS", "IMPORT", "FUNCTIONALCOMPLEXES", 
    "CONST", "INSTANCEOF", 

    # Tipos primitivos:
    "NUMBER_TYPE", "STRING_TYPE", "BOOLEAN_TYPE",
    "DATE_TYPE", "TIME_TYPE", "DATETIME_TYPE", "INT_TYPE",

    # Símbolos:
    "LBRACE", "RBRACE", "LPAREN", "RPAREN", "LBRACKET", "RBRACKET",
    "DOTDOT", "ASTERISK", "AT", "COLON", "COMMA", "HYPHEN", "DOUBLE_HYPHEN",
    "ARROW_RL", "ARROW_LR", "DOT",
    "ARROW_RL_COMPOSITION", "ARROW_RL_AGGREGATION",

    # Identificadores e Literais:
    "CLASS_NAME", "INSTANCE_NAME", "RELATION_NAME", "NEW_DATATYPE",
    "STRING", "DATE_LITERAL", "TIME_LITERAL", "DATETIME_LITERAL", "NUMBER",
]

# =============================================================================
# 2. MAPA DE PALAVRAS RESERVADAS (reserved)
# =============================================================================
reserved = {
    # Classes
    "event": "EVENT", "situation": "SITUATION", "process": "PROCESS",
    "category": "CATEGORY", "mixin": "MIXIN", "phaseMixin": "PHASEMIXIN",
    "roleMixin": "ROLEMIXIN", "historicalRoleMixin": "HISTORICALROLEMIXIN",
    "kind": "KIND", "collective": "COLLECTIVE", "quantity": "QUANTITY",
    "quality": "QUALITY", "mode": "MODE", "intrinsic-mode": "INTRINSICMODE",
    "extrinsic-mode": "EXTRINSICMODE", "subkind": "SUBKIND", "phase": "PHASE",
    "role": "ROLE", "historicalRole": "HISTORICALROLE", "type": "TYPE",

    # Relações
    "material": "MATERIAL", "derivation": "DERIVATION", "comparative": "COMPARATIVE",
    "mediation": "MEDIATION", "characterization": "CHARACTERIZATION",
    "externalDependence": "EXTERNALDEPENDENCE", "componentOf": "COMPONENTOF",
    "memberOf": "MEMBEROF", "subCollectionOf": "SUBCOLLECTIONOF",
    "subQualityOf": "SUBQUALITYOF", "instantiation": "INSTANTIATION",
    "termination": "TERMINATION", "participational": "PARTICIPATIONAL",
    "participation": "PARTICIPATION", "historicalDependence": "HISTORICALDEPENDENCE",
    "creation": "CREATION", "manifestation": "MANIFESTATION", "bringsAbout": "BRINGSABOUT",
    "triggers": "TRIGGERS", "composition": "COMPOSITION", "aggregation": "AGGREGATION",
    "inherence": "INHERENCE", "value": "VALUE", "formal": "FORMAL",
    "constitution": "CONSTITUTION", "specializes": "SPECIALIZES",

    # Outros
    "relator": "RELATOR", "datatype": "DATATYPE", "of": "OF",
    "association": "ASSOCIATION_NAME", "enum": "ENUM", "relation": "RELATION",
    "genset": "GENSET", "disjoint": "DISJOINT", "complete": "COMPLETE",
    "general": "GENERAL", "specifics": "SPECIFICS", "categorizer": "CATEGORIZER",
    "where": "WHERE", "package": "PACKAGE", "class": "CLASS", "import": "IMPORT",
    "functional-complexes": "FUNCTIONALCOMPLEXES", 
    "const": "CONST", "instanceOf": "INSTANCEOF",

    # Tipos
    "number": "NUMBER_TYPE", "string": "STRING_TYPE", "boolean": "BOOLEAN_TYPE",
    "date": "DATE_TYPE", "time": "TIME_TYPE", "datetime": "DATETIME_TYPE", "int": "INT_TYPE",
}

