import os
import sys
import json  # <-- Importante para formatar a AST
from collections import Counter

# --- Importações dos nossos módulos ---

# (REQUISITO 2) Importa o lexer, necessário para a Análise Léxica (Fase 1)
from lexer.lexer import lexer

# Importa a função principal do parser (Fase 2)
from parser.parser import parse_tonto_code

# =============================================================================
# EXEMPLOS DE ENTRADA (REQUISITO 1: Mantidos)
# =============================================================================

TEST_EXAMPLES = {
    "1": {
        "name": "CarOwnershipExample",
        "code": """
// Exemplo 1: Car Ownership
package CarOwnership 

kind Organization
subkind CarAgency specializes Organization
kind Car

relator CarOwnership {
    @mediation
    -- involvesOwner -- [1] CarAgency

    @mediation
    -- involvesProperty -- [1] Car
}
""",
    },
    "2": {
        "name": "CarRentalExample",
        "code": """
// Exemplo 2: Car Rental
package CarRental 

kind Person

role Employee specializes Person
role ResponsibleEmployee specializes Employee

phase DeceasedPerson specializes Person
phase LivingPerson specializes Person

phase Child specializes LivingPerson
phase Teenager specializes LivingPerson
phase Adult specializes LivingPerson

disjoint complete genset AgePhase {
    general LivingPerson
    specifics Child, Teenager, Adult
}

disjoint complete genset LifeStatus {
    general Person
    specifics DeceasedPerson, LivingPerson
}

roleMixin Customer

role PersonalCustomer specializes Customer, Person

kind Organization

role CorporateCustomer specializes Organization

kind Car

phase AvailableCar specializes Car
phase UnderMaintenanceCar specializes Car

role RentalCar specializes AvailableCar

relator CarRental {
    @mediation
    -- involvesRental -- [1] RentalCar
    
    -- involvesMediator -- [1] ResponsibleEmployee
    
    @mediation
    -- involvesCustomer --[1] Customer
}
""",
    },
    "3": {
        "name": "FoodAllergyExample",
        "code": """
// Exemplo 3: Alergia Alimentar
import alergiaalimentar

package alergiaalimentar

kind Paciente

kind Alimento

subkind Proteina of functional-complexes  specializes Componente_Alimentar 

phase Crianca of functional-complexes  specializes Paciente 

phase Adulto of functional-complexes  specializes Paciente 

subkind Aditivo_Alimentar of functional-complexes  specializes Componente_Alimentar 

subkind Carboidrato of functional-complexes  specializes Componente_Alimentar 

subkind Imuno_Mediada of relators  specializes Alergia 

subkind Nao_Imuno_Mediada of relators  specializes Alergia 

mode Sintoma

subkind Cutaneo of intrinsic-modes  specializes Sintoma 

subkind Gastrointestinal of intrinsic-modes  specializes Sintoma 

subkind Respiratorio of intrinsic-modes  specializes Sintoma 

subkind Sistemico of intrinsic-modes  specializes Sintoma 

role Alergeno of functional-complexes  specializes Componente_Alimentar 

relator Tratamento

relator Diagnostico

subkind Mista of relators  specializes Alergia 

kind Profissional_de_Saude

subkind Ingrediente of functional-complexes  specializes Alimento 

subkind Formula of functional-complexes  specializes Alimento 

subkind Teste_de_Dosagem_IgE_Serica of functional-complexes  specializes Procedimento 

subkind Teste_de_Provocacao_Oral of functional-complexes  specializes Procedimento 

kind Procedimento

subkind Dieta_de_Exclusao of relators  specializes Tratamento 

subkind Medicamento of relators  specializes Tratamento 

subkind Imunoterapia_Oral of relators  specializes Tratamento 

quality Comobidarde_Alergica

quality Heranca_Genetica

event Reacao_Cruzada specializes Reacao_Adversa 

relator Alergia

event Reacao_Adversa

kind Componente_Alimentar

event Consumo_Alimentar

subkind Teste_Cutaneo of functional-complexes  specializes Procedimento 

mode Disposicao_Alergica

situation Exposicao_ao_Alergeno

relator Avaliacao_de_Risco

quality Nivel_de_Risco

genset disjoint_complete {
    general Componente_Alimentar
    specifics Proteina, Aditivo_Alimentar, Carboidrato
}

genset disjoint_complete {
    general Alergia
    specifics Imuno_Mediada, Mista, Nao_Imuno_Mediada
}

genset disjoint_complete {
    general Sintoma
    specifics Respiratorio, Sistemico, Gastrointestinal, Cutaneo
}

genset disjoint_complete {
    general Procedimento
    specifics Teste_Cutaneo, Teste_de_Dosagem_IgE_Serica, Teste_de_Provocacao_Oral
}

genset disjoint_complete {
    general Alimento
    specifics Formula, Ingrediente
}

genset disjoint_complete {
    general Paciente
    specifics Crianca, Adulto
}

genset disjoint_complete {
    general Tratamento
    specifics Imunoterapia_Oral, Medicamento, Dieta_de_Exclusao
}
""",
    },
    "4": {
        "name": "TDAHExample",
        "code": """
// Exemplo 4: TDAH
import TDAH

package TDAH

category Hyperactivity_Symptom

category Neurologically_Based_Condition specializes Medical_Condition 

mixin Medical_Condition 

category Inattention_Symptom 

role Patient specializes Person 

relator Medical_Report

role Doctor specializes Person 

kind Person

mode Behavioral_Therapy

mode Medication_Therapy

subkind Methylphenidate_ specializes Medicine 

subkind Dextroamphetamine_ specializes Medicine 

relator Prescription

phase Preschool_Age specializes Patient 

phase School_Age specializes Patient 

phase Teenager specializes Patient 

phase Adult specializes Patient 

quality Birth_Sex

kind Medicine

role Psychologist specializes Person 

kind Criterion_B

kind Criterion_C

kind Criterion_D

kind Criterion_E

kind Criterion_A1a specializes Hyperactivity_Symptom 

kind Criterion_A1b specializes Hyperactivity_Symptom 

kind Criterion_A1c specializes Hyperactivity_Symptom 

kind Criterion_A1d specializes Hyperactivity_Symptom 

kind Criterion_A1e specializes Hyperactivity_Symptom 

kind Criterion_A1f specializes Hyperactivity_Symptom 

kind Criterion_A1g specializes Hyperactivity_Symptom 

kind Criterion_A1h specializes Hyperactivity_Symptom 

kind Criterion_A1i specializes Hyperactivity_Symptom 

kind Criterion_A2a specializes Inattention_Symptom 

kind Criterion_A2b specializes Inattention_Symptom 

kind Criterion_A2c specializes Inattention_Symptom 

kind Criterion_A2d specializes Inattention_Symptom 

kind Criterion_A2e specializes Inattention_Symptom 

kind Criterion_A2f specializes Inattention_Symptom 

kind Criterion_A2g specializes Inattention_Symptom 

kind Criterion_A2h specializes Inattention_Symptom 

kind Criterion_A2i specializes Inattention_Symptom 

quality Severity

subkind Criterion_A1 specializes Criterion_A 

subkind Criterion_A2 specializes Criterion_A 

kind Criterion_A

kind ADHD specializes Neurologically_Based_Condition 

disjoint complete genset TypesOfMedicine {
    general Medicine
    specifics Dextroamphetamine_, Methylphenidate_
}

disjoint complete genset PhasesOfAPatient{
    general Patient
    specifics Preschool_Age, School_Age, Adult, Teenager
}
""",
    },
}


def imprimir_relatorio_amigavel(ast):
    """
    Transforma a AST bruta em uma árvore visual amigável.
    Versão atualizada para suportar Relations com Source/Target Cardinality.
    """
    print("\n" + "="*60)
    print("RESUMO ESTRUTURAL DA ONTOLOGIA".center(60))
    print("="*60)

    # 1. PACOTE
    pkg_name = ast['package']['name']
    print(f"\n📦 PACOTE: {pkg_name}")
    
    # 2. IMPORTS
    if ast['imports']:
        print("   └── 📥 IMPORTS:")
        for imp in ast['imports']:
            print(f"       • {imp['target']}")

    print("   │")

    # 3. DECLARAÇÕES
    declarations = ast['declarations']
    if not declarations:
        print("   └── (Nenhuma declaração encontrada)")
        return

    for i, decl in enumerate(declarations):
        is_last_decl = (i == len(declarations) - 1)
        prefix = "   └──" if is_last_decl else "   ├──"
        sub_prefix = "       " if is_last_decl else "   │   "

        tipo = decl.get('type')

        # --- VISUALIZAÇÃO DE CLASSE ---
        if tipo == 'ClassDeclaration':
            stereo = decl['stereotype']
            name = decl['name']
            specs = decl['specializes']
            nature = decl['nature']
            
            # Cabeçalho
            info_extra = ""
            if nature: info_extra += f" ({nature})"
            if specs:  info_extra += f" ➡️ Specializes: {', '.join(specs)}"
            
            print(f"{prefix} 📄 CLASSE: {name}")
            print(f"{sub_prefix}├── Estereótipo: <<{stereo}>>{info_extra}")

            # Corpo
            body = decl.get('body')
            members = body['members'] if body and 'members' in body else []
            
            if not members:
                print(f"{sub_prefix}└── (Sem atributos ou relações internas)")
            else:
                for j, member in enumerate(members):
                    is_last_mem = (j == len(members) - 1)
                    mem_pref = "└──" if is_last_mem else "├──"
                    
                    if member['type'] == 'Attribute':
                        # Atributos usam 'cardinality' simples
                        card = member.get('cardinality')
                        card_str = f" [{card}]" if card else ""
                        constr = f" {{{member['constraints'][0]}}}" if member.get('constraints') else ""
                        print(f"{sub_prefix}{mem_pref} 🔹 [Atributo] {member['name']} : {member['datatype']}{card_str}{constr}")
                    
                    elif member['type'] == 'RelationPole':
                        # Relações agora usam target/source cardinality
                        tgt_card = member.get('target_cardinality') or member.get('cardinality') or "1"
                        src_card = member.get('source_cardinality')
                        
                        src_str = f"[{src_card}] " if src_card else ""
                        arrow = member.get('arrow', '--')
                        rel_name = member.get('name')
                        name_str = f" {rel_name} " if rel_name else " "
                        
                        target_cls = member.get('target_class') or member.get('target')

                        print(f"{sub_prefix}{mem_pref} 🔗 [Relação] {src_str}{arrow}{name_str}[{tgt_card}] ➝ {target_cls}")

        # --- VISUALIZAÇÃO DE RELAÇÃO EXTERNA (Relator) ---
        elif tipo == 'RelationDeclaration':
            print(f"{prefix} 🔗 RELAÇÃO EXTERNA: {decl['name']}")
            print(f"{sub_prefix}├── Tipo: <<{decl['relation_type']}>>")
            
            body = decl.get('body')
            members = body['members'] if body and 'members' in body else []
            
            if members:
                 for j, member in enumerate(members):
                    is_last_mem = (j == len(members) - 1)
                    mem_pref = "└──" if is_last_mem else "├──"
                    
                    if member['type'] == 'RelationPole':
                         # Lógica adaptada para relator
                         tgt_card = member.get('target_cardinality') or member.get('cardinality') or "1"
                         src_card = member.get('source_cardinality')
                         src_str = f"[{src_card}] " if src_card else ""
                         arrow = member.get('arrow', '--')
                         target_cls = member.get('target_class') or member.get('target')
                         
                         print(f"{sub_prefix}{mem_pref} Conecta: {src_str}{arrow} [{tgt_card}] ➝ {target_cls}")
            else:
                print(f"{sub_prefix}└── (Sem conexões definidas)")

        # --- VISUALIZAÇÃO DE ENUM ---
        elif tipo == 'EnumDeclaration':
            print(f"{prefix} 🔢 ENUM: {decl['name']}")
            membros = ", ".join(decl['members'])
            print(f"{sub_prefix}└── Valores: {{{membros}}}")

        # --- VISUALIZAÇÃO DE DATATYPE ---
        elif tipo == 'DataTypeDeclaration':
            print(f"{prefix} 💾 DATATYPE: {decl['name']}")
            attrs = decl['attributes']
            if not attrs:
                 print(f"{sub_prefix}└── (Vazio)")
            else:
                for j, attr in enumerate(attrs):
                    is_last_mem = (j == len(attrs) - 1)
                    mem_pref = "└──" if is_last_mem else "├──"
                    print(f"{sub_prefix}{mem_pref} • {attr['name']} : {attr['datatype']}")

        # --- VISUALIZAÇÃO DE GENSET ---
        elif tipo == 'GeneralizationSet':
            print(f"{prefix} 🔱 GENSET: {decl['name']}")
            mods = ", ".join(decl['modifiers']) if decl['modifiers'] else "Normal"
            cat = f" (Categorizer: {decl['categorizer']})" if decl.get('categorizer') else ""
            
            print(f"{sub_prefix}├── Propriedades: {{{mods}}}{cat}")
            print(f"{sub_prefix}├── Geral: {decl['general']}")
            print(f"{sub_prefix}└── Específicos: {', '.join(decl['specifics'])}")
            
        # --- VISUALIZAÇÃO DE TYPE (High Order) ---
        elif tipo == 'HighOrderType':
            print(f"{prefix} 🆙 TYPE: {decl['name']}")

    print("\n" + "="*60 + "\n")


# =============================================================================
# FUNÇÕES DE ANÁLISE
# =============================================================================


def run_analysis_lexica(codigo_para_analise, nome_do_teste):
    """Executa a ANÁLISE LÉXICA (Fase 1)"""
    print(f"\n--- Iniciando Análise LÉXICA para: {nome_do_teste} ---")

    token_counts = Counter()
    lexer.lineno = 1
    lexer.input(codigo_para_analise)

    print("\n=== VISÃO ANALÍTICA (LISTA DE TOKENS) ===")
    while True:
        token = lexer.token()
        if not token:
            break
        print(
            f"  [Tipo: {token.type:<20} Lexema: '{token.value}' Linha: {token.lineno}]"
        )
        token_counts[token.type] += 1

    print("\n" + "=" * 50)
    print("=== TABELA DE SÍNTESE (CONTAGEM DE TOKENS) ===".center(50))
    print("=" * 50)
    if not token_counts:
        print("Nenhum token foi encontrado.")
    else:
        for token_type, count in sorted(token_counts.items()):
            print(f"  {token_type:<25}: {count}")
    print("\n--- Análise Léxica Concluída ---")


def run_analysis_sintatica(codigo_para_analise, nome_do_teste):
    """Executa a ANÁLISE SINTÁTICA (Fase 2)"""
    print(f"\n--- Iniciando Análise SINTÁTICA para: {nome_do_teste} ---")

    ast_result = parse_tonto_code(codigo_para_analise)

    if ast_result:
        print("\n[SUCESSO] A estrutura sintática está CORRETA. Gerando relatório...")

        # 1. Opção de ver o JSON puro (útil para debug)
        # print(json.dumps(ast_result, indent=2))

        # 2. NOVA VISUALIZAÇÃO AMIGÁVEL
        imprimir_relatorio_amigavel(ast_result)

    else:
        print("\n[FALHA] A análise sintática falhou.")
        print("Verifique os erros reportados acima.")


def run_analysis_semantica(codigo_para_analise, nome_do_teste):
    """Placeholder para a ANÁLISE SEMÂNTICA (Fase 3)"""
    print(f"\n--- Iniciando Análise SEMÂNTICA para: {nome_do_teste} ---")
    print("\n[PENDENTE] A Análise Semântica (Fase 3) ainda não foi implementada.")


# =============================================================================
# LOOP PRINCIPAL (MAIN)
# =============================================================================


def main():
    analysis_functions = {
        "1": ("Análise Léxica (Fase 1)", run_analysis_lexica),
        "2": ("Análise Sintática (Fase 2)", run_analysis_sintatica),
        "3": ("Análise Semântica (Fase 3)", run_analysis_semantica),
    }

    while True:
        print("\n" + "=" * 60)
        print("  ANALISADOR DE LINGUAGEM TONTO".center(60))
        print("=" * 60)
        print("Selecione o TIPO de análise que deseja executar:")
        for key, (name, _) in analysis_functions.items():
            print(f"  {key}. {name}")
        print("  Q. Sair")

        tipo_escolha = input("Digite sua escolha: ").strip().upper()

        if tipo_escolha == "Q":
            print("Saindo...")
            break

        if tipo_escolha not in analysis_functions:
            print("Opção inválida.")
            continue

        selected_analysis_name, funcao_analise = analysis_functions[tipo_escolha]

        while True:
            print("\n" + "-" * 60)
            print(f"Executando: {selected_analysis_name}")
            print("Selecione uma opção para analisar:")

            for key, example in TEST_EXAMPLES.items():
                print(f"  {key}. {example['name']}")
            print("  E. Analisar um arquivo externo (.tonto)")
            print("  V. Voltar ao menu anterior")

            exemplo_escolha = input("Digite sua escolha: ").strip().upper()

            if exemplo_escolha == "V":
                break

            codigo_para_analise = ""
            nome_do_teste = ""

            if exemplo_escolha in TEST_EXAMPLES:
                codigo_para_analise = TEST_EXAMPLES[exemplo_escolha]["code"]
                nome_do_teste = TEST_EXAMPLES[exemplo_escolha]["name"]

            elif exemplo_escolha == "E":
                file_path = input(
                    "Digite o caminho completo para o arquivo .tonto: "
                ).strip()
                if not os.path.exists(file_path):
                    print(f"\n[ERRO] Arquivo não encontrado: {file_path}")
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        codigo_para_analise = f.read()
                    nome_do_teste = f"Arquivo Externo: {os.path.basename(file_path)}"
                except Exception as e:
                    print(f"\n[ERRO] Não foi possível ler o arquivo: {e}")
                    continue
            else:
                print("Opção inválida.")
                continue

            # Executa a análise
            funcao_analise(codigo_para_analise, nome_do_teste)
            input("\nPressione ENTER para continuar...")
            break


if __name__ == "__main__":
    main()
