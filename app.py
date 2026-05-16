import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page settings
st.set_page_config(
    page_title="Corre Rica",
    page_icon="🏃",
    layout="wide"
)

@st.cache_data
def get_data(path: str) -> pd.DataFrame:
    """Load and cache processed data files."""
    df = pd.read_csv(path)
    return df


# Functions

def filtering_data(df: pd.DataFrame, training_session, training_type) -> pd.DataFrame:
    df = df[(df['training_type'] == training_type) & (df['session'] == training_session)]
    return df

def display_main_metrics(df: pd.DataFrame) -> None:
    """Display running metrics"""
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("⚡ Pace Médio",      f"{df['pace'].mean().round(2)} min/km")
    col2.metric("🦵 Cadência Média",  f"{int(df['spm'].mean())} spm")
    col3.metric("📏 Distância Total", f"{(df['distance'].iloc[-1] / 1000).round(2)} km")
    col4.metric("⏱️ Duração",         df['ts_duration'].iloc[-1])

def hr_vs_pace(df: pd.DataFrame):
    """Plot a chart to show HR & Pace"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=df['ts_duration'],
        y=df['heart_rate'],
        mode='lines',
        line=dict(color='green', width=1),
        name='FC'
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df['ts_duration'],
        y=df['pace'],
        mode='lines',
        line=dict(color='blue', width=1),
        name='Pace'
    ), secondary_y=True)

    fig.update_layout(
        title='FC e Pace ao longo do treino',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_yaxes(title_text='BPM', secondary_y=False)
    fig.update_yaxes(title_text='min/km', secondary_y=True, autorange='reversed')

    return fig

def time_per_zone(df: pd.DataFrame):
    """Plot a chart to show time spent in each HR zone"""
    tempo_por_zona = df.groupby('zone').size().reset_index(name='segundos')
    tempo_por_zona['minutos'] = tempo_por_zona['segundos'] / 60
    tempo_por_zona['label'] = tempo_por_zona['segundos'].apply(
        lambda s: f"{int((s % 3600) // 60):02d}:{int(s % 60):02d}"
    )

    cores = {
        'Z1': 'blue',
        'Z2': 'green',
        'Z3': 'yellow',
        'Z4': 'orange',
        'Z5': 'red'
    }

    fig = px.bar(
        tempo_por_zona,
        x='minutos',
        y='zone',
        orientation='h',
        text='label',
        color='zone',
        color_discrete_map=cores,
        title='⏱️ Tempo por Zona de FC'
    )

    fig.update_traces(textposition='outside', width=0.4)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    return fig


def main() -> None:
    """Main function to orchestrate the dashboard layout."""
    st.title('🏃 Corre Rica, Compare meus treinos!')
    st.subheader('Calma, eu cansei!')
    st.divider()

    # Load data
    df = get_data('./data/processed/treinos.csv')

    # Sidebar filters
    sessions = sorted(df['session'].unique())
    training_types = sorted(df['training_type'].unique())

    training_type = st.sidebar.selectbox(
        "📋 Tipo de treino:",
        options=training_types
    )
    session1 = st.sidebar.select_slider(
        "🔵 Treino 1:",
        options=sessions
    )
    session2 = st.sidebar.select_slider(
        "🔴 Treino 2:",
        options=sessions
    )

    # Filtering data
    df_s1 = filtering_data(df, session1, training_type)
    df_s2 = filtering_data(df, session2, training_type)

    # Split screen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🔵 Treino {session1}")
        display_main_metrics(df_s1)
        st.plotly_chart(hr_vs_pace(df_s1), use_container_width=True)
        st.plotly_chart(time_per_zone(df_s1), use_container_width=True)

    with col2:
        st.subheader(f"🔴 Treino {session2}")
        display_main_metrics(df_s2)
        st.plotly_chart(hr_vs_pace(df_s2), use_container_width=True)
        st.plotly_chart(time_per_zone(df_s2), use_container_width=True)


if __name__ == '__main__':
    main()
    st.markdown("""<style> #MainMenu, footer, header {visibility: hidden;} </style>""", unsafe_allow_html=True)