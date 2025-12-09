import json
from collections import defaultdict
from typing import List, Dict, Tuple, Any
import itertools


# ==============================================================================
# 1. SUBKIND PATTERN (Kind -> Subkind(s) + Genset Disjoint)
# ==============================================================================
def check_subkind_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Subkind pattern.
    Regra Semântica Principal: O Genset DEVE ser 'disjoint'.
    """
    errors = []
    found = []

    kinds = {}
    subkinds_by_general = defaultdict(list)
    gensets_by_general = defaultdict(list)

    # 1. Coleta de Declarações (Classes e Gensets)
    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")
            name = decl.get("name")
            if stereotype == "kind":
                kinds[name] = decl
            elif stereotype == "subkind":
                for super_type in decl.get("specializes", []):
                    subkinds_by_general[super_type].append(decl)
        elif decl_type == "GeneralizationSet":  # Ajustado para a AST do main.py
            general_name = decl.get("general")
            if general_name:
                gensets_by_general[general_name].append(decl)

    # 2. Validação do Padrão Subkind
    for kind_name, kind_decl in kinds.items():
        subkinds = subkinds_by_general.get(kind_name, [])
        if len(subkinds) < 2:
            continue

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            modifiers = genset_decl.get("modifiers", [])
            is_disjoint = "disjoint" in modifiers
            is_complete = "complete" in modifiers
            genset_name = genset_decl.get("name", "N/A")

            # Requisito Semântico: O Genset DEVE ser 'disjoint' para Subkinds
            if not is_disjoint:
                errors.append(
                    {
                        "type": "Semantic Error (Mandatory Constraint - Coerção)",
                        "pattern": "Subkind Pattern",
                        "message": f"ERRO POR COERÇÃO: O Genset '{genset_name}' que especializa a Kind '{kind_name}' com Subkinds DEVE ser declarado como 'disjoint'.",
                        "lineno": genset_decl.get("lineno", "N/A"),
                    }
                )
                continue  # Não é um padrão Subkind válido

            genset_specifics_names = set(genset_decl.get("specifics", []))

            if len(genset_specifics_names) >= 2:
                # Checa se todos os subkinds que especializam essa Kind estão no Genset
                actual_subkinds_names = set(
                    s["name"]
                    for s in subkinds
                    if s.get("specializes", [kind_name])[0] == kind_name
                )

                if actual_subkinds_names.issubset(genset_specifics_names):
                    found.append(
                        {
                            "pattern": "Subkind Pattern",
                            "kind": kind_name,
                            "subkinds": list(actual_subkinds_names),
                            "genset_name": genset_name,
                            "is_complete": is_complete,
                            # CORREÇÃO: Usar .get() para evitar KeyError se lineno não estiver na AST
                            "lineno": kind_decl.get("lineno", "N/A"),
                        }
                    )
                    break

    return found, errors


# ==============================================================================
# 2. ROLE PATTERN (Kind -> Role(s) + Genset Non-Disjoint)
# ==============================================================================
def check_role_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Role Pattern.
    Regra Semântica Principal: O Genset NÃO DEVE ser 'disjoint'.
    """
    errors = []
    found = []

    kinds = {}
    roles_by_general = defaultdict(list)
    gensets_by_general = defaultdict(list)

    # 1. Coleta de Declarações
    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")
            name = decl.get("name")
            if stereotype == "kind":
                kinds[name] = decl
            elif stereotype == "role":
                for super_type in decl.get("specializes", []):
                    roles_by_general[super_type].append(decl)
        elif decl_type == "GeneralizationSet":  # Ajustado para a AST do main.py
            general_name = decl.get("general")
            if general_name:
                gensets_by_general[general_name].append(decl)

    # 2. Validação do Padrão Role
    for kind_name, kind_decl in kinds.items():
        roles = roles_by_general.get(kind_name, [])
        if len(roles) < 2:
            continue

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            modifiers = genset_decl.get("modifiers", [])
            is_disjoint = "disjoint" in modifiers
            is_complete = "complete" in modifiers
            genset_name = genset_decl.get("name", "N/A")

            # Requisito Semântico: O Genset NÃO DEVE ser 'disjoint' para Roles
            if is_disjoint:
                errors.append(
                    {
                        "type": "Semantic Error (Coercion Conflict)",  # Coerção: Role exige Non-Disjoint
                        "pattern": "Role Pattern",
                        "message": f"ERRO POR COERÇÃO: O Genset '{genset_name}' que especializa a Kind '{kind_name}' com Roles não deve ser declarado como 'disjoint' (conflito de coerção).",
                        "lineno": genset_decl.get("lineno", "N/A"),
                    }
                )

            genset_specifics_names = set(genset_decl.get("specifics", []))

            if len(genset_specifics_names) >= 2:
                actual_roles_names = set(
                    r["name"]
                    for r in roles
                    if r.get("specializes", [kind_name])[0] == kind_name
                )

                if actual_roles_names.issubset(genset_specifics_names):
                    found.append(
                        {
                            "pattern": "Role Pattern",
                            "kind": kind_name,
                            "roles": list(actual_roles_names),
                            "genset_name": genset_name,
                            "is_complete": is_complete,
                            # CORREÇÃO: Usar .get() para evitar KeyError se lineno não estiver na AST
                            "lineno": kind_decl.get("lineno", "N/A"),
                        }
                    )
                    break

    return found, errors


# ==============================================================================
# 3. PHASE PATTERN (Kind -> Phase(s) + Genset Disjoint OBRIGATÓRIO)
# ==============================================================================
def check_phase_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Phase Pattern.
    Regra Semântica Principal: O Genset DEVE ser 'disjoint'.
    """
    errors = []
    found = []

    kinds = {}
    phases_by_general = defaultdict(list)
    gensets_by_general = defaultdict(list)

    # 1. Coleta de Declarações
    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")
            name = decl.get("name")
            if stereotype == "kind":
                kinds[name] = decl
            elif stereotype == "phase":
                for super_type in decl.get("specializes", []):
                    phases_by_general[super_type].append(decl)
        elif decl_type == "GeneralizationSet":  # Ajustado para a AST do main.py
            general_name = decl.get("general")
            if general_name:
                gensets_by_general[general_name].append(decl)

    # 2. Validação do Padrão Phase
    for kind_name, kind_decl in kinds.items():
        phases = phases_by_general.get(kind_name, [])
        if len(phases) < 2:
            continue

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            modifiers = genset_decl.get("modifiers", [])
            is_disjoint = "disjoint" in modifiers
            is_complete = "complete" in modifiers
            genset_name = genset_decl.get("name", "N/A")

            # Requisito Semântico: O Genset DEVE ser 'disjoint'
            if not is_disjoint:
                errors.append(
                    {
                        "type": "Semantic Error (Mandatory Constraint - Coerção)",  # Coerção: Exige Disjoint
                        "pattern": "Phase Pattern",
                        "message": f"ERRO POR COERÇÃO: O Genset '{genset_name}' que especializa a Kind '{kind_name}' com Phases DEVE ser declarado como 'disjoint'.",
                        "lineno": genset_decl.get("lineno", "N/A"),
                    }
                )
                continue

            genset_specifics_names = set(genset_decl.get("specifics", []))

            if len(genset_specifics_names) >= 2:
                actual_phases_names = set(
                    p["name"]
                    for p in phases
                    if p.get("specializes", [kind_name])[0] == kind_name
                )

                if actual_phases_names.issubset(genset_specifics_names):
                    found.append(
                        {
                            "pattern": "Phase Pattern",
                            "kind": kind_name,
                            "phases": list(actual_phases_names),
                            "is_disjoint": is_disjoint,
                            "is_complete": is_complete,
                            # CORREÇÃO: Usar .get() para evitar KeyError se lineno não estiver na AST
                            "lineno": kind_decl.get("lineno", "N/A"),
                        }
                    )
                    break

    return found, errors


# ==============================================================================
# 4. RELATOR PATTERN (Kind(s) + Role(s) + Relator @mediation + @material relation)
# ==============================================================================
def check_relator_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Relator Pattern.
    """
    errors = []
    found = []

    kinds = {}
    roles_by_general = defaultdict(list)
    relators = {}
    material_relations = []

    # 1. Coleta de Declarações
    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        name = decl.get("name")

        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")
            if stereotype == "kind":
                kinds[name] = decl
            elif stereotype == "role":
                for super_type in decl.get("specializes", []):
                    roles_by_general[super_type].append(decl)
            elif stereotype == "relator":
                relators[name] = decl

        elif decl_type == "RelationDeclaration":
            # Relações Materiais (externas, declaradas fora das classes)
            if (
                decl.get("stereotype") == "material"
                or decl.get("relation_type") == "material"
            ):
                material_relations.append(decl)
            # Relator declarado como RelationDeclaration (modelo alternativo)
            elif decl.get("stereotype") == "relator":
                relators[name] = decl
        elif decl_type == "InlineRelation":
            # Relações Materiais (inline, declaradas fora das classes)
            if decl.get("stereotype") == "material":
                material_relations.append(decl)

    # 2. Identifica pares de Roles que especializam Kinds distintas
    valid_roles = {
        role["name"]: role
        for sublist in roles_by_general.values()
        for role in sublist
        if len(role.get("specializes", [])) == 1
    }
    role_pairs = list(itertools.combinations(valid_roles.keys(), 2))

    for role_name1, role_name2 in role_pairs:
        role1 = valid_roles[role_name1]
        role2 = valid_roles[role_name2]

        kind1 = role1.get("specializes", [None])[0]
        kind2 = role2.get("specializes", [None])[0]

        # O padrão exige que as Roles especializem Kinds distintas
        if not kind1 or not kind2 or kind1 == kind2:
            continue

        # 3. Validar o Relator de Mediação (Pelo menos 2 mediações para as Roles)
        found_relator = None
        for relator_name, relator_decl in relators.items():
            # Acessa relações internas (dentro do 'body' do Relator)
            terminations = relator_decl.get("body", {}).get("relations", [])

            # Tentativa alternativa para Classes (relatores) que podem ter membros
            if not terminations and relator_decl.get("body", {}).get("members"):
                terminations = relator_decl["body"]["members"]

            mediation_count = 0

            for term in terminations:
                # O AST do parser deve ter o campo 'stereotype' e 'target' (ou 'target_class')
                target_cls = term.get("target") or term.get("target_class")
                if term.get("stereotype") == "mediation" and target_cls in [
                    role_name1,
                    role_name2,
                ]:
                    mediation_count += 1

            if mediation_count >= 2:
                found_relator = relator_decl
                break

        # 4. Validar a Relação Material Externa
        found_material_relation = None
        for mat_rel_decl in material_relations:
            # Verifica se os alvos da relação material correspondem aos pares de Roles
            target1 = mat_rel_decl.get("source_class") or mat_rel_decl.get("target1")
            target2 = mat_rel_decl.get("target_class") or mat_rel_decl.get("target2")

            if (target1 == role_name1 and target2 == role_name2) or (
                target1 == role_name2 and target2 == role_name1
            ):

                # A verificação do estereótipo já foi feita na coleta (material)
                found_material_relation = mat_rel_decl
                break

        if found_relator and found_material_relation:
            found.append(
                {
                    "pattern": "Relator Pattern",
                    "relator_name": found_relator["name"],
                    "role1": role_name1,
                    "role2": role_name2,
                    "material_relation": found_material_relation.get(
                        "relation_name", "N/A"
                    ),
                    "lineno": found_relator.get("lineno", "N/A"),
                }
            )
        elif found_relator or found_material_relation:
            # Dedução de Padrão Incompleto (Sobrecarga)
            missing_part = []
            if not found_relator:
                missing_part.append("Relator com mediação")
            if not found_material_relation:
                missing_part.append("relação @material externa")

            if missing_part:
                errors.append(
                    {
                        "type": "Incomplete Pattern (Deduction Failure)",  # Incompleto
                        "pattern": "Relator Pattern",
                        "message": f"DEDUÇÃO DE PADRÃO INCOMPLETO: Foi detectada parte da estrutura do Relator Pattern (Roles '{role_name1}' e '{role_name2}'), mas está faltando: {', '.join(missing_part)}.",
                        # CORREÇÃO: Usar .get() para evitar KeyError se lineno não estiver na AST
                        "lineno": role1.get(
                            "lineno", "N/A"
                        ),  # Linha da primeira Role como referência
                    }
                )

    return found, errors


# ==============================================================================
# 5. MODE PATTERN (Mode -> @characterization + @externalDependence)
# ==============================================================================
def check_mode_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Mode Pattern.
    """
    errors = []
    found = []

    kinds = {}
    modes = {}

    # 1. Coleta de Declarações (Kinds e Modes)
    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")
            name = decl.get("name")
            if stereotype == "kind":
                kinds[name] = decl
            elif stereotype == "mode":
                modes[name] = decl

    # 2. Validação do Padrão Mode
    for mode_name, mode_decl in modes.items():

        # --- CORREÇÃO DE ERRO AQUI ---
        # 1. Acessa o 'body' de forma mais defensiva, aceitando None/null
        mode_body = mode_decl.get("body")

        # 2. Verifica se o body é um dicionário antes de tentar acessar chaves aninhadas
        if not isinstance(mode_body, dict):
            # Se o corpo for None, malformado, ou ausente, não há relações internas.
            body_relations = []
        else:
            # Se o corpo existe e é um dicionário, tenta buscar as relações
            body_relations = mode_body.get("relations", mode_body.get("members", []))
        # --- FIM DA CORREÇÃO ---

        char_relation = None
        ext_dep_relation = None

        for rel in body_relations:
            stereotype = rel.get("stereotype")
            if stereotype == "characterization":
                char_relation = rel
            elif stereotype == "externalDependence":
                ext_dep_relation = rel

        if char_relation and ext_dep_relation:
            target_char = char_relation.get("target") or char_relation.get(
                "target_class"
            )
            target_ext_dep = ext_dep_relation.get("target") or ext_dep_relation.get(
                "target_class"
            )

            # 3. Validação: Alvos são Kinds existentes?
            if target_char not in kinds or target_ext_dep not in kinds:
                errors.append(
                    {
                        "type": "Invalid Target (Incomplete Pattern)",  # Incompleto
                        "pattern": "Mode Pattern",
                        "message": f"DEDUÇÃO DE PADRÃO INCOMPLETO: O Mode '{mode_name}' está conectado a uma classe alvo ('{target_char}' ou '{target_ext_dep}') que não é uma Kind declarada.",
                        "lineno": mode_decl.get("lineno", "N/A"),
                    }
                )
                continue

            # 4. Validação Semântica: Kinds caracterizadas e dependentes devem ser distintas (idealmente)
            if target_char == target_ext_dep:
                errors.append(
                    {
                        "type": "Semantic Warning (Coercion)",
                        "pattern": "Mode Pattern",
                        "message": f"AVISO DE COERÇÃO: O Mode '{mode_name}' usa Characterization e External Dependence para a mesma Kind '{target_char}'. O Pattern clássico sugere Kinds distintas.",
                        "lineno": mode_decl.get("lineno", "N/A"),
                    }
                )

            # Padrão Mode completo encontrado
            found.append(
                {
                    "pattern": "Mode Pattern",
                    "mode_name": mode_name,
                    "characterizes": target_char,
                    "depends_on": target_ext_dep,
                    "lineno": mode_decl.get("lineno", "N/A"),
                }
            )
        else:
            # Dedução de Padrão Incompleto (Sobrecarga)
            missing_rel = " @characterization" if not char_relation else ""
            missing_rel += " @externalDependence" if not ext_dep_relation else ""

            errors.append(
                {
                    "type": "Incomplete Pattern (Deduction Failure)",  # Incompleto
                    "pattern": "Mode Pattern",
                    "message": f"DEDUÇÃO DE PADRÃO INCOMPLETO: O Mode '{mode_name}' está faltando a relação interna obrigatória:{missing_rel}.",
                    "lineno": mode_decl.get("lineno", "N/A"),
                }
            )

    return found, errors


# ==============================================================================
# 6. ROLEMIXIN PATTERN (RoleMixin -> Roles + Genset Disjoint Obrigatório)
# ==============================================================================
def check_rolemixin_pattern(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do RoleMixin Pattern.

    Regras Semânticas:
    ------------------
    1. Se um RoleMixin for especializado por uma ou mais Roles,
       ENTÃO deve existir um GeneralizationSet cujo 'general' = RoleMixin.

    2. Este Genset DEVE possuir o modificador 'disjoint'.

    3. O GenSet deve listar AO MENOS duas classes do tipo 'role'.

    4. Todos os 'specifics' do Genset devem ser estereótipo 'role'.

    Retorna:
        found_patterns: lista de padrões válidos encontrados.
        semantic_errors: lista de violações semânticas.
    """
    errors = []
    found = []

    # ----------------------------------------------------------------------
    # 1. COLETA PRELIMINAR
    # ----------------------------------------------------------------------
    rolemixins = {}
    roles = {}
    gensets_by_general = defaultdict(list)
    specializes_map = defaultdict(list)

    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")

        # Classes Normais
        if decl_type == "ClassDeclaration":
            name = decl.get("name")
            stereotype = decl.get("stereotype")

            # ATENÇÃO: estereótipo vindo da AST costuma ser "roleMixin"
            if stereotype == "roleMixin":
                rolemixins[name] = decl

            elif stereotype == "role":
                roles[name] = decl

            # mapear especializações (Super → [Subclasses])
            for sup in decl.get("specializes", []):
                specializes_map[sup].append(name)

        # GeneralizationSets
        elif decl_type == "GeneralizationSet":
            general = decl.get("general")
            if general:
                gensets_by_general[general].append(decl)

    # ----------------------------------------------------------------------
    # 2. VERIFICAÇÃO DO PADRÃO (LÓGICA ALTERADA)
    # ----------------------------------------------------------------------
    for rm_name, rm_decl in rolemixins.items():
        lineno_rm = rm_decl.get("lineno", "N/A")

        # Quais roles realmente especializam o RoleMixin?
        specializing_roles = [
            role_name
            for role_name in specializes_map.get(rm_name, [])
            if role_name in roles
        ]

        # Caso 1: RoleMixin não é especializado por nenhuma role → não há padrão
        if len(specializing_roles) == 0:
            continue  # Não gera erro, apenas não configura padrão

        # Caso 2: RoleMixin especializado por roles → Genset obrigatório
        associated_gensets = gensets_by_general.get(rm_name, [])
        pattern_found_in_genset = False

        # O Genset é obrigatório, mas se ele estiver ausente, devemos reportar o erro
        if not associated_gensets:
            errors.append(
                {
                    "type": "Incomplete Pattern (Mandatory Genset Missing)",
                    "pattern": "RoleMixin Pattern",
                    "message": (
                        f"O RoleMixin '{rm_name}' é especializado por Roles "
                        f"({', '.join(specializing_roles)}), mas NÃO possui "
                        f"nenhum GeneralizationSet. O padrão exige um Genset "
                        f"com modificador 'disjoint' cobrindo as Roles especializantes."
                    ),
                    "lineno": lineno_rm,
                }
            )
            # Continua o loop do RoleMixin para o próximo, o erro já foi reportado
            continue

        # ------------------------------------------------------------------
        # 3. Verificar cada Genset associado ao RoleMixin
        # ------------------------------------------------------------------
        for gs in associated_gensets:
            gs_name = gs.get("name", "N/A")
            gs_modifiers = gs.get("modifiers", [])
            gs_specifics = set(gs.get("specifics", []))
            gs_lineno = gs.get("lineno", "N/A")

            is_valid_genset = True  # Flag para checar se este Genset é válido

            # Regra: Genset DEVE ser 'disjoint'
            if "disjoint" not in gs_modifiers:
                errors.append(
                    {
                        "type": "Semantic Error (Mandatory Constraint)",
                        "pattern": "RoleMixin Pattern",
                        "message": (
                            f"O Genset '{gs_name}' associado ao RoleMixin '{rm_name}' "
                            f"DEVE ser declarado como 'disjoint'."
                        ),
                        "lineno": gs_lineno,
                    }
                )
                is_valid_genset = False
                # Continua verificando outros Gensets (se houver), mas não marca este como válido.

            # Regra: Ao menos duas roles
            if len(gs_specifics) < 2:
                errors.append(
                    {
                        "type": "Incomplete Pattern (Too Few Specifics)",
                        "pattern": "RoleMixin Pattern",
                        "message": (
                            f"O Genset '{gs_name}' associado ao RoleMixin '{rm_name}' "
                            f"possui menos de duas classes em 'specifics'. "
                            f"O padrão exige pelo menos duas roles."
                        ),
                        "lineno": gs_lineno,
                    }
                )
                is_valid_genset = False

            # Regra: Todos os specifics devem ser roles
            non_role_specifics = [name for name in gs_specifics if name not in roles]
            if non_role_specifics:
                errors.append(
                    {
                        "type": "Semantic Error (Type Violation)",
                        "pattern": "RoleMixin Pattern",
                        "message": (
                            f"O Genset '{gs_name}' possui 'specifics' que não são Roles: "
                            f"{', '.join(non_role_specifics)}. "
                            f"O RoleMixin Pattern exige somente estereótipos 'role'."
                        ),
                        "lineno": gs_lineno,
                    }
                )
                is_valid_genset = False

            # ------------------------------------------------------------------
            # NOVO CHECK: Verificar se as Roles especializantes estão no Genset
            # ------------------------------------------------------------------
            if is_valid_genset:
                missing_in_genset = set(specializing_roles) - gs_specifics

                if missing_in_genset:
                    errors.append(
                        {
                            "type": "Incomplete Pattern (Missing Specifics)",
                            "pattern": "RoleMixin Pattern",
                            "message": (
                                "DEDUÇÃO DE PADRÃO INCOMPLETO: "
                                f"O Genset '{gs_name}' não inclui todas as Roles especializantes. "
                                f"Roles ausentes: {', '.join(missing_in_genset)}."
                            ),
                            "lineno": gs_lineno,
                        }
                    )

                # Se o Genset é válido em termos de tipos e modificadores, considera-se o padrão encontrado
                # mesmo se houver Roles faltando (para que o erro de dedução seja o único reportado, não a ausência total)
                if not missing_in_genset:
                    pattern_found_in_genset = True
                    found.append(
                        {
                            "pattern": "RoleMixin Pattern",
                            "rolemixin": rm_name,
                            "roles_grouped": list(gs_specifics),
                            "genset_name": gs_name,
                            "lineno": lineno_rm,
                            "is_disjoint": True,
                        }
                    )

        # Se houver Gensets, mas nenhum deles satisfez as condições mínimas (disjoint e >= 2 roles),
        # ou se o Genset válido falhou ao cobrir as roles, o erro de Genset Missing não é reportado.
        # Mas garantimos que o erro de Missing Specifics ou Constraint Violation seja reportado.

    return found, errors


# ==============================================================================
# FUNÇÃO PRINCIPAL DE ANÁLISE SEMÂNTICA E FORMATO DE SAÍDA
# ==============================================================================
def run_semantic_checks(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Orquestra a execução de todos os verificadores de padrões de ontologia.
    """
    all_found = []
    all_errors = []

    checkers = [
        check_subkind_pattern,
        check_role_pattern,
        check_phase_pattern,
        check_relator_pattern,
        check_mode_pattern,
        check_rolemixin_pattern,
    ]

    for checker in checkers:
        found, errors = checker(ast)
        all_found.extend(found)
        all_errors.extend(errors)

    return all_found, all_errors


def format_unified_output(found_patterns: List[Dict], validation_errors: List[Dict]):
    """
    Formata a saída unificada conforme os três requisitos.
    """

    # (1) Padrões encontrados por linhas de código
    output_found = []
    for p in found_patterns:
        # Tenta extrair a Kind (ou RoleMixin/Mode/Relator) e os specifics (Subkinds/Roles/Phases)
        general_name = p.get("kind") or p.get("rolemixin") or p.get("rolemixin_name")

        specifics_list = p.get("subkinds") or p.get("roles_grouped") or p.get("phases")

        details = ""
        if p["pattern"] == "RoleMixin Pattern":
            details = (
                f"RoleMixin: {general_name} -> Roles: " f"{', '.join(specifics_list)}"
            )

        elif general_name and specifics_list:
            details = f"Kind: {general_name} -> Specifics: {', '.join(specifics_list)}"
        elif p["pattern"] == "Relator Pattern":
            details = f"Roles mediadas: {p['role1']} e {p['role2']}. Relator: {p['relator_name']}"
        elif p["pattern"] == "Mode Pattern":
            details = f"Caracteriza: {p['characterizes']} e Depende: {p['depends_on']}"

        output_found.append(
            f"  [LINHA {p.get('lineno', 'N/A')}] Padrão {p['pattern']} encontrado. {details}"
        )

    # (2) Erros a serem corrigidos por coerção
    output_coercion = []
    for e in validation_errors:
        if "Coerção" in e["type"] or "Coercion" in e["type"]:
            message = (
                e["message"]
                .replace("ERRO POR COERÇÃO: ", "")
                .replace("AVISO DE COERÇÃO: ", "")
            )
            output_coercion.append(
                f"  [LINHA {e.get('lineno', 'N/A')}] ERRO DE COERÇÃO: ({e['pattern']}): {message}"
            )

    # (3) Dedução de padrões incompletos, usando sobrecarregamento
    output_incomplete = []
    for e in validation_errors:
        if "Incomplete Pattern" in e["type"] or "Invalid Target" in e["type"]:
            message = e["message"].replace("DEDUÇÃO DE PADRÃO INCOMPLETO: ", "")
            output_incomplete.append(
                f"  [LINHA {e.get('lineno', 'N/A')}] PADRÃO INCOMPLETO (Dedução/Sobrecarga): ({e['pattern']}): {message}"
            )

    print("\n" + "=" * 60)
    print("        RELATÓRIO UNIFICADO DE ANÁLISE SEMÂNTICA".center(60))
    print("=" * 60)

    print("\n(1) PADRÕES DE PROJETO ENCONTRADOS POR LINHA DE CÓDIGO:")
    if output_found:
        print("\n".join(output_found))
    else:
        print("  Nenhum padrão de projeto completo foi encontrado.")

    print("\n" + "-" * 60)
    print(
        "\n(2) ERROS A SEREM CORRIGIDOS POR COERÇÃO (Violações de Restrições Semânticas):"
    )
    if output_coercion:
        print("\n".join(output_coercion))
    else:
        print("  Nenhum erro de coerção encontrado.")

    print("\n" + "-" * 60)
    print("\n(3) DEDUÇÃO DE PADRÕES INCOMPLETOS / AMBIGUIDADE (Sobrecarga de Regras):")
    if output_incomplete:
        print("\n".join(output_incomplete))
    else:
        print("  Nenhuma estrutura de padrão incompleta ou ambígua detectada.")
    print("\n" + "=" * 60)


# --- Bloco Main (Mantido para testes) ---
if __name__ == "__main__":
    # Exemplo de AST que usa a estrutura GeneralizationSet do seu parser:
    dummy_ast = {
        "package": "Teste",
        "declarations": [
            # 1. Subkind Pattern (Correto) - Linha 1-4
            {
                "type": "ClassDeclaration",
                "stereotype": "kind",
                "name": "Pessoa",
                "lineno": 1,
            },
            {
                "type": "ClassDeclaration",
                "stereotype": "subkind",
                "name": "Homem",
                "specializes": ["Pessoa"],
                "lineno": 2,
            },
            {
                "type": "ClassDeclaration",
                "stereotype": "subkind",
                "name": "Mulher",
                "specializes": ["Pessoa"],
                "lineno": 3,
            },
            {
                "type": "GeneralizationSet",
                "name": "Genero",
                "modifiers": ["disjoint", "complete"],
                "general": "Pessoa",
                "specifics": ["Homem", "Mulher"],
                "lineno": 4,
            },
            # 2. Role Pattern (ERRO POR COERÇÃO: Genset é 'disjoint' - Linha 5-8
            {
                "type": "ClassDeclaration",
                "stereotype": "kind",
                "name": "Agente",
                "lineno": 5,
            },
            {
                "type": "ClassDeclaration",
                "stereotype": "role",
                "name": "Cliente",
                "specializes": ["Agente"],
                "lineno": 6,
            },
            {
                "type": "ClassDeclaration",
                "stereotype": "role",
                "name": "Vendedor",
                "specializes": ["Agente"],
                "lineno": 7,
            },
            {
                "type": "GeneralizationSet",
                "name": "PapeisAgente",
                "modifiers": ["disjoint"],  # O Role Pattern exige Non-disjoint. ERRO!
                "general": "Agente",
                "specifics": ["Cliente", "Vendedor"],
                "lineno": 8,
            },
            # 3. Phase Pattern (Kind sem lineno para forçar o erro e testar a correção) - Linha 9-11
            {
                "type": "ClassDeclaration",
                "stereotype": "kind",
                "name": "Documento",
            },  # Sem lineno propositalmente
            {
                "type": "ClassDeclaration",
                "stereotype": "phase",
                "name": "Rascunho",
                "specializes": ["Documento"],
                "lineno": 10,
            },
            {
                "type": "ClassDeclaration",
                "stereotype": "phase",
                "name": "Final",
                "specializes": ["Documento"],
                "lineno": 11,
            },
            {
                "type": "GeneralizationSet",
                "name": "FasesDoc",
                "modifiers": ["disjoint"],
                "general": "Documento",
                "specifics": ["Rascunho", "Final"],
                "lineno": 12,
            },
        ],
    }

    found_patterns, validation_errors = run_semantic_checks(dummy_ast)
    format_unified_output(found_patterns, validation_errors)
