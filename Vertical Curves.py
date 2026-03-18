# Vertical Curves.py - IRC:73-2023 Vertical Curve Design & Verification Tool

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import datetime
import io
import pandas as pd
import re

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title='Vertical Curve Explorer',
    page_icon=':triangular_ruler:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ----------------------------------------------------------------------
# GLOBAL CSS
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# THEME DEFINITIONS
# ----------------------------------------------------------------------
THEMES = {
    'Dark': {
        'bg':          '#0D1117',
        'bg_card':     '#161B22',
        'bg_sidebar':  '#010409',
        'bg_plot':     '#0D1117',
        'text':        '#C9D1D9',
        'text_head':   '#E6EDF3',
        'text_muted':  '#8B949E',
        'border':      '#21262D',
        'border_soft': '#30363D',
        'primary':     '#58A6FF',
        'success':     '#3FB950',
        'danger':      '#FF7B72',
        'warning':     '#F0883E',
        'envelope':    '#C9D1D9',
        'grid':        '#21262D',
        'chip_bg':     '#0D1117',
    },
    'Light': {
        'bg':          '#F6F8FA',
        'bg_card':     '#FFFFFF',
        'bg_sidebar':  '#F0F2F5',
        'bg_plot':     '#FFFFFF',
        'text':        '#24292F',
        'text_head':   '#1C2128',
        'text_muted':  '#57606A',
        'border':      '#D0D7DE',
        'border_soft': '#BFC8D3',
        'primary':     '#0969DA',
        'success':     '#1A7F37',
        'danger':      '#CF222E',
        'warning':     '#9A6700',
        'envelope':    '#57606A',
        'grid':        '#E8ECEF',
        'chip_bg':     '#F6F8FA',
    },
    'Slate': {
        'bg':          '#1C2333',
        'bg_card':     '#222D3F',
        'bg_sidebar':  '#151C2B',
        'bg_plot':     '#1C2333',
        'text':        '#CDD9E5',
        'text_head':   '#ADBAC7',
        'text_muted':  '#768390',
        'border':      '#2D3F54',
        'border_soft': '#3D4F63',
        'primary':     '#6CB6FF',
        'success':     '#57AB5A',
        'danger':      '#E5534B',
        'warning':     '#C69026',
        'envelope':    '#ADBAC7',
        'grid':        '#2D3F54',
        'chip_bg':     '#1C2333',
    },
    'High Contrast': {
        'bg':          '#000000',
        'bg_card':     '#0A0A0A',
        'bg_sidebar':  '#050505',
        'bg_plot':     '#000000',
        'text':        '#FFFFFF',
        'text_head':   '#FFFFFF',
        'text_muted':  '#AAAAAA',
        'border':      '#333333',
        'border_soft': '#444444',
        'primary':     '#00BFFF',
        'success':     '#00FF88',
        'danger':      '#FF3344',
        'warning':     '#FFB300',
        'envelope':    '#FFFFFF',
        'grid':        '#1A1A1A',
        'chip_bg':     '#000000',
    },
}

# Theme is selected in sidebar — we need a temporary read before sidebar renders
# Use session_state to persist selection
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Dark'

def inject_theme(t):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

html,body,[class*="css"]{{font-family:'Inter',sans-serif;background:{t['bg']};color:{t['text']};}}
.stApp{{background:{t['bg']};}}
.main .block-container{{padding-top:0.8rem;padding-bottom:1.5rem;max-width:100%;background:{t['bg']};}}

section[data-testid="stSidebar"]{{background:{t['bg_sidebar']};border-right:1px solid {t['border']};}}
section[data-testid="stSidebar"] *{{color:{t['text_muted']}!important;}}
section[data-testid="stSidebar"] hr{{border-color:{t['border']}!important;margin:0.7rem 0!important;}}
section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] h4,section[data-testid="stSidebar"] h5{{
    color:{t['text_head']}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;letter-spacing:0.04em!important;}}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stCheckbox label{{color:{t['text']}!important;}}

.vc-header{{display:flex;align-items:center;justify-content:space-between;
    background:{t['bg_card']};border:1px solid {t['border']};border-left:3px solid {t['primary']};
    border-radius:8px;padding:0.75rem 1.4rem;margin-bottom:0.9rem;}}
.vc-header-left h1{{font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:600;color:{t['text_head']};margin:0;}}
.vc-header-left p{{font-size:0.72rem;color:{t['text_muted']};margin:0.2rem 0 0;}}
.vc-header-right{{display:flex;flex-wrap:wrap;gap:0.35rem;align-items:center;justify-content:flex-end;}}

.chip{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:0.67rem;font-weight:500;
    padding:0.18rem 0.6rem;border-radius:20px;letter-spacing:0.04em;border:1px solid;white-space:nowrap;}}
.chip-blue{{color:{t['primary']};border-color:{t['primary']};background:{t['chip_bg']};}}
.chip-green{{color:{t['success']};border-color:{t['success']};background:{t['chip_bg']};}}
.chip-amber{{color:{t['warning']};border-color:{t['warning']};background:{t['chip_bg']};}}
.chip-purple{{color:#D2A8FF;border-color:#6E40C9;background:{t['chip_bg']};}}
.chip-muted{{color:{t['text_muted']};border-color:{t['border_soft']};background:{t['chip_bg']};}}

.formula-strip{{display:flex;gap:0.6rem;margin-bottom:0.7rem;background:{t['bg_card']};border:1px solid {t['border']};
    border-radius:8px;padding:0.65rem 1rem;font-family:'JetBrains Mono',monospace;font-size:0.78rem;}}
.formula-strip .divider{{color:{t['border_soft']};margin:0 0.2rem;}}
.f-label{{color:{t['text_muted']};font-size:0.65rem;text-transform:uppercase;letter-spacing:0.07em;margin-right:0.4rem;}}
.f-eq{{color:{t['text']};}}
.f-eq.f1{{color:{t['primary']};}}
.f-eq.f2{{color:{t['danger']};}}
.f-sub{{color:{t['text_muted']};font-size:0.65rem;margin-left:0.5rem;}}

.formula-card{{background:{t['bg_card']};border:1px solid {t['border']};border-left:3px solid {t['primary']};
    border-radius:6px;padding:0.55rem 1rem;margin-bottom:0.5rem;font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:{t['text']};}}
.formula-card.red{{border-left-color:{t['danger']};}}

.stDownloadButton button{{background:{t['bg_card']}!important;color:{t['primary']}!important;border:1px solid {t['border_soft']}!important;
    font-family:'JetBrains Mono',monospace!important;font-size:0.74rem!important;font-weight:500!important;
    border-radius:6px!important;padding:0.35rem 1rem!important;width:100%;transition:all 0.15s!important;}}
.stDownloadButton button:hover{{background:{t['primary']}!important;color:#fff!important;border-color:{t['primary']}!important;}}

.metric-tile{{background:{t['bg_card']};border:1px solid {t['border']};border-top:2px solid {t['border']};
    border-radius:6px;padding:0.55rem 0.9rem;transition:border-top-color 0.2s;}}
.metric-tile:hover{{border-top-color:{t['primary']};}}
.metric-tile .label{{font-size:0.6rem;color:{t['text_muted']};text-transform:uppercase;letter-spacing:0.09em;font-weight:600;}}
.metric-tile .value{{font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;color:{t['primary']};}}
.metric-tile .unit{{font-size:0.6rem;color:{t['text_muted']};}}

.info-box{{background:{t['bg_card']};border:1px solid {t['primary']};border-radius:6px;padding:0.7rem 1rem;font-size:0.76rem;color:{t['primary']};margin-bottom:0.8rem;}}
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:{t['bg']};}}
::-webkit-scrollbar-thumb{{background:{t['border_soft']};border-radius:3px;}}
::-webkit-scrollbar-thumb:hover{{background:{t['text_muted']};}}
.stDataFrame{{border:1px solid {t['border']}!important;border-radius:6px;}}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# IRC DATA
# ----------------------------------------------------------------------
sd_table={20:(20,40,None),25:(25,50,None),30:(30,60,None),40:(45,90,135),50:(60,120,235),
    60:(80,160,300),65:(90,180,340),80:(130,260,470),100:(180,360,640),120:(250,500,835)}
heights={'SSD':(1.2,0.15),'ISD':(1.2,1.20),'OSD':(1.2,1.20)}
sd_index={'SSD':0,'ISD':1,'OSD':2}
OSD_MIN=40
VALID_CREST_SD_TYPES=('SSD','ISD','OSD')
WARN_PREFIX='WARN:'
NO_DATA_MARKER='-'
DEFAULT_CREST_SD_TYPE='ISD'
hsd_table={spd:vals[0] for spd,vals in sd_table.items()}
SAG_H1=0.75
SAG_ALPHA=1.0
SAG_TAN=np.tan(np.radians(SAG_ALPHA))

def headlight_factor(S):
    return 2*SAG_H1 + 2*S*SAG_TAN

k_min_crest={
    'SSD':{20:0.9,25:1.4,30:2.0,35:3.6,40:4.6,50:8.2,60:14.5,65:18.4,80:38.4,100:73.6,120:110.0},
    'ISD':{20:1.7,25:2.6,30:3.8,35:6.7,40:8.4,50:15.0,60:26.7,65:33.8,80:70.4,100:135.0,120:200.0},
    'OSD':{40:28.4,50:57.5,60:93.7,65:120.4,80:230.1,100:426.7,120:650.0},
}
k_min_sag={20:1.8,25:2.6,30:3.5,35:5.5,40:6.6,50:10.0,60:14.9,65:17.4,80:27.9,100:41.5,120:60.0}
grade_change_threshold={20:1.5,25:1.5,30:1.5,35:1.5,40:1.2,50:1.0,60:0.8,65:0.8,80:0.6,100:0.5,120:0.5}
min_length_standard={20:15,25:15,30:15,40:20,50:30,60:40,65:40,80:50,100:60,120:100}
min_length_expressway={**min_length_standard,80:70,100:85,120:100}
formula_label={'SSD':('h1=1.2m, h2=0.15m',''),'ISD':('h1=1.2m, h2=1.20m',''),'OSD':('h1=1.2m, h2=1.20m','')}
all_speeds=list(sd_table.keys())
standard_speeds=[s for s in all_speeds if s!=120]

SPD_COLORS={
    20:'#79C0FF',25:'#56D364',30:'#F0883E',35:'#D2A8FF',
    40:'#FF7B72',50:'#FFA657',60:'#39D353',65:'#58A6FF',
    80:'#BC8CFF',100:'#FF9BCE',120:'#E6EDF3'
}

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Vertical Curve Explorer")
    st.markdown("---")
    st.markdown("##### Theme ")
    theme_name = st.radio('Theme', list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state['theme']), label_visibility='collapsed')
    st.session_state['theme'] = theme_name
    T = THEMES[theme_name]
    inject_theme(T)

    COLORS = {
        'primary':   T['primary'],  'danger':  T['danger'],
        'success':   T['success'],  'warning': T['warning'],
        'muted':     T['text_muted'], 'border': T['border'],
        'bg_card':   T['bg_card'],  'bg_plot': T['bg_plot'],
        'axis_label_color': T['text_muted'],
        'envelope_line':    T['envelope'],
        'grid_color':       T['grid'],
    }

    PLOTLY_BASE = dict(
        paper_bgcolor=T['bg_card'], plot_bgcolor=T['bg_plot'],
        font=dict(family='JetBrains Mono, monospace', color=T['text'], size=11),
        xaxis=dict(
            title=dict(text='Deviation Angle   N', font=dict(size=12, color=T['text_muted'])),
            gridcolor=T['grid'], gridwidth=1, zerolinecolor=T['border_soft'], zeroline=True,
            tickfont=dict(color=T['text_muted'], size=10), tickformat='.4f',
            showspikes=True, spikecolor=T['primary'], spikethickness=1, spikedash='dot', spikemode='across',
        ),
        yaxis=dict(
            title=dict(text='Length of Vertical Curve   L  (m)', font=dict(size=12, color=T['text_muted'])),
            gridcolor=T['grid'], gridwidth=1, zerolinecolor=T['border_soft'], zeroline=True,
            tickfont=dict(color=T['text_muted'], size=10),
            showspikes=True, spikecolor=T['primary'], spikethickness=1, spikedash='dot', spikemode='across',
        ),
        legend=dict(
            bgcolor=T['bg_card'], bordercolor=T['border'], borderwidth=1,
            font=dict(size=10, color=T['text']),
            x=0.01, y=0.99, xanchor='left', yanchor='top',
            itemclick='toggle', itemdoubleclick='toggleothers',
        ),
        hovermode='closest',
        hoverlabel=dict(bgcolor=T['bg_card'], bordercolor=T['border_soft'], font=dict(family='JetBrains Mono', size=11, color=T['text'])),
        dragmode='pan',
        margin=dict(l=70, r=30, t=55, b=65), height=530,
        newshape=dict(line_color=T['primary']),
    )

    st.markdown("---")
    st.markdown("##### Mode ")
    app_mode = st.radio('Mode', ('Design', 'Verify Existing'), label_visibility='collapsed')
    st.markdown("---")
    st.markdown("##### Road Type ")
    expressway = st.toggle('Expressway', value=False)
    if expressway:
        st.markdown("<span style='font-size:0.72rem;color:#A78BFA'>120 km/h enabled | Lmin: 80→70, 100→85, 120→100 m</span>", unsafe_allow_html=True)
    min_length = min_length_expressway if expressway else min_length_standard
    available_speeds = all_speeds if expressway else standard_speeds
    st.markdown("---")
    st.markdown("##### Curve Type ")
    curve_type = st.radio('Curve Type', ('Crest', 'Sag'), index=0, label_visibility='collapsed')
    st.markdown("---")
    st.markdown("##### Sight Distance Type ")
    if curve_type == 'Crest':
        sd_type = st.radio('Sight Distance Type', ('SSD','ISD','OSD'), index=1, label_visibility='collapsed')
    else:
        sd_type = 'HSD'
        st.markdown("**HSD**")
    st.markdown("---")
    if app_mode == 'Design':
        st.markdown("##### Design Speeds (km/h) ")
        avail_for_sd = available_speeds if sd_type!='OSD' else [s for s in available_speeds if s >= OSD_MIN]
        defaults = [s for s in ([80,100,120] if expressway else [80,100]) if s in avail_for_sd]
        selected_speeds = st.multiselect('Speeds', avail_for_sd, default=defaults, format_func=lambda x: f'{x} km/h', label_visibility='collapsed')
        st.markdown("---")
        st.markdown("##### View ")
        split_formulas = st.toggle('Formula Split', value=False)
        st.markdown("---")
        st.markdown("##### Options ")
        show_min = st.checkbox('Min Length (Table 7.5)', value=True)
        show_env = st.checkbox('L = S Envelope', value=True)
    else:
        selected_speeds = []
        split_formulas = show_min = show_env = False
    st.markdown("---")
    st.caption(f"IRC:73-2023 | {datetime.date.today().strftime('%d %b %Y')}")

# ----------------------------------------------------------------------
# FORMULA STRINGS & DERIVED VALUES
# ----------------------------------------------------------------------
f1_crest="L = (N*S^2) / ((sqrt(2*h1) + sqrt(2*h2))^2)"
f2_crest="L = 2S - ((sqrt(2*h1) + sqrt(2*h2))^2) / N"
f1_sag="L = (N*S^2) / (2*h1 + 2S*tan(alpha))"
f2_sag="L = 2S - (2*h1 + 2S*tan(alpha)) / N"
view_mode = "Formula Analysis" if split_formulas else "Design Chart"

if curve_type == 'Crest' and sd_type in heights:
    h1_c, h2_c = heights[sd_type]
    denom_crest = (np.sqrt(2*h1_c) + np.sqrt(2*h2_c))**2
    h_note = formula_label[sd_type][0]
else:
    denom_crest = None
    h_note = f'h1={SAG_H1}m, alpha={SAG_ALPHA} deg' if curve_type == 'Sag' else 'HSD'

# ----------------------------------------------------------------------
# PLOTLY CHART HELPERS
# ----------------------------------------------------------------------
def make_N_arr(n=3000):
    return np.linspace(0.0001, 0.30, n)

def curve_traces(spd, S_val, dv, Lmin, color, label, show_min_flag):
    N_arr = make_N_arr()
    Nx = dv / S_val
    traces = []
    # F2 segment
    mf2 = N_arr <= Nx + 1e-9
    Nf2 = N_arr[mf2]
    Lf2 = np.maximum(2*S_val - dv/Nf2, Lmin if show_min_flag else 0)
    v2 = (Lf2 >= 0) & np.isfinite(Lf2)
    if v2.any():
        traces.append(go.Scatter(x=Nf2[v2], y=Lf2[v2], mode='lines', name=label,
            line=dict(color=color, width=2.2),
            hovertemplate=f'<b>{label}</b><br>N = %{{x:.5f}}<br>L = %{{y:.1f}} m  <i>(F2)</i><extra></extra>',
            legendgroup=label, showlegend=True))
    # F1 segment
    mf1 = N_arr >= Nx - 1e-9
    Nf1 = N_arr[mf1]
    Lf1 = np.maximum((Nf1 * S_val**2) / dv, Lmin if show_min_flag else 0)
    v1 = (Lf1 >= 0) & np.isfinite(Lf1)
    if v1.any():
        traces.append(go.Scatter(x=Nf1[v1], y=Lf1[v1], mode='lines', name=label,
            line=dict(color=color, width=2.2),
            hovertemplate=f'<b>{label}</b><br>N = %{{x:.5f}}<br>L = %{{y:.1f}} m  <i>(F1)</i><extra></extra>',
            legendgroup=label, showlegend=False))
    # Crossover dot
    L_cross = max((Nx * S_val**2) / dv, Lmin if show_min_flag else 0)
    traces.append(go.Scatter(x=[Nx], y=[L_cross], mode='markers',
        marker=dict(color=color, size=9, line=dict(color='white', width=1.5)),
        name=label,
        hovertemplate=f'<b>{label}</b><br>Crossover N = {Nx:.5f}<br>L = S = {S_val} m<extra></extra>',
        legendgroup=label, showlegend=False))
    return traces

def envelope_trace(dv_fn):
    S_arr = np.linspace(5, 1500, 5000)
    Ne = np.array([dv_fn(S)/S for S in S_arr])
    v = (Ne>0) & (Ne<0.30) & np.isfinite(Ne) & (S_arr>0)
    return go.Scatter(x=Ne[v], y=S_arr[v], mode='lines', name='L = S  (envelope)',
        line=dict(color='#C9D1D9', width=1.2, dash='dash'),
        hovertemplate='L = S boundary<br>N = %{x:.5f}<br>S = %{y:.1f} m<extra></extra>')

def lmin_traces(spds, min_len, show_min_flag):
    if not show_min_flag: return []
    seen = {}
    for s in spds:
        Lm = min_len.get(s)
        if Lm: seen.setdefault(Lm, []).append(s)
    out = []
    for Lm, ss in sorted(seen.items()):
        out.append(go.Scatter(x=[0,0.30], y=[Lm,Lm], mode='lines',
            line=dict(color='#8B949E', width=1, dash='dashdot'),
            name=f'Lmin={Lm}m  ({", ".join(str(x) for x in ss)} km/h)',
            hovertemplate=f'Lmin = {Lm} m<extra></extra>'))
    return out

def apply_base_layout(fig, title, title_color):
    layout = dict(**PLOTLY_BASE)
    layout['title'] = dict(text=title, font=dict(size=13, color=title_color), x=0.02, xanchor='left')
    fig.update_layout(**layout)

# ----------------------------------------------------------------------
# PLOT FUNCTIONS
# ----------------------------------------------------------------------
def crest_design(selected_speeds, sd_type, show_min, show_env):
    fig = go.Figure()
    for spd in selected_speeds:
        Sv = sd_table[spd][sd_index[sd_type]]
        if Sv is None: continue
        for t in curve_traces(spd, Sv, denom_crest, min_length.get(spd,0), SPD_COLORS.get(spd,'#8B949E'), f'{spd} km/h  (S={Sv}m)', show_min):
            fig.add_trace(t)
    if show_env: fig.add_trace(envelope_trace(lambda S: denom_crest))
    for t in lmin_traces(selected_speeds, min_length, show_min): fig.add_trace(t)
    apply_base_layout(fig, 'Design Chart — Crest Vertical Curve  |  ← F2 · crossover ○ · F1 →', COLORS['success'])
    return fig

def crest_analysis(selected_speeds, sd_type, show_min, show_env):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Formula 1 — valid when L ≥ S', 'Formula 2 — valid when L ≤ S'])
    N_arr = make_N_arr()
    L_max = 0
    for spd in selected_speeds:
        Sv = sd_table[spd][sd_index[sd_type]]
        if Sv is None: continue
        col = SPD_COLORS.get(spd,'#8B949E')
        lbl = f'{spd} km/h  (S={Sv}m)'
        Lmin = min_length.get(spd, 0)
        # F1 — valid for all N, clip to positive
        L1 = (N_arr * Sv**2) / denom_crest
        v1 = (L1 >= 0) & np.isfinite(L1)
        fig.add_trace(go.Scatter(x=N_arr[v1], y=L1[v1], mode='lines', name=lbl,
            line=dict(color=col, width=2), legendgroup=lbl, showlegend=True,
            hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'), row=1, col=1)
        L_max = max(L_max, L1[v1].max() if v1.any() else 0)
        # F2 — only valid where L >= 0 and N <= crossover
        Nx = denom_crest / Sv
        mf2 = N_arr <= Nx + 1e-9
        L2 = 2*Sv - denom_crest / N_arr[mf2]
        v2 = (L2 >= 0) & np.isfinite(L2)
        if v2.any():
            fig.add_trace(go.Scatter(x=N_arr[mf2][v2], y=L2[v2], mode='lines', name=lbl,
                line=dict(color=col, width=2), legendgroup=lbl, showlegend=False,
                hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'), row=1, col=2)
            L_max = max(L_max, L2[v2].max())
    if show_env:
        S_arr = np.linspace(5,1500,5000)
        Ne = denom_crest / S_arr
        v = (Ne>0)&(Ne<0.30)&np.isfinite(Ne)
        ec = COLORS['envelope_line']
        fig.add_trace(go.Scatter(x=Ne[v], y=S_arr[v], mode='lines', name='L=S boundary',
            line=dict(color=ec, width=1.2, dash='dash'),
            hovertemplate='L=S<br>N=%{x:.5f}<extra></extra>'), row=1, col=1)
        fig.add_trace(go.Scatter(x=Ne[v], y=S_arr[v], mode='lines', name='L=S boundary',
            line=dict(color=ec, width=1.2, dash='dash'), showlegend=False,
            hovertemplate='L=S<br>N=%{x:.5f}<extra></extra>'), row=1, col=2)
    ymax = min(int(L_max * 1.15 / 50 + 1) * 50, 3000) if L_max > 0 else 1500
    layout = dict(**PLOTLY_BASE)
    layout['title'] = dict(text='Formula Analysis — Crest Vertical Curve', font=dict(size=13, color=COLORS['primary']), x=0.02)
    yax  = {**PLOTLY_BASE['yaxis'],  'range': [0, ymax]}
    yax2 = {**PLOTLY_BASE['yaxis'],  'range': [0, ymax], 'title': dict(text='')}
    xax  = {**PLOTLY_BASE['xaxis'],  'range': [0, 0.30]}
    xax2 = {**PLOTLY_BASE['xaxis'],  'range': [0, 0.30]}
    layout['yaxis'] = yax; layout['yaxis2'] = yax2
    layout['xaxis'] = xax; layout['xaxis2'] = xax2
    fig.update_layout(**layout)
    return fig

def sag_design(selected_speeds, show_min, show_env):
    fig = go.Figure()
    for spd in selected_speeds:
        Sv = hsd_table.get(spd)
        if Sv is None: continue
        ds = headlight_factor(Sv)
        for t in curve_traces(spd, Sv, ds, min_length.get(spd,0), SPD_COLORS.get(spd,'#8B949E'), f'{spd} km/h  (HSD={Sv}m)', show_min):
            fig.add_trace(t)
    if show_env: fig.add_trace(envelope_trace(headlight_factor))
    for t in lmin_traces(selected_speeds, min_length, show_min): fig.add_trace(t)
    apply_base_layout(fig, 'Design Chart — Sag Vertical Curve  |  ← F2 · crossover ○ · F1 →', COLORS['warning'])
    return fig

def sag_analysis(selected_speeds, show_min, show_env):
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Formula 1 — valid when L ≥ S', 'Formula 2 — valid when L ≤ S'])
    N_arr = make_N_arr()
    L_max = 0
    for spd in selected_speeds:
        Sv = hsd_table.get(spd)
        if Sv is None: continue
        ds = headlight_factor(Sv)
        col = SPD_COLORS.get(spd,'#8B949E')
        lbl = f'{spd} km/h  (HSD={Sv}m)'
        # F1
        L1 = (N_arr * Sv**2) / ds
        v1 = (L1 >= 0) & np.isfinite(L1)
        fig.add_trace(go.Scatter(x=N_arr[v1], y=L1[v1], mode='lines', name=lbl,
            line=dict(color=col, width=2), legendgroup=lbl, showlegend=True,
            hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'), row=1, col=1)
        L_max = max(L_max, L1[v1].max() if v1.any() else 0)
        # F2 — only valid where N <= crossover and L >= 0
        Nx = ds / Sv
        mf2 = N_arr <= Nx + 1e-9
        L2 = 2*Sv - ds / N_arr[mf2]
        v2 = (L2 >= 0) & np.isfinite(L2)
        if v2.any():
            fig.add_trace(go.Scatter(x=N_arr[mf2][v2], y=L2[v2], mode='lines', name=lbl,
                line=dict(color=col, width=2), legendgroup=lbl, showlegend=False,
                hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'), row=1, col=2)
            L_max = max(L_max, L2[v2].max())
    if show_env:
        S_arr = np.linspace(5,1500,5000)
        Ne = np.array([headlight_factor(S)/S for S in S_arr])
        v = (Ne>0)&(Ne<0.30)&np.isfinite(Ne)
        ec = COLORS['envelope_line']
        fig.add_trace(go.Scatter(x=Ne[v], y=S_arr[v], mode='lines', name='L=S boundary',
            line=dict(color=ec, width=1.2, dash='dash'),
            hovertemplate='L=S<br>N=%{x:.5f}<extra></extra>'), row=1, col=1)
        fig.add_trace(go.Scatter(x=Ne[v], y=S_arr[v], mode='lines', name='L=S boundary',
            line=dict(color=ec, width=1.2, dash='dash'), showlegend=False,
            hovertemplate='L=S<br>N=%{x:.5f}<extra></extra>'), row=1, col=2)
    ymax = min(int(L_max * 1.15 / 50 + 1) * 50, 3000) if L_max > 0 else 1500
    layout = dict(**PLOTLY_BASE)
    layout['title'] = dict(text='Formula Analysis — Sag Vertical Curve', font=dict(size=13, color=COLORS['warning']), x=0.02)
    yax  = {**PLOTLY_BASE['yaxis'],  'range': [0, ymax]}
    yax2 = {**PLOTLY_BASE['yaxis'],  'range': [0, ymax], 'title': dict(text='')}
    xax  = {**PLOTLY_BASE['xaxis'],  'range': [0, 0.30]}
    xax2 = {**PLOTLY_BASE['xaxis'],  'range': [0, 0.30]}
    layout['yaxis'] = yax; layout['yaxis2'] = yax2
    layout['xaxis'] = xax; layout['xaxis2'] = xax2
    fig.update_layout(**layout)
    return fig

PLOTLY_CONFIG = {
    'displayModeBar': True,
    'scrollZoom': True,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d'],
    'toImageButtonOptions': {'format':'png','filename':'vertical_curve','height':600,'width':1600,'scale':2}
}

# ----------------------------------------------------------------------
# PARSE / NORMALISE HELPERS
# ----------------------------------------------------------------------
def parse_N(val):
    if val is None: raise ValueError('N is required')
    had_percent = False
    if isinstance(val, (int, float, np.number)):
        out = float(val)
    else:
        s = str(val).strip().replace(',','.')
        if not s: raise ValueError('N is required')
        if s.endswith('%'):
            had_percent = True; out = float(s[:-1])/100.0
        else:
            out = float(s)
    if not np.isfinite(out): raise ValueError('N must be a finite number')
    if out <= 0: raise ValueError('N must be > 0')
    if not had_percent and out >= 1:
        raise ValueError('Plain N must be decimal < 1 (e.g. 0.01). For percent enter 1%.')
    return out

def normalize_curve_type(value, default='Crest'):
    raw = '' if value is None else str(value).strip()
    if not raw: raw = str(default).strip()
    rl = raw.lower()
    if rl in ('crest','c'): return 'Crest'
    if rl in ('sag','s'): return 'Sag'
    raise ValueError('Curve type must be Crest or Sag')

def normalize_crest_sd_type(value, default=DEFAULT_CREST_SD_TYPE):
    fallback = str(default).strip().upper() if default else DEFAULT_CREST_SD_TYPE
    raw = '' if value is None else str(value).strip().upper()
    if not raw: raw = fallback if fallback in VALID_CREST_SD_TYPES else DEFAULT_CREST_SD_TYPE
    if raw not in VALID_CREST_SD_TYPES: raise ValueError(f'SD type "{raw}" invalid')
    return raw

def resolve_verify_inputs(curve_value, sd_value, default_curve_type, default_crest_sd):
    curve_used = normalize_curve_type(curve_value, default_curve_type)
    if curve_used == 'Sag': return curve_used, 'HSD'
    return curve_used, normalize_crest_sd_type(sd_value, default_crest_sd)

def normalize_header(header):
    return re.sub(r'_+','_',re.sub(r'[^a-z0-9]+','_',str(header).strip().lower())).strip('_')

def duplicate_columns_after_mapping(columns):
    return pd.Index(columns)[pd.Index(columns).duplicated()].unique().tolist()

def nonnegative_length(value):
    value = float(value)
    return value if np.isfinite(value) and value >= 0 else None

def parse_speed(spd_in):
    spd_f = float(str(spd_in).strip().replace(',','.'))
    if not np.isfinite(spd_f): raise ValueError('Speed must be a finite number')
    if not spd_f.is_integer(): raise ValueError('Speed must be a whole number from the IRC table')
    return int(spd_f)

def parse_positive_number(value, label):
    num = float(str(value).strip().replace(',','.'))
    if not np.isfinite(num): raise ValueError(f'{label} must be a finite number')
    if num <= 0: raise ValueError(f'{label} must be > 0')
    return num

# ----------------------------------------------------------------------
# DESIGN MODE
# ----------------------------------------------------------------------
_design_mode = (app_mode == 'Design')

if _design_mode and curve_type == 'Crest':
    _road_label = 'Expressway' if expressway else 'Standard'
    st.markdown(
        '<div class="vc-header">'
        '<div class="vc-header-left"><h1>Vertical Curve Explorer</h1>'
        f'<p>IRC:73-2023 | Crest Curve | {sd_type}</p></div>'
        '<div class="vc-header-right">'
        f'<span class="chip chip-blue">{h_note}</span>'
        f'<span class="chip chip-green">{_road_label}</span>'
        '</div></div>',
        unsafe_allow_html=True
    )

    if not split_formulas:
        st.markdown(f"""<div class="formula-strip">
          <span class="f-label">F1</span><span class="f-eq f1">{f1_crest}</span><span class="f-sub">valid L >= S</span>
          <span class="divider"> | </span>
          <span class="f-label">F2</span><span class="f-eq f2">{f2_crest}</span><span class="f-sub">valid L <= S</span>
          <span class="divider"> | </span><span class="f-sub">governing = max(F1, F2) >= Lmin</span>
        </div>""", unsafe_allow_html=True)
    else:
        cf1, cf2 = st.columns(2)
        with cf1: st.markdown(f'<div class="formula-card">F1 - {f1_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when L >= S</span></div>', unsafe_allow_html=True)
        with cf2: st.markdown(f'<div class="formula-card red">F2 - {f2_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when L <= S</span></div>', unsafe_allow_html=True)

    if selected_speeds and denom_crest:
        fc = crest_design(selected_speeds, sd_type, show_min, show_env) if 'Design Chart' in view_mode else crest_analysis(selected_speeds, sd_type, show_min, show_env)
        st.plotly_chart(fc, use_container_width=True, config=PLOTLY_CONFIG)
    elif not selected_speeds:
        st.info('Select at least one design speed from the sidebar.')

    if selected_speeds and denom_crest:
        st.markdown("---")
        st.markdown("**Quick Reference — Crest**")
        cols = st.columns(len(selected_speeds))
        for col, spd in zip(cols, selected_speeds):
            Sv = sd_table[spd][sd_index[sd_type]]
            Lmin = min_length.get(spd, 0)
            if Sv:
                Nx = round(denom_crest/Sv, 4)
                Ld = round(max(max((Nx*Sv**2)/denom_crest, 2*Sv-denom_crest/Nx), Lmin), 1)
            else:
                Nx = Ld = '-'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (S)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>', unsafe_allow_html=True)

elif _design_mode and curve_type == 'Sag':
    _road_label = 'Expressway' if expressway else 'Standard'
    st.markdown(
        '<div class="vc-header">'
        '<div class="vc-header-left"><h1>Vertical Curve Explorer</h1>'
        '<p>IRC:73-2023 | Sag Curve | HSD</p></div>'
        '<div class="vc-header-right">'
        f'<span class="chip chip-amber">h1={SAG_H1}m | alpha={SAG_ALPHA} deg</span>'
        f'<span class="chip chip-green">{_road_label}</span>'
        '</div></div>',
        unsafe_allow_html=True
    )

    if not split_formulas:
        st.markdown(f"""<div class="formula-strip">
          <span class="f-label">F1</span><span class="f-eq f1">{f1_sag}</span><span class="f-sub">valid L >= S</span>
          <span class="divider"> | </span>
          <span class="f-label">F2</span><span class="f-eq f2">{f2_sag}</span><span class="f-sub">valid L <= S</span>
          <span class="divider"> | </span><span class="f-sub">governing = max(F1, F2) >= Lmin</span>
        </div>""", unsafe_allow_html=True)
    else:
        sf1, sf2 = st.columns(2)
        with sf1: st.markdown(f'<div class="formula-card">F1 - {f1_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when L >= S</span></div>', unsafe_allow_html=True)
        with sf2: st.markdown(f'<div class="formula-card red">F2 - {f2_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when L <= S</span></div>', unsafe_allow_html=True)

    if selected_speeds:
        fs = sag_design(selected_speeds, show_min, show_env) if 'Design Chart' in view_mode else sag_analysis(selected_speeds, show_min, show_env)
        st.plotly_chart(fs, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info('Select at least one design speed from the sidebar.')

    if selected_speeds:
        st.markdown("---")
        st.markdown("**Quick Reference — Sag**")
        cols = st.columns(len(selected_speeds))
        for col, spd in zip(cols, selected_speeds):
            Sv = hsd_table.get(spd)
            Lmin = min_length.get(spd, 0)
            if Sv:
                ds = headlight_factor(Sv)
                Nx = round(ds/Sv, 4)
                Ld = round(max(max((Nx*Sv**2)/ds, 2*Sv-ds/Nx), Lmin), 1)
            else:
                Nx = Ld = '-'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (HSD)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CALCULATOR SECTION
# ----------------------------------------------------------------------
if _design_mode:
    st.markdown("### Design Input Calculator")
    st.markdown("Compute required lengths. Curve_Type: Crest/Sag (blank=Crest). SD_Type applies to Crest only; Sag always uses HSD.")
    _tmpl = pd.DataFrame({'N':['0.045','7.2%','0.031','5.5%','0.038'],'Speed_kmh':[60,80,100,65,80],'SD_Type':['SSD','ISD','','OSD',''],'Curve_Type':['Crest','Crest','Crest','Crest','Sag']})
    _tb = io.StringIO(); _tmpl.to_csv(_tb, index=False)
    tm, tb = st.tabs(['Manual Entry', 'Batch Upload'])

    def compute_row(N_in, spd_in, sdt_in, curve_type='crest'):
        try:
            spd = parse_speed(spd_in); N_v = parse_N(N_in)
            curve_type = str(curve_type).strip().lower()
            if spd == 120 and not expressway: return {'error':'120 km/h for Expressway only'}
            if spd not in sd_table: return {'error':f'Speed {spd} not in IRC table'}
            Lmn = min_length.get(spd, 0)
            if curve_type == 'sag':
                Sv = hsd_table.get(spd)
                if Sv is None: return {'error':f'HSD not defined for {spd} km/h'}
                den_ = headlight_factor(Sv); sd_used = 'HSD'
            else:
                sdt = str(sdt_in).strip().upper()
                if sdt not in VALID_CREST_SD_TYPES: return {'error':f'SD type "{sdt}" invalid'}
                if sdt == 'OSD' and spd < OSD_MIN: return {'error':f'OSD N/A for {spd} km/h'}
                Sv = sd_table[spd][sd_index[sdt]]
                if Sv is None: return {'error':f'{sdt} not defined for {spd} km/h'}
                h1_,h2_ = heights[sdt]; den_ = (np.sqrt(2*h1_)+np.sqrt(2*h2_))**2; sd_used = sdt
            L1 = nonnegative_length((N_v*Sv**2)/den_)
            L2 = nonnegative_length(2*Sv - den_/N_v)
            candidates = [(lbl,l) for lbl,l in (('F1 (L>=S)',L1),('F2 (L<=S)',L2)) if l is not None]
            if not candidates: return {'error':'No valid curve length from IRC formulas'}
            gov,Lg = max(candidates, key=lambda x:x[1])
            Ld = max(Lg, Lmn); K = round(Ld/(N_v*100.0), 2)
            notes = []
            if L2 is None: notes.append('F2 negative → ignored')
            if Lmn > Lg: notes.append('Lmin governs'); gov = 'Lmin (Table 7.5)'
            if expressway: notes.append('Expressway Lmin')
            return {'S (m)':Sv,'SD/HSD used':sd_used,
                'F1 valid length (m)':round(L1,2) if L1 is not None else NO_DATA_MARKER,
                'F2 valid length (m)':round(L2,2) if L2 is not None else NO_DATA_MARKER,
                'Adopted basis':gov,'Minimum length Lmin (m)':Lmn,
                'Adopted curve length (m)':round(Ld,2),'Adopted K = L / [100 x N(decimal)]':K,
                'Notes':' | '.join(notes) if notes else NO_DATA_MARKER,'error':None}
        except Exception as e:
            return {'error':str(e)}

    def results_from_df(df):
        rows = []
        default_crest_sd = sd_type if sd_type in VALID_CREST_SD_TYPES else DEFAULT_CREST_SD_TYPE
        for i,row in df.iterrows():
            base = {'Row':i+1,'N (input)':row.get('N',NO_DATA_MARKER),'Speed (km/h)':row.get('Speed_kmh',NO_DATA_MARKER),'Curve Type':NO_DATA_MARKER,'SD Type used':NO_DATA_MARKER}
            try:
                curve_used = normalize_curve_type(row.get('Curve_Type',''),'Crest')
                crest_sd_used = normalize_crest_sd_type(row.get('SD_Type',''),default_crest_sd) if curve_used=='Crest' else 'HSD'
                base.update({'Curve Type':curve_used,'SD Type used':crest_sd_used})
                r = compute_row(row['N'],row['Speed_kmh'],crest_sd_used,curve_used.lower())
            except Exception as e:
                r = {'error':str(e)}
            if r.get('error'):
                base.update({k:NO_DATA_MARKER for k in ['S (m)','SD/HSD used','F1 valid length (m)','F2 valid length (m)','Adopted curve length (m)','Adopted K = L / [100 x N(decimal)]','Adopted basis','Minimum length Lmin (m)']})
                base['Notes'] = f'{WARN_PREFIX} {r["error"]}'
            else:
                base.update({k:v for k,v in r.items() if k!='error'})
            rows.append(base)
        return pd.DataFrame(rows)

    def plot_calc(res_df):
        valid = res_df[~res_df['Notes'].str.startswith(WARN_PREFIX,na=False)].copy()
        if valid.empty: st.warning('No valid rows to plot.'); return
        fig = go.Figure()
        Nbg = np.linspace(0.0001, 0.30, 3000)
        plotted = set()
        for spd in sorted(valid['Speed (km/h)'].astype(int).unique()):
            col = SPD_COLORS.get(spd,'#8B949E')
            Lmin = min_length.get(spd, 0)
            rows = valid[valid['Speed (km/h)'].astype(int)==spd]
            for sdt in rows[rows['Curve Type']=='Crest']['SD Type used'].unique():
                if sdt=='HSD': continue
                h1_,h2_ = heights[sdt]; den_ = (np.sqrt(2*h1_)+np.sqrt(2*h2_))**2
                Sv = sd_table[spd][sd_index[sdt]]
                if Sv is None: continue
                Ld = np.maximum(np.maximum((Nbg*Sv**2)/den_, 2*Sv-den_/Nbg), Lmin)
                lbl = f'{spd} km/h Crest ({sdt})'
                if lbl not in plotted:
                    dash = 'solid' if sdt=='SSD' else ('dash' if sdt=='ISD' else 'dot')
                    fig.add_trace(go.Scatter(x=Nbg,y=Ld,mode='lines',name=lbl,
                        line=dict(color=col,width=1.5,dash=dash),opacity=0.45,
                        hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'))
                    plotted.add(lbl)
            if len(rows[rows['Curve Type']=='Sag'])>0:
                Sv = hsd_table.get(spd)
                if Sv:
                    ds = headlight_factor(Sv)
                    Ld = np.maximum(np.maximum((Nbg*Sv**2)/ds, 2*Sv-ds/Nbg), Lmin)
                    lbl = f'{spd} km/h Sag (HSD)'
                    if lbl not in plotted:
                        fig.add_trace(go.Scatter(x=Nbg,y=Ld,mode='lines',name=lbl,
                            line=dict(color=col,width=1.5,dash='dashdot'),opacity=0.45,
                            hovertemplate=lbl+'<br>N=%{x:.5f}<br>L=%{y:.1f}m<extra></extra>'))
                        plotted.add(lbl)
        for _,row in valid.iterrows():
            spd = int(row['Speed (km/h)']); n_in=parse_N(row['N (input)']); l_out=float(row['Adopted curve length (m)'])
            col=SPD_COLORS.get(spd,'#8B949E'); sym='circle' if row['Curve Type']=='Crest' else 'square'
            fig.add_trace(go.Scatter(x=[n_in],y=[l_out],mode='markers',
                marker=dict(color=col,size=10,symbol=sym,line=dict(color='white',width=1.5)),
                name=f'Row {row["Row"]} — {spd} km/h {row["Curve Type"]}',
                hovertemplate=f'Row {row["Row"]}<br>N={n_in:.5f}<br>L={l_out:.1f}m<extra></extra>'))
        layout = dict(**PLOTLY_BASE)
        layout['title'] = dict(text=f'Calculated — {len(valid)} location(s)  |  ○ Crest  □ Sag',font=dict(size=12,color=COLORS['success']),x=0.02)
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with tm:
        st.markdown("<span style='font-size:0.78rem;color:#8B949E'>N as decimal < 1 (e.g. 0.01) or explicit percent (e.g. 1%). Bare values like 1 rejected. Blank SD_Type uses sidebar default. Blank Curve_Type defaults to Crest.</span>", unsafe_allow_html=True)
        dr = pd.DataFrame({'N':['0.045','7.2%','0.031','3.8%'],'Speed_kmh':[60,80,100,80],'SD_Type':['','ISD','SSD',''],'Curve_Type':['Crest','Crest','Crest','Sag']})
        idf = st.data_editor(dr, num_rows='dynamic', width="stretch",
            column_config={'N':st.column_config.TextColumn('N / grade change (decimal or %)',required=True),
                'Speed_kmh':st.column_config.SelectboxColumn('Speed (km/h)',options=available_speeds,required=True),
                'SD_Type':st.column_config.SelectboxColumn('SD Type (blank=sidebar default)',options=['','SSD','ISD','OSD']),
                'Curve_Type':st.column_config.SelectboxColumn('Curve Type (blank=Crest)',options=['','Crest','Sag'])},
            hide_index=True, key='manual_editor')
        if idf is not None and len(idf)>0:
            rdf = results_from_df(idf)
            st.markdown("#### Results")
            st.dataframe(rdf, width="stretch", hide_index=True)
            co = io.StringIO(); rdf.to_csv(co, index=False)
            st.download_button('Download Results (CSV)', data=co.getvalue(), file_name=f'vc_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv', key='dl_manual')
            st.markdown("#### Plot"); plot_calc(rdf)

    with tb:
        c1, c2 = st.columns([3,1])
        with c1:
            st.markdown('<div class="info-box"><b>CSV columns:</b> <code>N</code> | <code>Speed_kmh</code> | <code>SD_Type</code> (opt) | <code>Curve_Type</code> (opt)<br>N as decimal < 1 or explicit %. Blank Curve_Type → Crest. Blank SD_Type → sidebar default. Sag always uses HSD. Header required. Aliases accepted.</div>', unsafe_allow_html=True)
        with c2:
            st.download_button('Template', data=_tb.getvalue(), file_name='vc_template.csv', mime='text/csv', key='dl_tmpl')
        up = st.file_uploader('Upload CSV', type=['csv'], label_visibility='collapsed', key='batch_uploader')
        if up is not None:
            try:
                rdf2 = pd.read_csv(up, dtype={'N':str})
                rdf2.columns = [c.strip() for c in rdf2.columns]
                cm = {}
                for c in rdf2.columns:
                    cl = normalize_header(c)
                    if cl in ('n','deviation_angle','dev_angle','angle'): cm[c]='N'
                    elif cl in ('speed_kmh','speed_km_h','speed','design_speed','v'): cm[c]='Speed_kmh'
                    elif cl in ('sd_type','sd','sight_distance'): cm[c]='SD_Type'
                    elif cl in ('curve_type','curve','vc_type','vertical_curve'): cm[c]='Curve_Type'
                rdf2 = rdf2.rename(columns=cm)
                dup_cols = duplicate_columns_after_mapping(rdf2.columns)
                if dup_cols: st.error(f'Duplicate columns: {", ".join(dup_cols)}.')
                elif 'N' not in rdf2.columns or 'Speed_kmh' not in rdf2.columns: st.error('CSV must have N and Speed_kmh columns.')
                else:
                    if 'SD_Type' not in rdf2.columns: rdf2['SD_Type']=''
                    if 'Curve_Type' not in rdf2.columns: rdf2['Curve_Type']=''
                    st.success(f'{len(rdf2):,} rows loaded.')
                    with st.spinner('Computing...'):
                        res2 = results_from_df(rdf2)
                    tot=len(res2); err=res2['Notes'].str.startswith(WARN_PREFIX,na=False).sum()
                    lgov=res2['Notes'].str.contains('Lmin governs',na=False).sum()
                    nc=(res2['Curve Type']=='Crest').sum(); ns=(res2['Curve Type']=='Sag').sum()
                    s1,s2,s3,s4,s5=st.columns(5)
                    s1.metric('Total',f'{tot:,}'); s2.metric('Crest',f'{nc:,}'); s3.metric('Sag',f'{ns:,}')
                    s4.metric('Lmin governs',f'{lgov:,}'); s5.metric('Errors',f'{err:,}')
                    st.dataframe(res2, width="stretch", hide_index=True)
                    co2=io.StringIO(); res2.to_csv(co2,index=False)
                    st.download_button('Download Results (CSV)',data=co2.getvalue(),file_name=f'vc_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',mime='text/csv',key='dl_batch')
                    plot_calc(res2)
            except Exception as e:
                st.error(f'Error reading file: {e}')

# ----------------------------------------------------------------------
# VERIFY MODE
# ----------------------------------------------------------------------
if not _design_mode:
    expr_chip = '<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''
    ct_chip = '<span class="chip chip-blue">Crest</span>' if curve_type=='Crest' else '<span class="chip chip-amber">Sag</span>'
    sd_chip = f'<span class="chip chip-blue">{sd_type}</span>' if curve_type=='Crest' else '<span class="chip chip-amber">HSD</span>'
    road_chip = '<span class="chip chip-green">Expressway</span>' if expressway else '<span class="chip chip-green">Standard</span>'
    verify_curve_default = curve_type
    verify_crest_sd_default = sd_type if sd_type in VALID_CREST_SD_TYPES else DEFAULT_CREST_SD_TYPE
    st.markdown(
        '<div class="vc-header">'
        '<div class="vc-header-left"><h1>Verify Existing Curve</h1><p>IRC:73-2023 | Adequacy Check</p></div>'
        f'<div class="vc-header-right">{ct_chip}{sd_chip}{road_chip}{expr_chip}</div>'
        '</div>',
        unsafe_allow_html=True
    )

    def verify_curve(N_decimal, L, spd, cv_type, sdt, expr):
        """
        Verification — mirrors the design chart (IRC:73-2023).
        N_crossover = denom / S_req divides the chart at L = S.
          N >= N_crossover → F1 → L_req = (N × S²) / denom
          N <  N_crossover → F2 → L_req = 2S − denom / N
        L_required = max(L_req, Lmin). ADEQUATE if L >= L_required AND K >= K_min.
        """
        try:
            N_v = parse_positive_number(N_decimal, 'N')
            if N_v >= 1: return {'error':'N must be decimal < 1 (e.g. 0.01) or explicit percent (e.g. 1%)'}
            N_pct_val = N_v * 100.0
            L_v = parse_positive_number(L, 'L')
            spd = parse_speed(spd); cv_type = normalize_curve_type(cv_type)
            if spd not in sd_table: return {'error':f'Speed {spd} not in IRC table'}
            if spd==120 and not expr: return {'error':'120 km/h for Expressway only'}
            Lmn = min_length.get(spd, 0)
            K_exist = round(L_v / N_pct_val, 2)
            if cv_type == 'Sag':
                S_req = hsd_table.get(spd)
                if S_req is None: return {'error':f'HSD not defined for {spd} km/h'}
                denom = headlight_factor(S_req); Kmin = k_min_sag.get(spd); sdt_used = 'HSD'
            else:
                sdt = normalize_crest_sd_type(sdt, DEFAULT_CREST_SD_TYPE)
                if sdt=='OSD' and spd<OSD_MIN: return {'error':f'OSD N/A for {spd} km/h (min {OSD_MIN} km/h)'}
                S_req = sd_table[spd][sd_index[sdt]]
                if S_req is None: return {'error':f'{sdt} not defined for {spd} km/h'}
                h1_,h2_ = heights[sdt]; denom = (np.sqrt(2*h1_)+np.sqrt(2*h2_))**2
                Kmin = k_min_crest.get(sdt,{}).get(spd); sdt_used = sdt
            N_crossover = round(denom/S_req, 6)
            if N_v >= N_crossover:
                formula_branch = 'F1  (N ≥ N_crossover, L ≥ S)'
                L_formula = (N_v*S_req**2)/denom
            else:
                formula_branch = 'F2  (N < N_crossover, L < S)'
                L_formula = 2*S_req - denom/N_v
            L_required = round(max(L_formula, Lmn), 2)
            lmin_governs = Lmn > L_formula
            lreq_pass = L_v >= L_required
            lreq_margin = round(L_v - L_required, 2)
            k_pass = (Kmin is None) or (K_exist >= Kmin)
            k_margin = round(K_exist - Kmin, 2) if Kmin is not None else None
            gct = grade_change_threshold.get(spd)
            vc_required = (gct is None) or (N_pct_val > gct)
            return {'error':None,'N_decimal':round(N_v,5),'N_crossover':N_crossover,
                'formula_branch':formula_branch,'S_req':S_req,'L_formula':round(L_formula,2),
                'L_min':Lmn,'lmin_governs':lmin_governs,'L_required':L_required,
                'lreq_pass':lreq_pass,'lreq_margin':lreq_margin,
                'K_exist':K_exist,'K_min':Kmin,'k_pass':k_pass,'k_margin':k_margin,
                'gct':gct,'vc_required':vc_required,'sdt_used':sdt_used}
        except Exception as e:
            return {'error':str(e)}

    def failing_checks(res):
        issues = []
        if not res['lreq_pass']: issues.append(f'Curve length (need {res["L_required"]}m, have {res.get("L_input","?")}m)')
        if res['K_min'] is not None and not res['k_pass']: issues.append(f'K value (need {res["K_min"]}, have {res["K_exist"]})')
        return issues

    def review_note_for_result(res):
        issues = []
        if not res['lreq_pass']: issues.append(f'Length short by {abs(res["lreq_margin"]):.2f} m (L_req={res["L_required"]}m)')
        if res['K_min'] is not None and not res['k_pass']: issues.append(f'K short by {abs(res["k_margin"]):.2f}')
        return '; '.join(issues) if issues else 'All checks passed'

    def render_check(label, passed, value, required, unit, margin, note=None):
        icon='PASS' if passed else 'FAIL'
        color=COLORS['success'] if passed else COLORS['danger']
        ms=f'+{margin} {unit}' if margin>=0 else f'{margin} {unit}'
        mc=COLORS['success'] if margin>=0 else COLORS['danger']
        st.markdown(f"""<div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']};border-left:3px solid {color};border-radius:6px;padding:0.55rem 1rem;margin-bottom:0.5rem;font-family:'JetBrains Mono',monospace;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.8rem;color:#C9D1D9;">{icon}  {label}</span>
            <span style="font-size:0.75rem;color:{mc};font-weight:600;">{ms}</span>
          </div>
          <div style="font-size:0.68rem;color:{COLORS['muted']};margin-top:3px;">
            Available: <b style="color:#C9D1D9;">{value} {unit}</b> &nbsp;|&nbsp; Required: <b style="color:#C9D1D9;">{required} {unit}</b>{' &nbsp;|&nbsp; '+note if note else ''}
          </div></div>""", unsafe_allow_html=True)

    def render_verify_result(res, spd, L_input, curve_type_used, label=None):
        if res.get('error'): st.error(f'{WARN_PREFIX} {res["error"]}'); return
        all_pass = res['lreq_pass'] and res['k_pass']
        vc=COLORS['success'] if all_pass else COLORS['danger']
        vt='ADEQUATE' if all_pass else 'INADEQUATE'
        vi='PASS' if all_pass else 'FAIL'
        prefix=f'{label} | ' if label else ''
        lmin_note='  ←  Lmin governs' if res['lmin_governs'] else ''
        st.markdown(f"""<div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']};border-left:4px solid {vc};border-radius:8px;padding:0.7rem 1.2rem;margin-bottom:0.6rem;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;font-weight:600;color:{vc};">{vi}  {prefix}{vt}</div>
          <div style="font-size:0.68rem;color:{COLORS['muted']};margin-top:3px;">
            {curve_type_used} | {spd} km/h | {res['sdt_used']} | N = {res['N_decimal']} | L = {L_input} m | K = {res['K_exist']}
          </div>
          <div style="font-size:0.67rem;color:{COLORS['muted']};margin-top:2px;">
            N_crossover = {res['N_crossover']} → {res['formula_branch']} | S_req = {res['S_req']} m | L_required = {res['L_required']} m{lmin_note}
          </div></div>""", unsafe_allow_html=True)
        lms=f'+{res["lreq_margin"]} m' if res['lreq_margin']>=0 else f'{res["lreq_margin"]} m'
        lc=COLORS['success'] if res['lreq_pass'] else COLORS['danger']
        gl='Lmin (Table 7.5)' if res['lmin_governs'] else res['formula_branch'].split('(')[0].strip()
        st.markdown(f"""<div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']};border-left:3px solid {lc};border-radius:6px;padding:0.55rem 1rem;margin-bottom:0.5rem;font-family:'JetBrains Mono',monospace;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.8rem;color:#C9D1D9;">{'PASS' if res['lreq_pass'] else 'FAIL'}  Curve Length  —  SD achieved + Lmin satisfied</span>
            <span style="font-size:0.75rem;color:{lc};font-weight:600;">{lms}</span>
          </div>
          <div style="font-size:0.68rem;color:{COLORS['muted']};margin-top:3px;">
            Provided: <b style="color:#C9D1D9;">{L_input} m</b> &nbsp;|&nbsp; Required: <b style="color:#C9D1D9;">{res['L_required']} m</b> &nbsp;|&nbsp; Governing: {gl}
          </div></div>""", unsafe_allow_html=True)
        if res['K_min'] is not None:
            render_check('K Value  (IRC Table 7.3)', res['k_pass'], res['K_exist'], res['K_min'], '', res['k_margin'], 'K = L / [100 × N]')
        else:
            st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-left:3px solid {COLORS["muted"]};border-radius:6px;padding:0.45rem 1rem;margin-bottom:0.45rem;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:{COLORS["muted"]};">INFO: K_min not listed in IRC Table 7.3 for 120 km/h</div>', unsafe_allow_html=True)
        if res['gct'] is not None:
            vc_note=('VC not required' if not res['vc_required'] else 'VC required')+f' at this grade change  (threshold {res["gct"]}%)'
            st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-left:3px solid {COLORS["muted"]};border-radius:6px;padding:0.45rem 1rem;margin-bottom:0.45rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;color:{COLORS["muted"]};">INFO: {vc_note}</div>', unsafe_allow_html=True)

    def verify_report_row(row_num, review_status, reviewer_note, failing_checks_text, spd, L_input, curve_type_used, sdt_used, res=None):
        ok = res and not res.get('error')
        def g(key, fallback=NO_DATA_MARKER): return res[key] if ok and res.get(key) is not None else fallback
        k_check=('PASS' if res['k_pass'] else ('FAIL' if res['K_min'] is not None else 'N/A')) if ok else NO_DATA_MARKER
        k_margin=(res['k_margin'] if res['k_margin'] is not None else 'N/A') if ok else NO_DATA_MARKER
        return {'Review Status':review_status,'Reviewer Note':reviewer_note,'Failing Checks':failing_checks_text,
            'Row':row_num,'Speed (km/h)':spd,'Curve Type':curve_type_used,'SD Basis':sdt_used,
            'N (decimal)':g('N_decimal'),'L Provided (m)':L_input,'S_req (m)':g('S_req'),
            'N_crossover':g('N_crossover'),'Formula Branch':g('formula_branch'),
            'L from Formula (m)':g('L_formula'),'Lmin — Table 7.5 (m)':g('L_min'),
            'Lmin Governs':('Yes' if res['lmin_governs'] else 'No') if ok else NO_DATA_MARKER,
            'L_required (m)':g('L_required'),
            'Length Status':('PASS' if res['lreq_pass'] else 'FAIL') if ok else NO_DATA_MARKER,
            'Length Margin (m)':g('lreq_margin'),'K = L / [100×N]':g('K_exist'),
            'K_min — Table 7.3':g('K_min','N/A'),'K Status':k_check,'K Margin':k_margin,
            'VC Required at Grade Change':('Yes' if res['vc_required'] else 'No') if ok else NO_DATA_MARKER,
            'Grade Change Threshold (%)':g('gct')}

    def verify_error_row(row_num, spd, N_input, L_input, curve_type_used, sdt_used, message):
        return verify_report_row(row_num=row_num,review_status='ERROR',
            reviewer_note=f'{WARN_PREFIX} {message} | N entered: {N_input}',
            failing_checks_text='Input/processing error',
            spd=spd if spd not in (None,'') else NO_DATA_MARKER,
            L_input=L_input if L_input not in (None,'') else NO_DATA_MARKER,
            curve_type_used=curve_type_used if curve_type_used not in (None,'') else NO_DATA_MARKER,
            sdt_used=sdt_used if sdt_used not in (None,'') else NO_DATA_MARKER,res=None)

    def verify_to_row(res, row_num, spd, N_input, L_input, curve_type_used, sdt_used):
        if res.get('error'): return verify_error_row(row_num,spd,N_input,L_input,curve_type_used,sdt_used,res['error'])
        all_pass = res['lreq_pass'] and res['k_pass']
        fc = failing_checks({**res,'L_input':L_input})
        return verify_report_row(row_num=row_num,
            review_status='ADEQUATE' if all_pass else 'INADEQUATE',
            reviewer_note=review_note_for_result(res),
            failing_checks_text=', '.join(fc) if fc else 'None',
            spd=spd,L_input=L_input,curve_type_used=curve_type_used,sdt_used=res['sdt_used'],res=res)

    vtm, vtb = st.tabs(['Manual Entry', 'Batch Upload'])

    with vtm:
        st.markdown(f"<span style='font-size:0.78rem;color:#8B949E'>N as decimal < 1 (e.g. 0.01) or explicit percent (e.g. 1%). Bare values like 1 rejected. Blank Curve_Type uses sidebar default ({verify_curve_default}). Blank SD_Type uses sidebar default for Crest ({verify_crest_sd_default}); Sag always uses HSD.</span>", unsafe_allow_html=True)
        v_default = pd.DataFrame({'N':['0.045','7.2%','3.6%'],'L (m)':[260.0,400.0,180.0],'Speed_kmh':[80,100,80],'SD_Type':['ISD','ISD',''],'Curve_Type':['Crest','Crest','Sag']})
        v_idf = st.data_editor(v_default, num_rows='dynamic', width='stretch',
            column_config={'N':st.column_config.TextColumn('N / grade change (decimal or %)',required=True),
                'L (m)':st.column_config.NumberColumn('L (m)',min_value=1.0,step=1.0,format='%.1f',required=True),
                'Speed_kmh':st.column_config.SelectboxColumn('Speed (km/h)',options=available_speeds,required=True),
                'SD_Type':st.column_config.SelectboxColumn('SD Type (blank=sidebar default)',options=['','SSD','ISD','OSD']),
                'Curve_Type':st.column_config.SelectboxColumn('Curve Type (blank=sidebar default)',options=['','Crest','Sag'])},
            hide_index=True, key='verify_manual_editor')
        if v_idf is not None and len(v_idf)>0:
            v_rows=[]
            for i,row in v_idf.iterrows():
                try:
                    N_input=row['N']; N_p=parse_N(N_input)
                    L_v=parse_positive_number(row['L (m)'],'L')
                    spd_v=parse_speed(row['Speed_kmh'])
                    curve_v,sdt_v=resolve_verify_inputs(row.get('Curve_Type',''),row.get('SD_Type',''),verify_curve_default,verify_crest_sd_default)
                    res=verify_curve(N_p,L_v,spd_v,curve_v,sdt_v,expressway)
                    st.markdown(f'**Curve {i+1}** — {curve_v}, {spd_v} km/h, N={N_input}, L={L_v}m, SD={sdt_v}')
                    render_verify_result(res,spd_v,L_v,curve_v)
                    v_rows.append(verify_to_row(res,i+1,spd_v,N_input,L_v,curve_v,sdt_v))
                except Exception as e:
                    st.error(f'Row {i+1}: {e}')
                    v_rows.append(verify_error_row(i+1,row.get('Speed_kmh',NO_DATA_MARKER),row.get('N',NO_DATA_MARKER),row.get('L (m)',NO_DATA_MARKER),row.get('Curve_Type',verify_curve_default),row.get('SD_Type',verify_crest_sd_default),str(e)))
            if v_rows:
                vdf=pd.DataFrame(v_rows)
                st.markdown("#### Summary Table")
                st.dataframe(vdf,width='stretch',hide_index=True)
                vcsv=io.StringIO(); vdf.to_csv(vcsv,index=False)
                st.download_button('Export Verification Report (CSV)',data=vcsv.getvalue(),file_name=f'vc_verify_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',mime='text/csv',key='dl_verify_manual')

    with vtb:
        v_tmpl=pd.DataFrame({'N':['0.045','7.2%','3.6%','0.031'],'L_m':[260.0,400.0,180.0,120.0],'Speed_kmh':[80,100,80,60],'Curve_Type':['Crest','Crest','Sag','Crest'],'SD_Type':['ISD','ISD','','SSD']})
        v_tb_buf=io.StringIO(); v_tmpl.to_csv(v_tb_buf,index=False)
        vc1,vc2=st.columns([3,1])
        with vc1:
            st.markdown(f'<div class="info-box"><b>CSV columns:</b> <code>N</code> | <code>L_m</code> | <code>Speed_kmh</code> | <code>Curve_Type</code> (opt) | <code>SD_Type</code> (opt)<br>Blank Curve_Type → sidebar default ({verify_curve_default}). Blank SD_Type → sidebar default for Crest ({verify_crest_sd_default}). Sag always uses HSD. N as decimal < 1 or explicit %. Header required.</div>', unsafe_allow_html=True)
        with vc2:
            st.download_button('Template',data=v_tb_buf.getvalue(),file_name='vc_verify_template.csv',mime='text/csv',key='dl_verify_tmpl')
        v_up=st.file_uploader('Upload CSV',type=['csv'],label_visibility='collapsed',key='verify_batch_uploader')
        if v_up is not None:
            try:
                v_raw=pd.read_csv(v_up,dtype={'N':str})
                v_raw.columns=[c.strip() for c in v_raw.columns]
                vcm={}
                for c in v_raw.columns:
                    cl=normalize_header(c)
                    if cl in ('n','deviation_angle','dev_angle','angle'): vcm[c]='N'
                    elif cl in ('l_m','l','length','curve_length'): vcm[c]='L_m'
                    elif cl in ('speed_kmh','speed_km_h','speed','design_speed','v'): vcm[c]='Speed_kmh'
                    elif cl in ('sd_type','sd','sight_distance'): vcm[c]='SD_Type'
                    elif cl in ('curve_type','curve','vc_type','vertical_curve'): vcm[c]='Curve_Type'
                v_raw=v_raw.rename(columns=vcm)
                dup_cols=duplicate_columns_after_mapping(v_raw.columns)
                if dup_cols: st.error(f'Duplicate columns: {", ".join(dup_cols)}.')
                elif 'N' not in v_raw.columns or 'L_m' not in v_raw.columns or 'Speed_kmh' not in v_raw.columns:
                    st.error('CSV must have N, L_m, and Speed_kmh columns.')
                else:
                    if 'SD_Type' not in v_raw.columns: v_raw['SD_Type']=''
                    if 'Curve_Type' not in v_raw.columns: v_raw['Curve_Type']=''
                    st.success(f'{len(v_raw):,} rows loaded.')
                    v_rows=[]
                    for i,row in v_raw.iterrows():
                        try:
                            N_input=row['N']; N_p=parse_N(N_input)
                            L_v=parse_positive_number(row['L_m'],'L'); spd_v=parse_speed(row['Speed_kmh'])
                            curve_v,sdt_v=resolve_verify_inputs(row.get('Curve_Type',''),row.get('SD_Type',''),verify_curve_default,verify_crest_sd_default)
                            res=verify_curve(N_p,L_v,spd_v,curve_v,sdt_v,expressway)
                            v_rows.append(verify_to_row(res,i+1,spd_v,N_input,L_v,curve_v,sdt_v))
                        except Exception as e:
                            v_rows.append(verify_error_row(i+1,row.get('Speed_kmh',NO_DATA_MARKER),row.get('N',NO_DATA_MARKER),row.get('L_m',NO_DATA_MARKER),row.get('Curve_Type',verify_curve_default),row.get('SD_Type',verify_crest_sd_default),str(e)))
                    vdf=pd.DataFrame(v_rows)
                    tot=len(vdf); adq=(vdf['Review Status']=='ADEQUATE').sum()
                    inadq=(vdf['Review Status']=='INADEQUATE').sum(); errs=(vdf['Review Status']=='ERROR').sum()
                    vs1,vs2,vs3,vs4=st.columns(4)
                    vs1.metric('Total',f'{tot:,}'); vs2.metric('Adequate',f'{adq:,}')
                    vs3.metric('Inadequate',f'{inadq:,}'); vs4.metric('Errors',f'{errs:,}')
                    st.dataframe(vdf,width='stretch',hide_index=True)
                    vcsv=io.StringIO(); vdf.to_csv(vcsv,index=False)
                    st.download_button('Export Verification Report (CSV)',data=vcsv.getvalue(),file_name=f'vc_verify_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',mime='text/csv',key='dl_verify_batch')
            except Exception as e:
                st.error(f'Error reading file: {e}')

# ----------------------------------------------------------------------
# FOOTNOTE
# ----------------------------------------------------------------------
en='Expressway: Lmin 80→70, 100→85, 120→100m | ' if expressway else ''
st.markdown(f'* {en}Lmin IRC:73-2023 Table 7.5 | Crest: SSD/ISD/OSD with h1/h2 per sight-distance type | Sag: HSD with h1={SAG_H1}m and alpha={SAG_ALPHA}° | OSD≥{OSD_MIN}km/h | 120km/h Expressway only | K = L / [100×N(decimal)]', unsafe_allow_html=True)
