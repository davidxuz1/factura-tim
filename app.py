import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

st.title("Generador de Facturas")

# Datos del encabezado
col1, col2 = st.columns(2)
cliente = col1.text_input("Empresa Cliente", "Cliente Ejemplo")
fecha = col2.date_input("Fecha de la factura", datetime.date.today())

st.write("Añade filas haciendo clic en el botón '+' al final de la tabla. Rellena los datos manualmente.")

# Inicializar la tabla en memoria
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "CODIGO": [""], "TALLA": [""], "UNIDAD": [0], "CAJA": [0], "PRECIO": [0.0]
    })

# Tabla interactiva dinámica
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)
st.session_state.df = edited_df

# Cálculos
df_calc = edited_df.copy()
df_calc.fillna({'UNIDAD': 0, 'CAJA': 0, 'PRECIO': 0}, inplace=True)
df_calc['CANTIDAD'] = df_calc['CAJA'] * df_calc['UNIDAD']
df_calc['SUBTOTAL'] = df_calc['CANTIDAD'] * df_calc['PRECIO']

# Fila final EUROTRAN
total_cajas = df_calc['CAJA'].sum()
total_subtotal = df_calc['SUBTOTAL'].sum()

fila_total = pd.DataFrame([{
    "CODIGO": "EUROTRAN", "TALLA": "", "UNIDAD": "", "CAJA": total_cajas,
    "CANTIDAD": "", "PRECIO": "", "SUBTOTAL": total_subtotal
}])

# Mostrar resumen
st.subheader("Resumen Calculado")
df_final = pd.concat([df_calc, fila_total], ignore_index=True)
st.dataframe(df_final, use_container_width=True, hide_index=True)

# Lógica de PDF
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "FACTURA", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, f"Cliente: {cliente}", ln=True)
    pdf.cell(0, 10, f"Fecha: {fecha.strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)

    with pdf.table(text_align="CENTER") as table:
        cabecera = table.row()
        for col in ["CODIGO", "TALLA", "UNIDAD", "CAJA", "CANTIDAD", "PRECIO", "SUBTOTAL"]:
            cabecera.cell(col)
        
        for _, fila in df_final.iterrows():
            row = table.row()
            row.cell(str(fila["CODIGO"]))
            row.cell(str(fila["TALLA"]))
            row.cell(str(fila["UNIDAD"]))
            row.cell(str(fila["CAJA"]))
            row.cell(str(fila["CANTIDAD"]))
            row.cell(f"{fila['PRECIO']:.2f}" if fila['PRECIO'] != "" else "")
            row.cell(f"{fila['SUBTOTAL']:.2f}" if fila['SUBTOTAL'] != "" else "")
            
    return bytes(pdf.output())

# Botón de exportación
st.download_button(
    label="📄 Exportar a PDF",
    data=generar_pdf(),
    file_name=f"Factura_{cliente}.pdf",
    mime="application/pdf"
)