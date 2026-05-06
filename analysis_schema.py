from __future__ import annotations

EVENT_MARKERS = [
    {"id": "initial_contact", "label": "Contato inicial"},
    {"id": "loading_response", "label": "Resposta à carga"},
    {"id": "mid_stance", "label": "Médio apoio"},
    {"id": "terminal_stance", "label": "Apoio terminal"},
    {"id": "pre_swing", "label": "Pré-balanço"},
    {"id": "initial_swing", "label": "Balanço inicial"},
    {"id": "mid_swing", "label": "Balanço médio"},
    {"id": "terminal_swing", "label": "Balanço terminal"},
]

BILATERAL_TEMPORAL_MARKERS = [
    {"id": "ic_right_1", "label": "Contato inicial direito 1"},
    {"id": "to_left_1", "label": "Retirada do pé esquerdo 1"},
    {"id": "ic_left_1", "label": "Contato inicial esquerdo 1"},
    {"id": "to_right_1", "label": "Retirada do pé direito 1"},
    {"id": "ic_right_2", "label": "Contato inicial direito 2"},
    {"id": "to_left_2", "label": "Retirada do pé esquerdo 2"},
    {"id": "ic_left_2", "label": "Contato inicial esquerdo 2"},
]


GAIT_MODE_OPTIONS = [
    "independente,",
    "com auxílio de um par de muletas canadenses,",
    "com auxílio de muletas axilares,",
    "com auxílio de bengala à direita,",
    "com auxílio de bengala à esquerda,",
    "com auxílio de andador reciprocado,",
    "com auxílio de andador triangular,",
    "com auxílio de muleta axilar à direita,",
    "com auxílio de muleta axilar à esquerda,",
    "com auxílio de muleta canadense à direita,",
    "com auxílio de muleta canadense à esquerda,",
    "com apoio de terceiros,",
]

SUPPORT_OPTIONS = [
    "com estabilidade no apoio",
    "com instabilidade",
    "não se aplica",
]

STEP_WIDTH_OPTIONS = [
    "adequada",
    "aumentada",
    "diminuída",
    "não se aplica",
]

INITIAL_CONTACT_OPTIONS = [
    "o toque do calcanhar",
    "a planta do pé",
    "o antepé",
    "a borda lateral do pé",
    "a borda medial do pé",
    "não se aplica",
]

LOADING_RESPONSE_OPTIONS = [
    "há adequada queda do antepé",
    "há súbita queda do antepé",
    "não ocorre queda do antepé",
    "não se aplica",
]

ROLLING_OPTIONS = [
    "adequado",
    "inadequado",
    "ausente",
    "não se aplica",
]

RETROFOOT_OPTIONS = [
    "posição adequada",
    "valgo",
    "varo",
]

FOREFOOT_OPTIONS = [
    "posição neutra",
    "abdução",
    "adução",
    "pronação",
    "supinação",
]

LEG_ADVANCEMENT_OPTIONS = [
    "ocorre lentamente",
    "ocorre rapidamente",
    "não ocorre",
    "não se aplica",
]

MIDSTANCE_OPTIONS = [
    "o paciente realiza apoio plantígrado com antepé e retropé neutros",
    "o paciente realiza apoio em antepé com antepé e retropé neutros",
    "o paciente realiza apoio plantígrado com adução do antepé e retropé neutro",
    "o paciente realiza apoio plantígrado com abdução do antepé e retropé neutro",
    "o paciente realiza apoio plantígrado com pronação do antepé e retropé neutro",
    "o paciente realiza apoio plantígrado com supinação do antepé e retropé neutro",
    "o paciente realiza apoio plantígrado com antepé neutro e retropé varo",
    "o paciente realiza apoio plantígrado com antepé neutro e retropé valgo",
    "o paciente realiza apoio plantígrado com abdução do antepé e retropé valgo",
    "o paciente realiza apoio plantígrado com abdução do antepé e retropé varo",
    "o paciente realiza apoio plantígrado com adução do antepé e retropé valgo",
    "o paciente realiza apoio plantígrado com adução do antepé e retropé varo",
    "o paciente realiza apoio plantígrado com pronação do antepé e retropé valgo",
    "o paciente realiza apoio plantígrado com supinação do antepé e retropé varo",
    "não se aplica",
]

PLANTAR_FLEXION_OPTIONS = [
    "é adequada",
    "é aumentada",
    "é diminuída",
    "não se aplica",
]

HEEL_OFF_OPTIONS = [
    "adequadamente no apoio terminal",
    "tardiamente no pré-balanço",
    "precocemente no médio apoio",
    "precocemente no médio apoio associado à extensão do joelho",
    "precocemente no médio apoio associado à máxima extensão do joelho alcançada",
    "como mecanismo compensatório para liberação do pé oposto",
    "não se aplica",
]

FOOT_PROGRESSION_OPTIONS = [
    "posição neutra",
    "rotação interna",
    "rotação externa",
    "realiza apoio plantígrado",
    "mantém apoio plantígrado",
    "mantém apoio em antepé",
    "não se aplica",
]

SWING_PROGRESSION_OPTIONS = [
    "manutenção do ângulo de progressão",
    "inversão do ângulo de progressão",
    "acentuação do ângulo de progressão",
    "diminuição do ângulo de progressão",
    "não se aplica",
]

FOOT_CLEARANCE_OPTIONS = [
    "ocorre adequadamente com boa dorsiflexão do tornozelo na fase de balanço",
    "ocorre com dificuldade, embora mantenha flexão plantar do tornozelo no balanço médio",
    "ocorre com dificuldade, embora mantenha flexão plantar do tornozelo no balanço médio e terminal",
    "ocorre no balanço inicial, quando o antepé arrasta no solo",
    "ocorre no balanço inicial e médio, quando o antepé arrasta no solo",
    "ocorre no balanço inicial, médio e terminal, quando o antepé arrasta no solo",
    "ocorre durante todo o balanço",
    "não se aplica",
]

KNEE_FLEXION_OPTIONS = [
    "flexão adequada",
    "flexão acentuada",
    "flexão aumentada",
    "flexão diminuída",
    "não se aplica",
]

KNEE_EXTENSION_OPTIONS = [
    "extensão adequada no apoio simples",
    "extensão brusca",
    "extensão brusca no apoio simples",
    "extensão precoce na resposta à carga",
    "extensão tardia no apoio terminal",
    "flexão no apoio simples",
    "hiperextensão",
    "persistência da extensão",
    "manutenção da extensão",
    "manutenção da hiperextensão",
    "não se aplica",
]

KNEE_TERMINAL_OPTIONS = [
    "extensão apropriada",
    "extensão inapropriada",
    "não se aplica",
]

HIP_FLEXION_OPTIONS = [
    "flexão adequada",
    "flexão acentuada",
    "flexão diminuída",
    "não se aplica",
]

HIP_EXTENSION_OPTIONS = [
    "há extensão completa",
    "permanece em flexão",
    "há diminuição da flexão",
    "não se aplica",
]

HIP_SWING_OPTIONS = [
    "apropriada",
    "aumentada",
    "diminuída",
    "acentuada",
    "não se aplica",
]

HIP_ADDUCTION_OPTIONS = [
    "abdução adequada",
    "adução adequada",
    "adução diminuída",
    "acentuada",
    "não se aplica",
]

HIP_SWING_FRONTAL_OPTIONS = [
    "abdução",
    "abdução exacerbada",
    "adução",
    "adução diminuída",
    "não se aplica",
]

HIP_ROTATION_OPTIONS = [
    "posição neutra quanto às rotações durante todo o ciclo",
    "rotação interna durante todo o ciclo",
    "rotação externa no contato inicial e resposta de carga",
    "rotação externa durante o balanço",
    "não se aplica",
]

PELVIS_TILT_OPTIONS = [
    "A pelve apresenta anteversão adequada durante todo o ciclo.",
    "A pelve apresenta aumento da anteversão no apoio simples.",
    "A pelve apresenta aumento da anteversão no apoio simples à direita.",
    "A pelve apresenta aumento da anteversão no apoio simples à esquerda.",
    "A pelve apresenta aumento da anteversão no apoio simples bilateralmente.",
    "A pelve apresenta redução da anteversão no balanço terminal e contato inicial à direita.",
    "A pelve apresenta redução da anteversão no balanço terminal e contato inicial à esquerda.",
    "A pelve apresenta redução da anteversão no balanço terminal e contato inicial bilateralmente.",
    "A pelve apresenta manutenção deste padrão na fase de apoio bilateralmente.",
]

PELVIS_OBLIQUITY_OPTIONS = [
    "A inclinação da pelve é adequada.",
    "A inclinação da pelve é inadequada, a hemipelve direita permanece elevada em relação à hemipelve esquerda durante todo o ciclo.",
    "A inclinação da pelve é inadequada, a hemipelve esquerda permanece elevada em relação à hemipelve direita durante todo o ciclo.",
    "A inclinação da pelve é inadequada, com queda acentuada da hemipelve contralateral ao apoio.",
    "A inclinação da pelve é inadequada, com elevação da hemipelve ipsilateral ao balanço.",
    "Não se aplica.",
]

PELVIS_ROTATION_OPTIONS = [
    "A rotação pélvica é adequada.",
    "A hemipelve direita está retraída em relação à hemipelve esquerda durante todo o ciclo.",
    "A hemipelve esquerda está retraída em relação à hemipelve direita durante todo o ciclo.",
    "A rotação pélvica ocorre com amplitude de movimento acentuada.",
    "Não se aplica.",
]

TRUNK_POSITION_OPTIONS = [
    "O tronco permanece em posição normal durante todo o ciclo.",
    "O tronco permanece anteriorizado no pré-balanço.",
    "O tronco permanece posteriorizado no médio apoio.",
    "O tronco permanece posteriorizado no balanço terminal e contato inicial.",
]

TRUNK_LEAN_OPTIONS = [
    "Não ocorre inclinação lateral do tronco durante todo o ciclo.",
    "Há inclinação lateral do tronco para o lado apoiado.",
    "Há persistência da inclinação lateral do tronco para a direita durante todo o ciclo.",
    "Há persistência da inclinação lateral do tronco para a esquerda durante todo o ciclo.",
    "Ocorre inclinação lateral do tronco para a direita durante o apoio simples do membro inferior direito.",
    "Ocorre inclinação lateral do tronco para a direita durante o apoio simples do membro inferior esquerdo.",
    "Ocorre inclinação lateral do tronco para a esquerda durante o apoio simples do membro inferior direito.",
    "Ocorre inclinação lateral do tronco para a esquerda durante o apoio simples do membro inferior esquerdo.",
]

UPPER_LIMB_OPTIONS = [
    "Há reciprocação dos membros superiores.",
    "Não há reciprocação dos membros superiores.",
]
