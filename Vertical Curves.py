import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import streamlit as st
import datetime
import io
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Summit Curve Explorer',
    page_icon='🛣️',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
    section[data-testid="stSidebar"] hr {
        border-color: #1E293B !important; margin: 1rem 0 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .main .block-container {
        padding-top: 1.2rem; padding-bottom: 1rem; max-width: 100%;
    }
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border-radius: 10px; padding: 1.2rem 2rem;
        margin-bottom: 1rem; border-left: 4px solid #3B82F6;
    }
    .app-header h1 {
        font-family: 'IBM Plex Mono', monospace; font-size: 1.4rem;
        font-weight: 700; color: #F1F5F9; margin: 0; letter-spacing: -0.02em;
    }
    .app-header p { font-size: 0.8rem; color: #94A3B8; margin: 0.3rem 0 0 0; }
    .app-header .badge {
        display: inline-block; background: #1E3A5F;
        border: 1px solid #3B82F6; color: #93C5FD;
        font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
        padding: 0.15rem 0.5rem; border-radius: 4px;
        margin-right: 0.4rem; letter-spacing: 0.05em;
    }
    .formula-card {
        background: #F8FAFC; border-radius: 8px; padding: 0.6rem 1rem;
        margin-bottom: 0.5rem; border-left: 3px solid #3B82F6;
        font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: #1E293B;
    }
    .formula-card.green { border-left-color: #276749; }
    .formula-card.red   { border-left-color: #EF4444; }
    .stDownloadButton button {
        background-color: #1E3A5F !important; color: #93C5FD !important;
        border: 1px solid #3B82F6 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem !important; font-weight: 600 !important;
        letter-spacing: 0.05em !important; border-radius: 6px !important;
        padding: 0.4rem 1.2rem !important; width: 100%;
    }
    .stDownloadButton button:hover {
        background-color: #3B82F6 !important; color: #FFFFFF !important;
    }
    .metric-tile {
        background: #0F172A; border: 1px solid #1E293B;
        border-radius: 8px; padding: 0.5rem 0.9rem;
    }
    .metric-tile .label {
        font-size: 0.65rem; color: #64748B; text-transform: uppercase;
        letter-spacing: 0.08em; font-weight: 600;
    }
    .metric-tile .value {
        font-family: 'IBM Plex Mono', monospace; font-size: 1.0rem;
        font-weight: 700; color: #93C5FD;
    }
    .metric-tile .unit { font-size: 0.65rem; color: #64748B; }
    .footnote {
        font-size: 0.7rem; color: #94A3B8;
        border-top: 1px solid #E2E8F0;
        padding-top: 0.5rem; margin-top: 0.5rem;
    }
    .info-box {
        background: #EFF6FF; border: 1px solid #BFDBFE;
        border-radius: 8px; padding: 0.8rem 1rem;
        font-size: 0.8rem; color: #1E40AF; margin-bottom: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ── IRC Data ──────────────────────────────────────────────────────────────────
sd_table = {
    20:  (20,   40,  None),
    25:  (25,   50,  None),
    30:  (30,   60,  None),
    40:  (45,   90,  135),
    50:  (60,  120,  235),
    60:  (80,  160,  300),
    65:  (90,  180,  340),
    80:  (130, 260,  470),
    100: (180, 360,  640),
    120: (250, 500,  835),
}
heights  = {'SSD': (1.2, 0.15), 'ISD': (1.2, 1.20), 'OSD': (1.2, 1.20)}
sd_index = {'SSD': 0, 'ISD': 1, 'OSD': 2}
OSD_MIN  = 40
min_length = {20:15, 25:15, 30:15, 40:20, 50:30,
              60:40, 65:40, 80:50, 100:60, 120:100}
formula_label = {
    'SSD': ('h₁ = 1.2 m,  h₂ = 0.15 m', 'Driver eye height / tail-light object'),
    'ISD': ('h₁ = 1.2 m,  h₂ = 1.20 m', 'Driver eye height / oncoming driver eye'),
    'OSD': ('h₁ = 1.2 m,  h₂ = 1.20 m', 'Driver eye height / oncoming driver eye'),
}

# SD-aware default axis ranges — ISD/OSD have larger denom so crossover
# sits at smaller N values; push xmax in so envelope is visible by default
SD_XMAX_DEFAULT = {'SSD': 0.16, 'ISD': 0.08, 'OSD': 0.06}
SD_XMAX_MAX     = {'SSD': 0.30, 'ISD': 0.20, 'OSD': 0.15}
SD_XGRID_DEFAULT= {'SSD': 0.02, 'ISD': 0.01, 'OSD': 0.01}

speeds    = list(sd_table.keys())
colors    = plt.cm.tab10(np.linspace(0, 0.85, len(speeds)))
spd_color = {spd: col for spd, col in zip(speeds, colors)}

BLUE  = '#2B6CB0'
RED   = '#C53030'
GREEN = '#276749'

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛣️ Summit Curve\nExplorer")
    st.markdown("---")

    st.markdown("##### View Mode")
    view_mode = st.radio('View Mode',
                         ('📐 Design Chart', '🔬 Formula Analysis'),
                         label_visibility='collapsed')

    st.markdown("---")
    st.markdown("##### Sight Distance Type")
    sd_type = st.radio('Sight Distance Type', ('SSD', 'ISD', 'OSD'),
                       horizontal=True, label_visibility='collapsed')

    st.markdown("---")
    st.markdown("##### Design Speeds  (km/h)")
    available = speeds if sd_type != 'OSD' else [s for s in speeds if s >= OSD_MIN]
    defaults  = [s for s in [60, 80, 100] if s in available]
    selected_speeds = st.multiselect(
        'Design Speeds', available, default=defaults,
        format_func=lambda x: f'{x} km/h',
        label_visibility='collapsed'
    )

    st.markdown("---")
    st.markdown("##### Options")
    show_min = st.checkbox('Min Length  (Table 7.5)', value=True)
    show_env = st.checkbox('L = S Envelope', value=True)

    st.markdown("---")
    st.markdown("##### Axis Range")
    _xmax_def = SD_XMAX_DEFAULT[sd_type]
    _xmax_max = SD_XMAX_MAX[sd_type]
    _xgrd_def = SD_XGRID_DEFAULT[sd_type]
    xmax  = st.slider('N max  (deviation angle)', 0.01, _xmax_max,
                      _xmax_def, 0.005, format='%.3f')
    ymax  = st.slider('Y max  (curve length m)', 100, 1500, 700, 50)
    st.markdown("##### Grid Spacing")
    xgrid = st.slider('N grid', 0.002, 0.05, _xgrd_def, 0.002, format='%.3f')
    ygrid = st.slider('Y grid', 25, 200, 100, 25)

    st.markdown("---")
    st.caption(f"IRC:73-2023  |  {datetime.date.today().strftime('%d %b %Y')}")

# ── Derived values ────────────────────────────────────────────────────────────
h1, h2  = heights[sd_type]
denom   = (np.sqrt(2*h1) + np.sqrt(2*h2))**2
h_note, h_desc = formula_label[sd_type]
idx = sd_index[sd_type]
N   = np.linspace(0.0005, xmax, 2000)   # deviation angle array, named N

f1_str = ('L = N · S²  /  (√2h₁ + √2h₂)²'
          if sd_type == 'SSD' else 'L = N · S²  /  (2√2h)²')
f2_str = ('L = 2S  −  (√2h₁ + √2h₂)²  /  N'
          if sd_type == 'SSD' else 'L = 2S  −  (2√2h)²  /  N')
fg_str = 'L = max(F₁, F₂),  then  max(L, Lmin)'

# ── Header ────────────────────────────────────────────────────────────────────
mode_label = 'Design Chart' if '📐' in view_mode else 'Formula Analysis'
st.markdown(f"""
<div class="app-header">
    <h1>Summit Curve Length Explorer</h1>
    <p>Crest Vertical Curve  ·  IRC:73-2023  ·  {mode_label}</p>
    <div style="margin-top:0.6rem">
        <span class="badge">{sd_type}</span>
        <span class="badge">{h_note}</span>
        <span class="badge">{mode_label}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Formula cards ─────────────────────────────────────────────────────────────
if '📐' in view_mode:
    col_g, col_sp = st.columns([2, 1])
    with col_g:
        st.markdown(
            f'<div class="formula-card green">▶  Governing  —  {fg_str}<br>'
            f'<span style="color:#64748B;font-size:0.72rem">'
            f'F₁ valid when L ≥ S  |  F₂ valid when L ≤ S  |  '
            f'floor applied from IRC Table 7.5</span></div>',
            unsafe_allow_html=True)
    with col_sp:
        st.markdown(
            f'<div class="formula-card" style="font-size:0.74rem;line-height:1.6">'
            f'F₁: {f1_str}<br>F₂: {f2_str}</div>',
            unsafe_allow_html=True)
else:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown(
            f'<div class="formula-card">▶  Formula 1  —  {f1_str}<br>'
            f'<span style="color:#64748B;font-size:0.72rem">'
            f'Valid when  L ≥ S</span></div>',
            unsafe_allow_html=True)
    with col_f2:
        st.markdown(
            f'<div class="formula-card red">▶  Formula 2  —  {f2_str}<br>'
            f'<span style="color:#64748B;font-size:0.72rem">'
            f'Valid when  L ≤ S</span></div>',
            unsafe_allow_html=True)

# ── Shared plot helpers ───────────────────────────────────────────────────────
matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def style_ax(ax):
    ax.set_facecolor('#FAFBFC')
    ax.tick_params(labelsize=8.5, colors='#4A5568')
    for spine in ax.spines.values():
        spine.set_edgecolor('#E2E8F0')

def apply_grid_and_labels(ax):
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.set_xticks(np.arange(0, xmax + xgrid, xgrid))
    ax.set_yticks(np.arange(0, ymax + ygrid, ygrid))
    ax.grid(True, color='#E2E8F0', linewidth=0.7, zorder=0)
    ax.set_xlabel('Deviation Angle   N', fontsize=10,
                  color='#4A5568', labelpad=6)
    ax.set_ylabel('Length of Vertical Curve   L  (m)', fontsize=10,
                  color='#4A5568', labelpad=6)

def draw_envelope(ax):
    """Draw L=S envelope. Returns (N_env, S_r, mask) or None."""
    if not show_env:
        return None
    S_r  = np.linspace(5, max(ymax * 1.5, 1500), 6000)
    N_e  = denom / S_r
    mask = (N_e > 0) & (N_e < xmax) & (S_r > 0) & (S_r < ymax)
    if mask.any():
        ax.plot(N_e[mask], S_r[mask],
                color='#111111', linewidth=1.1,
                linestyle='--', alpha=0.80, zorder=5)
    return N_e, S_r, mask

def draw_min_lines(ax):
    if not show_min:
        return
    seen = {}
    for spd in selected_speeds:
        S_val = sd_table[spd][idx]
        if S_val is None:
            continue
        Lmin = min_length.get(spd)
        if Lmin:
            seen.setdefault(Lmin, []).append(spd)
    for Lmin, spds in seen.items():
        if 0 < Lmin < ymax:
            ax.axhline(Lmin, color='#94A3B8', linewidth=0.9,
                       linestyle='-.', alpha=0.60, zorder=2)
            ax.text(xmax * 0.998, Lmin + ymax * 0.008,
                    f'Lmin = {Lmin} m  ({", ".join(str(s) for s in spds)} km/h)',
                    fontsize=6, color='#64748B',
                    ha='right', va='bottom', alpha=0.9)

def finalize_legend(ax, extra_handles=None, extra_labels=None):
    if not selected_speeds:
        return
    h, l = ax.get_legend_handles_labels()
    if extra_handles:
        h += extra_handles
        l += extra_labels
    leg = ax.legend(handles=h, labels=l,
                    fontsize=8, loc='upper left',
                    framealpha=0.92, edgecolor='#CBD5E0',
                    ncol=2 if len(selected_speeds) > 5 else 1)
    leg.get_frame().set_linewidth(0.8)

def std_extra_handles():
    eh = [Line2D([0], [0], color='#111111', linewidth=1.1,
                 linestyle='--', label='L = S  boundary')]
    el = ['L = S  boundary']
    if show_min:
        eh.append(Line2D([0], [0], color='#94A3B8', linewidth=0.9,
                          linestyle='-.', label='Lmin  (Table 7.5)'))
        el.append('Lmin  (Table 7.5)')
    return eh, el

# ── Design Chart ──────────────────────────────────────────────────────────────
def build_design_chart():
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#FFFFFF')
    style_ax(ax)

    for spd in selected_speeds:
        S_val = sd_table[spd][idx]
        if S_val is None:
            continue
        col  = spd_color[spd]
        Lmin = min_length.get(spd, 0)

        L1    = (N * S_val**2) / denom
        L2    = 2*S_val - denom / N
        L_gov = np.maximum(L1, L2)
        L_des = np.maximum(L_gov, Lmin)

        ax.plot(N, L_des, color=col, linewidth=2.0,
                label=f'{spd} km/h  (S = {S_val} m)',
                solid_capstyle='round', zorder=3)

        # Crossover dot at (N_x, S_val)
        N_x = denom / S_val
        if 0 < N_x < xmax and 0 < S_val < ymax:
            ax.plot(N_x, S_val, 'o', color=col,
                    markersize=5, zorder=6, alpha=0.85)

        # Shade where Lmin governs
        if show_min and Lmin > 0:
            mask_floor = (L_gov < Lmin)
            if mask_floor.any():
                ax.fill_between(N[mask_floor],
                                L_gov[mask_floor], Lmin,
                                color=col, alpha=0.06, zorder=1)

    result = draw_envelope(ax)
    if show_env and result is not None:
        N_e, S_r, mask = result
        if mask.any():
            mid = len(N_e[mask]) // 3
            ax.annotate('L = S',
                        xy=(N_e[mask][mid], S_r[mask][mid]),
                        xytext=(-38, 18), textcoords='offset points',
                        fontsize=8, fontstyle='italic',
                        color='#111111', fontweight='bold',
                        arrowprops=dict(arrowstyle='-',
                                        color='#888888', lw=0.6))

    draw_min_lines(ax)
    apply_grid_and_labels(ax)

    ax.set_title(
        f'Summit Curve — Governing Length  [{fg_str}]\n'
        f'{sd_type}   |   {h_note}   |   '
        f'Dots mark F1 ↔ F2 crossover  |  Shaded = Lmin governs',
        fontsize=9, fontweight='bold', color=GREEN, pad=10
    )
    ax.text(0.975, 0.965, 'Governing: max(F₁, F₂) ≥ Lmin',
            transform=ax.transAxes, fontsize=7.5,
            ha='right', va='top', color=GREEN,
            bbox=dict(boxstyle='round,pad=0.45',
                      facecolor='#F0FFF4', edgecolor=GREEN,
                      linewidth=0.8, alpha=0.92))

    finalize_legend(ax, *std_extra_handles())
    plt.tight_layout(pad=2.0)
    return fig

# ── Formula Analysis ──────────────────────────────────────────────────────────
def build_analysis_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor('#FFFFFF')

    for ax, fnum in [(ax1, 1), (ax2, 2)]:
        style_ax(ax)

        for spd in selected_speeds:
            S_val = sd_table[spd][idx]
            if S_val is None:
                continue
            col = spd_color[spd]
            L   = (N * S_val**2) / denom if fnum == 1 else 2*S_val - denom/N
            ax.plot(N, L, color=col, linewidth=1.8,
                    label=f'{spd} km/h  (S = {S_val} m)',
                    solid_capstyle='round')

        result = draw_envelope(ax)
        if show_env and result is not None:
            N_e, S_r, mask = result
            if mask.any():
                shade_col = '#2B6CB0' if fnum == 1 else '#C53030'
                if fnum == 1:
                    ax.fill_betweenx(S_r[mask], N_e[mask], xmax,
                                     color=shade_col, alpha=0.04, zorder=0)
                else:
                    ax.fill_betweenx(S_r[mask], 0, N_e[mask],
                                     color=shade_col, alpha=0.04, zorder=0)
                mid       = len(N_e[mask]) // 3
                offset    = (-38, 18) if fnum == 1 else (-38, -18)
                label_txt = 'L > S' if fnum == 1 else 'L < S'
                ax.annotate(label_txt,
                            xy=(N_e[mask][mid], S_r[mask][mid]),
                            xytext=offset, textcoords='offset points',
                            fontsize=8.5, fontstyle='italic',
                            color='#111111', fontweight='bold',
                            arrowprops=dict(arrowstyle='-',
                                            color='#888888', lw=0.6))

        for spd in selected_speeds:
            S_val = sd_table[spd][idx]
            if S_val and 0 < S_val < ymax:
                ax.axhline(S_val, color=spd_color[spd],
                           linewidth=0.4, linestyle='--', alpha=0.18)

        draw_min_lines(ax)
        apply_grid_and_labels(ax)

        condition = 'L ≥ S' if fnum == 1 else 'L ≤ S'
        fstr      = f1_str  if fnum == 1 else f2_str
        tcol      = BLUE    if fnum == 1 else RED
        ax.set_title(
            f'Formula {fnum}   [{fstr}]\n'
            f'Valid when  {condition}   |   {sd_type}   |   {h_note}',
            fontsize=8.5, fontweight='bold', color=tcol, pad=10
        )
        badge_bg  = '#EBF4FF' if fnum == 1 else '#FFF5F5'
        badge_txt = 'Valid  →  RIGHT of envelope' if fnum == 1 \
                    else 'Valid  →  LEFT of envelope'
        badge_ec  = BLUE if fnum == 1 else RED
        ax.text(0.975, 0.965, badge_txt,
                transform=ax.transAxes, fontsize=7.5,
                ha='right', va='top', color=badge_ec,
                bbox=dict(boxstyle='round,pad=0.45',
                          facecolor=badge_bg, edgecolor=badge_ec,
                          linewidth=0.8, alpha=0.92))

        finalize_legend(ax, *std_extra_handles())

    plt.tight_layout(pad=2.0)
    return fig

# ── Render chart ──────────────────────────────────────────────────────────────
fig = build_design_chart() if '📐' in view_mode else build_analysis_chart()
st.pyplot(fig, use_container_width=True)

# ── Download chart ────────────────────────────────────────────────────────────
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=180,
            bbox_inches='tight', facecolor='#FFFFFF')
buf.seek(0)
ts       = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'summit_{sd_type}_{mode_label.replace(" ","_")}_{ts}.png'
st.download_button('⬇  Download Plot', data=buf,
                   file_name=filename, mime='image/png')

# ── Quick reference tiles ─────────────────────────────────────────────────────
if selected_speeds:
    st.markdown("---")
    st.markdown("**Quick Reference**")
    cols = st.columns(len(selected_speeds))
    for col, spd in zip(cols, selected_speeds):
        S_val = sd_table[spd][idx]
        Lmin  = min_length.get(spd, 0)
        N_x   = round(denom / S_val, 4) if S_val else '—'
        if S_val:
            L_gov = max((N_x * S_val**2) / denom, 2*S_val - denom/N_x)
            L_des = round(max(L_gov, Lmin), 1)
        else:
            L_des = '—'
        with col:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="label">{spd} km/h</div>
                <div class="value">{S_val} <span class="unit">m (S)</span></div>
                <div class="label" style="margin-top:4px">Crossover  N = {N_x}</div>
                <div class="label">L at crossover = {L_des} m</div>
                <div class="label">Lmin = {Lmin} m</div>
            </div>
            """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# ── Design Input Calculator ───────────────────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📋 Design Input Calculator")
st.markdown(
    "<span style='font-size:0.82rem;color:#475569'>"
    "Compute required vertical curve lengths for a list of locations. "
    "Global SD type from the sidebar is the fallback — override per row "
    "by adding a <b>SD_Type</b> column in your CSV.</span>",
    unsafe_allow_html=True
)

# ── Compute engine (shared by both tabs) ──────────────────────────────────────
def compute_row(N_in, spd_in, sdt_in, n_fmt='decimal'):
    """
    Returns dict of computed values for one input row.
    n_fmt: 'decimal' (0.045) or 'percent' (4.5 → divides by 100)
    """
    try:
        spd = int(float(spd_in))
        N_v = float(N_in)
        sdt = str(sdt_in).strip().upper()

        if n_fmt == 'percent':
            N_v = N_v / 100.0

        if spd not in sd_table:
            return {'error': f'Speed {spd} not in IRC table'}
        if sdt not in ('SSD', 'ISD', 'OSD'):
            return {'error': f'SD type "{sdt}" invalid — use SSD / ISD / OSD'}
        if sdt == 'OSD' and spd < OSD_MIN:
            return {'error': f'OSD N/A for {spd} km/h  (min 40 km/h)'}
        if N_v <= 0:
            return {'error': 'N must be > 0'}

        sd_i  = sd_index[sdt]
        S_val = sd_table[spd][sd_i]
        if S_val is None:
            return {'error': f'{sdt} not defined for {spd} km/h'}

        h1_, h2_ = heights[sdt]
        den_     = (np.sqrt(2*h1_) + np.sqrt(2*h2_))**2

        L1   = (N_v * S_val**2) / den_
        L2   = 2*S_val - den_ / N_v
        L_g  = max(L1, L2)
        Lmn  = min_length.get(spd, 0)
        L_d  = max(L_g, Lmn)
        K    = round(L_d / N_v, 2)

        gov  = 'F1  (L ≥ S)' if L1 >= L2 else 'F2  (L ≤ S)'
        k_note = '' if L1 >= L2 else '  [L<S regime]'
        notes = []
        if Lmn > L_g:
            notes.append('Lmin governs')
        if sdt == 'OSD' and spd == OSD_MIN:
            notes.append('OSD @ boundary speed')

        return {
            'S (m)':            S_val,
            'L1 (m)':           round(L1, 2),
            'L2 (m)':           round(L2, 2),
            'Governing':        gov,
            'Lmin (m)':         Lmn,
            'Required L (m)':   round(L_d, 2),
            'K = L/N':          f'{K}{k_note}',
            'Notes':            ' | '.join(notes) if notes else '—',
            'error':            None,
        }
    except Exception as e:
        return {'error': str(e)}


def results_from_df(df, n_fmt):
    """Run compute_row over a dataframe, return results dataframe."""
    rows = []
    for i, row in df.iterrows():
        # Resolve SD type: row-level overrides global
        sdt_row = str(row.get('SD_Type', '')).strip().upper()
        sdt_use = sdt_row if sdt_row in ('SSD', 'ISD', 'OSD') else sd_type

        r = compute_row(row['N'], row['Speed_kmh'], sdt_use, n_fmt)

        base = {
            'Row':          i + 1,
            'N (input)':    row['N'],
            'Speed (km/h)': row['Speed_kmh'],
            'SD Type used': sdt_use,
        }
        if r.get('error'):
            base['Required L (m)'] = '—'
            base['K = L/N']        = '—'
            base['Governing']      = '—'
            base['Lmin (m)']       = '—'
            base['Notes']          = f'⚠ {r["error"]}'
        else:
            base.update({k: v for k, v in r.items() if k != 'error'})
        rows.append(base)

    return pd.DataFrame(rows)


# ── Template CSV for download ─────────────────────────────────────────────────
_template = pd.DataFrame({
    'N':          [0.045, 0.072, 0.031, 0.055],
    'Speed_kmh':  [60,    80,    100,   65],
    'SD_Type':    ['SSD', 'ISD', '',    'OSD'],   # blank = use global
})
_tmpl_buf = io.StringIO()
_template.to_csv(_tmpl_buf, index=False)

# ── Two tabs ──────────────────────────────────────────────────────────────────
tab_manual, tab_batch = st.tabs(['✏️  Manual Entry', '📁  Batch Upload'])

# ─────────────────────────────────────────────────────────────────────────────
with tab_manual:
    st.markdown(
        "<span style='font-size:0.8rem;color:#64748B'>"
        "Edit rows directly. Blank SD_Type uses the global sidebar selection.</span>",
        unsafe_allow_html=True)

    n_fmt_manual = st.radio(
        'N format', ('Decimal  (e.g. 0.045)', 'Percentage  (e.g. 4.5)'),
        horizontal=True, key='nfmt_manual'
    )
    nfmt_m = 'percent' if 'Percent' in n_fmt_manual else 'decimal'

    _default_rows = pd.DataFrame({
        'N':          [0.045, 0.072, 0.031],
        'Speed_kmh':  [60,    80,    100],
        'SD_Type':    ['',    'ISD', 'SSD'],
    })

    input_df = st.data_editor(
        _default_rows,
        num_rows='dynamic',
        use_container_width=True,
        column_config={
            'N': st.column_config.NumberColumn(
                'N  (deviation angle)', min_value=0.0001,
                max_value=500.0, step=0.001, format='%.4f', required=True),
            'Speed_kmh': st.column_config.SelectboxColumn(
                'Speed (km/h)', options=speeds, required=True),
            'SD_Type': st.column_config.SelectboxColumn(
                'SD Type  (blank = global)', options=['', 'SSD', 'ISD', 'OSD']),
        },
        hide_index=True,
        key='manual_editor',
    )

    if input_df is not None and len(input_df) > 0:
        res_df = results_from_df(input_df, nfmt_m)
        st.markdown("#### Results")
        st.dataframe(res_df, use_container_width=True, hide_index=True)

        csv_out = io.StringIO()
        res_df.to_csv(csv_out, index=False)
        st.download_button(
            '⬇  Download Results (CSV)',
            data=csv_out.getvalue(),
            file_name=f'vc_results_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv', key='dl_manual'
        )

# ─────────────────────────────────────────────────────────────────────────────
with tab_batch:
    # Template download
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            '<div class="info-box">'
            '<b>CSV format:</b> Three columns — '
            '<code>N</code> (deviation angle) · '
            '<code>Speed_kmh</code> · '
            '<code>SD_Type</code> (optional — blank rows use global sidebar SD type)<br>'
            'Column order must match. Header row required.'
            '</div>',
            unsafe_allow_html=True)
    with c2:
        st.download_button(
            '⬇  Download Template CSV',
            data=_tmpl_buf.getvalue(),
            file_name='summit_curve_template.csv',
            mime='text/csv', key='dl_template'
        )

    n_fmt_batch = st.radio(
        'N format in your file',
        ('Decimal  (e.g. 0.045)', 'Percentage  (e.g. 4.5)'),
        horizontal=True, key='nfmt_batch'
    )
    nfmt_b = 'percent' if 'Percent' in n_fmt_batch else 'decimal'

    uploaded = st.file_uploader(
        'Upload CSV', type=['csv'],
        label_visibility='collapsed', key='batch_uploader'
    )

    if uploaded is not None:
        try:
            raw_df = pd.read_csv(uploaded)

            # Normalise column names — strip spaces, fix case
            raw_df.columns = [c.strip() for c in raw_df.columns]
            col_map = {}
            for c in raw_df.columns:
                cl = c.lower().replace(' ', '_')
                if cl in ('n', 'deviation_angle', 'dev_angle', 'angle'):
                    col_map[c] = 'N'
                elif cl in ('speed_kmh', 'speed', 'design_speed', 'v'):
                    col_map[c] = 'Speed_kmh'
                elif cl in ('sd_type', 'sd', 'sight_distance', 'type'):
                    col_map[c] = 'SD_Type'
            raw_df = raw_df.rename(columns=col_map)

            if 'N' not in raw_df.columns or 'Speed_kmh' not in raw_df.columns:
                st.error('CSV must have N and Speed_kmh columns. '
                         'Download the template above for reference.')
            else:
                if 'SD_Type' not in raw_df.columns:
                    raw_df['SD_Type'] = ''

                st.success(f'{len(raw_df):,} rows loaded.')

                with st.spinner('Computing...'):
                    res_df = results_from_df(raw_df, nfmt_b)

                # Summary stats
                total    = len(res_df)
                errors   = res_df['Notes'].str.startswith('⚠').sum()
                lmin_gov = res_df['Notes'].str.contains('Lmin governs',
                                  na=False).sum()

                s1, s2, s3 = st.columns(3)
                s1.metric('Total rows', f'{total:,}')
                s2.metric('Lmin governs', f'{lmin_gov:,}')
                s3.metric('Flagged / errors', f'{errors:,}')

                st.markdown("#### Results")
                st.dataframe(res_df, use_container_width=True, hide_index=True)

                csv_out = io.StringIO()
                res_df.to_csv(csv_out, index=False)
                st.download_button(
                    '⬇  Download Results (CSV)',
                    data=csv_out.getvalue(),
                    file_name=f'vc_results_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv', key='dl_batch'
                )

        except Exception as e:
            st.error(f'Error reading file: {e}')

# ── Footnote ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footnote">
* Minimum lengths from IRC:73-2023 Table 7.5 &nbsp;|&nbsp;
50/70, 60/85 → crest value used &nbsp;|&nbsp;
OSD applicable ≥ 40 km/h only &nbsp;|&nbsp;
Design Chart: governing = max(F₁, F₂) floored at Lmin &nbsp;|&nbsp;
K = L/N  (rate of grade change — verify against IRC Table 7.4)
</div>
""", unsafe_allow_html=True)

plt.close(fig)
