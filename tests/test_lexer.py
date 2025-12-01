# Acessa o objeto 'lexer' dentro do arquivo 'lexer.py' no pacote 'lexer'
from ..lexer.lexer import lexer 
# Acessa o dicionário 'tokens' e 'reserved' do arquivo 'tokens.py' no pacote 'lexer'
from ..lexer.tokens import tokens 
# (Note os dois pontos '..' para subir um nível e entrar no pacote 'lexer')

# Função auxiliar para processar um bloco de código
def run_lexer_test(code_example, test_name):
    print("=" * 50)
    print(f"--- INÍCIO DO TESTE: {test_name} ---")
    print("=" * 50)
    
    # Reseta o lexer
    lexer.input(code_example)
    
    # Processa e imprime os tokens
    while True:
        tok = lexer.token()
        if not tok:
            break
        # Usamos apenas tok.lineno pois find_column foi removida do lexer.py
        print(f"Tipo: {tok.type:<25} | Lexema: '{str(tok.value):<20}' | Linha: {tok.lineno}")
        
    print("-" * 50)
    print(f"--- FIM DO TESTE: {test_name} ---")
    print("\n\n")


# =============================================================================
# EXEMPLOS DE TESTE
# =============================================================================

# Exemplo 1: CarOwnership
def test_example_1_car_ownership():
    code = """
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
"""
    run_lexer_test(code, "CarOwnershipExample")


# Exemplo 2: CarRental
def test_example_2_car_rental():
    code = """
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
"""
    run_lexer_test(code, "CarRentalExample")


# Exemplo 3: alergiaalimentar
def test_example_3_food_allergy():
    code = """
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
"""
    run_lexer_test(code, "FoodAllergyExample")


# Exemplo 4: TDAH
def test_example_4_tdah():
    code = """
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
"""
    run_lexer_test(code, "TDAHExample")


# =============================================================================
# EXECUÇÃO DOS TESTES
# =============================================================================

if __name__ == '__main__':
    test_example_1_car_ownership()
    test_example_2_car_rental()
    test_example_3_food_allergy()
    test_example_4_tdah()