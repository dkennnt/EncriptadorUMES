import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Encriptador UMES", layout="wide")

st.title("Encriptador UMES")

# CONFIGURACIÓN DEL ALFABETO
alfabeto_lista = list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ_")

if 'mapeo' not in st.session_state:
    st.session_state.mapeo = {c: i+1 for i, c in enumerate(alfabeto_lista)}

st.header("1. Definición del Abecedario")
with st.expander("Configurar Mapeo de Letras"):
    cols = st.columns(7)
    temp_mapeo = {}
    duplicado = False
    valor_duplicado = None

    for i, char in enumerate(alfabeto_lista):
        with cols[i % 7]:
            # Quitamos el max_value para permitir cualquier número
            val = st.number_input(f"'{char}'", min_value=0, 
                                  value=st.session_state.mapeo[char], 
                                  key=f"input_{char}")
            
            # Verificación de duplicados en tiempo real
            if val in temp_mapeo.values():
                duplicado = True
                valor_duplicado = val
            temp_mapeo[char] = val

    if duplicado:
        st.error(f"❌ Error: El número **{valor_duplicado}** ya está asignado a otra letra. Por favor, usa valores únicos.")
        # No actualizamos el session_state si hay error
    else:
        st.session_state.mapeo = temp_mapeo
        st.success("✅ Alfabeto validado: Todos los valores son únicos.")

#CONFIGURACIÓN DE LA MATRIZ
st.header("2. Matriz Encriptadora (K)")
dim = st.number_input("Dimensión de la matriz (n x n):", 2, 6, 3)

m_vals = []
st.write(f"Ingresa los valores de tu matriz de {dim}x{dim}:")
cols_mat = st.columns(dim)
for i in range(dim):
    row = []
    for j in range(dim):
        with cols_mat[j]:
            val = st.number_input(f"M[{i+1},{j+1}]", value=1 if i==j else 0, key=f"mat_{i}_{j}")
            row.append(val)
    m_vals.append(row)
matriz_k = np.array(m_vals)

#PROCESAMIENTO
st.divider()

# Solo procedemos si no hay duplicados en el alfabeto
if not duplicado:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🔒 Encriptar")
        msg_in = st.text_input("Texto para encriptar:").upper()
        if msg_in:
            msg_in = msg_in.replace(" ", "_")
            while len(msg_in) % dim != 0: msg_in += "_"
            
            indices = [st.session_state.mapeo.get(c, 0) for c in msg_in]
            bloques = [indices[i:i+dim] for i in range(0, len(indices), dim)]
            
            resultado_nums = []
            for b in bloques:
                res = np.dot(matriz_k, np.array(b))
                resultado_nums.extend(res)
                
            st.write("**Números resultantes:**")
            st.code(", ".join(map(str, np.round(resultado_nums, 2))))

    with col_right:
        st.subheader("🔓 Desencriptar")
        nums_in = st.text_input("Pega los números (separados por coma):")
        if nums_in:
            try:
                nums_list = [float(x.strip()) for x in nums_in.split(",")]
                bloques_enc = [nums_list[i:i+dim] for i in range(0, len(nums_list), dim)]
                
                m_inv = np.linalg.inv(matriz_k)
                mapeo_inv = {v: k for k, v in st.session_state.mapeo.items()}
                
                texto_final = ""
                detalles_pasos = []
                
                for b in bloques_enc:
                    res_orig = np.dot(m_inv, np.array(b))
                    res_final = np.round(res_orig).astype(int)
                    
                    letras_bloque = [mapeo_inv.get(n, "?") for n in res_final]
                    texto_final += "".join(letras_bloque)
                    detalles_pasos.append({"vector_c": b, "vector_p": res_final, "letras": letras_bloque})
                
                st.write("**Texto recuperado:**")
                st.success(texto_final)

                with st.expander("🔍 Ver proceso técnico de desencriptación"):
                    st.write("### 1. Matriz Inversa ($K^{-1}$)")
                    m_inv_visual = np.where(np.abs(m_inv) < 1e-9, 0, m_inv)
                    st.dataframe(pd.DataFrame(m_inv_visual))
                    
                    st.write("### 2. Multiplicación de Matrices")
                    st.latex(r"P = K^{-1} \cdot C")
                    for idx, p in enumerate(detalles_pasos):
                        st.write(f"**Bloque {idx+1}:**")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("Vector C (Cifrado):")
                            st.text(p['vector_c'])
                        with c2:
                            st.write("Vector P (Original):")
                            st.text(p['vector_p'])
                            st.write(f"Letras: {' - '.join(p['letras'])}")
                        st.divider()
                        
            except np.linalg.LinAlgError:
                st.error("La matriz no es invertible (Det=0).")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("⚠️ El procesamiento está bloqueado hasta que corrijas los números repetidos en el abecedario.")

st.write(f"""
         
         
         Hecho por: Marcos Cruz 202325501 - Katherine Archila 202325508. 
         
         Puntos y derechos reservados :D.
         
         
         """)