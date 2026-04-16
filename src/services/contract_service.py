import os
from fpdf import FPDF
from flask import current_app
from datetime import date


def _safe(text) -> str:
    return str(text or '').encode('latin-1', 'replace').decode('latin-1')


def _fmt_date(d) -> str:
    """Formatea una fecha (date o str ISO) a DD/MM/YYYY."""
    if not d:
        return ''
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except ValueError:
            return d
    return d.strftime('%d/%m/%Y')


def _calc_age(date_of_birth) -> str:
    if not date_of_birth:
        return ''
    today = date.today()
    age = today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )
    return str(age)


# ── Contenido compartido ──────────────────────────────────────────────────────

# Cada ítem es (prefijo_numero, texto_sin_numero) para poder controlar la sangría
ASPECTOS_GENERALES = [
    ("1.", "La Escuela de Artes Furor y Pasión es una institución de aprendizaje enfocada en la danza profesional, que tiene como función la formación y perfeccionamiento de las capacidades de aspirantes y bailarines. Como institución, nos distinguimos de los grupos de baile principalmente por manejar programas académicos basados en competencias y diferenciación por niveles y edad, lo que le permite al estudiante llegar al conocimiento y la experiencia de baile."),
    ("2.", "Los ensayos se realizarán principalmente en el salón de la Calle 10 N 3a – 42. Adicionalmente si no es posible por causas ajenas o se requiere un espacio diferente. Cualquier cambio de horario o cancelación de ensayo se realizará por vía telefónica o por mensaje a los grupos de WhatsApp de la escuela."),
    ("3.", "La inasistencia de clase menor a un mes se contará como falla, mas no como suspensión o aplazamiento del curso. Lo cual mantendrá la misma fecha de pago y se realizará cobro."),
    ("4.", "El pago de la mensualidad se recibirá durante los ensayos el mismo día del mes que inicio clases."),
    ("5.", "Las clases perdidas independiente de cuál sea la razón no generan reprogramación o reembolso del dinero."),
]

COMPROMISOS = [
    ("1.", "Me comprometo a participar de las actividades organizadas por la escuela aparte de las clases del curso."),
    ("2.", "Me comprometo a informar inmediatamente cualquier tipo de restricción médica o terapéutica que me impida realizar total o parcialmente cualquiera de los ejercicios establecidos y a presentar soportes del mismo."),
    ("3.", "El proceso es individual."),
    ("4.", "El estudiante mayor de edad es su propio representante."),
    ("5.", "En el caso de pertenecer a grupos de competencia, es obligatorio adquirir vestuario, zapatos o utensilios necesarios."),
]

SANCIONES = [
    ("1.", "El llegar más de 10 minutos tarde al ensayo o sin la ropa adecuada, representa una multa de $4.000 y una rutina de acondicionamiento físico intermedio. Faltar a más de 2 ensayos en un mes acarrea una multa de $30.000 y una rutina de acondicionamiento físico intensa."),
    ("2.", "El no lograr las técnicas o ejercicios establecidos como requerimientos para participar de coreografías, dará como sanción la no participación del estudiante en el espectáculo hasta lograr los requerimientos mínimos."),
    ("3.", "El no cumplir las órdenes del profesor o tener un comportamiento que se considere inadecuado durante las salidas académicas o en competencias, dará como resultado la suspensión de la participación del estudiante o del grupo en el evento."),
    ("4.", "Agredir de forma verbal a un compañero o profesor acarrea la suspensión de 3 clases consecutivas y una multa económica de $30.000. Agredir de forma física a un compañero o profesor acarrea la expulsión permanente de la escuela."),
]

TEXTO_AUTORIZACION = (
    "Furor y Pasión Escuela de Danza, encuentra en las redes sociales y medios digitales una gran oportunidad "
    "de expansión. Por ende, se realizarán tomas fotográficas y de video, de ensayos, eventos o sesiones, para "
    "difundir en las diferentes plataformas institucionales. Y es importante contar la autorización de los "
    "estudiantes y acudientes para poder difundir dicho material. Al firmar el presente reglamento reconozco el "
    "compromiso y disciplina que se requiere para cumplir el programa planteado, el cual conocí previamente y "
    "acepto en totalidad. Confirmo que leí y acepto las normas aquí establecidas, así como doy mi autorización "
    "para el manejo de imagen y contenido audiovisual de manera pública como se solicita en este formato."
)

# Ancho del número + espacio (sangría para el texto que continúa)
NUM_W = 7   # ancho de la celda del número
LINE_H = 5  # altura de línea para multi_cell


def _add_numbered_list(pdf: FPDF, items: list, W: int):
    """
    Renderiza una lista numerada con sangría consistente.
    El número ocupa NUM_W mm y el texto ocupa el resto, alineado en todas las líneas.
    """
    text_w = W - NUM_W
    for num, text in items:
        y_before = pdf.get_y()
        x_base = pdf.get_x()

        # Número
        pdf.cell(NUM_W, LINE_H, _safe(num), ln=False)

        # Texto con sangría: multi_cell avanza el cursor, luego lo reposicionamos
        pdf.multi_cell(text_w, LINE_H, _safe(text))

        # Pequeño espacio entre ítems
        pdf.ln(1)


def _build_base_pdf() -> tuple:
    """Crea el PDF con encabezado y retorna (pdf, ancho_util, margen_izq)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    W = 170

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(W, 8, _safe("REGLAMENTO PARA PROCESOS DE FORMACION"), ln=True, align='C')
    pdf.cell(W, 8, _safe("FUROR Y PASION ESCUELA DE DANZA"), ln=True, align='C')
    pdf.ln(5)

    return pdf, W


def _add_content_sections(pdf: FPDF, W: int):
    """Agrega aspectos generales, compromisos y sanciones al PDF."""
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(W, 6, _safe("Aspectos generales:"), ln=True)
    pdf.set_font("Arial", '', 9)
    _add_numbered_list(pdf, ASPECTOS_GENERALES, W)

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(W, 6, _safe("COMPROMISO DE LOS ESTUDIANTES Y PADRES"), ln=True)
    pdf.set_font("Arial", '', 9)
    _add_numbered_list(pdf, COMPROMISOS, W)

    pdf.ln(2)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(W, 6, _safe("SANCIONES GRUPOS DE COMPETENCIA"), ln=True)
    pdf.set_font("Arial", '', 9)
    _add_numbered_list(pdf, SANCIONES, W)

    pdf.ln(5)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(W, LINE_H, _safe(TEXTO_AUTORIZACION))
    pdf.ln(10)


def _save_pdf(pdf: FPDF, document_id: str) -> str:
    """Guarda el PDF y retorna la ruta del archivo."""
    contracts_dir = os.path.join(current_app.root_path, 'uploads', 'contracts')
    os.makedirs(contracts_dir, exist_ok=True)
    filename = f"contrato_{document_id}.pdf"
    filepath = os.path.join(contracts_dir, filename)
    pdf.output(filepath)
    return filepath


def _add_signature_image(pdf: FPDF, signature_path: str, x: float, y: float,
                          w: float = 50, h: float = 20):
    """
    Inserta la imagen de firma si existe y es válida.
    Acepta tanto rutas absolutas como relativas (relativas a uploads/).
    """
    if not signature_path:
        return

    # Si no es ruta absoluta, construirla desde la carpeta uploads de la app
    if not os.path.isabs(signature_path):
        abs_path = os.path.join(current_app.root_path, 'uploads', signature_path)
    else:
        abs_path = signature_path

    if os.path.exists(abs_path):
        try:
            pdf.image(abs_path, x=x, y=y, w=w, h=h)
        except Exception as e:
            current_app.logger.warning(f"[Contract] No se pudo insertar firma '{abs_path}': {e}")
    else:
        current_app.logger.warning(f"[Contract] Firma no encontrada en: {abs_path}")


def _field_row(pdf: FPDF, left_label: str, left_value: str,
               right_label: str = None, right_value: str = None,
               W: int = 170, left_w: int = 90):
    """
    Dibuja una fila de campos con etiqueta en negrita y valor en normal.
    Si right_label es None, el campo ocupa todo el ancho.
    """
    right_w = W - left_w

    if right_label is not None:
        # Columna izquierda
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(len(left_label) * 2.2, 6, _safe(left_label), ln=False)
        pdf.set_font("Arial", '', 10)
        label_px = len(left_label) * 2.2
        pdf.cell(left_w - label_px, 6, _safe(left_value), ln=False)

        # Columna derecha
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(len(right_label) * 2.2, 6, _safe(right_label), ln=False)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, _safe(right_value), ln=True)
    else:
        # Fila completa
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(len(left_label) * 2.2, 6, _safe(left_label), ln=False)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, _safe(left_value), ln=True)


# ── Contrato Mayor de Edad ────────────────────────────────────────────────────

def _generate_adult_contract(student_data, signature_path: str) -> str:
    """
    Contrato para estudiantes mayores de edad.
    - Tipo de documento: C.C.
    - Una sola firma: la del estudiante.
    """
    pdf, W = _build_base_pdf()

    # Fecha de ingreso
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 6, _safe("FECHA DE INGRESO:"), ln=False)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, _safe(student_data.created_at.strftime('%d/%m/%Y') if student_data.created_at else ''), ln=True)
    pdf.ln(3)

    # ── Datos del alumno ──
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(W, 6, _safe("DATOS DEL ALUMNO"), ln=True)
    pdf.set_font("Arial", '', 10)

    _field_row(pdf,
               "NOMBRE: ", _safe(student_data.full_name),
               "C.C.: ",   _safe(student_data.document_id),
               W=W)

    _field_row(pdf,
               "EDAD: ",              _safe(_calc_age(student_data.date_of_birth)),
               "FECHA DE NACIMIENTO: ", _safe(_fmt_date(student_data.date_of_birth)),
               W=W)

    _field_row(pdf, "CEL: ", _safe(student_data.phone), W=W)
    _field_row(pdf, "DIRECCION: ", _safe(student_data.address), W=W)
    _field_row(pdf, "CORREO: ",    _safe(student_data.email or ''), W=W)

    pdf.ln(5)

    # Contenido reglamentario
    _add_content_sections(pdf, W)

    # ── Firma única: estudiante ──
    pdf.ln(25)
    sig_y = pdf.get_y()

    line_x = pdf.l_margin + (W / 2) - 25
    _add_signature_image(pdf, signature_path, x=line_x, y=sig_y, w=50, h=14)

    pdf.ln(14)
    pdf.cell(W, 6, "__________________________________", 0, 1, 'C')
    pdf.cell(W, 6, _safe("Firma del Estudiante"), 0, 1, 'C')

    return _save_pdf(pdf, student_data.document_id)


# ── Contrato Menor de Edad ────────────────────────────────────────────────────

def _generate_minor_contract(student_data, signature_path: str,
                              guardian_signature_path: str = None) -> str:
    """
    Contrato para estudiantes menores de edad.
    - Tipo de documento del estudiante: T.I.
    - Dos firmas: acudiente (izquierda) y estudiante (derecha).
    """
    pdf, W = _build_base_pdf()

    # Fecha de ingreso
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(35, 6, _safe("FECHA DE INGRESO:"), ln=False)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, _safe(student_data.created_at.strftime('%d/%m/%Y') if student_data.created_at else ''), ln=True)
    pdf.ln(3)

    # ── Datos del alumno ──
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(W, 6, _safe("DATOS DEL ALUMNO"), ln=True)
    pdf.set_font("Arial", '', 10)

    _field_row(pdf,
               "NOMBRE: ", _safe(student_data.full_name),
               "T.I.: ",   _safe(student_data.document_id),
               W=W)

    _field_row(pdf,
               "EDAD: ",              _safe(_calc_age(student_data.date_of_birth)),
               "FECHA DE NACIMIENTO: ", _safe(_fmt_date(student_data.date_of_birth)),
               W=W)

    _field_row(pdf, "CEL: ",      _safe(student_data.phone), W=W)
    _field_row(pdf, "DIRECCION: ", _safe(student_data.address), W=W)
    _field_row(pdf, "CORREO: ",    _safe(student_data.email or ''), W=W)

    pdf.ln(4)

    # ── Datos del acudiente ──
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(W, 6, _safe("DATOS DEL ACUDIENTE"), ln=True)
    pdf.set_font("Arial", '', 10)

    _field_row(pdf,
               "NOMBRE: ", _safe(student_data.guardian_full_name or ''),
               "CEL: ",    _safe(student_data.guardian_phone or ''),
               W=W)

    _field_row(pdf, "PARENTESCO: ", _safe(student_data.guardian_relationship or ''), W=W)
    _field_row(pdf, "CORREO: ",     _safe(student_data.guardian_email or ''), W=W)

    pdf.ln(5)

    # Contenido reglamentario
    _add_content_sections(pdf, W)

    # ── Dos firmas: acudiente | estudiante ──
    pdf.ln(25)
    sig_y = pdf.get_y()

    _add_signature_image(pdf, guardian_signature_path,
                         x=pdf.l_margin + 15, y=sig_y, w=50, h=14)
    _add_signature_image(pdf, signature_path,
                         x=pdf.l_margin + 105, y=sig_y, w=50, h=14)

    pdf.ln(14)
    pdf.cell(80, 6, "__________________________________", 0, 0, 'C')
    pdf.cell(10)
    pdf.cell(80, 6, "__________________________________", 0, 1, 'C')

    pdf.cell(80, 6, _safe("Firma del Acudiente"), 0, 0, 'C')
    pdf.cell(10)
    pdf.cell(80, 6, _safe("Firma del Estudiante"), 0, 1, 'C')

    return _save_pdf(pdf, student_data.document_id)


# ── Punto de entrada público ──────────────────────────────────────────────────

class ContractService:
    @staticmethod
    def generate_student_contract(student_data, signature_path,
                                   guardian_signature_path=None) -> str:
        """
        Genera el contrato adecuado según la edad del estudiante.

        - Mayor de edad (is_minor=False): contrato con C.C. y firma del estudiante.
        - Menor de edad (is_minor=True):  contrato con T.I., firma del acudiente
          y firma del estudiante.

        Si guardian_signature_path no se pasa, intenta usar student_data.guardian_signature_path.
        """
        # Resolver firma del estudiante: parámetro > campo del modelo
        resolved_signature = signature_path or getattr(student_data, 'signature_path', None)

        # Resolver firma del acudiente: parámetro > campo del modelo
        resolved_guardian_signature = guardian_signature_path or getattr(student_data, 'guardian_signature_path', None)

        if student_data.is_minor:
            return _generate_minor_contract(student_data, resolved_signature,
                                            resolved_guardian_signature)
        else:
            return _generate_adult_contract(student_data, resolved_signature)
