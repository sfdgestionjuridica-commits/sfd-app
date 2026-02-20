import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from core.database import engine, Base, SessionLocal
from core.models import Cliente, Empresa, Proceso

Base.metadata.create_all(bind=engine)

import os
import json
import requests
import random
from datetime import datetime
from sqlalchemy import text

def enviar_whatsapp(numero, mensaje):
    try:
        url = "https://api.ultramsg.com/INSTANCE_ID/messages/chat"

        payload = {
            "token": "TU_TOKEN",
            "to": numero,
            "body": mensaje
        }

        response = requests.post(url, data=payload)

        return response.json()

    except Exception as e:
        return str(e)

# 🔥 PASO 2 — CAPTURAR RADICADO (DESPUÉS DE CREAR TABLAS)
query_params = st.query_params
radicado_url = query_params.get("radicado", None)

if radicado_url:

    st.set_page_config(page_title="Carga de Documentos", layout="wide")

    st.title("📄 Carga de Documentos del Caso")
    st.success(f"Radicado: {radicado_url}")

    st.markdown("### 📂 Documentos requeridos")

    # 🔒 VALIDACIÓN CRÍTICA
    if not radicado_url:
        st.error("❌ No se recibió el radicado en la URL")
        st.stop()

    # 📁 Ruta del cliente
    ruta_base = os.path.join("uploads", "CLIENTES", radicado_url)

    if not os.path.exists(ruta_base):
        os.makedirs(ruta_base, exist_ok=True)


    # -------------------------
    # 📌 DOCUMENTOS PRINCIPALES
    # -------------------------

    doc_id = st.file_uploader(
        "📄 Documento de identidad del cliente",
        type=["pdf", "jpg", "png"],
        key="doc_id"
    )


    paz_salvo = st.file_uploader(
        "📄 Paz y Salvo del abogado anterior",
        type=["pdf"],
        key="paz_salvo"
    )

    doc_contraparte = st.file_uploader(
        "📄 Documento de identidad de la contraparte (opcional)",
        type=["pdf", "jpg", "png"],
        key="doc_contraparte"
    )

    # -------------------------
    # 📌 PRUEBAS DEL CASO
    # -------------------------

    pruebas = st.file_uploader(
        "📁 Pruebas y documentos del caso",
        type=["pdf", "jpg", "png"],
        accept_multiple_files=True,
        key="pruebas"
    )

    st.markdown("---")

    # 🔐 VARIABLES SEGURAS (EVITA ERRORES DE PYLANCE)

    nombre = locals().get("nombre", "")
    error_email = locals().get("error_email", False)
    rol = locals().get("rol", "")
    error_radicado = locals().get("error_radicado", False)


    # 🔒 VALIDADOR GLOBAL DEL FORMULARIO
    formulario_valido = True

    # ❌ Validación nombre
    if not nombre:
        formulario_valido = False

    # ❌ Validación correos
    if error_email:
        formulario_valido = False

    # ❌ Validación contraparte
    nombre_contraparte_val = st.session_state.get("contraparte_nombre", "")
    if not nombre_contraparte_val:
        formulario_valido = False

    # ❌ Validaciones para rol 2 y 4
    if rol in ["2", "4"] and "radicado" in st.query_params:

        # Radicado obligatorio
        if 'error_radicado' in locals() and error_radicado:
           formulario_valido = False

        # Documento identidad
        if not st.session_state.get("doc_id"):
           formulario_valido = False

        # Paz y salvo
        if not st.session_state.get("paz_salvo"):
           formulario_valido = False


    # -------------------------
    # 📌 BOTÓN DE CARGA
    # -------------------------

    if st.button("📤 Guardar documentos"):

        try:

            # 📄 Documento identidad cliente
            if doc_id:
                with open(os.path.join(ruta_base, "DOC_001_ID_CLIENTE.pdf"), "wb") as f:
                    f.write(doc_id.read())

            # 📄 Documento contraparte
            if doc_contraparte:
                with open(os.path.join(ruta_base, "DOC_002_ID_CONTRAPARTE.pdf"), "wb") as f:
                    f.write(doc_contraparte.read())

            # 📄 Paz y salvo
            if paz_salvo:
                with open(os.path.join(ruta_base, "DOC_003_PAZ_Y_SALVO.pdf"), "wb") as f:
                    f.write(paz_salvo.read())

            # 📁 Pruebas múltiples
            if pruebas:
                ruta_pruebas = os.path.join(ruta_base, "pruebas")
                os.makedirs(ruta_pruebas, exist_ok=True)

                for i, archivo in enumerate(pruebas, start=1):
                    nombre_archivo = f"PRB_{str(i).zfill(3)}_{archivo.name}"

                    with open(os.path.join(ruta_pruebas, nombre_archivo), "wb") as f:
                        f.write(archivo.read())

            st.success("✅ Documentos cargados correctamente")
            
            st.markdown("### 📌 Estado del proceso")

            st.info("""
            Su caso ha sido recibido y **entra en proceso de revisión jurídica** por nuestro equipo.
                    
            ⏳ **Tiempo estimado:** 3 días hábiles
            """)
            
            st.warning("""
            📲 **Muy importante**

            Nos estaremos comunicando con usted para agendar una cita **presencial o virtual**.

            Debe estar atento a:
            • Su número de WhatsApp registrado  
            • Su correo electrónico  

            ⚠️ Sin esta comunicación no se podrá continuar con el proceso.
            """)

            st.success("🤝 Gracias por confiar en SFD Gestión Jurídica")

            st.markdown("---")

            st.markdown("### 🔐 Finalizar proceso de forma segura")

            col1, col2 = st.columns([1,1])

            with col1:
               if st.button("✅ Finalizar y salir", use_container_width=True):

                  # 🧹 Limpiar sesión completamente
                  for key in list(st.session_state.keys()):
                    del st.session_state[key]

                  st.success("🔒 Sesión finalizada correctamente")

                  st.info("🔄 Redirigiendo al inicio...")

                  # 🔁 Redirección limpia (reinicia la app)
                  st.rerun()

            with col2:
                st.markdown("""
                <div style="background-color:#f8f9fa;padding:10px;border-radius:8px;">
               💡 <b>Recomendación:</b><br>
                Puede cerrar esta ventana con total seguridad.
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error al guardar archivos: {e}")

    st.stop()

def scroll_to(id_element):
    st.markdown(f"""
        <script>
            setTimeout(function() {{
                var element = window.parent.document.getElementById("{id_element}");
                if (element) {{
                    element.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}, 200);
        </script>
    """, unsafe_allow_html=True)

def generar_link_formulario1(lead_id):
    return f"https://subsynodical-chololithic-leatha.ngrok-free.dev/?lead={lead_id}"


def generar_link_formulario2(radicado):
    return f"http://localhost:8501/?radicado={radicado}"

# 1. Configuración de Poder y Estética
st.set_page_config(page_title="SFD Gestión Jurídica", page_icon="⚖️", layout="wide")

# -------------------------------
# 📲 PANEL DE ENVÍO DE FORMULARIO 1 (INTERNO)
# -------------------------------

st.markdown("## 📲 Envío de formulario al cliente")

with st.expander("🚀 Enviar link de registro"):

    telefono_envio = st.text_input("Número de WhatsApp del cliente", placeholder="Ej: 573001234567")

    if st.button("📤 Enviar formulario"):

        if telefono_envio:

            # 🔢 Generar ID único
            lead_id = random.randint(10000, 99999)

            # 🔗 Generar link
            link_formulario1 = generar_link_formulario1(lead_id)

            # 📨 Construir mensaje completo
            mensaje = f"""📄 Bienvenido(a) a SFD Gestión Jurídica

Gracias por confiar en nosotros para el manejo de su situación jurídica.

Para brindarle una asesoría adecuada, hemos diseñado un proceso inicial de registro que nos permite analizar su caso con precisión.

👉 Por favor diligencie el siguiente formulario:

{link_formulario1}

📌 A partir de la información suministrada:
• Se realizará un estudio jurídico preliminar
• Se definirá la estrategia a seguir
• Se le contactará con los siguientes pasos

Su información será tratada con absoluta confidencialidad.

SFD Gestión Jurídica
Compromiso, estrategia y resultados.
"""

            import urllib.parse
            mensaje_codificado = urllib.parse.quote(mensaje)

            url_whatsapp = f"https://wa.me/57{telefono_envio}?text={mensaje_codificado}"

            st.markdown(
                f"""
                <script>
                window.open("{url_whatsapp}", "_blank");
                </script>
                """,
   
                unsafe_allow_html=True
            )


            st.markdown(f"[📲 Abrir WhatsApp]( {url_whatsapp} )")




            # 💾 Guardar en BD (opcional por ahora)
            db = SessionLocal()
            try:
                nuevo_lead = Cliente(
                    nombre="PENDIENTE",
                    documento="0",
                    correo="pendiente@correo.com",
                    celular=telefono_envio,
                    direccion="PENDIENTE"
                )
                db.add(nuevo_lead)
                db.commit()
            except:
                db.rollback()
            finally:
                db.close()

            # 📩 Mensaje listo
            mensaje = f"""📄 Bienvenido(a) a SFD Gestión Jurídica

Gracias por confiar en nosotros.

👉 Por favor registre sus datos aquí:
{link_formulario1}

📌 Su caso será analizado y le contactaremos en breve.

SFD Gestión Jurídica
Compromiso, estrategia y resultados"""

            # 🔗 Abrir WhatsApp Web
            url_whatsapp = f"https://wa.me/{telefono_envio}?text={mensaje.replace(' ', '%20')}"

            st.success("✅ Enlace generado correctamente")
            st.markdown(f"[👉 Enviar por WhatsApp]({url_whatsapp})")
        
        else:
            st.error("❌ Debe ingresar un número válido")


# Función para cargar la base de datos nacional
@st.cache_data
def cargar_datos_colombia():
    url = "https://raw.githubusercontent.com/marcovega/colombia-json/master/colombia.min.json"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return []

datos_colombia = cargar_datos_colombia()

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .nombre-presencia { color: #003366 !important; font-family: 'Playfair Display', serif !important; font-size: 80px !important; font-weight: 900 !important; line-height: 0.9 !important; margin: 0 !important; }
    .subtitulo-sutil { color: #777777 !important; font-family: 'Arial', sans-serif !important; font-size: 14px !important; text-transform: uppercase !important; letter-spacing: 4px !important; }
    .linea-poder { border-bottom: 5px solid #003366; margin: 20px 0px 40px 0px; }
    label { color: #003366 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Supremo SFD
# -------------------------------
# RUTA IMAGEN (TU NOMBRE EXACTO)
# -------------------------------
ruta = os.path.join("uploads", "logo_sfd-header.png")

# -------------------------------
# FUNCIÓN BASE64
# -------------------------------
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# -------------------------------
# HEADER PROFESIONAL (SIN ROMPER UI)
# -------------------------------
if os.path.exists(ruta):
    img_base64 = get_base64_image(ruta)

    st.markdown(f"""
        <style>
        /* SOLO HEADER - NO TOCAR INPUTS */
        .header-container {{
            position: sticky;
            top: 0;
            z-index: 999;
            background-color: white;
            padding-top: 5px;
            padding-bottom: 5px;
            border-bottom: 2px solid #C8A95A; /* línea dorada elegante */
        }}

        .header-container img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        </style>

        <div class="header-container">
            <img src="data:image/png;base64,{img_base64}">
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("⚠️ No se encontró la imagen en uploads/logo_sfd-header.png")

# -------------------------------
# ESPACIADO NATURAL (IMPORTANTE)
# -------------------------------
st.write("")  # evita que quede pegado

# -------------------------------
# SELECCIÓN DE ROL
# -------------------------------
st.markdown("## ⚖️ Seleccione su situación o rol en el proceso")

opciones = {
    "1": "👉 Quiero iniciar una demanda",
    "2": "👉 Ya tengo una demanda y quiero cambiar o continuar con otro abogado",
    "3": "👉 Me están demandando",
    "4": "👉 Me están demandando, pero ya tengo abogado",
    "5": "👉 Quiero hacer un trámite ante una entidad (no demanda)"
}

rol = st.radio(
    "seleccione su rol en el proceso",
    options=list(opciones.keys()),
    format_func=lambda x: opciones[x],
    index=None,
    label_visibility="collapsed" 
)

if rol is None:
    st.stop()

# 📲 ENVÍO FORMULARIO 1 POR WHATSAPP (CONTACTO INICIAL)

st.markdown("## 📲 Enviar formulario al cliente")

telefono_envio = st.text_input("Número de WhatsApp del cliente (con indicativo país)", placeholder="573001234567")

if telefono_envio:

    link_formulario1 = generar_link_formulario1(random.randint(10000,99999))

    mensaje = f"""📄 Bienvenido(a) a SFD Gestión Jurídica

Gracias por confiar en nosotros para el manejo de su situación jurídica.

Para brindarle una asesoría adecuada, hemos diseñado un proceso inicial de registro que nos permite analizar su caso con precisión.

👉 Por favor diligencie el siguiente formulario:
{link_formulario1}

📌 A partir de la información suministrada:
• Se realizará un estudio jurídico preliminar  
• Se definirá la estrategia a seguir  
• Se le contactará con los siguientes pasos  

Su información será tratada con absoluta confidencialidad.

SFD Gestión Jurídica  
Compromiso, estrategia y resultados.
"""

    mensaje_encoded = mensaje.replace(" ", "%20").replace("\n", "%0A")

    url_whatsapp = f"https://wa.me/{telefono_envio}?text={mensaje_encoded}"

    st.link_button("📲 Enviar mensaje por WhatsApp", url_whatsapp)


# 🔥 CONTROL DE FLUJO (AQUÍ VA)
flujo_documentos = rol in ["2", "4"]

# 🧠 CONTROL DE PASOS (SCROLL INTELIGENTE)
if "paso" not in st.session_state:
    st.session_state.paso = 1

if flujo_documentos:

    st.error("🚫 Este caso requiere documentación previa obligatoria")

    st.warning("""
    ⚠️ **Advertencia importante sobre cambio de representación legal**

    Usted ha indicado que su proceso ya fue iniciado o atendido previamente por otro abogado.

    Para asumir su representación es obligatorio contar con:
               
    • Paz y salvo del abogado anterior  
    """)

    # 👇 AQUÍ VA TU RADIO DE DOCUMENTOS
    dispone_docs = st.radio(
        "¿Dispone actualmente de este documento?",
        ["Sí", "No"],
        key="dispone_docs"
    )

    if dispone_docs == "Sí":
        st.success("✅ Puede continuar con el registro")
        # 👉 aquí sigue el formulario normal

    else:
        st.warning("⚠️ Continue con el registro pero debe necesariamente solicitar el Paz y Salvo al abogado anterior para poder asumir su representación")

#Bloque 1 Scroll
st.markdown('<div id="paso1"></div>', unsafe_allow_html=True)
st.markdown("## 1. Datos Personales")

col_n, col_d = st.columns(2)

nombre = col_n.text_input(
    "Nombres y Apellidos Completos*",
    key="nom_in",
    autocomplete="off"
)

with col_d:
    doc_raw = st.text_input("Número de Documento / NIT*", key="doc_in")

    if doc_raw:
        doc_limpio = ''.join(filter(str.isdigit, doc_raw))
        doc_formateado = f"{int(doc_limpio):,}".replace(",", ".")
        st.caption(f"📌 Verifique el número ingresado: {doc_formateado}")

if doc_raw and not doc_raw.isdigit():
    st.error("❌ El documento debe contener solo números")

col_e1, col_e2 = st.columns(2)

email = col_e1.text_input("Correo electrónico*", key="em_in")
conf_email = col_e2.text_input("Confirmar correo*", key="em_conf")

# Validación inmediata
error_email = False
if email and conf_email:
    if email != conf_email:
        st.error("❌ Los correos electrónicos no coinciden")
        error_email = True
    else:
        st.success("✅ Correos verificados correctamente")

# Control de pasos
if nombre:
    st.session_state.paso = 2
if doc_raw:
    st.session_state.paso = 3
if email and conf_email and not error_email:
    st.session_state.paso = 4

       # si selecciona 1, 3 o 5 entonces muestra todo el formulario 

# --- 2. DIRECCIÓN DE NOTIFICACIÓN FÍSICA ---
st.markdown("## Dirección de Notificación Física")
st.write("**Nomenclatura Exacta**")
d_cols = st.columns([1.5, 1, 1, 1, 0.5, 1, 1, 1, 1, 1.5])

with d_cols[0]: 
    via = st.selectbox("Nomenclatura", ["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"], key="v1")
with d_cols[1]: 
    n_1 = st.text_input("Número", key="n1")
with d_cols[2]: 
    l_1 = st.selectbox("Letra", ["-", "A", "B", "C", "D", "E"], key="l1")
with d_cols[3]: 
    ref_1 = st.selectbox("Referencia", ["-", "Bis", "Sur", "Este"], key="r1")
with d_cols[4]: 
    st.markdown("<h3 style='text-align:center; margin-top:20px;'>#</h3>", unsafe_allow_html=True)
with d_cols[5]: 
    n_2 = st.text_input("Número ", key="n2")
with d_cols[6]: 
    l_2 = st.selectbox("Letra ", ["-", "A", "B", "C", "D", "E"], key="l2")
with d_cols[7]: 
    n_3 = st.text_input("Número  ", key="n3")
with d_cols[8]: 
    ref_2 = st.selectbox("Referencia ", ["-", "Bis", "Sur", "Este"], key="r2")
with d_cols[9]: 
    apto = st.text_input("Adicional", placeholder="Apto 201", key="apto")

l1_v = "" if l_1 == "-" else l_1
r1_v = "" if ref_1 == "-" else ref_1
l2_v = "" if l_2 == "-" else l_2
r2_v = "" if ref_2 == "-" else ref_2

direccion_generada = f"{via} {n_1}{l1_v} {r1_v} # {n_2}{l2_v} - {n_3} {r2_v} {apto}".replace("  ", " ").strip()
st.text_input("Dirección que será registrada (Verificación Visual)*", value=direccion_generada, disabled=True)

# LAS DOS CASILLAS FUNDAMENTALES (DEPARTAMENTO Y MUNICIPIO)
col_dep, col_mun = st.columns(2)
lista_departamentos = [d['departamento'] for d in datos_colombia]
with col_dep:
    dep_sel = st.selectbox("Departamento*", ["Seleccione..."] + lista_departamentos, key="dep_sel")

with col_mun:
    municipios = []
    if dep_sel != "Seleccione...":
        municipios = next(d['ciudades'] for d in datos_colombia if d['departamento'] == dep_sel)
    mun_sel = st.selectbox("Municipio / Ciudad*", ["Seleccione..."] + municipios, key="mun_sel")

# --- 3. CONTACTO ---
st.markdown("## Contacto")
c_col1, c_col2 = st.columns(2)
celular = c_col1.text_input("Número de Celular Móvil*", key="cel")
es_wa = c_col2.radio("¿Es el mismo número para WhatsApp?*", ["Sí", "No"], horizontal=True, key="wa_check")
wa_final = celular
if es_wa == "No": wa_final = st.text_input("Número de WhatsApp específico*", key="wa_esp")

st.markdown("## Situación Laboral")

situacion_laboral = st.radio(
    "Seleccione su situación laboral*",
    ["Empleado", "Pensionado", "Independiente"],
    horizontal=True,
    key="sit_laboral"
)

empresa_pagador = ""
actividad_economica = ""

if situacion_laboral == "Empleado":
    empresa_pagador = st.text_input("Nombre de la empresa / Pagador*", key="empresa_pagador").upper()

elif situacion_laboral == "Pensionado":
    empresa_pagador = st.text_input("Entidad pagadora de la pensión*", key="entidad_pension").upper()

elif situacion_laboral == "Independiente":
    actividad_economica = st.text_input("Actividad económica*", key="actividad_economica").upper()
    
    st.markdown("## ¿Cómo nos conoció?")

origen_cliente = st.radio(
    "Seleccione una opción*",
    [
        "Recomendación / Boca a boca",
        "Referido por Colega",
        "Redes Sociales - Instagram",
        "Redes Sociales - Facebook",
        "Redes Sociales - Tik-Tok",
        "Búsqueda en Google / Web",
        "Cliente Recurrente"
    ],
    horizontal=False,
    key="origen_cliente"
)

# -------------------------------
# 4. INFORMACIÓN DE LA CONTRAPARTE
# -------------------------------
st.markdown("## 4. Información de la Contraparte")

# 🔴 OPCIONES 2 Y 4 → CASO EN CURSO
if rol in ["2", "4"]:

    # Nombre cambia según rol
    if rol == "2":
        label = "Nombre de la persona o entidad a quien demanda*"
    else:
        label = "Nombre de la persona o entidad que lo está demandando*"

    nombre_contraparte = st.text_input(label, key="contraparte_nombre")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Despacho judicial donde cursa el proceso*",
            key="juzgado"
        )

    with col2:
         radicado_input = st.text_input(
        "Número de radicado (23 dígitos)*",
        max_chars=23,
        key="radicado"
    )

    error_radicado = False

    if radicado_input:
        longitud = len(radicado_input)

        st.caption(f"{longitud} / 23 dígitos")

        if not radicado_input.isdigit():
            st.error("❌ El radicado solo debe contener números")
            error_radicado = True

        elif longitud != 23:
            st.error("❌ El número de radicado debe tener exactamente 23 dígitos")
            error_radicado = True

        else:
            st.success("✅ Radicado válido")

# 🟢 OPCIONES 1, 3 Y 5 → CASO NUEVO
else:

    label = ""

    if rol == "1":
        label = "Nombre de la persona o entidad a la que va a demandar*"
    elif rol == "3":
        label = "Nombre de la persona o entidad que lo demanda*"
    elif rol == "5":
        label = "Entidad ante la cual se va a iniciar el trámite administrativo*"

    if label:
        st.text_input(label, key="contraparte_nombre")


# ---------------------------------------
# 🔎 RELATO DEL CASO (OBLIGATORIO)
# ---------------------------------------

st.markdown("## 🧾 Relato del Caso (Requerido para estudio)")

tipo_relato = st.radio(
    "¿Cómo desea describir su caso?",
    ["✍️ Escribir relato", "🎤 Grabar o subir audio"]
)

# -------------------------------
# OPCIÓN 1: TEXTO
# -------------------------------
if tipo_relato == "✍️ Escribir relato":

    relato_texto = st.text_area(
        "Describa detalladamente su situación",
        height=200,
        placeholder="Explique los hechos relevantes de su caso, fechas, personas involucradas, situación actual, etc."
    )

# -------------------------------
# OPCIÓN 2: AUDIO
# -------------------------------
elif tipo_relato == "🎤 Grabar o subir audio":

    relato_audio = st.file_uploader(
        "Suba un audio explicando su caso",
        type=["mp3", "wav", "m4a"]
    )

    st.info("Puede grabar el audio desde su celular o computador y cargarlo aquí.")

# -------------------------------
# VALIDACIÓN (PRO)
# -------------------------------
if tipo_relato == "✍️ Escribir relato" and not relato_texto:
    st.warning("⚠️ Debe ingresar el relato del caso para continuar")

if tipo_relato == "🎤 Grabar o subir audio" and not relato_audio:
    st.warning("⚠️ Debe cargar un audio con la descripción del caso")

# -----------------------------------
# BLOQUE DINÁMICO CONTRAPARTE
# -----------------------------------
if rol not in ["2", "4"]:

    conoce_doc = st.radio("¿Conoce la cédula o NIT?", ["No", "Sí"])
    if conoce_doc == "Sí":
        st.text_input("Número de documento")

    conoce_emp = st.radio("¿Conoce la empresa?", ["No", "Sí"])
    if conoce_emp == "Sí":
        st.text_input("Empresa")

    conoce_email = st.radio("¿Conoce el correo?", ["No", "Sí"])
    if conoce_email == "Sí":
        st.text_input("Correo")

    conoce_direccion = st.radio("¿Conoce la dirección?", ["No", "Sí"])

    if conoce_direccion == "Sí":
       st.markdown("### Dirección de la Contraparte")

       d_cols_c = st.columns([1.3, 0.8, 0.8, 1, 0.4, 0.8, 0.8, 0.8, 1, 1.2])

       with d_cols_c[0]:
           via_c = st.selectbox("Nomenclatura", ["Calle", "Carrera", "Diagonal", "Transversal", "Avenida"], key="v1_cont")
       with d_cols_c[1]:
           n_1c = st.text_input("Número", key="n1_cont")
       with d_cols_c[2]:
           l_1c = st.selectbox("Letra", ["-", "A", "B", "C", "D", "E"], key="l1_cont")
       with d_cols_c[3]:
           ref_1c = st.selectbox("Referencia", ["-", "Bis", "Sur", "Este"], key="r1_cont")
       with d_cols_c[4]:
           st.markdown("<h3 style='text-align:center; margin-top:20px;'>#</h3>", unsafe_allow_html=True)
       with d_cols_c[5]:
           n_2c = st.text_input("Número ", key="n2_cont")
       with d_cols_c[6]:
           l_2c = st.selectbox("Letra ", ["-", "A", "B", "C", "D", "E"], key="l2_cont")
       with d_cols_c[7]:
           n_3c = st.text_input("Número  ", key="n3_cont")
       with d_cols_c[8]:
           ref_2c = st.selectbox("Referencia ", ["-", "Bis", "Sur", "Este"], key="r2_cont")
       with d_cols_c[9]:
           apto_c = st.text_input("Adicional", placeholder="Apto 201", key="apto_cont")

       l1_vc = "" if l_1c == "-" else l_1c
       r1_vc = "" if ref_1c == "-" else ref_1c
       l2_vc = "" if l_2c == "-" else l_2c
       r2_vc = "" if ref_2c == "-" else ref_2c

       direccion_generada_c = f"{via_c} {n_1c}{l1_vc} {r1_vc} # {n_2c}{l2_vc} - {n_3c} {r2_vc} {apto_c}".replace("  ", " ").strip()

       st.text_input("Verificación Dirección*", value=direccion_generada_c, disabled=True)

    # Departamento y municipio
       c_dep, c_mun = st.columns(2)
       lista_deps = [d['departamento'] for d in datos_colombia]

       with c_dep:
           dep_cont = st.selectbox("Departamento*", ["Seleccione..."] + lista_deps, key="dep_c")

       with c_mun:
           muns_cont = []
           if dep_cont != "Seleccione...":
               muns_cont = next(d['ciudades'] for d in datos_colombia if d['departamento'] == dep_cont)

           mun_cont = st.selectbox("Municipio / Ciudad*", ["Seleccione..."] + muns_cont, key="mun_c")

           direccion_cont_final = direccion_generada_c

# --- FUNCIÓN LIMPIA DE RADICADO ---
def generar_radicado_sfd(db, rol):

    if rol == "1":
        sufijo = "DTE"
    elif rol == "3":
        sufijo = "DDO"
    else:
        sufijo = "TRA"

    # 🔥 Buscar último radicado en la BD
    ultimo = db.query(Proceso).order_by(Proceso.id.desc()).first()

    if ultimo and ultimo.numero_rama:
        try:
            consecutivo = int(ultimo.numero_rama.split("-")[-1]) + 1
        except:
            consecutivo = 1
    else:
        consecutivo = 1

    consecutivo_str = str(consecutivo).zfill(5)

    return f"SFD-2026-{sufijo}-{consecutivo_str}"


# --- BOTÓN FINAL CORRECTO ---
st.markdown("---")

if st.button("REGISTRAR INFORMACIÓN Y GENERAR RADICADO"):

    db = SessionLocal()

    try:
        # 👇 TODO tu código aquí (SIN CAMBIARLO)

        nombre_contraparte_val = st.session_state.get("contraparte_nombre", "")

        if (
            nombre != ""
            and not error_email
            and nombre_contraparte_val != ""
            and (rol not in ["2", "4"] or not error_radicado)
        ):

            empresa = db.query(Empresa).filter(Empresa.nombre == "SFD Gestión Jurídica").first()

            if not empresa:
                empresa = Empresa(nombre="SFD Gestión Jurídica", nit="900000000")
                db.add(empresa)
                db.commit()
                db.refresh(empresa)

            nuevo_cliente = Cliente(
                empresa_id=empresa.id,
                nombre=nombre,
                documento=doc_raw,
                correo=email,
                celular=celular,
                direccion=direccion_generada
            )

            db.add(nuevo_cliente)
            db.commit()
            db.refresh(nuevo_cliente)

            radicado_final = generar_radicado_sfd(db, rol)

            if not radicado_final:
              st.error("❌ Error generando el radicado")
              st.stop()

            ruta_base = "uploads/CLIENTES"
            ruta_cliente = os.path.join(ruta_base, str(radicado_final))
            os.makedirs(ruta_cliente, exist_ok=True)

            nuevo_proceso = Proceso(
                empresa_id=empresa.id,
                cliente_id=nuevo_cliente.id,
                jurisdiccion="Pendiente",
                tipo_proceso="Pendiente",
                numero_rama=radicado_final,
                juzgado="Pendiente",
                ciudad="Pendiente",
                estado_actual="Activo"
            )

            db.add(nuevo_proceso)
            db.commit()

            st.success(f"📁 Radicado generado: {radicado_final}")

            # 🔗 Generar link formulario 2
            link_formulario2 = generar_link_formulario2(radicado_final)

            st.markdown("### 🎉 Bienvenido a SFD Gestión Jurídica")

            st.success("""
            Su información ha sido registrada correctamente.

            Para continuar con la validación de su caso, le solicitamos acceder al siguiente link para el procedimiento de cargar los documentos correspondientes.
            """)

            st.info(f"👉 Continúe aquí: {link_formulario2}")


        else:
            st.error("⚠️ Verifica que todos los campos estén completos y correctos")

    except Exception as e:
        db.rollback()
        st.error(f"❌ Error: {e}")

    finally:
        db.close()

# -----------------------
# 🔥 SCROLL GLOBAL (AL FINAL REAL)
# -----------------------
if "paso" in st.session_state:
    if st.session_state.paso == 1:
        scroll_to("paso1")
    elif st.session_state.paso == 2:
        scroll_to("paso2")
    elif st.session_state.paso == 3:
        scroll_to("paso3")
    elif st.session_state.paso == 4:
        scroll_to("paso4")


