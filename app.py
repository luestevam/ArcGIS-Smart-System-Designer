import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ArcGIS System Designer Web", layout="wide")

# --- ESTADO INICIAL ---
def init_state():
    if 'project' not in st.session_state:
        st.session_state.project = {
            "name": "", "client": "", "architect": "", "version": "11.1", "notes": ""
        }
    if 'workload' not in st.session_state:
        st.session_state.workload = {
            "registered": 1000, "concurrent_peak": 100, "peak_factor": 1.1,
            "dist": {"View-only": 70, "Editors": 15, "Utility Network": 5, "Raster/AI": 5, "Real-time": 5}
        }
    if 'servers' not in st.session_state:
        st.session_state.servers = []
    if 'catalog' not in st.session_state:
        st.session_state.catalog = None

# --- CONSTANTES DE ROLE ---
ROLES = {
    "Portal for ArcGIS": ["Portal", "Web Adaptor"],
    "ArcGIS Server (Hosting)": ["GIS Server", "Web Adaptor"],
    "ArcGIS Server (Federated)": ["GIS Server"],
    "ArcGIS Data Store": ["Data Store"],
    "ArcGIS Image Server": ["Image Server"],
    "ArcGIS Utility Network Server": ["GIS Server (UN)", "Utility Network Role"],
    "ArcGIS GeoEvent Server": ["GeoEvent Server"],
    "ArcGIS Monitor": ["ArcGIS Monitor Server"]
}

DS_SUBTYPES = ["Relational", "Tile Cache", "Object Store", "Spatiotemporal"]

# --- OPERAÇÕES PADRÃO POR ROLE ---
ROLE_DEFAULT_OPS = {
    "Portal for ArcGIS": ["Portal Login/Search", "Web Map Open", "Item Management"],
    "ArcGIS Server (Hosting)": ["Map Draw (Dynamic)", "Feature Query", "Feature Edit"],
    "ArcGIS Data Store": ["Database Transaction", "Search Indexing"],
    "ArcGIS Image Server": ["Raster Analysis", "Dynamic Image Export"],
    "ArcGIS Utility Network Server": ["UN Trace", "UN Validate Topology", "UN Feature Edit"],
    "ArcGIS GeoEvent Server": ["EPS Ingest", "Event Processing", "Stream Output"],
    "ArcGIS Monitor": ["Metric Collection", "Health Check Scrape"]
}

# --- LOGICA DE IA PARA CUSTOM OPS ---
def ia_model_suggestion(desc):
    desc = desc.lower()
    if "detecc" in desc or "raster" in desc: return "Image Service (Deep Learning)"
    if "edit" in desc or "campo" in desc: return "Feature Service (Editing)"
    if "gps" in desc or "tracking" in desc: return "GeoEvent (Real-time)"
    return "Map Service (Dynamic)"

# --- COMPONENTE DE CARREGAMENTO DE CATÁLOGO ---
def ui_catalog_manager():
    st.sidebar.header("📂 Catálogo System Designer")
    uploaded_file = st.sidebar.file_uploader("Upload Models (CSV/XLSX)", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Filtro rigoroso System Designer
            if 'Group' in df.columns and 'Release' in df.columns:
                df = df[df['Group'] == 'SD']
                st.session_state.catalog = df
                st.sidebar.success(f"Catálogo carregado: {len(df)} modelos.")
            else:
                st.sidebar.error("Formato de colunas inválido.")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler arquivo: {e}")

# --- TAB: PROJETO ---
def ui_project():
    st.header("📋 Dados do Projeto")
    c1, c2, c3 = st.columns(3)
    p = st.session_state.project
    p['name'] = c1.text_input("Nome do Projeto", p['name'])
    p['client'] = c2.text_input("Cliente", p['client'])
    p['architect'] = c3.text_input("Arquiteto", p['architect'])
    
    p['version'] = st.selectbox("ArcGIS Enterprise Version", ["11.2", "11.1", "10.9.1", "10.8.1"], index=1)
    p['notes'] = st.text_area("Observações e Premissas Estratégicas")

# --- TAB: WORKLOAD ---
def ui_workload():
    st.header("🚦 Modelagem de Workload")
    w = st.session_state.workload
    
    c1, c2, c3 = st.columns(3)
    w['registered'] = c1.number_input("Total Usuários Cadastrados", 1, 100000, w['registered'])
    w['concurrent_peak'] = c2.number_input("Usuários Simultâneos (Pico)", 1, 10000, w['concurrent_peak'])
    w['peak_factor'] = c3.slider("Peak Factor (Sazonalidade)", 1.0, 2.0, w['peak_factor'], 0.1)

    st.subheader("Distribuição de Perfis (%)")
    cd = st.columns(5)
    w['dist']['View-only'] = cd[0].number_input("Viewers", 0, 100, w['dist']['View-only'])
    w['dist']['Editors'] = cd[1].number_input("Editors", 0, 100, w['dist']['Editors'])
    w['dist']['Utility Network'] = cd[2].number_input("UN Users", 0, 100, w['dist']['Utility Network'])
    w['dist']['Raster/AI'] = cd[3].number_input("Image/AI", 0, 100, w['dist']['Raster/AI'])
    w['dist']['Real-time'] = cd[4].number_input("Real-time", 0, 100, w['dist']['Real-time'])

    total = sum(w['dist'].values())
    if total != 100:
        st.warning(f"Total: {total}%. Ajuste para 100% para cálculos precisos.")

# --- TAB: SERVIDORES ---
def ui_servers():
    st.header("🖥️ Hardware Plan (Server Roles)")
    
    with st.expander("➕ Adicionar Novo Servidor"):
        with st.form("add_server"):
            name = st.text_input("Nome do Servidor", "VM-GIS-PRD-01")
            c1, c2, c3 = st.columns(3)
            cpu = c1.number_input("vCPU (Cores)", 2, 128, 8)
            ram = c2.number_input("RAM (GB)", 4, 1024, 32)
            disk = c3.selectbox("Tipo de Disco", ["NVMe", "SSD", "HDD"])
            
            role = st.selectbox("ArcGIS Server Role", list(ROLES.keys()))
            subtype = ""
            if role == "ArcGIS Data Store":
                subtype = st.selectbox("Subtipo Data Store", DS_SUBTYPES)
            
            if st.form_submit_button("Registrar Servidor"):
                st.session_state.servers.append({
                    "name": name, "cpu": cpu, "ram": ram, "disk": disk, 
                    "role": role, "subtype": subtype, "ops": []
                })
                st.rerun()

    for i, s in enumerate(st.session_state.servers):
        with st.container(border=True):
            col_info, col_act = st.columns([4, 1])
            col_info.markdown(f"**{s['name']}** | {s['role']} {f'({s[u'subtype']})' if s[u'subtype'] else ''}")
            col_info.caption(f"Hardware: {s['cpu']} vCPU, {s['ram']}GB RAM, Disco {s['disk']} | Componentes: {', '.join(ROLES[s['role']])}")
            
            # Alertas de Boas Práticas
            if s['disk'] == "HDD" and s['role'] in ["ArcGIS Data Store", "ArcGIS Image Server", "ArcGIS Utility Network Server"]:
                st.error("🚨 Alerta: HDD detectado. Papéis de alta carga de I/O exigem SSD/NVMe.")
            
            if col_act.button("Remover", key=f"del_{i}"):
                st.session_state.servers.pop(i)
                st.rerun()

# --- TAB: CAPACITY MODEL ---
def ui_capacity():
    st.header("📊 Capacity Model & Model Assignment")
    if not st.session_state.servers:
        st.info("Adicione servidores para iniciar a atribuição de modelos.")
        return

    cat = st.session_state.catalog
    version = st.session_state.project['version']

    for s_idx, s in enumerate(st.session_state.servers):
        st.subheader(f"⚙️ Configuração de Operações: {s['name']}")
        
        # Botão para Gerar Operações Automáticas
        if st.button(f"Gerar Operações Macro para {s['role']}", key=f"gen_btn_{s_idx}"):
            for op_name in ROLE_DEFAULT_OPS.get(s['role'], []):
                s['ops'].append({"name": op_name, "model": "Select Model...", "users": 10, "is_custom": False})
            st.rerun()

        # Renderização das Operações existentes
        for o_idx, op in enumerate(s['ops']):
            c = st.columns([3, 3, 1, 1])
            # Adicionado key única combinando índice do servidor e da operação
            c[0].text_input("Operação", op['name'], key=f"op_name_{s_idx}_{o_idx}")
            
            if cat is not None:
                model_list = cat[cat['Release'].astype(str).str.contains(version)]['Model Name'].tolist()
                op['model'] = c[1].selectbox("Model Name (Catalog)", ["Select Model..."] + model_list, key=f"op_model_{s_idx}_{o_idx}")
            else:
                op['model'] = c[1].text_input("Model Name (Manual)", op['model'], key=f"op_model_man_{s_idx}_{o_idx}")
            
            op['users'] = c[2].number_input("Usuários", 0, 10000, op['users'], key=f"op_users_{s_idx}_{o_idx}")
            if c[3].button("🗑️", key=f"op_del_btn_{s_idx}_{o_idx}"):
                s['ops'].pop(o_idx)
                st.rerun()
        
        # Operação Custom com IA - CORREÇÃO DO ERRO DO PRINT
        with st.popover("➕ Adicionar Operação Custom (IA Suggestion)"):
            # Aqui adicionamos a key para diferenciar o campo de texto entre servidores
            desc_custom = st.text_input("Descreva a tarefa personalizada", key=f"input_custom_{s_idx}")
            if st.button("Sugerir Modelo", key=f"ia_suggest_btn_{s_idx}"):
                if desc_custom:
                    sug = ia_model_suggestion(desc_custom)
                    s['ops'].append({"name": f"Custom: {desc_custom[:20]}", "model": sug, "users": 5, "is_custom": True})
                    st.rerun()
                else:
                    st.warning("Descreva a tarefa primeiro.")
        st.divider()

# --- TAB: LICENCIAMENTO ---
def ui_licensing():
    st.header("🔑 Estimativa de Licenciamento")
    st.warning("⚠️ Disclaimer: Este cálculo é uma estimativa técnica de capacidade. Consulte seu representante Esri para cotações oficiais.")
    
    total_cores_server = 0
    for s in st.session_state.servers:
        if "Server" in s['role'] or "Image" in s['role']:
            total_cores_server += s['cpu']
    
    st.metric("Total vCPU para Licenciamento (GIS/Image Server)", total_cores_server)
    st.info(f"Regra Sugerida (Version {st.session_state.project['version']}): Licenciamento baseado em núcleos físicos ou vCPUs em ambiente virtualizado.")

# --- PDF GENERATOR ---
def build_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Relatorio ArcGIS System Designer Web", ln=True, align='C')
    
    pdf.set_font("Arial", "", 10)
    p = st.session_state.project
    pdf.cell(190, 7, f"Projeto: {p['name']} | Cliente: {p['client']} | Versao: {p['version']}", ln=True)
    pdf.cell(190, 7, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    
    for s in st.session_state.servers:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 8, f"SERVIDOR: {s['name']} | ROLE: {s['role']}", ln=True, fill=True, border=1)
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 6, f"Hardware: {s['cpu']} vCPU, {s['ram']}GB RAM, Disco {s['disk']}", ln=True, border='LR')
        
        for op in s['ops']:
            pdf.cell(190, 6, f"- Op: {op['name']} | Model: {op['model']} | Users: {op['users']}", ln=True, border='LR')
        pdf.cell(190, 1, "", ln=True, border='T')
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- MAIN ---
def main():
    init_state()
    st.title("🏗️ ArcGIS Smart System Designer v2026")
    
    ui_catalog_manager()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Projeto", "🚦 Workload", "🖥️ Servidores", "📊 Capacity Model", "🔑 Licenciamento"
    ])
    
    with tab1: ui_project()
    with tab2: ui_workload()
    with tab3: ui_servers()
    with tab4: ui_capacity()
    with tab5: 
        ui_licensing()
        if st.session_state.servers:
            pdf_bytes = build_pdf()
            st.download_button("📥 Baixar Relatório Técnico (PDF)", pdf_bytes, "System_Design_ArcGIS.pdf", "application/pdf")

if __name__ == "__main__":
    main()