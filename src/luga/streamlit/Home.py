import streamlit as st
from pathlib import Path
import base64
import pandas
import altair as alt

from luga.engine import process


CURRENT_DIRECTORY = Path(__file__).parent
STATIC_DIR = CURRENT_DIRECTORY / "static"


def img_to_base64(img_path: Path) -> str:
    img_bytes = img_path.read_bytes()
    return base64.b64encode(img_bytes).decode()


def add_header():
    LOGO_PATH = STATIC_DIR / "logo.png"
    st.sidebar.image(str(LOGO_PATH))


def add_sidebar():
    with st.sidebar:
        add_header()


def set_page_config():
    st.set_page_config(
        page_title="Lugaresi", layout="wide", initial_sidebar_state="expanded",
        page_icon=str(STATIC_DIR / "favicon.ico"),
    )

def check_file(return_file, key: str):
    if return_file:
        if return_file.type not in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/csv"]:
            st.error(f"Il file deve essere un file Excel o CSV. Ricevuto: {return_file.type}")
            return
        try:
            dataframe = pandas.read_excel(return_file)
        except:
            try:
                dataframe = pandas.read_csv(return_file, ';', header=None)
            except:
                st.error("Errore. Non riesco ad aprire il file. Sicuro sia un excel o csv?")
        # Forza i nomi delle colonne
        columns_names = list(dataframe.columns)
        columns_names[0] = 'ID'
        columns_names[1] = 'Giacenze'
        dataframe.columns = columns_names
        # Cambia il data type
        dataframe['ID'] = dataframe['ID'].astype(str)
        # Forza la prima colonna come indice
        dataframe = dataframe.set_index('ID')
        # Ritorna solo indice e giacenza.
        return dataframe.iloc[:, :1]

    else:
        st.error(f"Devi selezionare un file con giacenze {key.upper()}")
        return

def add_giacenze_view(df: pandas.DataFrame):
    st.write(f"Prodotti: {len(df)}")
    st.write(f"Totale prodotti: {df['Giacenze'].sum()}")
    st.dataframe(df, use_container_width=True)

def add_compare_section():
    st.header("Calcolo differenza giacenze")
    st.markdown("""
    Selezionare i file excel/csv per eseguire la differenza.
    Entrambi i file devono contenere almeno due colonne:

    - id oggetto
    - giacenza
    """)

    with st.form(key="form_compare", clear_on_submit=False):
        total_column, robot_column = st.columns(2)
        with total_column:
            file_totali = st.file_uploader(
                "Seleziona il file excel con le giacenze **TOTALI**.", key="upload_totali"
            )
        with robot_column:
            file_robot = st.file_uploader(
                "Seleziona il file excel con le giacenze **ROBOT**.", key="upload_robot"
            )
    
        submitted = st.form_submit_button("Calcola")
        if submitted:
            dataframe_totali = check_file(file_totali, 'totali')
            dataframe_robot = check_file(file_robot, 'robot')
            df_are_valid = dataframe_totali is not None and dataframe_robot is not None
            if df_are_valid:
                with total_column:
                    add_giacenze_view(dataframe_totali)
                with robot_column:
                    add_giacenze_view(dataframe_robot)
        else:
            return
    
    if submitted and df_are_valid:
        result_dataframe = process(dataframe_totali, dataframe_robot)
        st.write("Differenza delle giacenze (esposto):")
        col0, col1, col2 = st.columns([1, 2, 2])
        with col0:
            # count the number of None values in the DataFrame
            count_none = result_dataframe.isnull().sum().sum()
            count_zero = len(result_dataframe[result_dataframe == 0].dropna())
            filtered_result = result_dataframe[result_dataframe > 0].dropna()
            st.dataframe(filtered_result, use_container_width=True)

        count_esposti = int(result_dataframe['Giacenze'].sum())
        with col1:
            st.markdown(f"""
            - Prodotti: {len(result_dataframe)}
            - Prodotti con match in robot (non esposti): {count_zero}
            - Totale prodotti con match (esposti): {count_esposti}
            - Prodotti senza match: {count_none}
        """)
        
        with col2:
            # Create a Pandas DataFrame with the information provided
            data = pandas.DataFrame({
                'Prodotti': ['Prodotti non esposti', 'Prodotti esposti', 'Prodotti senza match'],
                'Count': [count_zero, count_esposti, count_none]
            })

            # Create an Altair chart
            chart = alt.Chart(data).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative", stack=True),
                color=alt.Color(field="Prodotti", type="nominal"),
            )
            st.altair_chart(chart, use_container_width=True)

        csv_result_bytes = result_dataframe.fillna('non_trovato').to_csv(sep=";")
        st.download_button(
            "Download this file as CSV",
            data=csv_result_bytes,
            file_name="result_differences.csv",
            mime="text/csv",
        )

def main():
    set_page_config()
    add_sidebar()
    st.title("Antica Farmacia Lugaresi")
    add_compare_section()


if __name__ == "__main__":
    main()
