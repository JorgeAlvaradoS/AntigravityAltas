"""
Seguros Atlas - Seguros de Gastos Médicos Mayores
Domain Knowledge Base, Plans Catalog, Claims Guide, Hospital Network,
Certified Agents Directory, and Actuarial Pricing Rules.
"""

from typing import Dict, List, Any

PLANS_CATALOG: Dict[str, Dict[str, Any]] = {
    "med-optimo": {
        "id": "med-optimo",
        "name": "Med Óptimo",
        "category": "Personal y Familiar",
        "badge": "Excelente Relación Valor-Precio",
        "color": "#508CBE",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/icono-med-optimo.png",
        "tagline": "Protección médica esencial con acceso a una red hospitalaria eficiente de costo mediano en todo México.",
        "description": (
            "Med Óptimo está diseñado para individuos y familias que buscan la tranquilidad de un Seguro de Gastos "
            "Médicos Mayores con primas altamente competitivas, respaldado por una red seleccionada de hospitales de "
            "costo eficiente y calidad certificada en toda la República Mexicana."
        ),
        "suma_asegurada_default": "$50,000,000 MXN",
        "suma_asegurada_options": ["$15,000,000 MXN", "$30,000,000 MXN", "$50,000,000 MXN"],
        "hospital_level": "Nivel Óptimo (Costo Mediano Eficiente)",
        "maternity_aid": "$18,000 MXN",
        "foreign_emergency": "Hasta $50,000 USD (viajes < 90 días)",
        "base_annual_premium": 14800,
        "highlights": [
            "Suma asegurada hasta $50,000,000 MXN por padecimiento",
            "Red de hospitales eficientes de costo mediano sin penalización en red",
            "Ayuda por maternidad de $18,000 MXN sin deducible ni coaseguro",
            "Med Asistencia 24/7: médico a domicilio y 2 ambulancias terrestres sin costo",
            "Cobertura del recién nacido desde el día 1 (con 10 meses de vigencia materna)",
            "Emergencia en el extranjero hasta por $50,000 USD",
        ],
        "coverages": {
            "Habitaciones Hospitalarias": "Habitación estándar privada con alimentos para el paciente",
            "Honorarios Médicos": "Tabulador Óptimo con pago directo a médicos en convenio (sin coaseguro adicional en red)",
            "Medicamentos": "Dentro y fuera del hospital con receta médica derivada del padecimiento cubierto",
            "Terapias y Rehabilitación": "Fisioterapia, inhaloterapia, quimioterapia y radioterapia cubiertas",
            "Ambulancia Terrestre": "2 primeros traslados anuales sin costo vía Med Asistencia ($600 MXN a partir del 3ro)",
            "Ayuda por Maternidad": "$18,000 MXN (parto normal o cesárea; periodo de espera de 10 meses)",
            "Padecimientos Congénitos": "Cubiertos para nacidos dentro de la vigencia de la póliza",
            "Asistencia en Viajes": "Emergencia médica en el extranjero y repatriación sanitaria",
        },
        "hospitals_sample": [
            "Hospital San Ángel Inn (Universidad, Chapultepec, Patriotismo, Sur)",
            "Hospital Star Médica (Roma, Lomas Verdes, Querétaro, Mérida, Chihuahua)",
            "Hospital Dalinde / Torre Médica Dalinde (CDMX)",
            "Christus Muguerza (Conchita, Saltillo, Puebla, Mérida, Reynosa)",
            "Hospital San José (Querétaro, Hermosillo, Celaya)",
            "Hospital Beneficencia Española (Puebla, Tampico, Veracruz)",
        ],
        "ideal_for": "Familias jóvenes, profesionistas independientes y personas que buscan optimizar el costo de su prima con respaldo hospitalario sólido.",
    },
    "med-plus": {
        "id": "med-plus",
        "name": "Med Plus",
        "category": "Personal y Familiar",
        "badge": "Más Popular en México",
        "color": "#FAA632",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_medplus.png",
        "tagline": "Amplia cobertura nacional en hospitales de alto prestigio y tecnología médica de vanguardia.",
        "description": (
            "Med Plus amplía tu acceso a los principales hospitales privados de alto nivel en México, integrando "
            "coberturas de alta especialidad como cirugía asistida por Robot Da Vinci, trasplante de órganos, "
            "asistencia dental y funeraria internacional, y reducción de coaseguro en red convenio."
        ),
        "suma_asegurada_default": "$100,000,000 MXN",
        "suma_asegurada_options": ["$50,000,000 MXN", "$80,000,000 MXN", "$100,000,000 MXN"],
        "hospital_level": "Nivel Amplio / Alto Prestigio Nacional",
        "maternity_aid": "$30,000 MXN",
        "foreign_emergency": "Hasta $100,000 USD (viajes < 90 días)",
        "base_annual_premium": 22600,
        "highlights": [
            "Suma asegurada hasta $100,000,000 MXN por padecimiento",
            "Amplia red de hospitales de alto nivel (Médica Sur, Ángeles, Puerta de Hierro, Español)",
            "Cirugía de mínima invasión y cirugía asistida por Robot Da Vinci cubierta",
            "Ayuda por maternidad de $30,000 MXN + cobertura de complicaciones del embarazo",
            "Asistencia Dental y Asistencia Funeraria Internacional incluidas sin costo adicional",
            "Reducción de coaseguro y deducible al atenderse en hospitales y médicos de convenio",
        ],
        "coverages": {
            "Habitaciones Hospitalarias": "Habitación privada de lujo + cama extra para acompañante",
            "Honorarios Médicos": "Tabulador Plus Amplio con red nacional de especialistas certificados",
            "Cirugía Robótica": "Cobertura integral para procedimientos con Robot Da Vinci en hospitales certificados",
            "Trasplante de Órganos": "Gastos médicos del receptor y del donante (vivo o cadavérico)",
            "Ayuda por Maternidad": "$30,000 MXN libre de deducible y coaseguro + cobertura al recién nacido",
            "Prótesis y Órtesis": "Prótesis ortopédicas, cardiovasculares y reconstructivas de alta tecnología",
            "Asistencias Incluidas": "Med Asistencia 24/7 + Asistencia Dental + Asistencia Funeraria Internacional",
            "Enfermera en Casa": "Hasta 30 días por prescripción del médico tratante",
        },
        "hospitals_sample": [
            "Hospital Médica Sur (Tlalpan, CDMX)",
            "Hospital Ángeles (Metropolitano, Mocel, Lindavista, Puebla, León, Querétaro, Tijuana)",
            "Hospital Español (Polanco, CDMX)",
            "Hospital Puerta de Hierro (Sur, Tepic, Colima)",
            "Christus Muguerza Alta Especialidad (Monterrey)",
            "Hospital CIMA (Hermosillo)",
        ],
        "ideal_for": "Familias y ejecutivos que desean acceso a hospitales privados de alto nivel y tecnología médica avanzada como cirugía robótica.",
    },
    "med-plus-elite": {
        "id": "med-plus-elite",
        "name": "Med Plus Elite",
        "category": "Personal y Familiar",
        "badge": "Acceso Hospitalario AAA sin Restricción",
        "color": "#6F6259",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_medpluselite.png",
        "tagline": "Acceso total a los hospitales más exclusivos y prestigiados de México con beneficios preferenciales Elite.",
        "description": (
            "Med Plus Elite ofrece libertad absoluta para atenderte en el 100% de los hospitales privados de México, "
            "incluyendo los centros médicos AAA más exclusivos del país (Centro Médico ABC, Ángeles Lomas/Pedregal, "
            "Zambrano Hellion, San Javier), con tabuladores médicos superiores y beneficios ejecutivos."
        ),
        "suma_asegurada_default": "$130,000,000 MXN",
        "suma_asegurada_options": ["$100,000,000 MXN", "$130,000,000 MXN", "Sin Límite Nacional"],
        "hospital_level": "Nivel Elite AAA (100% de Hospitales en México sin Penalización)",
        "maternity_aid": "$45,000 MXN",
        "foreign_emergency": "Hasta $150,000 USD + Segunda Opinión Internacional",
        "base_annual_premium": 34900,
        "highlights": [
            "Suma asegurada hasta $130,000,000 MXN (o equivalente en USD)",
            "Acceso libre a hospitales AAA: ABC Santa Fe/Observatorio, Ángeles Lomas/Pedregal, Zambrano Hellion",
            "Habitación tipo Suite / Junior Suite y cama extra para acompañante",
            "Ayuda por maternidad de $45,000 MXN + tamiz metabólico ampliado y cuidados neonatales",
            "Cero deducible en caso de accidente cubierto desde el primer peso",
            "Reconocimiento de antigüedad de otras compañías aseguradoras",
        ],
        "coverages": {
            "Habitaciones Hospitalarias": "Habitación Junior Suite / Suite con alimentos y cama para acompañante",
            "Honorarios Médicos": "Tabulador Elite Superior para médicos dentro y fuera de red",
            "Cero Deducible por Accidente": "Exención total del deducible en urgencias y hospitalizaciones por accidente",
            "Oncología e Inmunoterapia": "Terapias blanco, inmunoterapia, radiocirugía estereotáctica y cirugía robótica",
            "Ayuda por Maternidad": "$45,000 MXN + cobertura integral de complicaciones pre y postnatales",
            "Enfermera Privada": "Hasta 60 días de enfermería especializada a domicilio",
            "Segunda Opinión Médica": "Coordinación con centros médicos de excelencia en México y EE.UU.",
            "Tope de Coaseguro Preferencial": "Tope máximo de coaseguro reducido para proteger tu patrimonio",
        },
        "hospitals_sample": [
            "Centro Médico ABC (Campus Santa Fe y Campus Observatorio, CDMX)",
            "Hospital Ángeles Lomas y Hospital Ángeles Pedregal (CDMX)",
            "Hospital Zambrano Hellion TecSalud y Hospital San José TecSalud (Monterrey)",
            "Hospital Puerta de Hierro Andares y Hospital San Javier (Guadalajara)",
            "Hospital Médica Sur (CDMX)",
            "Hospital Ángeles Valle Oriente (Monterrey)",
        ],
        "ideal_for": "Directivos, empresarios y familias que exigen atención médica en los hospitales AAA más exclusivos de México sin restricciones de red.",
    },
    "plan-mundial": {
        "id": "plan-mundial",
        "name": "Plan Mundial",
        "category": "Personal y Familiar Internacional",
        "badge": "Cobertura Global EE.UU. y Resto del Mundo",
        "color": "#D9272E",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_planmundial.png",
        "tagline": "Libertad absoluta para elegir los mejores hospitales y especialistas en México, Estados Unidos y cualquier parte del mundo.",
        "description": (
            "Plan Mundial es la máxima expresión de protección médica de Seguros Atlas. Permite programar cirugías, "
            "tratamientos de alta especialidad y atender emergencias tanto en los mejores hospitales de México como "
            "en clínicas líderes a nivel internacional (EE.UU., Europa y el resto del mundo) mediante la red Global Medical."
        ),
        "suma_asegurada_default": "$5,000,000 USD",
        "suma_asegurada_options": ["$3,000,000 USD", "$5,000,000 USD", "Cobertura Global Ilimitada"],
        "hospital_level": "Red Internacional Global Medical + Red Elite AAA México",
        "maternity_aid": "$50,000 MXN / $2,500 USD",
        "foreign_emergency": "Atención Programada y de Emergencia Mundial con Pago Directo",
        "base_annual_premium": 52400,
        "highlights": [
            "Suma asegurada hasta $5,000,000 USD (atención programada y de emergencia en todo el mundo)",
            "Acceso directo a Mayo Clinic, Cleveland Clinic, MD Anderson, Johns Hopkins y Mount Sinai",
            "Coordinación internacional 24/7 vía Global Medical (954 308-39-32 / 855 209-80-25)",
            "Ambulancia aérea internacional y nacional sin límite de eventos por urgencia médica",
            "Acceso a medicamentos huérfanos, terapias génicas e inmunoterapia aprobada por FDA/EMA",
            "Pago directo internacional en hospitalizaciones mayores a 24 horas",
        ],
        "coverages": {
            "Cobertura Geográfica": "100% Mundial (México, Estados Unidos, Canadá, Europa, Asia y Latinoamérica)",
            "Pago Directo Internacional": "Gestión directa con hospitales en el extranjero vía Global Medical en estancias > 24h",
            "Ambulancia Aérea y Terrestre": "Traslado aéreo médico internacional entre hospitales de alta especialidad",
            "Oncología y Genómica Avanzada": "Estudios genómicos tumorales, protonterapia, CAR-T e inmunoterapia internacional",
            "Maternidad Internacional": "Ayuda de maternidad y cobertura de complicaciones en México y el extranjero",
            "Concierge Médico VIP": "Coordinación de citas internacionales, traducción médica y admisión hospitalaria prioritaria",
            "Trasplante Internacional": "Acceso a redes internacionales de trasplante de órganos y médula ósea",
            "Todo lo incluido en Med Plus Elite": "Acceso irrestricto al 100% de hospitales AAA en México sin penalización",
        },
        "hospitals_sample": [
            "Mayo Clinic (Rochester, Jacksonville, Scottsdale - EE.UU.)",
            "MD Anderson Cancer Center y Texas Medical Center (Houston, TX - EE.UU.)",
            "Cleveland Clinic (Ohio y Florida - EE.UU.) & Johns Hopkins Hospital (Baltimore - EE.UU.)",
            "Mount Sinai & NewYork-Presbyterian (Nueva York - EE.UU.)",
            "Clínica Universidad de Navarra (España) & Charité (Alemania)",
            "100% de la Red Elite AAA en México (ABC, Ángeles Lomas/Pedregal, Zambrano Hellion)",
        ],
        "ideal_for": "Familias globales, viajeros frecuentes, expatriados y altos directivos que desean acceso programado a la medicina de primer mundo en EE.UU. y Europa.",
    },
    "med-optimo-empresas": {
        "id": "med-optimo-empresas",
        "name": "Med Óptimo para Empresas",
        "category": "Empresas y Colectivos",
        "badge": "Prestación Laboral Competitiva",
        "color": "#508CBE",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_optimoempresas.png",
        "tagline": "Protección médica colectiva de alto valor y control presupuestal para PyMEs y corporativos.",
        "description": (
            "Solución colectiva para empresas a partir de 10 titulares que desean brindar una prestación de Gastos "
            "Médicos Mayores altamente valorada por sus colaboradores, con primas deducibles de impuestos y acceso "
            "a la red hospitalaria Óptima de Seguros Atlas."
        ),
        "suma_asegurada_default": "$30,000,000 MXN",
        "suma_asegurada_options": ["$10,000,000 MXN", "$30,000,000 MXN", "$50,000,000 MXN"],
        "hospital_level": "Nivel Óptimo Colectivo",
        "maternity_aid": "$18,000 MXN",
        "foreign_emergency": "Hasta $50,000 USD",
        "base_annual_premium": 11900,
        "highlights": [
            "Contratación colectiva desde 10 colaboradores titulares",
            "Primas 100% deducibles de impuestos como prestación de previsión social",
            "Portal empresarial para gestión ágil de altas, bajas y certificados",
            "Subgrupos personalizables por nivel organizacional (Operativo, Gerencial, Directivo)",
            "Atención prioritaria CITAMED 24/7 y campañas preventivas de salud ocupacional",
        ],
        "coverages": {
            "Administración de Colectividad": "Altas y bajas digitales con cobro prorrateado transparente",
            "Continuidad Garantizada": "Opción de conversión a póliza individual al separarse el colaborador de la empresa",
            "Maternidad Colectiva": "Cobertura de maternidad para titulares y cónyuges según reglas del grupo",
            "Asistencias": "Med Asistencia 24/7, orientación médica y ambulancias terrestres incluidas",
        },
        "hospitals_sample": [
            "Red Nacional Óptima (San Ángel Inn, Star Médica, Dalinde, Christus Muguerza, San José)"
        ],
        "ideal_for": "PyMEs, startups en crecimiento y empresas medianas que buscan atraer y retener talento con beneficios médicos sustentables.",
    },
    "med-plus-empresas": {
        "id": "med-plus-empresas",
        "name": "Med Plus para Empresas",
        "category": "Empresas y Colectivos",
        "badge": "Cobertura Ejecutiva Corporativa",
        "color": "#FAA632",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_medplusempresas.png",
        "tagline": "Póliza colectiva de nivel ejecutivo con acceso a hospitales de alto prestigio y tarifas corporativas.",
        "description": (
            "Diseñado para corporativos y grupos ejecutivos que requieren acceso a redes hospitalarias Amplia y Elite, "
            "esquemas de deducible en exceso (conexión con pólizas individuales), experiencia siniestral propia y "
            "coberturas integrales de maternidad, dental y visión."
        ),
        "suma_asegurada_default": "$100,000,000 MXN",
        "suma_asegurada_options": ["$50,000,000 MXN", "$100,000,000 MXN", "Sin Límite Corporativo"],
        "hospital_level": "Nivel Amplio y Elite Ejecutivo",
        "maternity_aid": "$35,000 MXN",
        "foreign_emergency": "Hasta $100,000 USD",
        "base_annual_premium": 18500,
        "highlights": [
            "Esquemas a la medida para grupos ejecutivos y grandes colectividades",
            "Acceso a hospitales de alto nivel y opción de subgrupo Elite AAA para directivos",
            "Reportes ejecutivos de siniestralidad y ejecutivo de cuenta dedicado en Seguros Atlas",
            "Cobertura de check-ups ejecutivos anuales y programas de bienestar corporativo",
            "Reconocimiento de antigüedad colectiva y eliminación de periodos de espera en grupos > 50 titulares",
        ],
        "coverages": {
            "Red Hospitalaria": "Acceso a Red Plus y configuración multi-nivel por categoría de puesto",
            "Siniestralidad Corporativa": "Dividendos o ajustes por buena experiencia siniestral según tamaño del grupo",
            "Enlace Póliza Individual": "Cláusula de conversión garantizada y conexión de deducible en exceso",
            "Asistencias Corporativas": "Med Asistencia, Dental, Visión y Asistencia Funeraria Internacional",
        },
        "hospitals_sample": [
            "Red Nacional Plus y Elite (Médica Sur, Ángeles, ABC, Zambrano Hellion, Puerta de Hierro, Español)"
        ],
        "ideal_for": "Corporativos, empresas multinacionales y consejos directivos que requieren prestaciones médicas de primer nivel.",
    },
    "basicos-estandarizados": {
        "id": "basicos-estandarizados",
        "name": "Básicos Estandarizados",
        "category": "Productos Estandarizados",
        "badge": "Regulado CONDUSEF / CNSF",
        "color": "#6F6259",
        "icon": "https://www.segurosatlas.com.mx/content/dam/segurosatlas/corporativo-2025/iconos/Medico_iconos_estandarizados.png",
        "tagline": "Coberturas básicas estandarizadas de Gastos Médicos Mayores, Accidentes Personales y Salud Dental.",
        "description": (
            "Productos con condiciones contractuales homogéneas autorizadas por la CNSF y CONDUSEF para facilitar "
            "la comparación y ofrecer un piso de protección accesible ante emergencias médicas, accidentes o cuidado dental."
        ),
        "suma_asegurada_default": "Hasta 1,000 UMAs Anuales",
        "suma_asegurada_options": ["Básico GMM", "Básico Accidentes Personales", "Básico Salud Dental"],
        "hospital_level": "Red Básica en Convenio",
        "maternity_aid": "Complicaciones del Embarazo Cubiertas",
        "foreign_emergency": "Territorio Nacional",
        "base_annual_premium": 6800,
        "highlights": [
            "Condiciones claras y estandarizadas reguladas por la CNSF y CONDUSEF",
            "Tres modalidades disponibles: Gastos Médicos Mayores, Accidentes Personales y Salud Dental",
            "Contratación simplificada y prima anual altamente accesible",
            "Respaldo financiero y red de atención de Seguros Atlas en todo el país",
        ],
        "coverages": {
            "Básico Gastos Médicos": "Hospitalización, honorarios quirúrgicos, medicamentos intrahospitalarios y urgencias",
            "Básico Accidentes Personales": "Muerte accidental y reembolso de gastos médicos por accidente",
            "Básico Salud Dental": "Consultas diagnósticas, limpiezas, radiografías, resinas y extracciones simples",
        },
        "hospitals_sample": [
            "Red Hospitalaria y Clínicas Dentales en Convenio Nacional Seguros Atlas"
        ],
        "ideal_for": "Personas que buscan su primer seguro médico o cobertura básica estandarizada al menor costo del mercado.",
    },
}


SINIESTRO_GUIDE: Dict[str, Any] = {
    "source_url": "https://www.segurosatlas.com.mx/en-caso-de-siniestro.html",
    "emergency_hotlines": [
        {
            "name": "CITAMED 24/7 (Gastos Médicos y Accidentes)",
            "subtitle": "Centro de Información Telefónica Atlas Med — Atención inmediata los 365 días",
            "phones": [
                {"label": "CDMX y Área Metropolitana", "number": "55 9177 5144", "tel": "5591775144"},
                {"label": "Interior de la República (Sin Costo)", "number": "800 849 3918", "tel": "8008493918"},
            ],
            "badge": "Urgencias Hospitalarias y Carta Pase",
        },
        {
            "name": "Med Asistencia 24/7",
            "subtitle": "Orientación médica telefónica, médico a domicilio y ambulancia terrestre",
            "phones": [
                {"label": "Desde México", "number": "55 5254 7086", "tel": "5552547086"},
                {"label": "Desde el Interior / Otro País", "number": "800 849 3917", "tel": "8008493917"},
            ],
            "badge": "2 Ambulancias Gratuitas / Año",
        },
        {
            "name": "Global Medical (Emergencia en el Extranjero)",
            "subtitle": "Coordinación internacional y pago directo fuera de México (estancias > 24h)",
            "phones": [
                {"label": "Internacional Directo", "number": "+1 (954) 308-3932", "tel": "+19543083932"},
                {"label": "Toll-Free EE.UU. y Canadá", "number": "+1 (855) 209-8025", "tel": "+18552098025"},
            ],
            "badge": "Atención Mundial 24/7",
        },
        {
            "name": "Línea Atlas General (Autos, Vida, Daños)",
            "subtitle": "Cabina nacional de siniestros y atención a clientes Seguros Atlas",
            "phones": [
                {"label": "CDMX Siniestros", "number": "55 9177 5050", "tel": "5591775050"},
                {"label": "Atención Clientes CDMX", "number": "55 9177 5220", "tel": "5591775220"},
            ],
            "badge": "Multiramo",
        },
    ],
    "pago_directo": {
        "title": "1. Pago Directo (Atención en Red Hospitalaria sin Desembolso Total)",
        "summary": (
            "Seguros Atlas liquida directamente al hospital y a los médicos en convenio los gastos procedentes, "
            "por lo que el asegurado únicamente cubre en el hospital su Deducible, Coaseguro (con reducción "
            "preferencial en red) y gastos personales no relacionados."
        ),
        "conditions": [
            "Aplica en hospitalizaciones de urgencia o enfermedad con estancia mínima de 24 horas.",
            "También aplica en cirugías o procedimientos de corta estancia cuando se programan con al menos 5 días hábiles de anticipación.",
            "Al acudir a Hospitales en Convenio obtienes reducción en deducible y/o coaseguro según tu plan.",
            "Al elegir Médicos en Convenio no pagas diferencias de honorarios por arriba del tabulador.",
            "Importante: La póliza debe encontrarse pagada y vigente (Pago Directo no opera durante el Periodo de Gracia).",
        ],
        "steps_emergency": [
            "Acude al hospital de la red correspondiente a tu plan (Med Óptimo, Med Plus, Med Plus Elite o Plan Mundial).",
            "Presenta tu credencial física o digital de Seguros Atlas y una identificación oficial vigente con fotografía.",
            "Reporta de inmediato tu ingreso a CITAMED al 55 9177 5144 o 800 849 3918 (o solicita al módulo hospitalario que lo notifique).",
            "Un coordinador médico de Seguros Atlas dará seguimiento a tu caso y emitirá la Carta Pase de autorización antes de tu alta.",
        ],
        "steps_programmed": [
            "Reúne con tu médico tratante el Informe Médico y el formato de Aviso de Accidente o Enfermedad debidamente requisitados.",
            "Anexa los resultados de estudios clínicos, laboratorio, imagenología o patología con interpretación que sustenten el diagnóstico.",
            "Incluye los datos del hospital, fecha programada, equipo quirúrgico (cirujano, anestesiólogo, ayudantes) y presupuesto de honorarios.",
            "Ingresa la solicitud al menos 5 días hábiles antes de la cirugía a través de tu Agente Seguros Atlas o módulo de Programación Médica.",
            "Recibe tu Carta Pase autorizada para ingresar al hospital con tranquilidad financiera.",
        ],
    },
    "reembolso": {
        "title": "2. Reembolso de Gastos Médicos",
        "summary": (
            "Opera cuando el asegurado decide atenderse en hospitales o con médicos fuera de la red de convenio, "
            "en consultas ambulatorias, compra de medicamentos de farmacia, análisis de laboratorio o terapias de rehabilitación."
        ),
        "checklist": [
            "Formato 'Aviso de Accidente o Enfermedad' llenado y firmado por el asegurado titular (en la primera reclamación del padecimiento).",
            "Formato 'Informe Médico' llenado y firmado por cada médico tratante con número de cédula profesional y especialidad.",
            "Facturas electrónicas (CFDI XML y PDF) originales a nombre del Asegurado Titular, con desglose fiscal de cada concepto.",
            "Recetas médicas detallando nombre del paciente, medicamentos, dosis y duración del tratamiento (acompañadas de sus facturas).",
            "Resultados e interpretación escrita de todos los estudios de laboratorio, rayos X, resonancias, tomografías o biopsias reclamadas.",
            "En caso de haber existido hospitalización: copia completa del expediente clínico e historial de cargos desglosado del hospital.",
            "Carátula de estado de cuenta bancario vigente (no mayor a 3 meses) con CLABE interbancaria de 18 dígitos a nombre del titular.",
            "Identificación oficial vigente (INE o Pasaporte) y comprobante de domicilio en reclamaciones superiores al umbral regulatorio.",
        ],
    },
    "med_asistencia_benefits": [
        {
            "service": "Orientación Médica Telefónica 24/7",
            "detail": "Médicos titulados disponibles las 24 horas para resolver dudas de síntomas, medicamentos y primeros auxilios sin costo.",
        },
        {
            "service": "Médico General a Domicilio",
            "detail": "Envío de médico a tu hogar u oficina con tarifa preferencial topada para valoración clínica sin salir de casa.",
        },
        {
            "service": "Ambulancia Terrestre de Urgencia",
            "detail": "Los primeros 2 traslados anuales en ambulancia terrestre son 100% gratuitos; a partir del 3er traslado aplica costo preferencial de $600 MXN.",
        },
        {
            "service": "Red de Descuentos Médicos",
            "detail": "Precios preferenciales en laboratorios clínicos, gabinetes de imagenología, ópticas, farmacias y enfermería.",
        },
    ],
    "offices": [
        {
            "name": "Oficina Corporativa Bosques de las Lomas",
            "address": "Paseo de los Tamarindos No. 60-PB, Col. Bosques de las Lomas, C.P. 05120, Alcaldía Cuajimalpa de Morelos, Ciudad de México.",
            "phone": "55 9177 5000",
        },
        {
            "name": "Oficina Roma Norte",
            "address": "Córdoba No. 42, Piso 9, Col. Roma Norte, C.P. 06700, Alcaldía Cuauhtémoc, Ciudad de México.",
            "phone": "55 9177 5220",
        },
    ],
}


ATLAS_AGENTS: List[Dict[str, Any]] = [
    {
        "id": "agt-001",
        "name": "Lic. Mariana Valdés Alcántara",
        "title": "Directora de Asesoría Patrimonial y Gastos Médicos Elite",
        "cedula": "CNSF-A294810-MX",
        "specialty": "Med Plus Elite & Plan Mundial Internacional",
        "plans_focus": ["med-plus-elite", "plan-mundial"],
        "branch": "Bosques de las Lomas, CDMX",
        "region": "CDMX / Nacional",
        "experience_years": 14,
        "rating": 4.98,
        "phone": "55 9177 5220 Ext. 4102",
        "whatsapp": "525591775220",
        "email": "mvaldes.agente@segurosatlas-asesores.com.mx",
        "avatar_initials": "MV",
        "bio": "Especialista certificada en programas médicos internacionales, segundas opiniones en EE.UU. y protección familiar de alto patrimonio.",
    },
    {
        "id": "agt-002",
        "name": "Act. Alejandro Monroy Betancourt",
        "title": "Agente Profesional Certificado Senior — Gastos Médicos",
        "cedula": "CNSF-B184729-MX",
        "specialty": "Med Plus & Protección Familiar Integral",
        "plans_focus": ["med-plus", "med-optimo"],
        "branch": "Roma Norte, CDMX",
        "region": "CDMX / Zona Centro",
        "experience_years": 11,
        "rating": 4.95,
        "phone": "55 9177 5220 Ext. 3208",
        "whatsapp": "525591775220",
        "email": "amonroy.agente@segurosatlas-asesores.com.mx",
        "avatar_initials": "AM",
        "bio": "Actuario por la UNAM especializado en optimización de deducibles, coaseguros y planeación de maternidad familiar.",
    },
    {
        "id": "agt-003",
        "name": "Lic. Sofía Garza Sada de la Fuente",
        "title": "Consejera Senior en Salud y Hospitales AAA",
        "cedula": "CNSF-C391044-NL",
        "specialty": "Med Plus Elite, TecSalud & Red Noreste",
        "plans_focus": ["med-plus-elite", "med-plus", "plan-mundial"],
        "branch": "San Pedro Garza García, Monterrey, N.L.",
        "region": "Norte / Monterrey",
        "experience_years": 12,
        "rating": 4.97,
        "phone": "81 8368 4900 Ext. 2105",
        "whatsapp": "528183684900",
        "email": "sgarza.agente@segurosatlas-asesores.com.mx",
        "avatar_initials": "SG",
        "bio": "Experta en atención hospitalaria en Zambrano Hellion, San José TecSalud y clínicas de alta especialidad en Texas.",
    },
    {
        "id": "agt-004",
        "name": "Ing. Roberto Villaseñor Orozco",
        "title": "Asesor Certificado en Protección Familiar y PyME",
        "cedula": "CNSF-B209412-JAL",
        "specialty": "Med Óptimo, Med Plus & Reconocimiento de Antigüedad",
        "plans_focus": ["med-optimo", "med-plus", "basicos-estandarizados"],
        "branch": "Puerta de Hierro, Guadalajara, Jal.",
        "region": "Occidente / Bajío",
        "experience_years": 9,
        "rating": 4.94,
        "phone": "33 3648 7100 Ext. 1409",
        "whatsapp": "523336487100",
        "email": "rvillasenor.agente@segurosatlas-asesores.com.mx",
        "avatar_initials": "RV",
        "bio": "Especialista en diseño de pólizas familiares accesibles y acompañamiento personalizado en programación de cirugías y reembolsos.",
    },
    {
        "id": "agt-005",
        "name": "Mtra. Claudia Domenech Ibarra",
        "title": "Directora de Beneficios para Empleados y Colectividades",
        "cedula": "CNSF-D902318-MX",
        "specialty": "Med Óptimo Empresas & Med Plus Empresas",
        "plans_focus": ["med-optimo-empresas", "med-plus-empresas"],
        "branch": "Bosques de las Lomas, CDMX",
        "region": "Nacional Corporativo",
        "experience_years": 16,
        "rating": 4.99,
        "phone": "55 9177 5000 Ext. 5011",
        "whatsapp": "525591775000",
        "email": "cdomenech.corporativo@segurosatlas-asesores.com.mx",
        "avatar_initials": "CD",
        "bio": "Especialista en estructuración de pólizas colectivas empresariales, control de siniestralidad y previsión social deducible.",
    },
]


KNOWLEDGE_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "id": "doc-med-optimo",
        "title": "Plan Med Óptimo — Seguro de Gastos Médicos Mayores Seguros Atlas",
        "category": "Planes Personales",
        "url": "#plan-med-optimo",
        "tags": ["med optimo", "optimo", "planes", "maternidad", "costo mediano", "hospitales", "suma asegurada"],
        "content": (
            "Med Óptimo de Seguros Atlas ofrece protección médica integral con acceso a una red de hospitales de "
            "costo mediano y alta eficiencia en todo México (San Ángel Inn, Star Médica, Dalinde, Christus Muguerza, "
            "Hospital San José). Suma asegurada hasta $50,000,000 MXN, ayuda por maternidad de $18,000 MXN libre de "
            "deducible y coaseguro (10 meses de espera), emergencia en el extranjero hasta $50,000 USD y Med Asistencia "
            "24/7 con 2 traslados en ambulancia terrestre gratuitos al año."
        ),
    },
    {
        "id": "doc-med-plus",
        "title": "Plan Med Plus — Amplia Red Hospitalaria y Cirugía Robótica Da Vinci",
        "category": "Planes Personales",
        "url": "#plan-med-plus",
        "tags": ["med plus", "plus", "robot da vinci", "maternidad", "dental", "funeraria", "medica sur", "angeles"],
        "content": (
            "Med Plus brinda acceso a una amplia red de hospitales de alto prestigio en México como Hospital Médica Sur, "
            "Hospital Español, Hospitales Ángeles (Metropolitano, Mocel, Lindavista, Puebla, Querétaro, León) y Puerta "
            "de Hierro. Cuenta con suma asegurada hasta $100,000,000 MXN, ayuda por maternidad de $30,000 MXN, cirugía "
            "asistida por Robot Da Vinci, trasplante de órganos, padecimientos congénitos y asistencias Dental y "
            "Funeraria Internacional incluidas."
        ),
    },
    {
        "id": "doc-med-plus-elite",
        "title": "Plan Med Plus Elite — Acceso al 100% de Hospitales AAA en México",
        "category": "Planes Personales",
        "url": "#plan-med-plus-elite",
        "tags": ["med plus elite", "elite", "abc", "angeles lomas", "angeles pedregal", "zambrano hellion", "suite"],
        "content": (
            "Med Plus Elite permite atenderte sin restricciones ni penalizaciones en el 100% de los hospitales privados "
            "de México, incluyendo los centros AAA más exclusivos: Centro Médico ABC (Santa Fe y Observatorio), "
            "Hospital Ángeles Lomas y Pedregal, Hospital Zambrano Hellion TecSalud en Monterrey y Hospital San Javier "
            "en Guadalajara. Ofrece suma asegurada hasta $130,000,000 MXN, habitación Suite/Junior Suite, ayuda de "
            "maternidad de $45,000 MXN, cero deducible por accidente y hasta 60 días de enfermera privada."
        ),
    },
    {
        "id": "doc-plan-mundial",
        "title": "Plan Mundial — Cobertura Médica Internacional en EE.UU. y el Mundo",
        "category": "Planes Internacionales",
        "url": "#plan-plan-mundial",
        "tags": ["plan mundial", "mundial", "internacional", "extranjero", "estados unidos", "mayo clinic", "global medical", "usd"],
        "content": (
            "Plan Mundial de Seguros Atlas ofrece cobertura total tanto en México como en el extranjero con suma "
            "asegurada de hasta $5,000,000 USD. Permite programar cirugías y tratamientos en Mayo Clinic, Cleveland "
            "Clinic, MD Anderson Cancer Center, Johns Hopkins y hospitales de Europa y el mundo a través de la red "
            "Global Medical (teléfonos +1 954 308-3932 y +1 855 209-8025). Incluye pago directo internacional en "
            "estancias mayores a 24 horas y ambulancia aérea internacional."
        ),
    },
    {
        "id": "doc-empresas",
        "title": "Med Óptimo y Med Plus para Empresas — Seguros de Gastos Médicos Colectivos",
        "category": "Empresas y PyMEs",
        "url": "#planes-section",
        "tags": ["empresas", "colectivo", "pyme", "empleados", "deducible de impuestos", "prestacion"],
        "content": (
            "Seguros Atlas cuenta con Med Óptimo para Empresas y Med Plus para Empresas a partir de 10 titulares. "
            "Las primas son deducibles de impuestos como previsión social, permite configurar subgrupos por nivel "
            "organizacional, ofrece cláusula de conversión a póliza individual y reconocimiento de antigüedad."
        ),
    },
    {
        "id": "doc-siniestro-pago-directo",
        "title": "En Caso de Siniestro: Cómo Funciona el Pago Directo y Carta Pase",
        "category": "Siniestros y Urgencias",
        "url": "#siniestros-section",
        "tags": ["siniestro", "pago directo", "carta pase", "hospitalizacion", "cirugia programada", "citamed"],
        "content": (
            "Con Pago Directo, Seguros Atlas liquida directamente al hospital y médicos en convenio los gastos "
            "procedentes en estancias mayores a 24 horas o cirugías de corta estancia programadas con 5 días hábiles "
            "de anticipación. Reporta de inmediato a CITAMED al 55 9177 5144 (CDMX) o 800 849 3918 (Interior). "
            "Para programar cirugía necesitas: Informe Médico, Aviso de Accidente o Enfermedad, estudios con "
            "interpretación y presupuesto quirúrgico. Al usar la red en convenio obtienes reducción en deducible y coaseguro."
        ),
    },
    {
        "id": "doc-siniestro-reembolso",
        "title": "Requisitos y Documentos para Trámite de Reembolso de Gastos Médicos",
        "category": "Siniestros y Reembolsos",
        "url": "#siniestros-section",
        "tags": ["reembolso", "facturas", "documentos", "informe medico", "aviso de accidente", "recetas", "clabe"],
        "content": (
            "Para solicitar un Reembolso en Seguros Atlas debes presentar: 1) Formato Aviso de Accidente o Enfermedad "
            "firmado por el titular, 2) Informe Médico firmado por el médico tratante, 3) Facturas CFDI (XML y PDF) a "
            "nombre del asegurado principal con desglose fiscal, 4) Recetas médicas y resultados de estudios con "
            "interpretación escrita, 5) Copia del expediente clínico en caso de hospitalización, y 6) Estado de cuenta "
            "bancario con CLABE interbancaria e identificación oficial."
        ),
    },
    {
        "id": "doc-med-asistencia",
        "title": "Med Asistencia 24/7 y Ambulancia Terrestre Gratuita",
        "category": "Asistencias y Teléfonos",
        "url": "#siniestros-section",
        "tags": ["med asistencia", "ambulancia", "medico a domicilio", "telefono", "orientacion medica"],
        "content": (
            "Med Asistencia de Seguros Atlas está disponible las 24 horas los 365 días en el 55 5254 7086 (México) "
            "y 800 849 3917. Incluye orientación médica telefónica ilimitada sin costo, envío de médico a domicilio "
            "con tarifa preferencial y los primeros 2 traslados anuales en ambulancia terrestre totalmente gratuitos "
            "(a partir del 3er servicio aplica un costo preferencial de $600 MXN)."
        ),
    },
    {
        "id": "doc-deducible-coaseguro",
        "title": "¿Qué son el Deducible, el Coaseguro y el Tope de Coaseguro?",
        "category": "Guía del Asegurado",
        "url": "#como-respondemos",
        "tags": ["deducible", "coaseguro", "tope de coaseguro", "como funciona", "accidente", "cero deducible"],
        "content": (
            "El Deducible es el monto fijo inicial que participa el asegurado por cada padecimiento cubierto (por "
            "ejemplo $15,000, $25,000, $40,000 o $60,000 MXN; a mayor deducible, menor prima anual). El Coaseguro "
            "es el porcentaje (5%, 10%, 15% o 20%) que participa el asegurado después de restar el deducible, y cuenta "
            "con un Tope Máximo de Coaseguro (ej. $55,000 a $85,000 MXN) a partir del cual Seguros Atlas paga el 100% "
            "de los gastos subsecuentes hasta el límite de la suma asegurada."
        ),
    },
    {
        "id": "doc-maternidad-recien-nacido",
        "title": "Cobertura de Maternidad, Complicaciones del Embarazo y Recién Nacido",
        "category": "Coberturas Especiales",
        "url": "#planes-section",
        "tags": ["maternidad", "embarazo", "parto", "cesarea", "recien nacido", "congenitos", "periodo de espera"],
        "content": (
            "Al cumplir al menos 10 meses de vigencia continua en la póliza de Seguros Atlas para la asegurada entre "
            "18 y 44 años, se otorga la Ayuda por Maternidad libre de deducible y coaseguro ($18,000 en Med Óptimo, "
            "$30,000 en Med Plus, $45,000 en Med Plus Elite y $50,000 MXN en Plan Mundial). Además, el recién nacido "
            "queda cubierto desde el primer día en padecimientos congénitos y nacimientos prematuros al darlo de alta "
            "dentro de los primeros 30 días naturales."
        ),
    },
]
