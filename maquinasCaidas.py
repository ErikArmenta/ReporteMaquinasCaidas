# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 06:07:42 2026

@author: acer
"""



import streamlit as st
from supabase import create_client
from datetime import datetime, timezone, timedelta
import pandas as pd

# 1. Configuración de página y Estilo "Estilo Perrote"
st.set_page_config(page_title="Andon Monitor System", layout="wide", page_icon="🏭")

# CSS Mejorado: Diseño Industrial Premium con Glow Animation
st.markdown("""
    <style>
    .main { background-color: #0d1117; }

    /* Tabs Estilizados */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #161b22;
        border-radius: 8px 8px 0px 0px;
        color: #8b949e;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636;
        color: white !important;
        font-weight: bold;
    }

    /* Card Premium con Glow */
    .glow-card {
        animation: glow-animation 2.5s infinite;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.3) 100%);
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    @keyframes glow-animation {
        0% { box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); border-color: rgba(255,255,255,0.1); }
        50% { box-shadow: 0 0 25px var(--glow-color); border-color: var(--glow-color); }
        100% { box-shadow: 0 0 5px rgba(0, 0, 0, 0.2); border-color: rgba(255,255,255,0.1); }
    }

    .footer-text {
        text-align: center;
        color: #484f58;
        padding: 30px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Conexión a Supabase
url = st.secrets["supa_secrets"]["SUPABASE_URL"]
key = st.secrets["supa_secrets"]["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- HEADER ---
c_logo, c_title = st.columns([1, 5])
with c_logo:
    try:
        st.image("EA_2.png", width=140)
    except:
        st.write("### EA INNOVATION")

with c_title:
    st.title("Andon Monitor System")
    st.caption("Developed by Master Engineer Erik Armenta | Industry 4.0 Solutions")

# --- FUNCIONES DE LOGICA ---
def get_status_color(minutos):
    if minutos < 30:
        return "rgba(35, 134, 54, 0.7)", "#ffffff", "🟢", False, ""
    elif minutos < 120:
        return "rgba(210, 153, 34, 0.7)", "#000000", "🟡", True, "#d29922"
    else:
        return "rgba(248, 81, 73, 0.7)", "#ffffff", "🔴", True, "#f85149"

# --- TABS PRINCIPALES ---
tab_dash, tab_form, tab_hist = st.tabs(["📊 DASHBOARD EN VIVO", "🚨 REPORTE DE CAÍDA", "📜 HISTORIAL DE PLANTA"])

# --- PESTAÑA 1: DASHBOARD CON FILTRO ---
with tab_dash:
    # Obtener todas las máquinas caídas
    res = supabase.table("maquinascaidas").select("*").eq("estado", "Caída").order("created_at", desc=True).execute()
    data_all = res.data

    if data_all:
        # --- NUEVO: FILTRO POR ÁREA ---
        areas_disponibles = sorted(list(set([m['area'] for m in data_all if m['area']])))
        area_seleccionada = st.selectbox("🔍 Filtrar por Área:", ["TODAS"] + areas_disponibles)

        if area_seleccionada == "TODAS":
            maquinas_filtradas = data_all
        else:
            maquinas_filtradas = [m for m in data_all if m['area'] == area_seleccionada]

        st.markdown(f"**Mostrando {len(maquinas_filtradas)} máquinas en paro**")

        # Grid de Cards
        cols = st.columns(3)
        for i, m in enumerate(maquinas_filtradas):
            # Lógica de tiempo: Usar la fecha real de la BD
            raw_date = m.get('created_at')
            if raw_date:
                # Convertimos a Pandas Timestamp forzando UTC y luego a objeto datetime nativo
                inicio_dt = pd.to_datetime(raw_date, utc=True).to_pydatetime()
            else:
                inicio_dt = datetime.now(timezone.utc)

            # Formatear la hora de inicio para mostrar en la card
            # Usamos inicio_dt que ya es un objeto datetime de Python seguro
            fmt_inicio = inicio_dt.strftime("%I:%M %p | %d-%b")

            # Calcular diferencia contra el tiempo actual en UTC
            ahora = datetime.now(timezone.utc)
            diff = ahora - inicio_dt
            minutos = int(diff.total_seconds() / 60)

            # Evitar negativos por desajustes mínimos
            if minutos < 0: minutos = 0

            bg, txt, icon, glow, glow_color = get_status_color(minutos)
            notas_raw = m.get('notas_seguimiento') if m.get('notas_seguimiento') else "Sin comentarios en bitácora."

            glow_class = "glow-card"
            glow_style = f"--glow-color: {glow_color};" if glow else "--glow-color: transparent;"

            with cols[i % 3]:
                st.markdown(f"""
                    <div class="{glow_class}" style="background-color:{bg}; color:{txt}; {glow_style}">
                        <div style="display: flex; justify-content: space-between; align-items: center; opacity: 0.8; font-size: 0.85em;">
                            <span>{m['area'].upper()}</span>
                            <span>{icon}</span>
                        </div>
                        <h2 style="margin: 10px 0; letter-spacing: -1px;">{m['nombre_maquina']}</h2>
                        <div style="background: rgba(0,0,0,0.25); padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 12px;">
                            <span style="font-size: 1.4em; font-family: monospace; font-weight: bold;">⏳ {minutos//60}h {minutos%60}m</span>
                            <br>
                            <span style="font-size: 0.85em; opacity: 0.9;">🕒 Inicio: {fmt_inicio}</span>
                        </div>
                        <p style="margin: 0; font-size: 0.95em;"><b>Falla:</b> {m['descripcion']}</p>
                        <p style="margin-top: 8px; font-size: 0.8em; opacity: 0.8;">🔧 {m['departamento']} | {m['responsable']}</p>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander("📝 Gestionar Bitácora / Reparación"):
                    nueva_nota = st.text_input("Agregar actualización:", key=f"note_{m['id']}")
                    c1, c2 = st.columns(2)

                    if c1.button("💾 Guardar Nota", key=f"btn_s_{m['id']}", use_container_width=True):
                        ts = datetime.now().strftime("%d/%m %H:%M")
                        full_notes = f"{notas_raw} \n [{ts}]: {nueva_nota}"
                        supabase.table("maquinascaidas").update({"notas_seguimiento": full_notes}).eq("id", m['id']).execute()
                        st.toast("Bitácora actualizada")
                        st.rerun()

                    if c2.button("✅ Reparada", key=f"btn_f_{m['id']}", type="primary", use_container_width=True):
                        supabase.table("maquinascaidas").update({
                            "estado": "Reparada",
                            "fecha_solucion": datetime.now(timezone.utc).isoformat()
                        }).eq("id", m['id']).execute()
                        st.rerun()

                    st.caption(f"**Historial:** {notas_raw}")
    else:
        st.success("🎉 Planta operando normalmente. No hay paros reportados.")

# --- PESTAÑA 2: REPORTE ---
with tab_form:
    st.subheader("📝 Registro de Incidencia")
    with st.form("form_registro", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            maquina = st.text_input("Máquina o Equipo")
            area = st.selectbox("Área de Piso", ["Fabricacion", "Final Assy", "Rotary", "Bending", "E. Final"])
            responsable = st.text_input("Responsable del reporte")

            st.write("---")
            st.markdown("🕒 **¿Cuándo ocurrió el paro?**")
            f_paro = st.date_input("Fecha", value=datetime.now())
            h_paro = st.time_input("Hora", value=datetime.now().time())

        with col_b:
            departamento = st.selectbox("Departamento Técnico", ["Prod Support", "Maintenance", "Quality", "Tooling"])
            descripcion = st.text_area("Descripción detallada de la falla", height=150)
            st.warning("Nota: Al usar una fecha anterior, el sistema calculará el tiempo acumulado correctamente.")

        if st.form_submit_button("🚨 REGISTRAR CAÍDA", use_container_width=True):
            # Combinamos fecha y hora manual
            dt_combined = datetime.combine(f_paro, h_paro).astimezone(timezone.utc)

            data_insert = {
                "nombre_maquina": maquina,
                "area": area,
                "responsable": responsable,
                "departamento": departamento,
                "descripcion": descripcion,
                "estado": "Caída",
                "created_at": dt_combined.isoformat() # Se envía la fecha retroactiva
            }
            supabase.table("maquinascaidas").insert(data_insert).execute()
            st.success(f"Reporte generado para {maquina}")
            st.rerun()

# --- PESTAÑA 3: HISTORIAL ---
with tab_hist:
    st.subheader("📜 Historial de Reparaciones")
    res_h = supabase.table("maquinascaidas").select("*").eq("estado", "Reparada").order("fecha_solucion", desc=True).execute()
    if res_h.data:
        df_h = pd.DataFrame(res_h.data)
        df_h['inicio'] = pd.to_datetime(df_h['created_at'])
        df_h['fin'] = pd.to_datetime(df_h['fecha_solucion'])
        df_h['Downtime (Hrs)'] = (df_h['fin'] - df_h['inicio']).dt.total_seconds() / 3600

        m_col1, m_col2 = st.columns(2)
        m_col1.metric("MTTR (Promedio Horas)", f"{df_h['Downtime (Hrs)'].mean():.2f}")
        m_col2.metric("Total Reparaciones", len(df_h))

        st.dataframe(df_h[['inicio', 'nombre_maquina', 'area', 'Downtime (Hrs)', 'responsable', 'descripcion']], use_container_width=True)
    else:
        st.info("No hay datos históricos disponibles.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"""
    <div class="footer-text">
        <p>Industrial Control Suite v2.0</p>
        <h3 style="color: #c9d1d9; margin-top: -10px;">Master Engineer Erik Armenta</h3>
        <p style="font-size: 0.8em; letter-spacing: 3px; color: #58a6ff;">EA INNOVATION</p>
    </div>
""", unsafe_allow_html=True)


