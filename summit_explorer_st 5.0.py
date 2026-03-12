import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import streamlit as st
import datetime
import io

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
    xmax  = st.slider('X max', 0.05, 0.30, 0.16, 0.01, format='%.2f')
    ymax  = st.slider('Y max', 100, 1200, 700, 50)
    st.markdown("##### Grid Spacing")
    xgrid = st.slider('X grid', 0.005, 0.05, 0.02, 0.005, format='%.3f')
    ygrid = st.slider('Y grid', 25, 200, 100, 25)

    st.markdown("---")
    st.caption(f"IRC:73-2023  |  {datetime.date.today().strftime('%d %b %Y')}")

# ── Derived values ────────────────────────────────────────────────────────────
h1, h2  = heights[sd_type]
denom   = (np.sqrt(2*h1) + np.sqrt(2*h2))**2
h_note, h_desc = formula_label[sd_type]
idx = sd_index[sd_type]
A   = np.linspace(0.0005, xmax, 2000)

f1_str = ('L = A · S²  /  (√2h₁ + √2h₂)²'
          if sd_type == 'SSD' else 'L = A · S²  /  (2√2h)²')
f2_str = ('L = 2S  −  (√2h₁ + √2h₂)²  /  A'
          if sd_type == 'SSD' else 'L = 2S  −  (2√2h)²  /  A')
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

# ── Shared helpers ────────────────────────────────────────────────────────────
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
    ax.set_xlabel('Deviation Angle   A  (N)', fontsize=10,
                  color='#4A5568', labelpad=6)
    ax.set_ylabel('Length of Vertical Curve   L  (m)', fontsize=10,
                  color='#4A5568', labelpad=6)

def draw_envelope(ax):
    if not show_env:
        return None
    S_r  = np.linspace(5, max(ymax, 1200), 4000)
    A_e  = denom / S_r
    mask = (A_e > 0) & (A_e < xmax) & (S_r > 0) & (S_r < ymax)
    if mask.any():
        ax.plot(A_e[mask], S_r[mask],
                color='#111111', linewidth=1.1,
                linestyle='--', alpha=0.80, zorder=5)
    return A_e, S_r, mask

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

        L1    = (A * S_val**2) / denom
        L2    = 2*S_val - denom / A
        L_gov = np.maximum(L1, L2)
        L_des = np.maximum(L_gov, Lmin)

        ax.plot(A, L_des, color=col, linewidth=2.0,
                label=f'{spd} km/h  (S = {S_val} m)',
                solid_capstyle='round', zorder=3)

        # Crossover dot
        A_x = denom / S_val
        if 0 < A_x < xmax and 0 < S_val < ymax:
            ax.plot(A_x, S_val, 'o', color=col,
                    markersize=5, zorder=6, alpha=0.85)

        # Shade where Lmin governs
        if show_min and Lmin > 0:
            mask_floor = (L_gov < Lmin)
            if mask_floor.any():
                ax.fill_between(A[mask_floor],
                                L_gov[mask_floor], Lmin,
                                color=col, alpha=0.06, zorder=1)

    # Envelope
    result = draw_envelope(ax)
    if show_env and result is not None:
        A_e, S_r, mask = result
        if mask.any():
            mid = len(A_e[mask]) // 3
            ax.annotate('L = S',
                        xy=(A_e[mask][mid], S_r[mask][mid]),
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

    extra_h = [Line2D([0], [0], color='#111111', linewidth=1.1,
                      linestyle='--', label='L = S  boundary')]
    extra_l = ['L = S  boundary']
    if show_min:
        extra_h.append(Line2D([0], [0], color='#94A3B8', linewidth=0.9,
                               linestyle='-.', label='Lmin  (Table 7.5)'))
        extra_l.append('Lmin  (Table 7.5)')
    finalize_legend(ax, extra_h, extra_l)
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
            L   = (A * S_val**2) / denom if fnum == 1 else 2*S_val - denom/A
            ax.plot(A, L, color=col, linewidth=1.8,
                    label=f'{spd} km/h  (S = {S_val} m)',
                    solid_capstyle='round')

        result = draw_envelope(ax)
        if show_env and result is not None:
            A_e, S_r, mask = result
            if mask.any():
                shade_col = '#2B6CB0' if fnum == 1 else '#C53030'
                if fnum == 1:
                    ax.fill_betweenx(S_r[mask], A_e[mask], xmax,
                                     color=shade_col, alpha=0.04, zorder=0)
                else:
                    ax.fill_betweenx(S_r[mask], 0, A_e[mask],
                                     color=shade_col, alpha=0.04, zorder=0)
                mid       = len(A_e[mask]) // 3
                offset    = (-38, 18) if fnum == 1 else (-38, -18)
                label_txt = 'L > S' if fnum == 1 else 'L < S'
                ax.annotate(label_txt,
                            xy=(A_e[mask][mid], S_r[mask][mid]),
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

        extra_h = [Line2D([0], [0], color='#111111', linewidth=1.1,
                          linestyle='--', label='L = S  boundary')]
        extra_l = ['L = S  boundary']
        if show_min:
            extra_h.append(Line2D([0], [0], color='#94A3B8', linewidth=0.9,
                                   linestyle='-.', label='Lmin  (Table 7.5)'))
            extra_l.append('Lmin  (Table 7.5)')
        finalize_legend(ax, extra_h, extra_l)

    plt.tight_layout(pad=2.0)
    return fig

# ── Render ────────────────────────────────────────────────────────────────────
fig = build_design_chart() if '📐' in view_mode else build_analysis_chart()
st.pyplot(fig, use_container_width=True)

# ── Download ──────────────────────────────────────────────────────────────────
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
        A_x   = round(denom / S_val, 4) if S_val else '—'
        if S_val:
            L_gov = max((A_x * S_val**2) / denom, 2*S_val - denom/A_x)
            L_des = round(max(L_gov, Lmin), 1)
        else:
            L_des = '—'
        with col:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="label">{spd} km/h</div>
                <div class="value">{S_val} <span class="unit">m (S)</span></div>
                <div class="label" style="margin-top:4px">Crossover  A = {A_x}</div>
                <div class="label">L at crossover = {L_des} m</div>
                <div class="label">Lmin = {Lmin} m</div>
            </div>
            """, unsafe_allow_html=True)

# ── Footnote ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footnote">
* Minimum lengths from IRC:73-2023 Table 7.5 &nbsp;|&nbsp;
50/70, 60/85 → crest value used &nbsp;|&nbsp;
OSD applicable ≥ 40 km/h only &nbsp;|&nbsp;
Design Chart: governing = max(F₁, F₂) floored at Lmin
</div>
""", unsafe_allow_html=True)

plt.close(fig)
