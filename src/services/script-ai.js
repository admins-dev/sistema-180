/** Script AI — Generates UGC scripts based on product/service info */

// Pre-built UGC script templates for different tones and formats
const TEMPLATES = {
    testimonial: {
        es: {
            professional: [
                `¡Hola! Tengo que contaros algo increíble sobre {producto}.\n\nLlevo {tiempo} usándolo y la verdad es que ha cambiado completamente mi {beneficio}.\n\nAntes probé mil cosas, pero nada me funcionaba como esto.\n\nLo mejor es que {ventaja_principal}, y el precio es muy competitivo.\n\nSi estáis buscando {necesidad}, os lo recomiendo al 100%. Link en bio. 👇`,
                `Buenos días, hoy quiero hablaros de {producto}.\n\nComo profesional del sector, puedo deciros que {ventaja_principal}.\n\nLlevo {tiempo} probándolo a fondo y los resultados hablan por sí solos: {beneficio}.\n\nLo que más me gusta es la relación calidad-precio.\n\nSi necesitáis {necesidad}, no busquéis más. Os dejo el enlace aquí abajo. 👇`,
            ],
            casual: [
                `Vale, TENGO que enseñaros esto 😱\n\n¿Veis esto? Es {producto} y literalmente me ha cambiado la vida.\n\nYo era de los que pensaba "bah, otro más"... pero NO. {ventaja_principal}.\n\nEn serio, {beneficio} desde que lo uso.\n\n¿Lo mejor? El precio. Es ridículo para lo que ofrece.\n\nOs dejo el link por aquí 🔗👇`,
                `STOP 🛑 Si todavía no conocéis {producto}, necesitáis verlo.\n\nLiteralmente {beneficio} desde la primera semana.\n\nMis amigos me preguntaban "¿qué estás haciendo diferente?" y yo... 😏\n\n{ventaja_principal} y encima {ventaja_extra}.\n\nLink en bio, de nada. ✨`,
            ],
            urgent: [
                `⚠️ ÚLTIMA HORA: {producto} tiene una oferta BRUTAL ahora mismo.\n\nOs lo digo porque yo lo compré a precio completo y me habría encantado pillar este descuento.\n\n{ventaja_principal} + {beneficio}... ¿Necesitáis más razones?\n\nLa oferta acaba en {tiempo}. Corred. Link aquí 👇🔥`,
                `🚨 Dejad lo que estéis haciendo. {producto} está de oferta y se acaba PRONTO.\n\nYo lo uso para {necesidad} y es lo mejor que he probado.\n\n{ventaja_principal}. Los resultados: {beneficio}.\n\nNo os lo penséis. El link está aquí abajo. ⏰💨`,
            ],
        },
        en: {
            professional: [
                `Hi everyone! I need to tell you about {producto}.\n\nI've been using it for {tiempo} and it has completely changed my {beneficio}.\n\nI tried everything before, but nothing worked like this.\n\nThe best part is {ventaja_principal}, and the price is super competitive.\n\nIf you're looking for {necesidad}, I 100% recommend it. Link in bio. 👇`,
            ],
            casual: [
                `OK you guys NEED to see this 😱\n\nThis is {producto} and it literally changed my life.\n\nI was one of those people who thought "meh, another one"... but NO. {ventaja_principal}.\n\nSeriously, {beneficio} since I started using it.\n\nBest part? The price. Insane value.\n\nLink below 🔗👇`,
            ],
            urgent: [
                `⚠️ BREAKING: {producto} has a CRAZY deal right now.\n\nI'm telling you because I bought it at full price and wish I had this discount.\n\n{ventaja_principal} + {beneficio}... Need more reasons?\n\nDeal ends in {tiempo}. Run. Link here 👇🔥`,
            ],
        }
    },
    tutorial: {
        es: {
            professional: [
                `Tutorial rápido: Cómo usar {producto} en 3 pasos.\n\n📌 Paso 1: {paso1}\n📌 Paso 2: {paso2}\n📌 Paso 3: {paso3}\n\nResultado: {beneficio}. Así de sencillo.\n\n{ventaja_principal} y lo notaréis desde el primer uso.\n\n¿Queréis probarlo? Link en la descripción. 👇`,
            ],
            casual: [
                `¿Queréis saber cómo consigo {beneficio}? Os lo enseño 👀\n\nEs súper fácil con {producto}:\n\n1️⃣ {paso1}\n2️⃣ {paso2}\n3️⃣ {paso3}\n\nY listo. Literalmente {ventaja_principal}.\n\nOs dejo el link por aquí ✨👇`,
            ],
        },
    },
    review: {
        es: {
            professional: [
                `Review honesta de {producto} después de {tiempo} de uso.\n\n✅ PROS:\n• {ventaja_principal}\n• {beneficio}\n• Relación calidad-precio excelente\n\n❌ CONTRAS:\n• {contra}\n\n🏆 VEREDICTO: {veredicto}\n\nNota: {nota}/10\n\n¿Os interesa? Link en bio.`,
            ],
            casual: [
                `Review REAL de {producto} — sin filtros 🎯\n\nVale, lo bueno: {ventaja_principal}. En serio, {beneficio}.\n\nLo no tan bueno: {contra}. Pero honestamente, no es para tanto.\n\nMi nota: {nota}/10 👌\n\nSi me preguntáis si lo volvería a comprar: SÍ, mil veces sí.\n\nLink aquí 👇`,
            ],
        },
    },
};

/** Generate a script from form data */
export function generateScript(config) {
    const {
        product,
        benefit,
        mainAdvantage,
        extraAdvantage = '',
        need,
        tone = 'casual',
        format = 'testimonial',
        language = 'es',
        duration = '30',
        contra = 'nada reseñable',
        verdict = 'Totalmente recomendado',
        rating = '9',
        step1 = '',
        step2 = '',
        step3 = '',
        timeUsed = 'unas semanas',
        timeDeal = '48h',
    } = config;

    const pool = TEMPLATES[format]?.[language]?.[tone]
        || TEMPLATES.testimonial.es.casual;

    // Pick a random template
    const template = pool[Math.floor(Math.random() * pool.length)];

    // Replace placeholders
    const script = template
        .replace(/{producto}/g, product || 'este producto')
        .replace(/{beneficio}/g, benefit || 'mis resultados')
        .replace(/{ventaja_principal}/g, mainAdvantage || 'la calidad es increíble')
        .replace(/{ventaja_extra}/g, extraAdvantage || 'tiene envío gratis')
        .replace(/{necesidad}/g, need || 'mejorar vuestra vida')
        .replace(/{tiempo}/g, format === 'review' ? timeUsed : (tone === 'urgent' ? timeDeal : timeUsed))
        .replace(/{contra}/g, contra)
        .replace(/{veredicto}/g, verdict)
        .replace(/{nota}/g, rating)
        .replace(/{paso1}/g, step1 || 'Abrir el producto')
        .replace(/{paso2}/g, step2 || 'Seguir las instrucciones')
        .replace(/{paso3}/g, step3 || 'Disfrutar los resultados');

    // Estimate read duration (avg 150 words/min for video)
    const wordCount = script.split(/\s+/).length;
    const estimatedSeconds = Math.round((wordCount / 150) * 60);

    return {
        text: script,
        wordCount,
        estimatedDuration: estimatedSeconds,
        targetDuration: parseInt(duration),
        format,
        tone,
        language,
    };
}

/** Get available formats */
export function getFormats() {
    return [
        { id: 'testimonial', label: '💬 Testimonial / Reseña', desc: 'Estilo UGC natural' },
        { id: 'tutorial', label: '📚 Tutorial', desc: 'Paso a paso educativo' },
        { id: 'review', label: '⭐ Review completa', desc: 'Análisis con pros/contras' },
    ];
}

/** Get available tones */
export function getTones() {
    return [
        { id: 'professional', label: '👔 Profesional', desc: 'Serio y confiable' },
        { id: 'casual', label: '😎 Casual', desc: 'Natural y cercano' },
        { id: 'urgent', label: '🔥 Urgente', desc: 'Con sentido de urgencia' },
    ];
}
