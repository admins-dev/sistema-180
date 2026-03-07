// ═══════════════════════════════════════════════
// Script Engine — Método Víctor Heras + UMV + SDD
// Umbral Mínimo de Viralidad
// SDD = Salud, Dinero, Desarrollo Personal, Sexo/Parejas
// ═══════════════════════════════════════════════

// SDD Pillars — Los 4 motivadores universales
const SDD_PILLARS = {
    salud: {
        id: 'salud', label: '🏥 Salud', color: '#10b981',
        desc: 'Bienestar, energía, longevidad, aspecto físico',
        hooks: {
            dolor: [
                'Tu cuerpo te está avisando y no le estás haciendo caso...',
                'Esto que haces CADA DÍA te está quitando 10 años de vida...',
                'El 80% de los problemas de salud son por esto tan simple...',
                'Lo que no te cuentan sobre lo que comes todos los días...',
            ],
            curiosidad: [
                'Descubrí el hábito que me cambió la salud en 30 días...',
                'Un médico me dijo algo que me dejó helado...',
                'Esto es lo que hacen las personas que NUNCA enferman...',
                'La ciencia acaba de descubrir por qué estás siempre cansado...',
            ],
            controversia: [
                'Los gimnasios no quieren que sepas esto...',
                'Llevas toda la vida desayunando MAL y nadie te lo dice...',
                'Tu médico no te va a contar esto pero yo sí...',
                'El deporte que haces te está destrozando las articulaciones...',
            ],
            educativo: [
                '3 hábitos que transforman tu salud en 21 días...',
                'El protocolo de mañana que cambió mi energía al 100%...',
                'Así es como duermo 7 horas y rindo el triple...',
                'Mini-guía: cómo mejorar tu salud sin cambiar tu rutina...',
            ],
            resultados: [
                'Perdí 12 kilos sin pisar un gimnasio. Te cuento cómo.',
                'De agotado a con energía infinita en 21 días.',
                'Antes vs Después de cambiar solo UNA cosa en mi alimentación.',
                'Un paciente revirtió su problema en 45 días con esto...',
            ],
            relatable: [
                'Tú cuando te acuestas a las 3AM y te preguntas por qué estás cansado...',
                'Si alguna vez te has sentido con cero energía, esto es para ti.',
                'POV: Descubres que llevas años comiendo algo que te está destruyendo.',
            ],
            urgencia: [
                'Si estás leyendo esto en 2026, todavía estás a tiempo de cambiar tu salud.',
                'Para de scrollear si te sientes cansado SIEMPRE.',
                'Tienes 30 días para cambiar esto o las consecuencias son irreversibles.',
            ]
        }
    },
    dinero: {
        id: 'dinero', label: '💰 Dinero', color: '#f59e0b',
        desc: 'Ingresos, negocios, libertad financiera, inversión',
        hooks: {
            dolor: [
                'El 90% de los {nicho} van a cerrar si no hacen esto...',
                'Estás perdiendo dinero cada día y no lo sabes...',
                'Si tienes un negocio de {nicho}, necesitas ver esto AHORA...',
                'Cometí este error financiero durante 3 años y casi pierdo todo...',
                'Lo que me habría gustado saber antes de abrir mi {nicho}...',
            ],
            curiosidad: [
                'Sabías que puedes triplicar tus ingresos sin gastar un euro?',
                'Un cliente facturó {cifra} euros en 30 días haciendo solo esto...',
                'La IA está a punto de cambiar tu negocio para siempre...',
                'Nadie habla de esta estrategia y funciona mejor que los anuncios...',
            ],
            controversia: [
                'El marketing tradicional está MUERTO para {nicho}...',
                'Los expertos no quieren que sepas esto sobre el dinero...',
                'Deja de gastar dinero en publicidad que no funciona...',
                'Todo lo que te han dicho sobre hacerte rico es MENTIRA...',
            ],
            educativo: [
                '3 cosas que todo {nicho} debería automatizar HOY...',
                'El sistema exacto que uso para facturar {cifra} euros al mes...',
                'Te enseño en 60 segundos cómo ganar dinero con {accion}...',
                'La herramienta que me ahorra 4 horas al día y me genera dinero...',
            ],
            resultados: [
                'De {pocos} a {muchos} clientes en {resultado_tiempo}. Te cuento cómo.',
                'Un cliente facturó {cifra} euros en 30 días con esto.',
                'Antes vs Después de implementar IA en un negocio de {nicho}.',
                'Este error me costó 2.300 euros. No lo cometas tú.',
            ],
            relatable: [
                'Tú cuando tu negocio de {nicho} no crece y no sabes por qué...',
                'Si alguna vez has pensado en cerrar tu negocio, esto es para ti.',
                'POV: Eres {nicho} y descubres que tu competencia ya usa IA.',
            ],
            urgencia: [
                'Si estás viendo esto en 2026, todavía estás a tiempo.',
                'Para de scrollear si tu {nicho} no llega a fin de mes.',
                'En 6 meses será demasiado tarde para hacer esto...',
            ]
        }
    },
    desarrollo: {
        id: 'desarrollo', label: '🧠 Desarrollo Personal', color: '#6366f1',
        desc: 'Mentalidad, productividad, hábitos, propósito',
        hooks: {
            dolor: [
                'Llevas años posponiendo tus sueños y lo sabes...',
                'La razón por la que te sientes estancado no es lo que crees...',
                'Si sigues haciendo lo mismo, en 5 años estarás IGUAL...',
                'Tu zona de confort te está robando la vida que mereces...',
            ],
            curiosidad: [
                'El hábito que separa a los exitosos del resto...',
                'La regla que cambió mi vida en 90 días...',
                'Descubrí por qué el 95% nunca consigue sus metas...',
                'Lo que Musk, Bezos y Jobs tienen en común (no es talento)...',
            ],
            controversia: [
                'La motivación es una MENTIRA y te voy a explicar por qué...',
                'Los libros de autoayuda te están haciendo MÁS mediocre...',
                'Levantarte a las 5AM NO te va a hacer exitoso...',
                'El pensamiento positivo está arruinando tu vida...',
            ],
            educativo: [
                '3 hábitos de los emprendedores de 7 cifras...',
                'El método que uso para ser productivo 12 horas al día...',
                'Mini-tutorial: cómo diseñar tu día perfecto...',
                'Así organizo mi semana para no trabajar los viernes...',
            ],
            resultados: [
                'Hace 1 año estaba arruinado. Hoy facturo {cifra} euros al mes.',
                'La regla que cambió mi vida en 90 días (con pruebas).',
                'De procrastinar TODO a completar 10x más cada día.',
            ],
            relatable: [
                'Tú cuando sabes lo que tienes que hacer pero no lo haces...',
                'Si alguna vez has pospuesto algo importante, esto es para ti.',
                'POV: Te das cuenta de que llevas 5 años en el mismo sitio.',
            ],
            urgencia: [
                'Si no cambias esto AHORA, en 5 años seguirás igual.',
                'Tu futuro se decide en los próximos 90 días.',
                'Esta oportunidad no va a durar para siempre.',
            ]
        }
    },
    parejas: {
        id: 'parejas', label: '❤️ Sexo / Parejas', color: '#ec4899',
        desc: 'Relaciones, atracción, confianza, comunicación',
        hooks: {
            dolor: [
                'Esto que haces está destruyendo tu relación sin que te des cuenta...',
                'La razón oculta por la que tus relaciones siempre terminan mal...',
                'Si tu pareja hace esto, necesitas ver este vídeo...',
                'El error que comete el 90% de las parejas y arruina todo...',
            ],
            curiosidad: [
                'La psicología detrás de la atracción (no es lo que crees)...',
                'Descubrí por qué algunas personas siempre atraen y otras no...',
                'Lo que las parejas que duran 50 años hacen diferente...',
                'Un psicólogo me reveló el secreto de las relaciones exitosas...',
            ],
            controversia: [
                'El consejo de pareja más popular es el MÁS destructivo...',
                'Los terapeutas de pareja no quieren que sepas esto...',
                'Sé tú mismo es el PEOR consejo de relaciones...',
                'La comunicación NO salva relaciones y te explico por qué...',
            ],
            educativo: [
                '3 señales de que tu relación va a durar (respaldado por ciencia)...',
                'La técnica que salvó mi relación en 2 semanas...',
                'Así se construye confianza real en una relación...',
                'Mini-guía: cómo tener conversaciones difíciles con tu pareja...',
            ],
            resultados: [
                'De casi divorciarnos a la mejor relación de nuestras vidas.',
                'Antes vs Después de aplicar esta técnica con mi pareja.',
                'Un consejo que cambió mi relación en 48 horas.',
            ],
            relatable: [
                'Tú cuando tu pareja te dice que tenemos que hablar...',
                'Si alguna vez te han dejado sin explicación, esto es para ti.',
                'POV: Tu ex te escribe después de 3 meses de silencio.',
            ],
            urgencia: [
                'Si no arreglas esto HOY, tu relación tiene fecha de caducidad.',
                'Para de scrollear si sientes que tu relación se está enfriando.',
                'Este vídeo puede salvar tu relación. En serio.',
            ]
        }
    }
};

const STORY_TEMPLATES = [
    'Hace {tiempo}, un {nicho} de {ciudad} tenía el mismo problema que tú. Solo recibía {pocos} clientes al mes y estaba a punto de cerrar. Entonces descubrimos que el problema no era su servicio, sino cómo captaba clientes. Implementamos {solucion} y en {resultado_tiempo} pasó de {pocos} a {muchos} clientes.',
    'Te voy a contar la historia de {nombre}, que tiene un negocio de {nicho}. Llevaba meses intentando crecer pero nada funcionaba. El problema real era que dependía al 100% del boca a boca. Cuando automatizamos su captación con {solucion}, todo cambió. En solo {resultado_tiempo}, {resultado}.',
    'Cuando empecé a trabajar con negocios de {nicho}, pensaba que lo más importante era el servicio. Estaba equivocado. Lo más importante es que la gente sepa que EXISTES. {nombre} tenía el mejor servicio de {ciudad}, pero solo {pocos} clientes al mes. Con {solucion}, ahora tiene {muchos} y puede elegir con quién trabaja.',
];

const MORALEJAS = [
    'La diferencia entre un negocio que crece y uno que cierra no es el producto — es el SISTEMA de captación.',
    'En 2026, si tu negocio no tiene un sistema automatizado, estás compitiendo con una mano atada.',
    'No necesitas más horas, necesitas MEJORES SISTEMAS. La IA no reemplaza tu trabajo — reemplaza las tareas que te roban tiempo.',
    'El secreto no es trabajar más, es tener un sistema que trabaje las 24 horas por ti.',
    'Si esperas a que los clientes vengan solos, tu competencia ya se los está llevando.',
    'La automatización no es el futuro — es el PRESENTE. Y los que no se adapten, van a desaparecer.',
];

const CTAS = {
    seguir: [
        'Sígueme para más estrategias como esta.',
        'Si te ha servido, dale a seguir para no perderte los próximos consejos.',
        'Guarda este vídeo y sígueme — cada semana comparto estrategias así.',
    ],
    comprar: [
        'Si quieres que implementemos esto en tu negocio, tienes el link en mi bio.',
        'Comenta INFO y te cuento cómo aplicar esto a tu negocio.',
        'Tienes una consulta gratuita de 15 minutos en el link de mi perfil.',
        'Mándame un DM con QUIERO y te explico cómo empezar.',
    ],
    comunidad: [
        'Únete a nuestra comunidad privada — link en bio.',
        'Tenemos un grupo exclusivo donde compartimos estas estrategias. Link en bio.',
    ]
};

const NICHOS = [
    'estética', 'peluquería', 'clínica dental', 'fisioterapia', 'restaurante',
    'gimnasio', 'inmobiliaria', 'taller mecánico', 'fotografía', 'abogado',
    'nutricionista', 'coaching', 'psicología', 'veterinaria', 'reformas'
];

// ── FORMATOS VIRALES ────────────────────────────
const VIRAL_FORMATS = {
    talking_head: {
        id: 'talking_head', label: '🗣️ Talking Head',
        desc: 'Hablando directo a cámara, conexión personal',
        notes: 'Buena iluminación, encuadre pecho/cara, contacto visual. Ideal para autoridad y confianza.',
        avatarTip: 'Avatar mirando a cámara, pose confiada',
        ejemplo: 'Persona hablando directo a cámara con subtítulos grandes',
        ideal: ['educativo', 'controversia', 'dolor'],
    },
    voiceover: {
        id: 'voiceover', label: '🎙️ Voz en Off',
        desc: 'Narración sobre imágenes/vídeo B-roll',
        notes: 'Audio limpio y profesional. Imágenes de apoyo que refuercen el mensaje. Subtítulos obligatorios.',
        avatarTip: 'No necesita avatar visible — solo voz + imágenes de apoyo',
        ejemplo: 'Voz narrando mientras se ven gráficos, stats, o escenas',
        ideal: ['educativo', 'curiosidad'],
    },
    pov: {
        id: 'pov', label: '👁️ POV (Punto de Vista)',
        desc: 'El espectador vive la situación en primera persona',
        notes: 'Texto tipo "POV: ..." en pantalla. El avatar reacciona como si el espectador fuera el protagonista.',
        avatarTip: 'Avatar actuando/reaccionando, mirando ligeramente fuera de cámara',
        ejemplo: 'POV: Le dices a un dentista que no se lava los dientes desde 2020',
        ideal: ['curiosidad', 'controversia'],
    },
    tutorial: {
        id: 'tutorial', label: '📚 Tutorial Rápido',
        desc: 'Enseña algo valioso en 30-60 segundos',
        notes: 'Pasos numerados, screencast o demo visual. La gente GUARDA estos vídeos (alto engagement).',
        avatarTip: 'Avatar señalando, explicando con gestos',
        ejemplo: 'Cómo configurar X en 3 pasos (con screencast)',
        ideal: ['educativo'],
    },
    storytime: {
        id: 'storytime', label: '📖 Storytime',
        desc: 'Contar una historia personal o de un cliente',
        notes: 'Narrativa con tensión, nudo y desenlace. El formato más poderoso para el UMV.',
        avatarTip: 'Avatar hablando con expresiones variadas, gesticulando',
        ejemplo: 'Os voy a contar lo que le pasó a un cliente hace 6 meses...',
        ideal: ['dolor', 'curiosidad'],
    },
    greenscreen: {
        id: 'greenscreen', label: '🟩 Green Screen',
        desc: 'Avatar delante de imagen/web/datos como fondo',
        notes: 'Señalar estadísticas, capturas de pantalla, noticias. Muy usado para reacciones y datos.',
        avatarTip: 'Avatar en esquina inferior, señalando el fondo',
        ejemplo: 'Persona señalando un titular de noticia o gráfico impactante',
        ideal: ['controversia', 'educativo'],
    },
    slideshow: {
        id: 'slideshow', label: '📱 Carrusel / Slideshow',
        desc: 'Slides con texto + imágenes que pasan',
        notes: 'Texto legible, 1 idea por slide, 5-8 slides. Los carruseles tienen MÁS alcance que los Reels en 2026.',
        avatarTip: 'No necesita avatar — puro texto visual o avatar en primera slide',
        ejemplo: '5 herramientas de IA que tu negocio necesita (slide por slide)',
        ideal: ['educativo', 'curiosidad'],
    },
    antes_despues: {
        id: 'antes_despues', label: '🔄 Antes / Después',
        desc: 'Transformación visual con comparativa',
        notes: 'Split screen o transición. Muy viral por el factor WOW de la transformación.',
        avatarTip: 'Avatar mostrando el antes y el después, reaccionando',
        ejemplo: 'Negocio de estética: 3 clientes/mes → 40 clientes/mes',
        ideal: ['curiosidad', 'dolor'],
    },
    reaction: {
        id: 'reaction', label: '😲 Reacción',
        desc: 'Reaccionar a contenido viral, noticias o tendencias',
        notes: 'Duet/Stitch style. Coger algo trending y aportar tu perspectiva. Muy fácil de producir.',
        avatarTip: 'Avatar viendo contenido, reaccionando con sorpresa/análisis',
        ejemplo: 'Reacciono a esta estrategia de marketing viral...',
        ideal: ['controversia', 'curiosidad'],
    },
    lista: {
        id: 'lista', label: '📋 Listicle (Top X)',
        desc: 'Lista numerada: Top 3, 5 errores, 7 claves...',
        notes: 'Cada punto con texto en pantalla. Retención altísima porque la gente espera al siguiente número.',
        avatarTip: 'Avatar contando con los dedos, enumerando',
        ejemplo: '5 errores que cometen los negocios de {nicho} (el 3 te va a sorprender)',
        ideal: ['educativo', 'dolor'],
    },
    entrevista: {
        id: 'entrevista', label: '🎤 Entrevista / Podcast Clip',
        desc: 'Clip de conversación tipo podcast',
        notes: 'Dos personas, clip del momento más impactante. Subtítulos grandes. Formato en auge.',
        avatarTip: 'Dos avatares en split o uno hablando con micro',
        ejemplo: 'El momento en que un emprendedor revela su secreto al entrevistador',
        ideal: ['curiosidad', 'controversia'],
    },
    challenge: {
        id: 'challenge', label: '🏆 Challenge / Reto',
        desc: 'Reto viral adaptado a tu nicho',
        notes: 'Usa trending audios. Adapta el challenge a tu marca. Fomenta que otros lo repitan.',
        avatarTip: 'Avatar participando en el reto con energía',
        ejemplo: 'Intento conseguir 10 clientes en 24 horas con solo IA',
        ideal: ['curiosidad', 'educativo'],
    },
};

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function fillTemplate(template, vars = {}) {
    let text = template;
    Object.entries(vars).forEach(([k, v]) => {
        text = text.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
    });
    return text;
}

export function generateScript(config) {
    const {
        nicho = 'negocio local',
        hookType = 'curiosidad',
        sddPillar = 'dinero',
        formato = 'talking_head',
        tono = 'profesional',
        duracion = '60s',
        plataforma = 'tiktok',
        ctaType = 'seguir',
        ciudad = 'Madrid',
    } = config;

    const vars = {
        nicho, ciudad,
        cifra: pick(['5.000', '10.000', '15.000', '20.000']),
        tiempo: pick(['6 meses', '1 año', '8 meses']),
        pocos: pick(['3', '5', '8']),
        muchos: pick(['30', '45', '60', '80']),
        nombre: pick(['María', 'Carlos', 'Laura', 'Jorge', 'Ana']),
        solucion: pick(['una web de captación + recepcionista IA', 'un sistema automatizado con IA', 'una estrategia digital con automatizaciones']),
        resultado_tiempo: pick(['30 días', '2 semanas', '45 días']),
        resultado: pick(['triplicó su facturación', 'pasó de 5 a 40 clientes', 'dejó de depender del boca a boca']),
        accion: pick(['captar clientes en automático', 'automatizar tu agenda', 'conseguir 20 clientes nuevos al mes']),
    };

    // Get hooks from SDD pillar
    const pillar = SDD_PILLARS[sddPillar] || SDD_PILLARS.dinero;
    const pillarHooks = pillar.hooks[hookType] || pillar.hooks.curiosidad;
    const hook = fillTemplate(pick(pillarHooks), vars);
    const story = fillTemplate(pick(STORY_TEMPLATES), vars);
    const moraleja = pick(MORALEJAS);
    const cta = pick(CTAS[ctaType] || CTAS.seguir);

    // Format info
    const formatInfo = VIRAL_FORMATS[formato] || VIRAL_FORMATS.talking_head;

    // UMV + SDD + Format note
    const umvNote = `UMV + SDD [${pillar.label}] + Formato [${formatInfo.label}]: Primera mitad mainstream ("${pillar.desc}"). Segunda mitad → target (${nicho}). Producción: ${formatInfo.notes}`;

    return {
        hook, story, moraleja, cta, umvNote,
        sddPillar: pillar.label,
        formato: formatInfo,
        config,
        timestamp: new Date().toISOString()
    };
}

export function getHookTypes() {
    return [
        { id: 'dolor', label: '😰 Dolor', desc: 'Problema que duele' },
        { id: 'curiosidad', label: '🤔 Curiosidad', desc: 'Algo que sorprende' },
        { id: 'controversia', label: '⚡ Controversia', desc: 'Va contra lo establecido' },
        { id: 'educativo', label: '📚 Educativo', desc: 'Enseña algo valioso' },
        { id: 'resultados', label: '📈 Resultados', desc: 'Transformación con pruebas' },
        { id: 'relatable', label: '🤝 Relatable', desc: 'Micro-escenario viral' },
        { id: 'urgencia', label: '🚨 Urgencia', desc: 'FOMO, actúa ya' },
    ];
}

export function getSddPillars() {
    return Object.values(SDD_PILLARS).map(p => ({
        id: p.id, label: p.label, desc: p.desc, color: p.color
    }));
}

export function getFormatos() {
    return Object.values(VIRAL_FORMATS).map(f => ({
        id: f.id, label: f.label, desc: f.desc, notes: f.notes,
        avatarTip: f.avatarTip, ejemplo: f.ejemplo, ideal: f.ideal
    }));
}

export function getCtaTypes() {
    return [
        { id: 'seguir', label: '👆 Seguir' },
        { id: 'comprar', label: '🛒 Comprar' },
        { id: 'comunidad', label: '👥 Comunidad' },
    ];
}

export function getNichos() { return NICHOS; }



