"""
Semantic analysis for TONTO (Textual Ontology Language).

Este módulo implementa a ANÁLISE SEMÂNTICA da linguagem TONTO,
focada na identificação e validação de Ontology Design Patterns (ODPs).

Pipeline Semântico
------------------
1. build_symbol_table(ast)
   Constrói uma visão unificada do modelo (symbol table), centralizando:
     - classes por estereótipo (kind, role, phase, mode, relator, roleMixin, ...)
     - mapa global de classes
     - conjuntos de generalização (GeneralizationSet)
     - mapa de especializações (super → subclasses)

2. util functions
   Conjunto de funções auxiliares defensivas:
     - extração segura de lineno
     - normalização de listas
     - helpers de fallback semântico

3. pattern checkers
   Cada padrão ontológico é validado por um checker independente,
   todos seguindo a assinatura comum:

       checker(ast, table) -> (found_patterns, validation_errors)

   Checkers disponíveis:
     - Subkind Pattern
     - Role Pattern
     - Phase Pattern
     - Relator Pattern
     - Mode Pattern
     - RoleMixin Pattern

4. run_semantic_checks(ast)
   Orquestra todos os checkers utilizando a symbol table compartilhada.

5. format_unified_output(found, errors)
   Produz um relatório unificado com:
     (1) padrões completos encontrados
     (2) erros por coerção (violações semânticas)
     (3) deduções incompletas / sobrecarga de regras

Observação Importante
---------------------
Todos os checkers utilizam a mesma symbol table para garantir:
  - consistência semântica global
  - ausência de diagnósticos contraditórios
  - facilidade de manutenção e extensão
"""

# ==============================================================================
# Imports
# ==============================================================================
import json
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
    Mantém None se nenhum valor estiver disponível.
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

    Estrutura da tabela:
      - classes_by_stereotype: { stereo -> { name -> decl } }
      - classes: { name -> decl }
      - gensets: [ GeneralizationSet decls ]
      - specializes_map: { super -> [subclasses] }

    Esta tabela é compartilhada por TODOS os checkers,
    garantindo consistência global.
    """
    table = {
        "classes_by_stereotype": defaultdict(dict),
        "classes": {},
        "gensets": [],
        "specializes_map": defaultdict(list),
    }

    for decl in ast.get("declarations", []):
        dtype = decl.get("type")

        if dtype == "ClassDeclaration":
            name = decl.get("name")
            stereo = decl.get("stereotype")

            if name:
                table["classes"][name] = decl

                if stereo:
                    table["classes_by_stereotype"][stereo][name] = decl

                # Super → Sub
                for sup in ensure_list(decl.get("specializes")):
                    table["specializes_map"][sup].append(name)

        elif dtype == "GeneralizationSet":
            table["gensets"].append(decl)

        # Relações são tratadas localmente nos checkers

    return table


# ==============================================================================
# 1. SUBKIND PATTERN (Kind -> Subkind(s) + Genset Disjoint)
# ==============================================================================
def check_subkind_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Subkind Pattern.

    Regras OntoUML:
    --------------
    - Uma Kind deve ser especializada por pelo menos dois Subkinds
    - Deve existir um GeneralizationSet associado (general = Kind)
    - O Genset DEVE ser 'disjoint'
    - Os specifics do Genset DEVEM ser apenas Subkinds
    - lineno do padrão = lineno do Genset (fallback para Kind)
    """
    errors = []
    found = []

    # ------------------------------------------------------------------
    # 1. Coleta de informações da AST
    # ------------------------------------------------------------------
    kinds = {}
    subkinds = {}
    specializes_map = defaultdict(list)
    gensets_by_general = defaultdict(list)

    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")

        if decl_type == "ClassDeclaration":
            name = decl.get("name")
            stereotype = decl.get("stereotype")

            if stereotype == "kind":
                kinds[name] = decl

            elif stereotype == "subkind":
                subkinds[name] = decl

            # mapear especializações (Super → [Subclasses])
            for super_type in decl.get("specializes", []):
                specializes_map[super_type].append(name)

        elif decl_type == "GeneralizationSet":
            general = decl.get("general")
            if general:
                gensets_by_general[general].append(decl)

    all_subkind_names = set(subkinds.keys())

    # ------------------------------------------------------------------
    # 2. Validação do Subkind Pattern
    # ------------------------------------------------------------------
    for kind_name, kind_decl in kinds.items():
        # Subkinds reais que especializam esta Kind
        actual_subkinds = [
            subkinds[name]
            for name in specializes_map.get(kind_name, [])
            if name in all_subkind_names
        ]

        if len(actual_subkinds) < 2:
            continue  # não configura Subkind Pattern

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            genset_name = genset_decl.get("name", "N/A")
            modifiers = set(genset_decl.get("modifiers", []))
            specifics = set(genset_decl.get("specifics", []))

            lineno_pattern = genset_decl.get("lineno", kind_decl.get("lineno"))

            # ------------------------------------------------------------------
            # FILTRO FUNDAMENTAL:
            # Genset só pode ser de Subkind se TODOS os specifics forem Subkinds
            # ------------------------------------------------------------------
            if not specifics.issubset(all_subkind_names):
                continue  # evita falso positivo (Phase, Role etc.)

            # Regra semântica obrigatória: disjoint
            if "disjoint" not in modifiers:
                errors.append(
                    {
                        "type": "Semantic Error (Mandatory Constraint - Coerção)",
                        "pattern": "Subkind Pattern",
                        "message": (
                            f"O Genset '{genset_name}' que especializa a Kind "
                            f"'{kind_name}' com Subkinds DEVE ser declarado como 'disjoint'."
                        ),
                        "lineno": lineno_pattern,
                    }
                )
                continue

            # Verifica cobertura real
            actual_subkind_names = {sk["name"] for sk in actual_subkinds}

            if actual_subkind_names.issubset(specifics):
                found.append(
                    {
                        "pattern": "Subkind Pattern",
                        "kind": kind_name,
                        "subkinds": sorted(list(actual_subkind_names)),
                        "genset_name": genset_name,
                        "is_complete": "complete" in modifiers,
                        "lineno": lineno_pattern,
                    }
                )
                break  # um Subkind Pattern por Kind é suficiente

    return found, errors


# ==============================================================================
# 2. ROLE PATTERN (Kind -> Role(s) + Genset NÃO disjoint)
# ==============================================================================
def check_role_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Role Pattern (OntoUML):

    Regras:
    -------
    - Uma Kind deve ser especializada por pelo menos dois Roles
    - Deve existir um GeneralizationSet associado (general = Kind)
    - O Genset NÃO DEVE ser 'disjoint' (coerção se estiver)
    - O Genset deve conter SOMENTE Roles (filtro ontológico obrigatório)
    - lineno do padrão = genset.lineno (fallback para kind)
    """
    errors: List[Dict] = []
    found: List[Dict] = []

    # ------------------------------------------------------------------
    # 1. Coleta via symbol table
    # ------------------------------------------------------------------
    kinds = table.get("classes_by_stereotype", {}).get("kind", {})
    roles = table.get("classes_by_stereotype", {}).get("role", {})
    gensets = table.get("gensets", [])
    specializes_map = table.get("specializes_map", {})

    all_role_names = set(roles.keys())

    # ------------------------------------------------------------------
    # 2. Validação do Role Pattern
    # ------------------------------------------------------------------
    for kind_name, kind_decl in kinds.items():
        # Roles reais que especializam esta Kind
        role_names = [
            n for n in specializes_map.get(kind_name, []) if n in all_role_names
        ]
        if len(role_names) < 2:
            continue  # não configura Role Pattern

        related_gs = [g for g in gensets if g.get("general") == kind_name]

        for gs in related_gs:
            gs_name = gs.get("name", "N/A")
            gs_mod = set(ensure_list(gs.get("modifiers")))
            gs_specs = set(ensure_list(gs.get("specifics")))

            # FILTRO CRÍTICO: considere apenas gensets compostos exclusivamente por roles
            if not gs_specs:
                continue
            if not gs_specs.issubset(all_role_names):
                continue  # ignora GS de Phase/Subkind/etc.

            # lineno do padrão = lineno do genset (fallback para kind)
            lineno_pattern = safe_lineno(gs, safe_lineno(kind_decl))

            # coerção: GS NÃO deve ser disjoint para Role Pattern
            if "disjoint" in gs_mod:
                errors.append(
                    {
                        "type": "Semantic Error (Coercion Conflict)",
                        "pattern": "Role Pattern",
                        "message": (
                            f"ERRO POR COERÇÃO: O Genset '{gs_name}' que especializa a Kind '{kind_name}' "
                            f"com Roles não deve ser declarado como 'disjoint'."
                        ),
                        "lineno": lineno_pattern,
                    }
                )

            # se GS cobre as roles reais -> pattern detectado
            if len(gs_specs) >= 2:
                actual_roles = set(role_names)
                if actual_roles and actual_roles.issubset(gs_specs):
                    found.append(
                        {
                            "pattern": "Role Pattern",
                            "kind": kind_name,
                            "roles": sorted(list(actual_roles)),
                            "genset_name": gs_name,
                            "is_complete": ("complete" in gs_mod),
                            "lineno": lineno_pattern,
                        }
                    )
                    break  # um Role Pattern por Kind é suficiente

    return found, errors


# ==============================================================================
# 3. PHASE PATTERN (Kind -> Phase(s) + Genset DISJOINT obrigatório)
# ==============================================================================
def check_phase_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Phase Pattern (OntoUML):

    Regras:
    -------
    - Uma Kind deve ser especializada por pelo menos duas Phases
    - Deve existir um GeneralizationSet associado (general = Kind)
    - O Genset DEVE ser 'disjoint' (coerção se não)
    - O Genset deve conter SOMENTE Phases (filtro ontológico)
    - lineno do padrão = genset.lineno (fallback para kind)
    """
    errors = []
    found = []

    # ------------------------------------------------------------------
    # 1. Coleta de informações da AST
    # ------------------------------------------------------------------
    kinds = {}
    phases = {}
    specializes_map = defaultdict(list)
    gensets_by_general = defaultdict(list)

    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")

        if decl_type == "ClassDeclaration":
            name = decl.get("name")
            stereotype = decl.get("stereotype")

            if stereotype == "kind":
                kinds[name] = decl

            elif stereotype == "phase":
                phases[name] = decl

            for super_type in decl.get("specializes", []):
                specializes_map[super_type].append(name)

        elif decl_type == "GeneralizationSet":
            general = decl.get("general")
            if general:
                gensets_by_general[general].append(decl)

    all_phase_names = set(phases.keys())

    # ------------------------------------------------------------------
    # 2. Validação do Phase Pattern
    # ------------------------------------------------------------------
    for kind_name, kind_decl in kinds.items():
        # Phases reais que especializam esta Kind
        actual_phases = [
            phases[name]
            for name in specializes_map.get(kind_name, [])
            if name in all_phase_names
        ]

        if len(actual_phases) < 2:
            continue  # não configura Phase Pattern

        associated_gensets = gensets_by_general.get(kind_name, [])

        for genset_decl in associated_gensets:
            genset_name = genset_decl.get("name", "N/A")
            modifiers = set(genset_decl.get("modifiers", []))
            specifics = set(genset_decl.get("specifics", []))

            lineno_pattern = genset_decl.get("lineno", kind_decl.get("lineno"))

            # --------------------------------------------------------------
            # FILTRO FUNDAMENTAL:
            # Genset só pode ser de Phase se TODOS os specifics forem Phases
            # --------------------------------------------------------------
            if not specifics.issubset(all_phase_names):
                continue  # ignora GS de Role/Subkind/etc.

            # Regra semântica obrigatória: Phase Pattern exige disjoint
            if "disjoint" not in modifiers:
                errors.append(
                    {
                        "type": "Semantic Error (Mandatory Constraint - Coerção)",
                        "pattern": "Phase Pattern",
                        "message": (
                            f"O Genset '{genset_name}' que especializa a Kind "
                            f"'{kind_name}' com Phases DEVE ser declarado como 'disjoint'."
                        ),
                        "lineno": lineno_pattern,
                    }
                )
                continue

            actual_phase_names = {p["name"] for p in actual_phases}

            if len(specifics) >= 2 and actual_phase_names.issubset(specifics):
                found.append(
                    {
                        "pattern": "Phase Pattern",
                        "kind": kind_name,
                        "phases": sorted(list(actual_phase_names)),
                        "is_disjoint": True,
                        "is_complete": ("complete" in modifiers),
                        "lineno": lineno_pattern,
                    }
                )
                break  # um Phase Pattern por Kind é suficiente

    return found, errors


# ==============================================================================
# 4. RELATOR PATTERN (Role(s) + Relator @mediation + @material)
# ==============================================================================
def check_relator_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Relator Pattern (OntoUML):

    Regras:
    -------
    - Pelo menos dois Roles que especializam Kinds distintas
    - Um Relator que possua >= 2 relações @mediation para essas Roles
    - Uma relação @material externa conectando exatamente as duas Roles
    - lineno do padrão: relator > material > role
    """
    errors = []
    found = []

    # ------------------------------------------------------------------
    # 1. Coleta de declarações
    # ------------------------------------------------------------------
    roles = {}
    relators = {}
    mediated_entities = {}  # role | kind | subkind
    specializes_map = defaultdict(list)
    material_relations = []

    for decl in ast.get("declarations", []):
        decl_type = decl.get("type")
        name = decl.get("name")

        # ------------------- Classes -------------------
        if decl_type == "ClassDeclaration":
            stereotype = decl.get("stereotype")

            if stereotype == "role":
                roles[name] = decl
                mediated_entities[name] = decl

            elif stereotype in {"kind", "subkind"}:
                mediated_entities[name] = decl

            elif stereotype == "relator":
                relators[name] = decl

            for sup in decl.get("specializes", []):
                specializes_map[sup].append(name)

        # ------------------- Relações externas -------------------
        elif decl_type in {"RelationDeclaration", "InlineRelation"}:
            if (
                decl.get("stereotype") == "material"
                or decl.get("relation_type") == "material"
            ):
                material_relations.append(decl)

    # Apenas roles com exatamente 1 supertype (simplificação ontológica comum)
    valid_roles = {
        name: r for name, r in roles.items() if len(r.get("specializes", [])) == 1
    }

    # ------------------------------------------------------------------
    # 2. Geração de pares válidos de Roles
    # ------------------------------------------------------------------
    role_pairs = list(itertools.combinations(valid_roles.keys(), 2))

    for r1_name, r2_name in role_pairs:
        r1 = valid_roles[r1_name]
        r2 = valid_roles[r2_name]

        kind1 = r1.get("specializes", [None])[0]
        kind2 = r2.get("specializes", [None])[0]

        # Regra: roles devem especializar Kinds distintas
        if not kind1 or not kind2 or kind1 == kind2:
            continue

        # ------------------------------------------------------------------
        # 3. Busca por Relator com mediação para ambas as Roles
        # ------------------------------------------------------------------
        found_relator = None

        for relator_decl in relators.values():
            body = relator_decl.get("body", {})
            terminations = body.get("relations") or body.get("members") or []

            mediated = set()
            for t in terminations:
                if t.get("stereotype") == "mediation":
                    target = t.get("target") or t.get("target_class")
                    if target in mediated_entities:
                        mediated.add(target)

            if {r1_name, r2_name}.issubset(mediated):
                found_relator = relator_decl
                break

        # ------------------------------------------------------------------
        # 4. Busca por relação @material externa conectando as Roles
        # ------------------------------------------------------------------
        found_material = None

        for mat in material_relations:
            t1 = (
                mat.get("source_class")
                or mat.get("target1")
                or mat.get("target_a")
                or mat.get("end1")
            )
            t2 = (
                mat.get("target_class")
                or mat.get("target2")
                or mat.get("target_b")
                or mat.get("end2")
            )

            if {t1, t2} == {r1_name, r2_name}:
                found_material = mat
                break

        # ------------------------------------------------------------------
        # 5. Classificação: completo ou incompleto
        # ------------------------------------------------------------------
        if found_relator and found_material:
            lineno_pattern = (
                found_relator.get("lineno")
                or found_material.get("lineno")
                or r1.get("lineno")
            )

            found.append(
                {
                    "pattern": "Relator Pattern",
                    "relator_name": found_relator.get("name"),
                    "roles": [r1_name, r2_name],
                    "material_relation": found_material.get(
                        "relation_name", found_material.get("name", "N/A")
                    ),
                    "lineno": lineno_pattern,
                }
            )

        elif found_relator or found_material:
            missing = []
            if not found_relator:
                missing.append("Relator com mediação")
            if not found_material:
                missing.append("relação @material externa")

            errors.append(
                {
                    "type": "Incomplete Pattern (Deduction Failure)",
                    "pattern": "Relator Pattern",
                    "message": (
                        f"DEDUÇÃO DE PADRÃO INCOMPLETO: Detecção parcial envolvendo "
                        f"Roles '{r1_name}' e '{r2_name}'. "
                        f"Faltando: {', '.join(missing)}."
                    ),
                    "lineno": r1.get("lineno"),
                }
            )

    return found, errors


# ==============================================================================
# 5. MODE PATTERN (Mode -> @characterization + @externalDependence)
# ==============================================================================
def check_mode_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Verifica instâncias do Mode Pattern.

    Regras:
      - Cada Mode deve ter relações internas @characterization e @externalDependence
      - Os alvos dessas relações devem ser Kinds declaradas
      - lineno retornado: prioridade -> mode.lineno, kind_char.lineno, kind_ext.lineno, 1 (fallback)
    Retorna: (found_patterns, errors)
    """
    errors: List[Dict] = []
    found: List[Dict] = []

    # --- Helpers locais (usa versões globais se existirem) ---
    def _ensure_list(v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        return [v]

    def _safe_lineno_of(decl):
        # tenta usar função global safe_lineno se disponível
        try:
            return globals().get(
                "safe_lineno",
                lambda d, fallback=1: (
                    int(d.get("lineno"))
                    if d and isinstance(d.get("lineno"), int) and d.get("lineno") > 0
                    else fallback
                ),
            )(decl, 1)
        except Exception:
            ln = decl.get("lineno") if isinstance(decl, dict) else None
            return ln if isinstance(ln, int) and ln > 0 else 1

    # --- Fonte de informações: usa 'table' (se fornecida) para acelerar buscas ---
    if table:
        kinds_map = table.get("classes_by_stereotype", {}).get("kind", {})
        modes_map = table.get("classes_by_stereotype", {}).get("mode", {})
    else:
        # fallback: varre AST
        kinds_map = {}
        modes_map = {}
        for decl in ast.get("declarations", []):
            if decl.get("type") == "ClassDeclaration":
                st = decl.get("stereotype")
                name = decl.get("name")
                if st == "kind":
                    kinds_map[name] = decl
                elif st == "mode":
                    modes_map[name] = decl

    # if table provided but modes_map empty, also fallback to AST scan (defensive)
    if not modes_map:
        for decl in ast.get("declarations", []):
            if (
                decl.get("type") == "ClassDeclaration"
                and decl.get("stereotype") == "mode"
            ):
                modes_map[decl.get("name")] = decl

    # --- Checagem por cada mode ---
    for mode_name, mode_decl in list(modes_map.items()):
        # defensive access to body
        body = mode_decl.get("body")
        if not isinstance(body, dict):
            body_relations = []
        else:
            # pode estar como 'relations' (parser novo) ou 'members' (parser alternativo)
            body_relations = _ensure_list(body.get("relations")) or _ensure_list(
                body.get("members")
            )

        # procura por characterization e externalDependence (aceita variações de campos)
        char_rel = None
        extdep_rel = None
        for r in body_relations:
            if not isinstance(r, dict):
                continue
            stereo = r.get("stereotype")
            # aceitar diferentes capitalizações caso o parser retorne assim
            if isinstance(stereo, str) and stereo.lower() == "characterization":
                char_rel = r
            elif isinstance(stereo, str) and stereo.lower() in (
                "externaldependence",
                "externaldependence",
            ):
                extdep_rel = r
            # também aceitar nomes diretos sem 'stereotype' (fallback)
            elif r.get("name") and r.get("name").lower().startswith("character"):
                char_rel = char_rel or r
            elif r.get("name") and "external" in r.get("name").lower():
                extdep_rel = extdep_rel or r

        # se ambos presentes -> validar alvos
        if char_rel and extdep_rel:
            target_char = (
                char_rel.get("target")
                or char_rel.get("target_class")
                or char_rel.get("targetClass")
            )
            target_ext = (
                extdep_rel.get("target")
                or extdep_rel.get("target_class")
                or extdep_rel.get("targetClass")
            )

            # normalize target names (strings) — se algum for lista, pega primeiro
            if isinstance(target_char, list):
                target_char = target_char[0] if target_char else None
            if isinstance(target_ext, list):
                target_ext = target_ext[0] if target_ext else None

            # targets devem existir como kinds
            if target_char not in kinds_map or target_ext not in kinds_map:
                errors.append(
                    {
                        "type": "Invalid Target (Incomplete Pattern)",
                        "pattern": "Mode Pattern",
                        "message": (
                            f"DEDUÇÃO DE PADRÃO INCOMPLETO: O Mode '{mode_name}' está conectado a um (ou ambos) alvo(s) "
                            f"('{target_char}', '{target_ext}') que não são Kinds declaradas."
                        ),
                        "lineno": _safe_lineno_of(mode_decl),
                    }
                )
                continue

            # se os alvos forem iguais, emitir aviso sem impedir descoberta do padrão
            if target_char == target_ext:
                errors.append(
                    {
                        "type": "Semantic Warning (Coercion)",
                        "pattern": "Mode Pattern",
                        "message": (
                            f"AVISO DE COERÇÃO: O Mode '{mode_name}' usa Characterization e ExternalDependence para a mesma Kind '{target_char}'."
                        ),
                        "lineno": _safe_lineno_of(mode_decl),
                    }
                )

            # padrão completo encontrado
            found.append(
                {
                    "pattern": "Mode Pattern",
                    "mode_name": mode_name,
                    "characterizes": target_char,
                    "depends_on": target_ext,
                    "lineno": _safe_lineno_of(mode_decl),
                }
            )

        else:
            # construir mensagem de missing
            missing = []
            if not char_rel:
                missing.append("@characterization")
            if not extdep_rel:
                missing.append("@externalDependence")

            errors.append(
                {
                    "type": "Incomplete Pattern (Deduction Failure)",
                    "pattern": "Mode Pattern",
                    "message": f"DEDUÇÃO DE PADRÃO INCOMPLETO: O Mode '{mode_name}' está faltando: {', '.join(missing)}.",
                    "lineno": _safe_lineno_of(mode_decl),
                }
            )

    return found, errors


# ==============================================================================
# 6. ROLEMIXIN PATTERN (RoleMixin → Roles + Genset disjoint obrigatório)
# ==============================================================================
def check_rolemixin_pattern(
    ast: Dict[str, Any], table: Dict[str, Any]
) -> Tuple[List[Dict], List[Dict]]:
    """
    RoleMixin Pattern:

    Regras Semânticas:
      1. Se um RoleMixin é especializado por ≥ 1 Roles → Genset é obrigatório
      2. O Genset DEVE ser 'disjoint'
      3. Genset deve listar ≥ 2 specifics
      4. Todos os specifics devem ser Roles
      5. O Genset deve cobrir TODAS as Roles especializantes
      6. lineno do padrão = genset.lineno (fallback roleMixin.lineno)
    """
    errors: List[Dict] = []
    found: List[Dict] = []

    # ------------------------------------------------------------------
    # Helpers defensivos
    # ------------------------------------------------------------------
    def _ensure_list(v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        return [v]

    def _safe_lineno(primary, fallback=None):
        for d in (primary, fallback):
            if isinstance(d, dict):
                ln = d.get("lineno")
                if isinstance(ln, int) and ln > 0:
                    return ln
        return 1

    # ------------------------------------------------------------------
    # Coleta estrutural (preferencialmente via table)
    # ------------------------------------------------------------------
    rolemixins = table.get("classes_by_stereotype", {}).get("roleMixin", {})
    roles = table.get("classes_by_stereotype", {}).get("role", {})
    gensets = table.get("gensets", [])
    specializes_map = table.get("specializes_map", {})

    all_role_names = set(roles.keys())

    # ------------------------------------------------------------------
    # Verificação por RoleMixin
    # ------------------------------------------------------------------
    for rm_name, rm_decl in rolemixins.items():
        lineno_rm = _safe_lineno(rm_decl)

        # Roles que especializam este RoleMixin
        specializing_roles = [
            r for r in specializes_map.get(rm_name, []) if r in all_role_names
        ]

        # Caso 0 — não há especialização por Role → não é padrão
        if not specializing_roles:
            continue

        # Gensets cujo general = RoleMixin
        related_gensets = [g for g in gensets if g.get("general") == rm_name]

        # ------------------------------------------------------------------
        # ERRO: Genset obrigatório ausente
        # ------------------------------------------------------------------
        if not related_gensets:
            errors.append(
                {
                    "type": "Incomplete Pattern (Mandatory Genset Missing)",
                    "pattern": "RoleMixin Pattern",
                    "message": (
                        f"O RoleMixin '{rm_name}' é especializado por Roles "
                        f"({', '.join(specializing_roles)}), mas NÃO possui "
                        f"nenhum GeneralizationSet."
                    ),
                    "lineno": lineno_rm,
                }
            )
            continue

        # ------------------------------------------------------------------
        # Verifica cada Genset associado
        # ------------------------------------------------------------------
        for gs in related_gensets:
            gs_name = gs.get("name", "N/A")
            gs_mod = set(_ensure_list(gs.get("modifiers")))
            gs_specs = set(_ensure_list(gs.get("specifics")))
            gs_lineno = _safe_lineno(gs, rm_decl)

            valid = True

            # (1) disjoint obrigatório
            if "disjoint" not in gs_mod:
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
                valid = False

            # (2) ao menos duas roles
            if len(gs_specs) < 2:
                errors.append(
                    {
                        "type": "Incomplete Pattern (Too Few Specifics)",
                        "pattern": "RoleMixin Pattern",
                        "message": (
                            f"O Genset '{gs_name}' possui menos de duas classes em 'specifics'."
                        ),
                        "lineno": gs_lineno,
                    }
                )
                valid = False

            # (3) specifics devem ser Roles
            non_roles = [s for s in gs_specs if s not in all_role_names]
            if non_roles:
                errors.append(
                    {
                        "type": "Semantic Error (Type Violation)",
                        "pattern": "RoleMixin Pattern",
                        "message": (
                            f"O Genset '{gs_name}' possui specifics que não são Roles: "
                            f"{', '.join(non_roles)}."
                        ),
                        "lineno": gs_lineno,
                    }
                )
                valid = False

            # (4) deve cobrir todas as Roles especializantes
            if valid:
                missing = set(specializing_roles) - gs_specs
                if missing:
                    errors.append(
                        {
                            "type": "Incomplete Pattern (Missing Specifics)",
                            "pattern": "RoleMixin Pattern",
                            "message": (
                                f"DEDUÇÃO DE PADRÃO INCOMPLETO: "
                                f"O Genset '{gs_name}' não inclui todas as Roles especializantes. "
                                f"Ausentes: {', '.join(sorted(missing))}."
                            ),
                            "lineno": gs_lineno,
                        }
                    )
                else:
                    # ✅ PADRÃO COMPLETO
                    found.append(
                        {
                            "pattern": "RoleMixin Pattern",
                            "rolemixin": rm_name,
                            "roles_grouped": sorted(gs_specs),
                            "genset_name": gs_name,
                            "is_disjoint": True,
                            "lineno": gs_lineno,
                        }
                    )

    return found, errors


# ==============================================================================
# FUNÇÃO PRINCIPAL DE ANÁLISE SEMÂNTICA
# ==============================================================================
def run_semantic_checks(ast: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    """
    Orquestra a execução de todos os verificadores semânticos
    utilizando uma symbol table unificada.

    Retorna:
        (found_patterns, validation_errors)
    """
    # 1. Construção da symbol table central
    table = build_symbol_table(ast)

    # 2. Lista de checkers semânticos
    checkers = [
        check_subkind_pattern,
        check_role_pattern,
        check_phase_pattern,
        check_relator_pattern,
        check_mode_pattern,
        check_rolemixin_pattern,
    ]

    all_found: List[Dict] = []
    all_errors: List[Dict] = []

    # 3. Execução coordenada
    for checker in checkers:
        found, errors = checker(ast, table)
        all_found.extend(found)
        all_errors.extend(errors)

    return all_found, all_errors


# ==============================================================================
# Helper para identificação do elemento central do padrão
# ==============================================================================
def extract_general_name(p: Dict[str, Any]) -> str:
    pattern = p.get("pattern")

    if pattern in {"Subkind Pattern", "Role Pattern", "Phase Pattern"}:
        return p.get("kind")

    if pattern == "RoleMixin Pattern":
        return p.get("rolemixin")

    if pattern == "Relator Pattern":
        return p.get("relator_name")

    if pattern == "Mode Pattern":
        return p.get("mode_name")

    return "<unknown>"


# ==============================================================================
# FORMATAÇÃO DO RELATÓRIO UNIFICADO
# ==============================================================================
def format_unified_output(found_patterns: List[Dict], validation_errors: List[Dict]):
    """
    Imprime relatório consolidado de análise semântica:

      (1) Padrões completos encontrados
      (2) Erros de coerção (violações semânticas obrigatórias)
      (3) Padrões incompletos / dedução / sobrecarga
    """

    # ------------------------------------------------------------------
    # (1) PADRÕES ENCONTRADOS
    # ------------------------------------------------------------------
    output_found = []

    for p in found_patterns:
        general_name = extract_general_name(p)

        specifics = (
            p.get("subkinds")
            or p.get("roles")
            or p.get("roles_grouped")
            or p.get("phases")
        )

        if p["pattern"] == "RoleMixin Pattern":
            details = (
                f"RoleMixin: {general_name} -> Roles: {', '.join(specifics or [])}"
            )

        elif p["pattern"] == "Relator Pattern":
            details = (
                f"Roles mediadas: {p.get('role1')} e {p.get('role2')}. "
                f"Relator: {p.get('relator_name')}"
            )

        elif p["pattern"] == "Mode Pattern":
            details = (
                f"Caracteriza: {p.get('characterizes')} | "
                f"Depende: {p.get('depends_on')}"
            )

        elif general_name and specifics:
            details = f"Kind: {general_name} -> Specifics: {', '.join(specifics)}"

        else:
            details = json.dumps(p, ensure_ascii=False)

        output_found.append(
            f"  [LINHA {p.get('lineno')}] "
            f"Padrão {p['pattern']} encontrado. {details}"
        )

    # ------------------------------------------------------------------
    # (2) ERROS DE COERÇÃO
    # ------------------------------------------------------------------
    output_coercion = []

    for e in validation_errors:
        if "Coerção" in e.get("type", "") or "Coercion" in e.get("type", ""):
            msg = (
                e["message"]
                .replace("ERRO POR COERÇÃO: ", "")
                .replace("AVISO DE COERÇÃO: ", "")
            )

            output_coercion.append(
                f"  [LINHA {e.get('lineno')}] "
                f"ERRO DE COERÇÃO ({e['pattern']}): {msg}"
            )

    # ------------------------------------------------------------------
    # (3) PADRÕES INCOMPLETOS / DEDUÇÃO
    # ------------------------------------------------------------------
    output_incomplete = []

    for e in validation_errors:
        if "Incomplete Pattern" in e.get("type", "") or "Invalid Target" in e.get(
            "type", ""
        ):
            msg = e["message"].replace("DEDUÇÃO DE PADRÃO INCOMPLETO: ", "")
            output_incomplete.append(
                f"  [LINHA {e.get('lineno')}] "
                f"PADRÃO INCOMPLETO ({e['pattern']}): {msg}"
            )

    # ------------------------------------------------------------------
    # IMPRESSÃO FINAL
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RELATÓRIO UNIFICADO DE ANÁLISE SEMÂNTICA".center(60))
    print("=" * 60)

    print("\n(1) PADRÕES DE PROJETO ENCONTRADOS:")
    print(
        "\n".join(output_found)
        if output_found
        else "  Nenhum padrão completo encontrado."
    )

    print("\n" + "-" * 60)
    print("\n(2) ERROS DE COERÇÃO (VIOLAÇÕES SEMÂNTICAS):")
    print(
        "\n".join(output_coercion)
        if output_coercion
        else "  Nenhum erro de coerção encontrado."
    )

    print("\n" + "-" * 60)
    print("\n(3) DEDUÇÃO DE PADRÕES INCOMPLETOS / AMBIGUIDADE:")
    print(
        "\n".join(output_incomplete)
        if output_incomplete
        else "  Nenhuma estrutura incompleta ou ambígua detectada."
    )

    print("\n" + "=" * 60)


# --- Bloco Main para teste rápido ---
if __name__ == "__main__":
    dummy_ast = {
        "package": "Teste",
        "declarations": [
            # Subkind example
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
            # Role example with disjoint GS (should produce coercion error)
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
                "modifiers": ["disjoint"],
                "general": "Agente",
                "specifics": ["Cliente", "Vendedor"],
                "lineno": 8,
            },
            # Phase example
            {
                "type": "ClassDeclaration",
                "stereotype": "kind",
                "name": "Documento",
            },  # intentionally no lineno
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
