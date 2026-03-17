# Vertical Curves.py - IRC:73-2023 Vertical Curve Design & Verification Tool
# Fixed version: Syntax errors, CSS typos, data gaps, and logic issues resolved

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import streamlit as st
import datetime
import io
import pandas as pd

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title='Vertical Curve Explorer',
    page_icon='🛣️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ----------------------------------------------------------------------
# GLOBAL CSS (Fixed typos)
# ----------------------------------------------------------------------
st.markdown("""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#0D1117;color:#C9D1D9;}
.stApp{background:#0D1117;}
.main .block-container{padding-top:0.8rem;padding-bottom:1.5rem;max-width:100%;background:#0D1117;}

/*  ── Sidebar ── */
section[data-testid="stSidebar"]{background:#010409;border-right:1px solid #21262D;}
section[data-testid="stSidebar"] *{color:#8B949E!important;}
section[data-testid="stSidebar"] hr{border-color:#21262D!important;margin:0.7rem 0!important;}
section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] h4,section[data-testid="stSidebar"] h5{
    color:#E6EDF3!important;font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;letter-spacing:0.04em!important;}
section[data-testid="stSidebar"]  .stRadio label,
section[data-testid="stSidebar"] .stCheckbox label{color:#C9D1D9!important;}

/* ── Header strip ── */
.vc-header{
    display:flex;align-items:center;justify-content:space-between;
    background:#161B22;border:1px solid #21262D;border-left:3px solid #58A6FF;
    border-radius:8px;padding:0.75rem 1.4rem;margin-bottom:0.9rem;
}
.vc-header-left h1{
    font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:600;
    color:#E6EDF3;margin:0;letter-spacing:-0.01em;
}
.vc-header-left p{font-size:0.72rem;color:#8B949E;margin:0.2rem 0 0;}
.vc-header-right{display:flex;flex-wrap:wrap;gap:0.35rem;align-items:center;justify-content:flex-end;}

/* ── Chips / badges ── */
.chip{
    display:inline-flex;align-items:center;
    font-family:'JetBrains Mono',monospace;font-size:0.67rem;font-weight:500;
    padding:0.18rem 0.6rem;border-radius:20px;letter-spacing:0.04em;
    border:1px solid;white-space:nowrap;
}
.chip-blue  {color:#79C0FF;border-color:#1F6FEB;background:#0D1117;}
.chip-green {color:#56D364;border-color:#238636;background:#0D1117;}
.chip-amber {color:#F0883E;border-color:#9E6A03;background:#0D1117;}
.chip-purple{color:#D2A8FF;border-color:#6E40C9;background:#0D1117;}
.chip-muted {color:#8B949E;border-color:#30363D;background:#0D1117;}

/* ── Formula strip ── */
.formula-strip{
    display:flex;gap:0.6rem;margin-bottom:0.7rem;
    background:#161B22;border:1px solid #21262D;border-radius:8px;padding:0.65rem 1rem;
    font-family:'JetBrains Mono',monospace;font-size:0.78rem;
}
.formula-strip .divider{color:#30363D;margin:0 0.2rem;}
.f-label{color:#8B949E;font-size:0.65rem;text-transform:uppercase;letter-spacing:0.07em;margin-right:0.4rem;}
.f-eq{color:#C9D1D9;}
.f-eq.f1{color:#79C0FF;}
.f-eq.f2{color:#FF7B72;}
.f-sub{color:#8B949E;font-size:0.65rem;margin-left:0.5rem;}

/* ── Formula cards (split view) ── */
.formula-card{background:#161B22;border:1px solid #21262D;border-left:3px solid #58A6FF;
    border-radius:6px;padding:0.55rem 1rem;margin-bottom:0.5rem;
    font-family:'JetBrains Mono',monospace;font-size:0.78rem;color:#C9D1D9;}
.formula-card.green{border-left-color:#238636;}
.formula-card.red  {border-left-color:#DA3633;}
.formula-card.amber{border-left-color:#9E6A03;}

/* ── Download button ── */
.stDownloadButton button{
    background:#161B22!important;color:#79C0FF!important;
    border:1px solid #30363D!important;font-family:'JetBrains Mono',monospace!important;
    font-size:0.74rem!important;font-weight:500!important;letter-spacing:0.03em!important;
    border-radius:6px!important;padding:0.35rem 1rem!important;width:100%;
    transition:all 0.15s!important;
}
.stDownloadButton button:hover{background:#1F6FEB!important;color:#fff!important;border-color:#1F6FEB!important;}

/* ── Metric tiles ── */
.metric-tile{
    background:#161B22;border:1px solid #21262D;border-top:2px solid #21262D;
     border-radius:6px;padding:0.55rem 0.9rem;transition:border-top-color 0.2s;
}
.metric-tile:hover{border-top-color:#58A6FF;}
.metric-tile .label{font-size:0.6rem;color:#8B949E;text-transform:uppercase;letter-spacing:0.09em;font-weight:600;}
.metric-tile .value{font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;color:#79C0FF;}
.metric-tile .unit{font-size:0.6rem;color:#8B949E;}
.metric-tile .sub{font-size:0.62rem;color:#8B949E;margin-top:3px;font-family:'JetBrains Mono',monospace;}

/* ── Info / warn boxes ── */
 .info-box{background:#161B22;border:1px solid #1F6FEB;border-radius:6px;
    padding:0.7rem 1rem;font-size:0.76rem;color:#79C0FF;margin-bottom:0.8rem;}
.footnote{font-size:0.67rem; color:#8B949E;border-top:1px solid #21262D;
    padding-top:0.5rem;margin-top:0.5rem;font-family:'JetBrains Mono',monospace;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#0D1117;}
::-webkit-scrollbar-thumb{background:#30363D;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#8B949E;}

/*  ── Dataframe ── */
.stDataFrame{border:1px solid #21262D!important;border-radius:6px;}
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# COLOUR PALETTE
# ----------------------------------------------------------------------
COLORS = {
    'primary':          '#58A6FF',
    'danger':           '#FF7B72',
    'success':          '#3FB950',
    'warning':          '#F0883E',
    'muted':            '#8B949E',
    'border':           '#21262D',
    'bg_card':          '#161B22',
    'bg_plot':          '#0D1117',
    'axis_label_color': '#8B949E',
    'envelope_line':    '#C9D1D9',
    'grid_color':       '#21262D',
}

# ----------------------------------------------------------------------
# IRC DATA & HELPERS
# ----------------------------------------------------------------------
sd_table={20:(20,40,None),25:(25,50,None),30:(30,60,None),40:(45,90,135),50:(60,120,235),60:(80,160,300),65:(90,180,340),80:(130,260,470),100:(180,360,640),120:(250,500,835)}
heights={'SSD':(1.2,0.15),'ISD':(1.2,1.20),'OSD':(1.2,1.20)}
sd_index={'SSD':0,'ISD':1,'OSD':2}
OSD_MIN=40
hsd_table={spd:vals[0] for spd,vals in sd_table.items()}
SAG_H1=0.75
SAG_ALPHA=1.0
SAG_TAN=np.tan(np.radians(SAG_ALPHA))

def headlight_factor(S):
    return 2*SAG_H1 + 2*S*SAG_TAN

# IRC Table 7.3 — K values for L≥S case (coefficient of N gives L)
k_min_crest = {
    'SSD': {20:0.9,  25:1.4,  30:2.0,  35:3.6,  40:4.6,
            50:8.2,  60:14.5, 65:18.4, 80:38.4, 100:73.6, 120:110.0},
    'ISD': {20:1.7,  25:2.6,  30:3.8,  35:6.7,  40:8.4,
            50:15.0, 60:26.7, 65:33.8, 80:70.4, 100:135.0, 120:200.0},
    'OSD': {40:28.4, 50:57.5, 60:93.7, 65:120.4,
            80:230.1, 100:426.7, 120:650.0},
}

k_min_sag = {
    20:1.8,  25:2.6,  30:3.5,  35:5.5,  40:6.6,
    50:10.0, 60:14.9, 65:17.4, 80:27.9, 100:41.5, 120:60.0
}

grade_change_threshold = {
    20:1.5, 25:1.5, 30:1.5, 35:1.5,
    40:1.2, 50:1.0, 60:0.8, 65:0.8,
    80:0.6, 100:0.5, 120:0.5
}

min_length_standard={20:15,25:15,30:15,40:20,50:30,60:40,65:40,80:50,100:60,120:100}
min_length_expressway={**min_length_standard,80:70,100:85,120:100}
formula_label={'SSD':('h₁=1.2m, h₂=0.15m',''),'ISD':('h₁=1.2m, h₂=1.20m',''),'OSD':('h₁=1.2m, h₂=1.20m','')}
all_speeds=list(sd_table.keys())
standard_speeds=[s for s in all_speeds if s!=120]
colors=plt.cm.tab10(np.linspace(0,0.85,len(all_speeds)))
spd_color={spd:col for spd,col in zip(all_speeds,colors)}

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛣️ Vertical Curve\nExplorer")
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
        split_formulas = False
        show_min = False
        show_env = False

    st.markdown("---")
    st.caption(f"IRC:73-2023 | {datetime.date.today().strftime('%d %b %Y')}")

# ----------------------------------------------------------------------
# FORMULA STRINGS
# ----------------------------------------------------------------------
f1_crest = "L = (N·S²) / ( (√(2h₁) + √(2h₂))² )"
f2_crest = "L = 2S − ( (√(2h₁) + √(2h₂))² ) / N"
f1_sag = "L = (N·S²) / (2h₁ + 2S·tanα)"
f2_sag = "L = 2S − (2h₁ + 2S·tanα) / N"
view_mode = "🔬 Formula Analysis" if split_formulas else "📐 Design Chart"

# ----------------------------------------------------------------------
# AUTO AXIS COMPUTATION
# ----------------------------------------------------------------------
def auto_axes(speeds, cv_type, sdt, L_cap=1200):
    items = []
    for spd in speeds:
        if cv_type == 'Crest':
            if sdt not in sd_index: continue
            Sv = sd_table[spd][sd_index[sdt]]
            if Sv is None: continue
            h1_, h2_ = heights[sdt]
            dv = (np.sqrt(2*h1_) + np.sqrt(2*h2_))**2
        else:
            Sv = sd_table[spd][0]
            dv = headlight_factor(Sv)
        items.append((spd, Sv, dv))
    
    if not items:
        return 0.16, 700, 0.02, 100

    items_sorted = sorted(items, key=lambda x: x[1])
    spd_top, Sv_top, dv_top = items_sorted[-1]
    Nx_top = dv_top / Sv_top
    N_f1_cap = (L_cap * dv_top) / (Sv_top**2)
    xmax_raw = max(Nx_top * 3.5, N_f1_cap)
    xmax = min(round(xmax_raw / 0.005) * 0.005 + 0.005, 0.30)
    xmax = max(xmax, 0.005)  # Floor to prevent tiny windows

    N_arr_tmp = np.linspace(0.0005, xmax, 1000)
    Lmax = 0
    for spd, Sv, dv in items:
        Lmin_ = min_length.get(spd, 0)
        L1 = (N_arr_tmp * Sv**2) / dv
        L2 = 2*Sv - dv / N_arr_tmp
        L  = np.maximum(np.maximum(L1, L2), Lmin_)
        finite = L[np.isfinite(L) & (L < 50000)]
        if len(finite): Lmax = max(Lmax, finite.max())
    ymax = min(int(Lmax * 1.20 / 50 + 1) * 50, 2000)
    xgrid = max(round(xmax / 8 / 0.005) * 0.005, 0.005)
    ygrid = max(round(ymax / 7 / 50) * 50, 50)
    return xmax, ymax, xgrid, ygrid

xmax, ymax, xgrid, ygrid = auto_axes(selected_speeds, curve_type, sd_type)

# ----------------------------------------------------------------------
# DERIVED VALUES
# ----------------------------------------------------------------------
if curve_type == 'Crest':
    if sd_type in heights:
        h1_c, h2_c = heights[sd_type]
        denom_crest = (np.sqrt(2*h1_c) + np.sqrt(2*h2_c))**2
        h_note = formula_label[sd_type][0]
    else:
        h1_c, h2_c = None, None
        denom_crest = None
        h_note = 'HSD'
else:
    denom_crest = None
    h_note = f'h₁={SAG_H1}m, α={SAG_ALPHA}°'

N_arr = np.linspace(0.0005, xmax, 2000)
f1 = f1_crest if curve_type == 'Crest' else f1_sag
f2 = f2_crest if curve_type == 'Crest' else f2_sag

# ----------------------------------------------------------------------
# PLOT HELPERS
# ----------------------------------------------------------------------
matplotlib.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

def style_ax(ax):
    ax.set_facecolor(COLORS['bg_plot'])
    ax.tick_params(labelsize=8.5, colors=COLORS['muted'])
    for s in ax.spines.values():
        s.set_edgecolor(COLORS['border'])

def apply_axes(ax):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks(np.arange(0, xmax + xgrid, xgrid))
    ax.set_yticks(np.arange(0, ymax + ygrid, ygrid))
    ax.grid(True, color=COLORS['grid_color'], linewidth=0.8, zorder=0)
    ax.set_xlabel('Deviation Angle   N', fontsize=9.5, color=COLORS['axis_label_color'], labelpad=6)
    ax.set_ylabel('Length of Vertical Curve   L  (m)', fontsize=9.5, color=COLORS['axis_label_color'], labelpad=6)

def draw_min_lines(ax, spds):
    if not show_min: return
    seen = {}
    for s in spds:
        Lm = min_length.get(s)
        if Lm: seen.setdefault(Lm, []).append(s)
    for i, (Lm, ss) in enumerate(sorted(seen.items())):
        if 0 < Lm < ymax:
            ax.axhline(Lm, color=COLORS['muted'], linewidth=0.8, linestyle='-.', alpha=0.50, zorder=2)
            v_offset = ymax * 0.012 if i % 2 == 0 else -ymax * 0.022
            va = 'bottom' if i % 2 == 0 else 'top'
            ax.text(xmax*0.998, Lm+v_offset, f'Lmin={Lm}m  ({", ".join(str(x) for x in ss)} km/h)', fontsize=6, color=COLORS['muted'], ha='right', va=va, alpha=0.85)

def draw_envelope(ax, dfn):
    if not show_env: return None, None, None
    Sr = np.linspace(5, max(ymax*1.5, 1500), 6000)
    Ne = np.array([dfn(S)/S for S in Sr])
    mk = (Ne>0) & (Ne<xmax) & (Sr>0) & (Sr<ymax)
    if mk.any():
        ax.plot(Ne[mk], Sr[mk], color=COLORS['envelope_line'], linewidth=1.1, linestyle='--', alpha=0.80, zorder=5)
    return Ne, Sr, mk  # Always return tuple

def fin_legend(ax, spds, eh=None, el=None):
    if not spds: return
    h, l = ax.get_legend_handles_labels()
    if eh: h += eh; l += el
    leg = ax.legend(handles=h, labels=l, fontsize=7.5, loc='upper left', framealpha=0.90, facecolor=COLORS['bg_card'], edgecolor=COLORS['border'], ncol=2 if len(spds)>5 else 1)
    leg.get_frame().set_linewidth(0.8)
    for txt in leg.get_texts(): txt.set_color('#C9D1D9')

def std_extra():
    eh = [Line2D([0],[0], color=COLORS['envelope_line'], linewidth=1.1, linestyle='--', label='L=S boundary')]
    el = ['L=S boundary']
    if show_min:
        eh.append(Line2D([0],[0], color=COLORS['muted'], linewidth=0.9, linestyle='-.', label='Lmin (Table 7.5)'))
        el.append('Lmin (Table 7.5)')
    return eh, el

def plot_segs(ax, spd, S_val, dv, Lmin, col, lbl):
    Nx = dv / S_val
    vis_any = False
    labelled = False
    if Nx >= xmax:
        Lf2 = np.maximum(2*S_val - dv/N_arr, Lmin)
        v = (Lf2 >= 0) & (Lf2 <= ymax)
        if v.any():
            ax.plot(N_arr[v], Lf2[v], color=col, linewidth=1.8, solid_capstyle='round', zorder=3, label=lbl)
            labelled = vis_any = True
            Nt, Lt = N_arr[v][-1], Lf2[v][-1]
            if Lt < ymax * 0.97:
                ax.annotate('', xy=(Nt + xmax*0.012, Lt), xytext=(Nt, Lt), arrowprops=dict(arrowstyle='->', color=col, lw=0.8))
    else:
        mf2 = (N_arr > 0) & (N_arr <= Nx + 1e-9)
        Nf2 = N_arr[mf2]
        if len(Nf2) > 0:
            Lf2 = np.maximum(2*S_val - dv/Nf2, Lmin)
            v = (Lf2 >= 0) & (Lf2 <= ymax)
            if v.any():
                ax.plot(Nf2[v], Lf2[v], color=col, linewidth=1.8, solid_capstyle='round', zorder=3, label=lbl)
                labelled = vis_any = True
        mf1 = (N_arr >= Nx - 1e-9)
        Nf1 = N_arr[mf1]
        if len(Nf1) > 0:
            Lf1 = np.maximum((Nf1 * S_val**2) / dv, Lmin)
            v = (Lf1 >= 0) & (Lf1 <= ymax)
            if v.any():
                ax.plot(Nf1[v], Lf1[v], color=col, linewidth=1.8, solid_capstyle='round', zorder=3, label='_nolegend_')
                vis_any = True  # Grok's valid fix
    if 0 < S_val < ymax:
        ax.plot(Nx, S_val, 'o', color=col, markersize=5, zorder=6, alpha=0.90, markeredgecolor='white', markeredgewidth=0.6)
    if not labelled:
        ax.plot([], [], color=col, linewidth=1.8, label=lbl)
    return vis_any

def add_env_annotation(ax, res):
    if show_env and res and res[0] is not None:
        Ne, Sr, mk = res
        if mk.any():
            mid = len(Ne[mk]) // 3
            ax.annotate('L = S', xy=(Ne[mk][mid], Sr[mk][mid]), xytext=(-38, 18), textcoords='offset points', fontsize=8, fontstyle='italic', color='#E6EDF3', fontweight='bold', arrowprops=dict(arrowstyle='-', color='#8B949E', lw=0.6))

# ----------------------------------------------------------------------
# PLOT FUNCTIONS (CACHED)
# ----------------------------------------------------------------------
@st.cache_data
def crest_design(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    style_ax(ax)
    inv = []
    for spd in selected_speeds:
        Sv = sd_table[spd][sd_index[sd_type]]
        if Sv is None: continue
        Lmin = min_length.get(spd, 0)
        if not plot_segs(ax, spd, Sv, denom_crest, Lmin, spd_color[spd], f'{spd} km/h (S={Sv}m)'):
            inv.append(spd)
    add_env_annotation(ax, draw_envelope(ax, lambda S: denom_crest))
    draw_min_lines(ax, selected_speeds)
    if inv:
        ax.text(0.01, 0.012, 'Not visible: ' + ', '.join(f'{s} km/h' for s in inv), transform=ax.transAxes, fontsize=6.5, color=COLORS['muted'], style='italic', va='bottom')
    apply_axes(ax)
    ax.set_title('Design Chart  —  Crest Vertical Curve', fontsize=9, fontweight='bold', color=COLORS['success'], pad=10)
    ax.text(0.975, 0.965, '← F2  ·  crossover ●  ·  F1 →', transform=ax.transAxes, fontsize=7, ha='right', va='top', color=COLORS['success'], bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['bg_card'], edgecolor=COLORS['success'], linewidth=0.7, alpha=0.90))
    fin_legend(ax, selected_speeds, *std_extra())
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def crest_analysis(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    for ax, fn in [(ax1, 1), (ax2, 2)]:
        style_ax(ax)
        for spd in selected_speeds:
            Sv = sd_table[spd][sd_index[sd_type]]
            if Sv is None: continue
            L = (N_arr * Sv**2) / denom_crest if fn == 1 else 2*Sv - denom_crest / N_arr
            ax.plot(N_arr, L, color=spd_color[spd], linewidth=1.8, label=f'{spd} km/h (S={Sv}m)', solid_capstyle='round')
        res = draw_envelope(ax, lambda S: denom_crest)
        if show_env and res and res[0] is not None:
            Ne, Sr, mk = res
            if mk.any():
                sh = '#1C4B8F' if fn == 1 else '#8B1A1A'
                if fn == 1: ax.fill_betweenx(Sr[mk], Ne[mk], xmax, color=sh, alpha=0.35, zorder=0)
                else: ax.fill_betweenx(Sr[mk], 0, Ne[mk], color=sh, alpha=0.35, zorder=0)
                mid = len(Ne[mk]) // 3
                off = (-38, 18) if fn == 1 else (-38, -18)
                lbl_col = COLORS['primary'] if fn == 1 else COLORS['danger']
                ax.annotate('L  > S' if fn == 1 else 'L  < S', xy=(Ne[mk][mid], Sr[mk][mid]), xytext=off, textcoords='offset points', fontsize=8.5, fontstyle='italic', color=lbl_col, fontweight='bold', arrowprops=dict(arrowstyle='-', color='#8B949E', lw=0.6))
        for spd in selected_speeds:
            Sv = sd_table[spd][sd_index[sd_type]]
            if Sv and 0 < Sv < ymax: ax.axhline(Sv, color=spd_color[spd], linewidth=0.4, linestyle='--', alpha=0.18)
        draw_min_lines(ax, selected_speeds)
        apply_axes(ax)
        cond = 'L ≥ S' if fn == 1 else 'L ≤ S'
        tcol = COLORS['primary'] if fn == 1 else COLORS['danger']
        ax.set_title(f'Formula {fn}  —  Valid when  {cond}', fontsize=9, fontweight='bold', color=tcol, pad=10)
        bt = 'Valid  →  right of envelope' if fn == 1 else 'Valid  →  left of envelope'
        ax.text(0.975, 0.965, bt, transform=ax.transAxes, fontsize=7, ha='right', va='top', color=tcol, bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['bg_card'], edgecolor=tcol, linewidth=0.7, alpha=0.90))
    fin_legend(ax, selected_speeds, *std_extra())
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def sag_design(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    style_ax(ax)
    inv = []
    for spd in selected_speeds:
        Sv = hsd_table.get(spd)
        if Sv is None: continue
        Lmin = min_length.get(spd, 0)
        ds = headlight_factor(Sv)
        if not plot_segs(ax, spd, Sv, ds, Lmin, spd_color[spd], f'{spd} km/h (HSD={Sv}m)'):
            inv.append(spd)
    add_env_annotation(ax, draw_envelope(ax, headlight_factor))
    draw_min_lines(ax, selected_speeds)
    if inv:
        ax.text(0.01, 0.012, 'Not visible: ' + ', '.join(f'{s} km/h' for s in inv), transform=ax.transAxes, fontsize=6.5, color=COLORS['muted'], style='italic', va='bottom')
    apply_axes(ax)
    ax.set_title('Design Chart  —  Sag Vertical Curve', fontsize=9, fontweight='bold', color=COLORS['warning'], pad=10)
    ax.text(0.975, 0.965, '← F2  ·  crossover ●  ·  F1 →', transform=ax.transAxes, fontsize=7, ha='right', va='top', color=COLORS['warning'], bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['bg_card'], edgecolor=COLORS['warning'], linewidth=0.7, alpha=0.90))
    fin_legend(ax, selected_speeds, *std_extra())
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def sag_analysis(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    for ax, fn in [(ax1, 1), (ax2, 2)]:
        style_ax(ax)
        for spd in selected_speeds:
            Sv = hsd_table.get(spd)
            if Sv is None: continue
            ds = headlight_factor(Sv)
            L = (N_arr * Sv**2) / ds if fn == 1 else 2*Sv - ds / N_arr
            ax.plot(N_arr, L, color=spd_color[spd], linewidth=1.8, label=f'{spd} km/h (HSD={Sv}m)', solid_capstyle='round')
        res = draw_envelope(ax, headlight_factor)
        if show_env and res and res[0] is not None:
            Ne, Sr, mk = res
            if mk.any():
                sh = '#1C4B8F' if fn == 1 else '#8B1A1A'
                if fn == 1: ax.fill_betweenx(Sr[mk], Ne[mk], xmax, color=sh, alpha=0.35, zorder=0)
                else: ax.fill_betweenx(Sr[mk], 0, Ne[mk], color=sh, alpha=0.35, zorder=0)
                mid = len(Ne[mk]) // 3
                off = (-38, 18) if fn == 1 else (-38, -18)
                lbl_col = COLORS['primary'] if fn == 1 else COLORS['danger']
                ax.annotate('L > S' if fn == 1 else 'L < S', xy=(Ne[mk][mid], Sr[mk][mid]), xytext=off, textcoords='offset points', fontsize=8.5, fontstyle='italic', color=lbl_col, fontweight='bold', arrowprops=dict(arrowstyle='-', color='#8B949E', lw=0.6))
        for spd in selected_speeds:
            Sv = hsd_table.get(spd)
            if Sv and 0 < Sv < ymax: ax.axhline(Sv, color=spd_color[spd], linewidth=0.4, linestyle='--', alpha=0.18)
        draw_min_lines(ax, selected_speeds)
        apply_axes(ax)
        cond = 'L ≥ S' if fn == 1 else 'L ≤ S'
        tcol = COLORS['primary'] if fn == 1 else COLORS['danger']
        ax.set_title(f'Formula {fn}  —  Valid when  {cond}', fontsize=9, fontweight='bold', color=tcol, pad=10)
        bt = 'Valid  →  right of envelope' if fn == 1 else 'Valid  →  left of envelope'
        ax.text(0.975, 0.965, bt, transform=ax.transAxes, fontsize=7, ha='right', va='top', color=tcol, bbox=dict(boxstyle='round,pad=0.4', facecolor=COLORS['bg_card'], edgecolor=tcol, linewidth=0.7, alpha=0.90))
    fin_legend(ax, selected_speeds, *std_extra())
    plt.tight_layout(pad=2.0)
    return fig

# ----------------------------------------------------------------------
# HELPER: parse_N (already exists, kept for clarity)
# ----------------------------------------------------------------------
def parse_N(val):
    """Parse N from any format — decimal float or string with % suffix."""
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(',', '.')
    if s.endswith('%'):
        return float(s[:-1]) / 100.0
    return float(s)

# ----------------------------------------------------------------------
# MAIN CONTENT
# ----------------------------------------------------------------------
_design_mode = (app_mode == 'Design')

if _design_mode and curve_type == 'Crest':
    expr_chip = 'EXPRESSWAY' if expressway else ''
    st.markdown(f"""
    <div class="vc-header">
      <div class="vc-header-left">
        <h1>Vertical Curve Explorer</h1>
        <p>IRC:73-2023  ·  Crest Curve  ·  {sd_type}</p>
      </div>
      <div class="vc-header-right">
        <span class="chip chip-blue">{h_note}</span>
        <span class="chip chip-green">{'Expressway' if expressway else 'Standard'}</span>
        {'<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not split_formulas:
        st.markdown(f"""
         <div class="formula-strip">
           <span class="f-label">F1</span>
           <span class="f-eq f1">{f1_crest}</span>
           <span class="f-sub">valid  L ≥ S</span>
           <span class="divider">  |   </span>
           <span class="f-label">F2</span>
           <span class="f-eq f2">{f2_crest}</span>
           <span class="f-sub">valid  L ≤ S</span>
           <span class="divider">  |   </span>
           <span class="f-sub">governing = max(F1, F2) ≥ Lmin</span>
         </div>
         """, unsafe_allow_html=True)
    else:
        cf1, cf2 = st.columns(2)
        with cf1: st.markdown(f'<div class="formula-card">F1  —  {f1_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≥ S</span></div>', unsafe_allow_html=True)
        with cf2: st.markdown(f'<div class="formula-card red">F2  —  {f2_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≤ S</span></div>', unsafe_allow_html=True)

    fc = crest_design(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid) if '📐' in view_mode else crest_analysis(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid)
    st.pyplot(fc, width="stretch")
    bc = io.BytesIO()
    fc.savefig(bc, format='png', dpi=180, bbox_inches='tight', facecolor=COLORS['bg_card'])
    bc.seek(0)
    st.download_button('⬇  Download Plot', data=bc, file_name=f'crest_{sd_type}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png', mime='image/png', key='dl_plot')
    plt.close(fc)

    if selected_speeds:
        st.markdown("---")
        st.markdown("**Quick Reference — Crest**")
        cols = st.columns(len(selected_speeds))
        for col, spd in zip(cols, selected_speeds):
            Sv = sd_table[spd][sd_index[sd_type]]
            Lmin = min_length.get(spd, 0)
            if Sv:
                Nx = round(denom_crest / Sv, 4)
                Lg = max((Nx * Sv**2) / denom_crest, 2*Sv - denom_crest / Nx)
                Ld = round(max(Lg, Lmin), 1)
            else:
                Nx = Ld = '—'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (S)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>', unsafe_allow_html=True)

elif _design_mode and curve_type == 'Sag':
    expr_chip = 'EXPRESSWAY' if expressway else ''
    st.markdown(f"""
    <div class="vc-header">
      <div class="vc-header-left">
        <h1>Vertical Curve Explorer</h1>
        <p>IRC:73-2023  ·  Sag Curve  ·  HSD</p>
      </div>
      <div class="vc-header-right">
        <span class="chip chip-amber">h₁={SAG_H1}m  ·  α={SAG_ALPHA}°</span>
        <span class="chip chip-green">{'Expressway' if expressway else 'Standard'}</span>
        {'<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not split_formulas:
        st.markdown(f"""
         <div class="formula-strip">
           <span class="f-label">F1</span>
           <span class="f-eq f1">{f1_sag}</span>
           <span class="f-sub">valid  L ≥ S</span>
           <span class="divider">  |   </span>
           <span class="f-label">F2</span>
           <span class="f-eq f2">{f2_sag}</span>
           <span class="f-sub">valid  L ≤ S</span>
           <span class="divider">  |   </span>
           <span class="f-sub">governing = max(F1, F2) ≥ Lmin</span>
         </div>
         """, unsafe_allow_html=True)
    else:
        sf1, sf2 = st.columns(2)
        with sf1: st.markdown(f'<div class="formula-card">F1  —  {f1_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≥ S</span></div>', unsafe_allow_html=True)
        with sf2: st.markdown(f'<div class="formula-card red">F2  —  {f2_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≤ S</span></div>', unsafe_allow_html=True)

    fs = sag_design(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid) if '📐' in view_mode else sag_analysis(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid)
    st.pyplot(fs, width="stretch")
    bs = io.BytesIO()
    fs.savefig(bs, format='png', dpi=180, bbox_inches='tight', facecolor=COLORS['bg_card'])
    bs.seek(0)
    st.download_button('⬇  Download Plot', data=bs, file_name=f'sag_HSD_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png', mime='image/png', key='dl_plot')
    plt.close(fs)

    if selected_speeds:
        st.markdown("---")
        st.markdown("**Quick Reference — Sag**")
        cols = st.columns(len(selected_speeds))
        for col, spd in zip(cols, selected_speeds):
            Sv = hsd_table.get(spd)
            Lmin = min_length.get(spd, 0)
            if Sv:
                ds = headlight_factor(Sv)
                Nx = round(ds / Sv, 4)
                Lg = max((Nx * Sv**2) / ds, 2*Sv - ds / Nx)
                Ld = round(max(Lg, Lmin), 1)
            else:
                Nx = Ld = '—'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (HSD)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CALCULATOR SECTION
# ----------------------------------------------------------------------
if _design_mode:
    st.markdown("### 📋 Design Input Calculator")
    st.markdown("Compute required lengths. Curve_Type column: Crest/Sag (blank=Crest). SD_Type applies to Crest only; Sag always uses HSD.", unsafe_allow_html=True)
    _tmpl = pd.DataFrame({'N': [0.045, 0.072, 0.031, 0.055, 0.038], 'Speed_kmh': [60, 80, 100, 65, 80], 'SD_Type': ['SSD', 'ISD', '', 'OSD', ''], 'Curve_Type': ['Crest', 'Crest', 'Crest', 'Crest', 'Sag']})
    _tb = io.StringIO()
    _tmpl.to_csv(_tb, index=False)
    tm, tb = st.tabs(['✏️  Manual Entry', '📁  Batch Upload'])

    def compute_row(N_in, spd_in, sdt_in, curve_type='crest'):
        try:
            spd = int(float(spd_in))
            N_v = parse_N(N_in)
            if N_v <= 0: return {'error': 'N must be > 0'}
            if spd == 120 and not expressway: return {'error': '120 km/h applicable for Expressway only'}
            if spd not in sd_table: return {'error': f'Speed {spd} not in IRC table'}
            Lmn = min_length.get(spd, 0)
            if curve_type == 'sag':
                Sv = hsd_table.get(spd)
                if Sv is None: return {'error': f'HSD not defined for {spd} km/h'}
                den_ = headlight_factor(Sv)
                sd_used = 'HSD'
            else:
                sdt = str(sdt_in).strip().upper()
                if sdt not in ('SSD', 'ISD', 'OSD'): return {'error': f'SD type "{sdt}" invalid'}
                if sdt == 'OSD' and spd < OSD_MIN: return {'error': f'OSD N/A for {spd} km/h (min {OSD_MIN} km/h)'}
                sdi = sd_index[sdt]
                Sv = sd_table[spd][sdi]
                if Sv is None: return {'error': f'{sdt} not defined for {spd} km/h'}
                h1_, h2_ = heights[sdt]
                den_ = (np.sqrt(2*h1_) + np.sqrt(2*h2_))**2
                sd_used = sdt
            L1 = (N_v * Sv**2) / den_
            L2 = 2*Sv - den_ / N_v
            Lg = max(L1, L2)
            Ld = max(Lg, Lmn)
            K = round(Ld / N_v, 2)
            gov = 'F1 (L≥S)' if L1 >= L2 else 'F2 (L≤S)'
            notes = []
            if Lmn > Lg: notes.append('Lmin governs')
            if expressway: notes.append('Expressway Lmin')
            kn = '' if L1 >= L2 else ' [L <S]'
            return {'S (m)': Sv, 'SD/HSD used': sd_used, 'L1 (m)': round(L1, 2), 'L2 (m)': round(L2, 2), 'Governing': gov, 'Lmin (m)': Lmn, 'Required L (m)': round(Ld, 2), 'K=L/N': f'{K}{kn}', 'Notes': ' | '.join(notes) if notes else '—', 'error': None}
        except Exception as e:
            return {'error': str(e)}

    def results_from_df(df):
        rows = []
        for i, row in df.iterrows():
            sdt_r = str(row.get('SD_Type', '')).strip().upper()
            sdt_u = sdt_r if sdt_r in ('SSD', 'ISD', 'OSD') else sd_type
            ct_r = str(row.get('Curve_Type', '')).strip().lower()
            ct_u = 'sag' if ct_r == 'sag' else 'crest'
            r = compute_row(row['N'], row['Speed_kmh'], sdt_u, ct_u)
            base = {'Row': i+1, 'N (input)': row['N'], 'Speed (km/h)': row['Speed_kmh'], 'Curve Type': ct_u.capitalize(), 'SD Type used': sdt_u if ct_u == 'crest' else 'HSD'}
            if r.get('error'):
                base.update({'Required L (m)': '—', 'K=L/N': '—', 'Governing': '—', 'Lmin (m)': '—', 'Notes': f'⚠ {r["error"]}'})
            else:
                base.update({k: v for k, v in r.items() if k != 'error'})
            rows.append(base)
        return pd.DataFrame(rows)

    def plot_calc(res_df):
        valid = res_df[~res_df['Notes'].str.startswith('⚠', na=False)].copy()
        if valid.empty:
            st.warning('No valid rows to plot.')
            return
        pspds = sorted(valid['Speed (km/h)'].astype(int).unique().tolist())
        nv = valid['N (input)'].apply(parse_N)
        lv = valid['Required L (m)'].astype(float)
        anmax = round(nv.max() * 1.25 + 0.005, 3)
        aymax = int(lv.max() * 1.25 / 50 + 1) * 50
        fig, ax = plt.subplots(figsize=(13, 6))
        fig.patch.set_facecolor('#FFFFFF')
        style_ax(ax)
        Nbg = np.linspace(0.0005, anmax, 2000)
        plotted = set()
        for spd in pspds:
            col = spd_color.get(spd, '#888888')
            Lmin = min_length.get(spd, 0)
            rows = valid[valid['Speed (km/h)'].astype(int) == spd]
            for sdt in rows[rows['Curve Type'] == 'Crest']['SD Type used'].unique():
                if sdt == 'HSD': continue
                h1_, h2_ = heights[sdt]
                den_ = (np.sqrt(2*h1_) + np.sqrt(2*h2_))**2
                Sv = sd_table[spd][sd_index[sdt]]
                if Sv is None: continue
                Ld = np.maximum(np.maximum((Nbg * Sv**2) / den_, 2*Sv - den_ / Nbg), Lmin)
                lbl = f'{spd} km/h Crest ({sdt})'
                ls = '-' if sdt == 'SSD' else ('--' if sdt == 'ISD' else ':')
                ax.plot(Nbg, Ld, color=col, linewidth=1.5, linestyle=ls, alpha=0.5, zorder=2, label=lbl if lbl not in plotted else '_nolegend_')
                plotted.add(lbl)
            if len(rows[rows['Curve Type'] == 'Sag']) > 0:
                Sv = hsd_table.get(spd)
                if Sv:
                    ds = headlight_factor(Sv)
                    Ld = np.maximum(np.maximum((Nbg * Sv**2) / ds, 2*Sv - ds / Nbg), Lmin)
                    lbl = f'{spd} km/h Sag (HSD)'
                    ax.plot(Nbg, Ld, color=col, linewidth=1.5, linestyle='-.', alpha=0.5, zorder=2, label=lbl if lbl not in plotted else '_nolegend_')
                    plotted.add(lbl)
        for _, row in valid.iterrows():
            spd = int(row['Speed (km/h)'])
            n_in = parse_N(row['N (input)'])
            l_out = float(row['Required L (m)'])
            col = spd_color.get(spd, '#888888')
            mk = 'o' if row['Curve Type'] == 'Crest' else 's'
            ax.plot(n_in, l_out, mk, color=col, markersize=7, zorder=6, markeredgecolor='white', markeredgewidth=0.8)
        ax.set_xlim(0, anmax)
        ax.set_ylim(0, aymax)
        ax.grid(True, color=COLORS['border'], linewidth=0.7, zorder=0)
        ax.set_xlabel('Deviation Angle   N', fontsize=10, color=COLORS['axis_label_color'], labelpad=6)
        ax.set_ylabel('Length of Vertical Curve   L  (m)', fontsize=10, color=COLORS['axis_label_color'], labelpad=6)
        ax.set_title(f'Calculated — {len(valid)} location(s) | ● Crest  ■ Sag | Background = governing curves', fontsize=9, fontweight='bold', color=COLORS['success'], pad=10)
        h_, l_ = ax.get_legend_handles_labels()
        if h_:
            leg = ax.legend(handles=h_, labels=l_, fontsize=7.5, loc='upper left', framealpha=0.92, edgecolor=COLORS['border'], ncol=2 if len(h_) > 4 else 1)
            leg.get_frame().set_linewidth(0.8)
        plt.tight_layout(pad=2.0)
        st.pyplot(fig, width="stretch")
        pb = io.BytesIO()
        fig.savefig(pb, format='png', dpi=180, bbox_inches='tight', facecolor='#FFFFFF')
        pb.seek(0)
        st.download_button('⬇  Download Plot (PNG)', data=pb, file_name=f'vc_calc_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png', mime='image/png', key=f'dl_cp_{id(res_df)}')
        plt.close(fig)

    with tm:
        st.markdown("<span style='font-size:0.78rem;color:#8B949E'>Enter N as decimal (e.g. 0.045).  Blank SD_Type uses sidebar. Blank Curve_Type → Crest.</span>", unsafe_allow_html=True)
        dr = pd.DataFrame({'N': [0.045, 0.072, 0.031, 0.038], 'Speed_kmh': [60, 80, 100, 80], 'SD_Type': ['', 'ISD', 'SSD', ''], 'Curve_Type': ['Crest', 'Crest', 'Crest', 'Sag']})
        idf = st.data_editor(dr, num_rows='dynamic', width="stretch", column_config={'N': st.column_config.NumberColumn('N  (decimal, e.g. 0.045)', min_value=0.0001, max_value=0.50, step=0.001, format='%.4f', required=True), 'Speed_kmh': st.column_config.SelectboxColumn('Speed (km/h)', options=available_speeds, required=True), 'SD_Type': st.column_config.SelectboxColumn('SD Type (blank=global)', options=['', 'SSD', 'ISD', 'OSD']), 'Curve_Type': st.column_config.SelectboxColumn('Curve Type', options=['Crest', 'Sag'])}, hide_index=True, key='manual_editor')
        if idf is not None and len(idf) > 0:
            rdf = results_from_df(idf)
            st.markdown("#### Results")
            st.dataframe(rdf, width="stretch", hide_index=True)
            co = io.StringIO()
            rdf.to_csv(co, index=False)
            st.download_button('⬇  Download Results (CSV)', data=co.getvalue(), file_name=f'vc_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv', key='dl_manual')
            st.markdown("#### Plot")
            plot_calc(rdf)

    with tb:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown('<div class="info-box"><b>CSV columns:</b> <code>N</code> ·  <code>Speed_kmh</code> · <code>SD_Type</code> (opt) ·  <code>Curve_Type</code> (Crest/Sag — blank=Crest)<br>N accepts decimal (0.045) or % suffix (4.5%). Header required. Aliases accepted.</div>', unsafe_allow_html=True)
        with c2:
            st.download_button('⬇  Template', data=_tb.getvalue(), file_name='vc_template.csv', mime='text/csv', key='dl_tmpl')
        up = st.file_uploader('Upload CSV', type=['csv'], label_visibility='collapsed', key='batch_uploader')
        if up is not None:
            try:
                rdf2 = pd.read_csv(up, dtype={'N': str})
                rdf2.columns = [c.strip() for c in rdf2.columns]
                cm = {}
                for c in rdf2.columns:
                    cl = c.lower().replace(' ', '_')
                    if cl in ('n', 'deviation_angle', 'dev_angle', 'angle'): cm[c] = 'N'
                    elif cl in ('speed_kmh', 'speed', 'design_speed', 'v'): cm[c] = 'Speed_kmh'
                    elif cl in ('sd_type', 'sd', 'sight_distance', 'type'): cm[c] = 'SD_Type'
                    elif cl in ('curve_type', 'curve', 'vc_type', 'vertical_curve'): cm[c] = 'Curve_Type'
                rdf2 = rdf2.rename(columns=cm)
                if 'N' not in rdf2.columns or 'Speed_kmh' not in rdf2.columns:
                    st.error('CSV must have N and Speed_kmh columns.')
                else:
                    if 'SD_Type' not in rdf2.columns: rdf2['SD_Type'] = ''
                    if 'Curve_Type' not in rdf2.columns: rdf2['Curve_Type'] = 'Crest'
                    st.success(f'{len(rdf2):,} rows loaded.')
                    with st.spinner('Computing...'):
                        res2 = results_from_df(rdf2)
                    tot = len(res2)
                    err = res2['Notes'].str.startswith('⚠').sum()
                    lgov = res2['Notes'].str.contains('Lmin governs', na=False).sum()
                    nc = (res2['Curve Type'] == 'Crest').sum()
                    ns = (res2['Curve Type'] == 'Sag').sum()
                    s1, s2, s3, s4, s5 = st.columns(5)
                    s1.metric('Total', f'{tot:,}')
                    s2.metric('Crest', f'{nc:,}')
                    s3.metric('Sag', f'{ns:,}')
                    s4.metric('Lmin governs', f'{lgov:,}')
                    s5.metric('Errors', f'{err:,}')
                    st.markdown("#### Results")
                    st.dataframe(res2, width="stretch", hide_index=True)
                    co2 = io.StringIO()
                    res2.to_csv(co2, index=False)
                    st.download_button('⬇  Download Results (CSV)', data=co2.getvalue(), file_name=f'vc_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv', key='dl_batch')
                    st.markdown("#### Plot")
                    plot_calc(res2)
            except Exception as e:
                st.error(f'Error reading file: {e}')

# ----------------------------------------------------------------------
# VERIFY MODE
# ----------------------------------------------------------------------
if not _design_mode:
    expr_chip = '<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''
    ct_chip = '<span class="chip chip-blue">Crest</span>' if curve_type == 'Crest' else '<span class="chip chip-amber">Sag</span>'
    st.markdown(f"""
    <div class="vc-header">
      <div class="vc-header-left">
        <h1>Verify Existing Curve</h1>
        <p>IRC:73-2023  ·  Adequacy Check</p>
      </div>
      <div class="vc-header-right">
        {ct_chip}
        {'<span class="chip chip-blue">' + sd_type + '</span>' if curve_type == 'Crest' else '<span class="chip chip-amber">HSD</span>'}
        <span class="chip chip-green">{'Expressway' if expressway else 'Standard'}</span>
        {expr_chip}
      </div>
    </div>
    """, unsafe_allow_html=True)

    def verify_curve(N_pct, L, spd, cv_type, sdt, expr):
        try:
            N_pct_val = float(N_pct)
            N_v = N_pct_val / 100.0
            L_v = float(L)
            spd = int(float(spd))
            sdt = str(sdt).strip().upper()
            if N_pct_val <= 0: return {'error': 'N must be > 0'}
            if L_v <= 0: return {'error': 'L must be > 0'}
            if spd not in sd_table: return {'error': f'Speed {spd} not in IRC table'}
            if spd == 120 and not expr: return {'error': '120 km/h applicable for Expressway only'}
            Lmn = min_length.get(spd, 0)
            K_exist = round(L_v / N_pct_val, 2)
            if cv_type == 'Sag':
                S_req = hsd_table.get(spd)
                if S_req is None: return {'error': f'HSD not defined for {spd} km/h'}
                den = headlight_factor(S_req)
                Kmin = k_min_sag.get(spd)
                sdt_used = 'HSD'
            else:
                if sdt not in ('SSD', 'ISD', 'OSD'): return {'error': f'SD type "{sdt}" invalid'}
                if sdt == 'OSD' and spd < OSD_MIN: return {'error': f'OSD N/A for {spd} km/h (min {OSD_MIN} km/h)'}
                sd_i = sd_index[sdt]
                S_req = sd_table[spd][sd_i]
                if S_req is None: return {'error': f'{sdt} not defined for {spd} km/h'}
                h1_, h2_ = heights[sdt]
                den = (np.sqrt(2*h1_) + np.sqrt(2*h2_))**2
                Kmin = k_min_crest.get(sdt, {}).get(spd)
                sdt_used = sdt
            S_ls = np.sqrt(L_v * den / N_v)
            case_ls_consistent = (L_v >= S_ls)
            S_lt = L_v / 2.0 + den / (2.0 * N_v)
            case_lt_consistent = (L_v < S_lt)
            if case_ls_consistent:
                S_avail = round(S_ls, 2)
                case_used = 'L ≥ S'
            elif case_lt_consistent:
                S_avail = round(S_lt, 2)
                case_used = 'L < S'
            else:
                S_avail = round(S_ls, 2)
                case_used = 'L ≥ S (conservative)'
            gct = grade_change_threshold.get(spd)
            vc_required = (gct is None) or (N_pct_val > gct)
            sd_pass = S_avail >= S_req
            sd_margin = round(S_avail - S_req, 2)
            k_pass = (Kmin is None) or (K_exist >= Kmin)
            k_margin = round(K_exist - Kmin, 2) if Kmin else None
            l_pass = L_v >= Lmn
            l_margin = round(L_v - Lmn, 2)
            return {'error': None, 'N_decimal': round(N_v, 5), 'K_exist': K_exist, 'S_avail': S_avail, 'S_req': S_req, 'case_used': case_used, 'sd_pass': sd_pass, 'sd_margin': sd_margin, 'K_min': Kmin, 'k_pass': k_pass, 'k_margin': k_margin, 'L_min': Lmn, 'l_pass': l_pass, 'l_margin': l_margin, 'gct': gct, 'vc_required': vc_required, 'sdt_used': sdt_used}
        except Exception as e:
            return {'error': str(e)}

    def render_check(label, passed, value, required, unit, margin, note=None):
        icon = '✅' if passed else '❌'
        color = COLORS['success'] if passed else COLORS['danger']
        margin_str = f'+{margin} {unit}' if margin >= 0 else f'{margin} {unit}'
        margin_col = COLORS['success'] if margin >= 0 else COLORS['danger']
        st.markdown(f"""
         <div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']}; border-left:3px solid {color};border-radius:6px; padding:0.55rem 1rem;margin-bottom:0.5rem; font-family:'JetBrains Mono',monospace;">
           <div style="display:flex;justify-content:space-between;align-items:center;">
             <span style="font-size:0.8rem;color:#C9D1D9;">{icon}  {label}</span>
             <span style="font-size:0.75rem;color:{margin_col};font-weight:600;">{margin_str}</span>
           </div>
           <div style="font-size:0.68rem;color:{COLORS['muted']};margin-top:3px;">
            Available:  <b style="color:#C9D1D9;">{value} {unit}</b> &nbsp;· &nbsp; Required:  <b style="color:#C9D1D9;">{required} {unit}</b>{' &nbsp;· &nbsp; ' + note if note else ''}
           </div>
         </div>
         """, unsafe_allow_html=True)

    def render_verify_result(res, spd, N_pct_input, L_input, label=None):
        if res.get('error'):
            st.error(f'⚠ {res["error"]}')
            return
        all_pass = res['sd_pass'] and res['k_pass'] and res['l_pass']
        verdict_color = COLORS['success'] if all_pass else COLORS['danger']
        verdict_text = 'ADEQUATE' if all_pass else 'INADEQUATE'
        verdict_icon = '✅' if all_pass else '❌'
        prefix = f'{label}  ·  ' if label else ''
        st.markdown(f"""
         <div style="background:{COLORS['bg_card']};border:1px solid {COLORS['border']}; border-left:4px solid {verdict_color};border-radius:8px; padding:0.7rem 1.2rem; margin-bottom:0.6rem; display:flex;justify-content:space-between;align-items:center;">
           <div>
             <div style="font-family:'JetBrains Mono',monospace;font-size:0.9rem; font-weight:600;color:{verdict_color};"> {verdict_icon}  {prefix}{verdict_text} </div>
             <div style="font-size:0.68rem;color:{COLORS['muted']};margin-top:2px;"> {curve_type}  ·  {spd} km/h  ·  {res['sdt_used']}  · N={res['N_decimal']} ({N_pct_input}%)  ·  L={L_input}m  ·  K={res['K_exist']}  ·  {res['case_used']} </div>
           </div>
         </div>
         """, unsafe_allow_html=True)
        render_check('Sight Distance  (' + res['sdt_used'] + ')', res['sd_pass'], res['S_avail'], res['S_req'], 'm', res['sd_margin'], f'case: {res["case_used"]}')
        if res['K_min'] is not None:
            render_check('K  (IRC Table 7.3)', res['k_pass'], res['K_exist'], res['K_min'], '', res['k_margin'], f'Kmin {spd} km/h {res["sdt_used"]}')
        else:
            st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-left:3px solid {COLORS["muted"]};border-radius:6px;padding:0.45rem 1rem;margin-bottom:0.45rem;font-family:JetBrains Mono,monospace;font-size:0.72rem;color:{COLORS["muted"]};">ℹ  K — Kmin not in IRC Table 7.3 for 120 km/h</div>', unsafe_allow_html=True)
        render_check('Minimum Curve Length  (IRC Table 7.5)', res['l_pass'], L_input, res['L_min'], 'm', res['l_margin'])
        if res['gct'] is not None:
            vc_note = ('VC not required' if not res['vc_required'] else 'VC required') + f' at this grade change (threshold {res["gct"]}%)'
            st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-left:3px solid {COLORS["muted"]};border-radius:6px;padding:0.45rem 1rem;margin-bottom:0.45rem;font-family:JetBrains Mono,monospace;font-size:0.68rem;color:{COLORS["muted"]};">ℹ  {vc_note}</div>', unsafe_allow_html=True)

    def verify_to_row(res, row_num, spd, N_pct_input, L_input, sdt_used):
        if res.get('error'):
            return {'Row': row_num, 'Speed (km/h)': spd, 'N (%)': N_pct_input, 'L (m)': L_input, 'Overall': '⚠ ' + res['error']}
        all_pass = res['sd_pass'] and res['k_pass'] and res['l_pass']
        return {'Row': row_num, 'Curve Type': curve_type, 'Speed (km/h)': spd, 'SD Type': sdt_used, 'N (%)': N_pct_input, 'N (decimal)': res['N_decimal'], 'L (m)': L_input, 'K': res['K_exist'], 'Case': res['case_used'], 'S available (m)': res['S_avail'], 'S required (m)': res['S_req'], 'SD': 'PASS' if res['sd_pass'] else 'FAIL', 'SD margin (m)': res['sd_margin'], 'K min': res['K_min'] if res['K_min'] else 'N/A', 'K check': 'PASS' if res['k_pass'] else ('FAIL' if res['K_min'] else 'N/A'), 'K margin': res['k_margin'] if res['k_margin'] is not None else 'N/A', 'L min (m)': res['L_min'], 'L check': 'PASS' if res['l_pass'] else 'FAIL', 'L margin (m)': res['l_margin'], 'Overall': 'ADEQUATE' if all_pass else 'INADEQUATE'}

    v_sdt = sd_type if curve_type == 'Crest' else 'HSD'
    vtm, vtb = st.tabs(['✏️  Manual Entry', '📁  Batch Upload'])

    with vtm:
        st.markdown("<span style='font-size:0.78rem;color:#8B949E'>Enter N as decimal (e.g. 0.045) or with % suffix (e.g. 4.5%).  SD type and Curve type from sidebar.</span>", unsafe_allow_html=True)
        v_default = pd.DataFrame({'N': [0.045, 0.072, '3.6%'], 'L (m)': [260.0, 400.0, 180.0], 'Speed_kmh': [80, 100, 80]})
        v_idf = st.data_editor(v_default, num_rows='dynamic', width='stretch', column_config={'N': st.column_config.TextColumn('N  (decimal or % suffix)', required=True), 'L (m)': st.column_config.NumberColumn('L (m)', min_value=1.0, step=1.0, format='%.1f', required=True), 'Speed_kmh': st.column_config.SelectboxColumn('Speed (km/h)', options=available_speeds, required=True)}, hide_index=True, key='verify_manual_editor')
        if v_idf is not None and len(v_idf) > 0:
            v_rows = []
            for i, row in v_idf.iterrows():
                try:
                    N_p = parse_N(row['N'])
                    N_pct = round(N_p * 100, 4)
                    L_v = float(row['L (m)'])
                    spd_v = int(row['Speed_kmh'])
                    res = verify_curve(N_pct, L_v, spd_v, curve_type, v_sdt, expressway)
                    st.markdown(f"**Curve {i+1}** — {spd_v} km/h, N={row['N']}, L={L_v}m")
                    render_verify_result(res, spd_v, N_pct, L_v)
                    v_rows.append(verify_to_row(res, i+1, spd_v, N_pct, L_v, v_sdt))
                except Exception as e:
                    st.error(f'Row {i+1}: {e}')
            if v_rows:
                vdf = pd.DataFrame(v_rows)
                vcsv = io.StringIO()
                vdf.to_csv(vcsv, index=False)
                st.download_button('⬇  Export Verification Report (CSV)', data=vcsv.getvalue(), file_name=f'vc_verify_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv', key='dl_verify_manual')

    with vtb:
        v_tmpl = pd.DataFrame({'N': ['0.045', '0.072', '3.6%', '0.031'], 'L_m': [260.0, 400.0, 180.0, 120.0], 'Speed_kmh': [80, 100, 80, 60], 'SD_Type': ['ISD', 'ISD', '', 'SSD']})
        v_tb_buf = io.StringIO()
        v_tmpl.to_csv(v_tb_buf, index=False)
        vc1, vc2 = st.columns([3, 1])
        with vc1:
            st.markdown('<div class="info-box"><b>CSV columns:</b> <code>N</code> (decimal or % suffix)  ·  <code>L_m</code> (curve length in m)  ·  <code>Speed_kmh</code>  ·  <code>SD_Type</code> (opt — blank uses sidebar)<br>Header required. Aliases accepted.</div>', unsafe_allow_html=True)
        with vc2:
            st.download_button('⬇  Template', data=v_tb_buf.getvalue(), file_name='vc_verify_template.csv', mime='text/csv', key='dl_verify_tmpl')
        v_up = st.file_uploader('Upload CSV', type=['csv'], label_visibility='collapsed', key='verify_batch_uploader')
        if v_up is not None:
            try:
                v_raw = pd.read_csv(v_up, dtype={'N': str})
                v_raw.columns = [c.strip() for c in v_raw.columns]
                vcm = {}
                for c in v_raw.columns:
                    cl = c.lower().replace(' ', '_')
                    if cl in ('n', 'deviation_angle', 'dev_angle', 'angle'): vcm[c] = 'N'
                    elif cl in ('l_m', 'l', 'length', 'curve_length', 'l(m)'): vcm[c] = 'L_m'
                    elif cl in ('speed_kmh', 'speed', 'design_speed', 'v'): vcm[c] = 'Speed_kmh'
                    elif cl in ('sd_type', 'sd', 'sight_distance', 'type'): vcm[c] = 'SD_Type'
                v_raw = v_raw.rename(columns=vcm)
                if 'N' not in v_raw.columns or 'L_m' not in v_raw.columns or 'Speed_kmh' not in v_raw.columns:
                    st.error('CSV must have N, L_m, and Speed_kmh columns.')
                else:
                    if 'SD_Type' not in v_raw.columns: v_raw['SD_Type'] = ''
                    st.success(f'{len(v_raw):,} rows loaded.')
                    v_rows = []
                    errors = 0
                    for i, row in v_raw.iterrows():
                        try:
                            N_p = parse_N(row['N'])
                            N_pct = round(N_p * 100, 4)
                            L_v = float(row['L_m'])
                            spd_v = int(float(row['Speed_kmh']))
                            sdt_r = str(row.get('SD_Type', '')).strip().upper()
                            sdt_v = sdt_r if sdt_r in ('SSD','ISD','OSD') else v_sdt
                            res = verify_curve(N_pct, L_v, spd_v, curve_type, sdt_v, expressway)
                            v_rows.append(verify_to_row(res, i+1, spd_v, N_pct, L_v, sdt_v))
                            if res.get('error'): errors += 1
                        except Exception as e:
                            v_rows.append({'Row': i+1, 'Overall': f'⚠ {e}'})
                            errors += 1
                    vdf = pd.DataFrame(v_rows)
                    tot = len(vdf)
                    adq = (vdf['Overall'] == 'ADEQUATE').sum()
                    inadq = (vdf['Overall'] == 'INADEQUATE').sum()
                    vs1, vs2, vs3, vs4 = st.columns(4)
                    vs1.metric('Total', f'{tot:,}')
                    vs2.metric('Adequate', f'{adq:,}')
                    vs3.metric('Inadequate', f'{inadq:,}')
                    vs4.metric('Errors', f'{errors:,}')
                    st.dataframe(vdf, width='stretch', hide_index=True)
                    vcsv = io.StringIO()
                    vdf.to_csv(vcsv, index=False)
                    st.download_button('⬇  Export Verification Report (CSV)', data=vcsv.getvalue(), file_name=f'vc_verify_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv', key='dl_verify_batch')
            except Exception as e:
                st.error(f'Error reading file: {e}')

# ----------------------------------------------------------------------
# FOOTNOTE
# ----------------------------------------------------------------------
en = 'Expressway: Lmin 80→70, 100→85, 120→100m | ' if expressway else ''
st.markdown(f'* {en}Lmin IRC:73-2023 Table 7.5 | Crest: SSD/ISD/OSD | Sag: HSD (h₁={SAG_H1}m, α={SAG_ALPHA}°, denom=1.50+0.035S) | OSD≥{OSD_MIN}km/h | 120km/h Expressway only | K=L/N (verify IRC Table 7.4)', unsafe_allow_html=True)