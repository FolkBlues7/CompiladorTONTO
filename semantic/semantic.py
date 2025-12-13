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

"""
Semantic analysis for TONTO (Textual Ontology Language).
Implementação completa com validação de padrões (ODPs).
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

        # Relações são tratadas localmente nos checkers se necessário

    return table

# ==============================================================================
# 1. SUBKIND PATTERN (Kind -> Subkind(s) + Genset Disjoint)
# ==============================================================================
def check_subkind_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []
    
    kinds = table["classes_by_stereotype"].get("kind", {})
    subkinds = table["classes_by_stereotype"].get("subkind", {})
    specializes_map = table["specializes_map"]
    
    # Mapear gensets por classe geral para acesso rápido
    gensets_by_general = defaultdict(list)
    for gs in table["gensets"]:
        gensets_by_general[gs.get("general")].append(gs)

    all_subkind_names = set(subkinds.keys())

    for kind_name, kind_decl in kinds.items():
        # Subkinds reais que especializam esta Kind
        actual_subkinds = [
            n for n in specializes_map.get(kind_name, [])
            if n in all_subkind_names
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

            # Regra: DEVE ser disjoint
            if "disjoint" not in modifiers:
                errors.append({
                    "type": "ERRO SEMÂNTICO (Violação de Rigidez)",
                    "pattern": "Subkind Pattern",
                    "message": f"O Genset '{genset_name}' (Kind '{kind_name}') DEVE ser 'disjoint'. Subkinds não podem se sobrepor.",
                    "lineno": lineno
                })
                continue

            # Verifica se cobre os subkinds encontrados
            if set(actual_subkinds).issubset(specifics):
                found.append({
                    "pattern": "Subkind Pattern",
                    "description": f"Kind '{kind_name}' particionada em {list(specifics)}",
                    "lineno": lineno
                })
                break

    return found, errors

# ==============================================================================
# 2. ROLE PATTERN (Kind -> Role(s) + Genset NÃO disjoint)
# ==============================================================================
def check_role_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    kinds = table["classes_by_stereotype"].get("kind", {})
    roles = table["classes_by_stereotype"].get("role", {})
    gensets = table["gensets"]
    specializes_map = table["specializes_map"]
    all_role_names = set(roles.keys())

    for kind_name, kind_decl in kinds.items():
        actual_roles = [n for n in specializes_map.get(kind_name, []) if n in all_role_names]
        
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

            # Regra: NÃO pode ser disjoint (Roles são anti-rígidos e podem se sobrepor)
            if "disjoint" in gs_mod:
                errors.append({
                    "type": "ERRO SEMÂNTICO (Violação Anti-Rigidez)",
                    "pattern": "Role Pattern",
                    "message": f"O Genset '{gs_name}' (Kind '{kind_name}') com Roles NÃO deve ser 'disjoint'. Um mesmo objeto pode ter múltiplos papéis.",
                    "lineno": lineno
                })

            if len(gs_specs) >= 2:
                found.append({
                    "pattern": "Role Pattern",
                    "description": f"Kind '{kind_name}' especializada pelos papéis {list(gs_specs)}",
                    "lineno": lineno
                })
                break

    return found, errors

# ==============================================================================
# 3. PHASE PATTERN (Kind -> Phase(s) + Genset DISJOINT obrigatório)
# ==============================================================================
def check_phase_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
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

        # Se o geral é Kind e os específicos são Phases
        if general in kinds and specifics and specifics.issubset(all_phase_names):
            if len(specifics) < 2:
                continue

            # Regra: DEVE ser disjoint (Phases são temporalmente disjuntas)
            if "disjoint" not in modifiers:
                errors.append({
                    "type": "ERRO SEMÂNTICO (Violação Temporal)",
                    "pattern": "Phase Pattern",
                    "message": f"O Genset '{gs.get('name')}' de Fases DEVE ser 'disjoint'. Um objeto não pode estar em duas fases ao mesmo tempo.",
                    "lineno": lineno
                })
            else:
                found.append({
                    "pattern": "Phase Pattern",
                    "description": f"Kind '{general}' muda de fase entre {list(specifics)}",
                    "lineno": lineno
                })

    return found, errors

# ==============================================================================
# 4. RELATOR PATTERN
# ==============================================================================
def check_relator_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    found = []
    errors = []
    relators = table["classes_by_stereotype"].get("relator", {})
    
    for rel_name, rel_decl in relators.items():
        body = rel_decl.get("body") or {}
        # O parser pode retornar 'members'
        members = body.get("members", [])
        
        # Filtra mediações (seja por estereótipo ou por ser RelationPole)
        mediations = [m for m in members if m.get("stereotype") == "mediation" or m.get("type") == "RelationPole"]
        
        if len(mediations) >= 2:
            targets = [m.get("target_class") for m in mediations]
            found.append({
                "pattern": "Relator Pattern",
                "description": f"Relator '{rel_name}' conecta: {targets}",
                "lineno": safe_lineno(rel_decl)
            })
        else:
            errors.append({
                "type": "AVISO SEMÂNTICO (Incompletude)",
                "pattern": "Relator Pattern",
                "message": f"O Relator '{rel_name}' deve mediar pelo menos 2 entidades.",
                "lineno": safe_lineno(rel_decl)
            })
            
    return found, errors

# ==============================================================================
# 5. MODE PATTERN
# ==============================================================================
def check_mode_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    found = []
    errors = []
    modes = table["classes_by_stereotype"].get("mode", {})

    for mode_name, mode_decl in modes.items():
        body = mode_decl.get("body") or {}
        members = body.get("members", [])
        
        has_char = False
        
        # Procura estereótipos nas relações internas
        for m in members:
            stereo = m.get("stereotype", "").lower() if m.get("stereotype") else ""
            if "characterization" in stereo: has_char = True
            
        if has_char:
            found.append({
                "pattern": "Mode Pattern",
                "description": f"Mode '{mode_name}' caracteriza uma entidade.",
                "lineno": safe_lineno(mode_decl)
            })
        else:
            errors.append({
                "type": "AVISO SEMÂNTICO",
                "pattern": "Mode Pattern",
                "message": f"Mode '{mode_name}' deveria ter uma relação de @characterization.",
                "lineno": safe_lineno(mode_decl)
            })

    return found, errors

# ==============================================================================
# 6. ROLEMIXIN PATTERN (FINALIZADO)
# ==============================================================================
def check_rolemixin_pattern(ast: Dict[str, Any], table: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
    errors = []
    found = []

    rolemixins = table["classes_by_stereotype"].get("roleMixin", {})
    roles = table["classes_by_stereotype"].get("role", {})
    specializes_map = table["specializes_map"]
    all_role_names = set(roles.keys())

    for rm_name, rm_decl in rolemixins.items():
        # Quais classes especializam este RoleMixin?
        specializers = specializes_map.get(rm_name, [])
        
        # Filtra apenas os que são Roles
        role_specializers = [s for s in specializers if s in all_role_names]

        if not role_specializers:
            continue

        # Verifica se existe um Genset cobrindo essas roles
        related_gs = [
            g for g in table["gensets"] 
            if g.get("general") == rm_name
        ]

        for gs in related_gs:
            modifiers = set(gs.get("modifiers", []))
            specifics = set(gs.get("specifics", []))
            lineno = safe_lineno(gs, safe_lineno(rm_decl))

            # Regra: RoleMixin exige Disjoint (pois separa Kinds diferentes)
            if "disjoint" not in modifiers:
                errors.append({
                    "type": "ERRO SEMÂNTICO (Abstração)",
                    "pattern": "RoleMixin Pattern",
                    "message": f"O Genset de '{rm_name}' deve ser 'disjoint', pois RoleMixins se aplicam a Kinds disjuntas.",
                    "lineno": lineno
                })
            else:
                found.append({
                    "pattern": "RoleMixin Pattern",
                    "description": f"RoleMixin '{rm_name}' generaliza papéis de entidades distintas {list(specifics)}.",
                    "lineno": lineno
                })

        if role_specializers and not related_gs:
             errors.append({
                "type": "AVISO DE DESIGN",
                "pattern": "RoleMixin Pattern",
                "message": f"RoleMixin '{rm_name}' é especializado por Roles {role_specializers}, mas não há um Genset explícito definindo essa generalização.",
                "lineno": safe_lineno(rm_decl)
            })

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

    # 1. Constrói a tabela de símbolos (Visão Global)
    table = build_symbol_table(ast)
    
    all_found = []
    all_errors = []

    # 2. Lista de Checkers para rodar
    checkers = [
        check_subkind_pattern,
        check_role_pattern,
        check_phase_pattern,
        check_relator_pattern,
        check_mode_pattern,
        check_rolemixin_pattern
    ]

    # 3. Execução
    for check_func in checkers:
        f, e = check_func(ast, table)
        all_found.extend(f)
        all_errors.extend(e)

    return all_found, all_errors

def format_unified_output(found, errors):
    """Gera o relatório bonito para o terminal"""
    print("\n" + "="*60)
    print("RELATÓRIO DE ANÁLISE SEMÂNTICA & PADRÕES (ODPs)".center(60))
    print("="*60 + "\n")

    if found:
        print("✅ PADRÕES ONTOLÓGICOS IDENTIFICADOS:")
        for f in found:
            print(f"   [Linha {f['lineno']}] {f['pattern']}")
            print(f"     └─ {f['description']}")
        print("")
    
    if errors:
        print("❌ VIOLAÇÕES E AVISOS SEMÂNTICOS:")
        for e in errors:
            print(f"   [Linha {e['lineno']}] {e['type']}")
            print(f"     └─ {e['message']}")
    else:
        if found:
            print("✨ Nenhuma violação semântica detectada nos padrões verificados.")
        else:
            print("ℹ️  Nenhum padrão ontológico complexo foi detectado.")
            
    print("\n" + "="*60 + "\n")