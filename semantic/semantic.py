"""
Semantic analysis for TONTO (Textual Ontology Language).
Implementação completa com validação de padrões (ODPs) e Output Estético.
"""

import itertools
from typing import List, Dict, Tuple, Any
from collections import defaultdict


# ==============================================================================
# Utilitários Semânticos
# ==============================================================================
def safe_lineno(node: Dict[str, Any], fallback: int = None) -> Any:
    """
    Retorna node['lineno'] se existir.
    Caso contrário, retorna fallback.
    """
    if isinstance(node, dict):
        return node.get("lineno", fallback)
    return fallback


def ensure_list(x):
    """
    Normaliza valores possivelmente nulos ou escalares em lista.
    """
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


# ==============================================================================
# Symbol Table Builder
# ==============================================================================
def build_symbol_table(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constrói uma symbol table central a partir da AST.
    """
    table = {
        "classes_by_stereotype": defaultdict(dict),
        "classes": {},
        "gensets": [],
        "specializes_map": defaultdict(list),
    }

    for decl in ast.get("declarations", []):
        dtype = decl.get("type")
        name = decl.get("name")

        # CASO 1: Classes Normais (Kind, Role, Phase...)
        if dtype == "ClassDeclaration":
            stereo = decl.get("stereotype")
            if name:
                table["classes"][name] = decl
                if stereo:
                    table["classes_by_stereotype"][stereo][name] = decl

                for sup in ensure_list(decl.get("specializes")):
                    table["specializes_map"][sup].append(name)

        # CASO 2: Relações Externas (Relator)
        elif dtype == "RelationDeclaration":
            rtype = decl.get("relation_type")
            if name:
                table["classes"][name] = decl
                if rtype:
                    table["classes_by_stereotype"][rtype.lower()][name] = decl

                for sup in ensure_list(decl.get("specializes")):
                    table["specializes_map"][sup].append(name)

        # CASO 3: Gensets
        elif dtype == "GeneralizationSet":
            table["gensets"].append(decl)

    return table


# ==============================================================================
# 1. SUBKIND PATTERN
# ==============================================================================
def check_subkind_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    kinds = table["classes_by_stereotype"].get("kind", {})
    subkinds = table["classes_by_stereotype"].get("subkind", {})
    specializes_map = table["specializes_map"]

    gensets_by_general = defaultdict(list)
    for gs in table["gensets"]:
        gensets_by_general[gs.get("general")].append(gs)

    all_subkind_names = set(subkinds.keys())

    for kind_name, kind_decl in kinds.items():
        actual_subkinds = [
            n for n in specializes_map.get(kind_name, []) if n in all_subkind_names
        ]

        if len(actual_subkinds) < 2:
            continue

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            genset_name = genset_decl.get("name", "N/A")
            modifiers = set(genset_decl.get("modifiers", []))
            specifics = set(genset_decl.get("specifics", []))
            lineno = safe_lineno(genset_decl, safe_lineno(kind_decl))

            if not specifics.issubset(all_subkind_names):
                continue

            if "disjoint" not in modifiers:
                errors.append(
                    {
                        "category": "COERCAO",
                        "type": "ERRO DE COERÇÃO (Subkind Pattern)",
                        "message": f"O Genset '{genset_name}' que especializa a Kind '{kind_name}' com Subkinds DEVE ser declarado como 'disjoint'.",
                        "lineno": lineno,
                    }
                )
                continue

            if set(actual_subkinds).issubset(specifics):
                found.append(
                    {
                        "pattern": "Subkind Pattern",
                        "description": f"Kind '{kind_name}' particionada em {list(specifics)}",
                        "lineno": lineno,
                    }
                )
                break

    return found, errors


# ==============================================================================
# 2. ROLE PATTERN
# ==============================================================================
def check_role_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    kinds = table["classes_by_stereotype"].get("kind", {})
    roles = table["classes_by_stereotype"].get("role", {})
    gensets = table["gensets"]
    specializes_map = table["specializes_map"]
    all_role_names = set(roles.keys())

    for kind_name, kind_decl in kinds.items():
        actual_roles = [
            n for n in specializes_map.get(kind_name, []) if n in all_role_names
        ]

        if len(actual_roles) < 2:
            continue

        related_gs = [g for g in gensets if g.get("general") == kind_name]

        for gs in related_gs:
            gs_name = gs.get("name", "N/A")
            gs_mod = set(ensure_list(gs.get("modifiers")))
            gs_specs = set(ensure_list(gs.get("specifics")))
            lineno = safe_lineno(gs, safe_lineno(kind_decl))

            if not gs_specs or not gs_specs.issubset(all_role_names):
                continue

            if "disjoint" in gs_mod:
                errors.append(
                    {
                        "category": "COERCAO",
                        "type": "ERRO DE COERÇÃO (Role Pattern)",
                        "message": f"O Genset '{gs_name}' que especializa a Kind '{kind_name}' com Roles NÃO deve ser 'disjoint'.",
                        "lineno": lineno,
                    }
                )

            if len(gs_specs) >= 2:
                found.append(
                    {
                        "pattern": "Role Pattern",
                        "description": f"Kind '{kind_name}' especializada pelos papéis {list(gs_specs)}",
                        "lineno": lineno,
                    }
                )
                break

    return found, errors


# ==============================================================================
# 3. PHASE PATTERN
# ==============================================================================
def check_phase_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    kinds = table["classes_by_stereotype"].get("kind", {})
    phases = table["classes_by_stereotype"].get("phase", {})
    gensets = table["gensets"]
    all_phase_names = set(phases.keys())

    for gs in gensets:
        general = gs.get("general")
        specifics = set(gs.get("specifics", []))
        modifiers = set(gs.get("modifiers", []))
        lineno = safe_lineno(gs)

        if general in kinds and specifics and specifics.issubset(all_phase_names):
            if len(specifics) < 2:
                continue

            if "disjoint" not in modifiers:
                errors.append(
                    {
                        "category": "COERCAO",
                        "type": "ERRO DE COERÇÃO (Phase Pattern)",
                        "message": f"O Genset '{gs.get('name')}' que especializa a Kind '{general}' com Phases DEVE ser declarado como 'disjoint'.",
                        "lineno": lineno,
                    }
                )
            else:
                found.append(
                    {
                        "pattern": "Phase Pattern",
                        "description": f"Kind '{general}' muda de fase entre {list(specifics)}",
                        "lineno": lineno,
                    }
                )

    return found, errors


# ==============================================================================
# 4. RELATOR PATTERN (versão ampliada)
# ==============================================================================
def check_relator_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    found = []
    errors = []

    roles = table["classes_by_stereotype"].get("role", {})
    kinds = table["classes_by_stereotype"].get("kind", {})
    relators = table["classes_by_stereotype"].get("relator", {})

    candidate_types = {}
    candidate_types.update(roles)
    candidate_types.update(kinds)

    material_relations = []
    for decl in ast.get("declarations", []):
        dtype = decl.get("type")
        if dtype in {"RelationDeclaration", "InlineRelation"}:
            stereo = str(decl.get("stereotype") or "").lower()
            rtype = str(decl.get("relation_type") or "").lower()
            if stereo == "material" or rtype == "material":
                material_relations.append(decl)

    for rel_name, rel_decl in relators.items():
        body = rel_decl.get("body") or {}
        members = body.get("members", [])

        mediated_targets = set()
        mediation_linenos = []  # vamos guardar linhas das mediações
        for m in members:
            m_type = m.get("type")
            stereo = str(m.get("stereotype") or "").lower()
            if stereo == "mediation" or m_type in {
                "RelationPole",
                "InternalRelationPole",
            }:
                target = m.get("target_class") or m.get("target")
                if target:
                    mediated_targets.add(target)
                # se o membro tiver linha, guardamos como possível fallback
                m_ln = m.get("lineno")
                if m_ln is not None:
                    mediation_linenos.append(m_ln)

        mediated_candidates = [t for t in mediated_targets if t in candidate_types]
        if len(mediated_candidates) < 2:
            continue

        pair_list = list(itertools.combinations(sorted(mediated_candidates), 2))

        # linha base do relator: tenta o próprio relator; se não tiver,
        # cai na primeira mediação que tiver linha
        rel_base_lineno = safe_lineno(
            rel_decl, mediation_linenos[0] if mediation_linenos else None
        )

        for t1_name, t2_name in pair_list:
            related_materials = []
            for mat in material_relations:
                m1 = mat.get("source_class") or mat.get("end1") or mat.get("target1")
                m2 = mat.get("target_class") or mat.get("end2") or mat.get("target2")
                if {m1, m2} == {t1_name, t2_name}:
                    related_materials.append(mat)

            if related_materials:
                mat_names = []
                mat_linenos = []
                for mat in related_materials:
                    mat_name = mat.get("relation_name") or mat.get("name") or "unnamed"
                    mat_names.append(mat_name)
                    if mat.get("lineno") is not None:
                        mat_linenos.append(mat["lineno"])

                # linha final: prioriza linha da relação material, se existir;
                # caso contrário, usa a base do relator
                lineno = mat_linenos[0] if mat_linenos else rel_base_lineno

                found.append(
                    {
                        "pattern": "Relator Pattern",
                        "description": (
                            f"Relator '{rel_name}' materializado por {mat_names} "
                            f"conectando {t1_name} e {t2_name}"
                        ),
                        "lineno": lineno,
                    }
                )
            else:
                errors.append(
                    {
                        "category": "INCOMPLETO",
                        "type": "PADRÃO INCOMPLETO (Relator Pattern)",
                        "message": (
                            f"Relator '{rel_name}' media '{t1_name}' e '{t2_name}', "
                            f"mas não foi encontrada relação @material entre eles."
                        ),
                        "lineno": rel_base_lineno,
                    }
                )

    return found, errors


# ==============================================================================
# 5. MODE PATTERN
# ==============================================================================
def check_mode_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    found = []
    errors = []
    modes = table["classes_by_stereotype"].get("mode", {})

    # print("\n=== DEBUG MODE PATTERN ===")
    for mode_name, mode_decl in modes.items():
        # print(f"MODE DEBUG -> {mode_name} | decl.lineno = {mode_decl.get('lineno')}")

        body = mode_decl.get("body") or {}
        members = body.get("members", [])

        has_char = False
        has_ext_dep = False

        for m in members:
            stereo = m.get("stereotype", "").lower() if m.get("stereotype") else ""
            if "characterization" in stereo:
                has_char = True
            if "externaldependence" in stereo:
                has_ext_dep = True

        if has_char:
            ln = safe_lineno(mode_decl)
            # print(f"MODE DEBUG -> {mode_name} | safe_lineno = {ln}")
            found.append(
                {
                    "pattern": "Mode Pattern",
                    "description": f"Mode '{mode_name}' caracteriza uma entidade.",
                    "lineno": ln,
                }
            )
        else:
            missing = []
            if not has_char:
                missing.append("@characterization")
            if not has_ext_dep:
                missing.append("@externalDependence")

            ln = safe_lineno(mode_decl)
            # print(f"MODE DEBUG -> {mode_name} | safe_lineno (INCOMPLETO) = {ln}")

            errors.append(
                {
                    "category": "INCOMPLETO",
                    "type": "PADRÃO INCOMPLETO (Mode Pattern)",
                    "message": f"O Mode '{mode_name}' está faltando: {', '.join(missing)}.",
                    "lineno": ln,
                }
            )

    return found, errors


# ==============================================================================
# 6. ROLEMIXIN PATTERN
# ==============================================================================
def check_rolemixin_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    rolemixins = table["classes_by_stereotype"].get("roleMixin", {})
    roles = table["classes_by_stereotype"].get("role", {})
    specializes_map = table["specializes_map"]
    all_role_names = set(roles.keys())

    for rm_name, rm_decl in rolemixins.items():
        specializers = specializes_map.get(rm_name, [])
        role_specializers = [s for s in specializers if s in all_role_names]

        if not role_specializers:
            continue

        related_gs = [g for g in table["gensets"] if g.get("general") == rm_name]

        for gs in related_gs:
            modifiers = set(gs.get("modifiers", []))
            specifics = set(gs.get("specifics", []))
            lineno = safe_lineno(gs, safe_lineno(rm_decl))

            if "disjoint" not in modifiers:
                errors.append(
                    {
                        "category": "COERCAO",
                        "type": "ERRO DE COERÇÃO (RoleMixin Pattern)",
                        "message": f"O Genset de '{rm_name}' deve ser 'disjoint', pois RoleMixins se aplicam a Kinds disjuntas.",
                        "lineno": lineno,
                    }
                )
            else:
                found.append(
                    {
                        "pattern": "RoleMixin Pattern",
                        "description": f"RoleMixin '{rm_name}' generaliza papéis distintos {list(specifics)}.",
                        "lineno": lineno,
                    }
                )

        if role_specializers and not related_gs:
            # Fallback: linha do RoleMixin; se por algum motivo vier sem,
            # usa a linha de um dos Roles que o especializam
            fallback_role_decl = roles.get(role_specializers[0])
            lineno = safe_lineno(rm_decl, safe_lineno(fallback_role_decl))

            errors.append(
                {
                    "category": "INCOMPLETO",
                    "type": "PADRÃO INCOMPLETO (RoleMixin Pattern)",
                    "message": (
                        f"RoleMixin '{rm_name}' é especializado por Roles, mas não há um Genset explícito."
                    ),
                    "lineno": lineno,
                }
            )

    return found, errors


# ==============================================================================
# ORQUESTRADOR PRINCIPAL
# ==============================================================================
def run_semantic_checks(ast):
    """
    Função principal chamada pelo main.py.
    """
    if not ast:
        return [], []

    table = build_symbol_table(ast)

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

    for check_func in checkers:
        f, e = check_func(ast, table)
        all_found.extend(f)
        all_errors.extend(e)

    return all_found, all_errors


# ==============================================================================
# FORMATADOR DE SAÍDA (ESTÉTICO)
# ==============================================================================
def format_unified_output(found, errors):
    """Gera o relatório bonito para o terminal seguindo a estrutura solicitada."""

    # Cores ANSI
    C_HEADER = "\033[95m"  # Magenta
    C_OK = "\033[92m"  # Verde
    C_FAIL = "\033[91m"  # Vermelho
    C_WARN = "\033[93m"  # Amarelo
    C_BOLD = "\033[1m"
    C_RESET = "\033[0m"

    print(f"\n{C_HEADER}{'='*60}")
    print(f"{'RELATÓRIO UNIFICADO DE ANÁLISE SEMÂNTICA'.center(60)}")
    print(f"{'='*60}{C_RESET}\n")

    # --- (1) PADRÕES ENCONTRADOS ---
    print(f"{C_BOLD}(1) PADRÕES DE PROJETO ENCONTRADOS:{C_RESET}")
    if found:
        for f in found:
            ln = f["lineno"]
            lineno_str = f"[LINHA {ln}]" if ln and ln > 0 else "[LINHA N/A]"
            print(f"  {C_OK}✅ {lineno_str} {f['pattern']}{C_RESET}")
            print(f"     └─ {f['description']}")
    else:
        print(f"  {C_WARN}Nenhum padrão completo encontrado.{C_RESET}")

    print(f"\n{'-'*60}\n")

    # Separação dos erros por categoria (definida nos checkers)
    coercion_errors = [e for e in errors if e.get("category") == "COERCAO"]
    incomplete_errors = [e for e in errors if e.get("category") == "INCOMPLETO"]

    # --- (2) ERROS DE COERÇÃO ---
    print(f"{C_BOLD}(2) ERROS DE COERÇÃO (VIOLAÇÕES SEMÂNTICAS):{C_RESET}")
    if coercion_errors:
        for e in coercion_errors:
            ln = e["lineno"]
            lineno_str = f"[LINHA {ln}]" if ln and ln > 0 else "[LINHA N/A]"
            print(f"  {C_FAIL}❌ {lineno_str} {e['type']}:{C_RESET}")
            print(f"     {e['message']}")
    else:
        print(f"  {C_OK}Nenhuma violação de coerção detectada.{C_RESET}")

    print(f"\n{'-'*60}\n")

    # --- (3) PADRÕES INCOMPLETOS ---
    print(f"{C_BOLD}(3) PADRÕES INCOMPLETOS POR SOBRECARREGAMENTO:{C_RESET}")
    if incomplete_errors:
        for e in incomplete_errors:
            ln = e["lineno"]
            lineno_str = f"[LINHA {ln}]" if ln and ln > 0 else "[LINHA N/A]"
            print(f"  {C_WARN}⚠️  {lineno_str} {e['type']}:{C_RESET}")
            print(f"     {e['message']}")
    else:
        print(f"  {C_OK}Nenhuma ambiguidade ou padrão incompleto detectado.{C_RESET}")

    print(f"\n{C_HEADER}{'='*60}{C_RESET}\n")
