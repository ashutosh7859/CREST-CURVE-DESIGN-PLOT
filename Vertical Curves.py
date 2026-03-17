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
#  PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title='Vertical Curve Explorer',
    page_icon='🛣️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ----------------------------------------------------------------------
#  GLOBAL CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#0D1117;color:#C9D1D9;}
.stApp{background:#0D1117;}
.main .block-container{padding-top:0.8rem;padding-bottom:1.5rem;max-width:100%;background:#0D1117;}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{background:#010409;border-right:1px solid #21262D;}
section[data-testid="stSidebar"] *{color:#8B949E!important;}
section[data-testid="stSidebar"] hr{border-color:#21262D!important;margin:0.7rem 0!important;}
section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] h4,section[data-testid="stSidebar"] h5{
    color:#E6EDF3!important;font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;letter-spacing:0.04em!important;}
section[data-testid="stSidebar"] .stRadio label,
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
.footnote{font-size:0.67rem;color:#8B949E;border-top:1px solid #21262D;
    padding-top:0.5rem;margin-top:0.5rem;font-family:'JetBrains Mono',monospace;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#0D1117;}
::-webkit-scrollbar-thumb{background:#30363D;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#8B949E;}

/* ── Dataframe ── */
.stDataFrame{border:1px solid #21262D!important;border-radius:6px;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
#  COLOUR PALETTE
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
#  IRC DATA & HELPERS
# ----------------------------------------------------------------------
sd_table={20:(20,40,None),25:(25,50,None),30:(30,60,None),40:(45,90,135),50:(60,120,235),60:(80,160,300),65:(90,180,340),80:(130,260,470),100:(180,360,640),120:(250,500,835)}
heights={'SSD':(1.2,0.15),'ISD':(1.2,1.20),'OSD':(1.2,1.20)}
sd_index={'SSD':0,'ISD':1,'OSD':2}
OSD_MIN=40
hsd_table={spd:vals[0] for spd,vals in sd_table.items()}
SAG_H1=0.75
SAG_ALPHA=1.0
SAG_TAN=np.tan(np.radians(SAG_ALPHA))

def sag_denom(S):
    return 2*SAG_H1+2*S*SAG_TAN

min_length_standard={20:15,25:15,30:15,40:20,50:30,60:40,65:40,80:50,100:60,120:100}
min_length_expressway={**min_length_standard,80:70,100:85,120:100}
formula_label={'SSD':('h₁=1.2m, h₂=0.15m',''),'ISD':('h₁=1.2m, h₂=1.20m',''),'OSD':('h₁=1.2m, h₂=1.20m','')}
all_speeds=list(sd_table.keys())
standard_speeds=[s for s in all_speeds if s!=120]
colors=plt.cm.tab10(np.linspace(0,0.85,len(all_speeds)))
spd_color={spd:col for spd,col in zip(all_speeds,colors)}

# ----------------------------------------------------------------------
#  SIDEBAR (FIXED)
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛣️ Vertical Curve\nExplorer")
    st.markdown("---")
    
    st.markdown("##### Road Type")
    expressway=st.toggle('Expressway',value=False)
    if expressway:
        st.markdown("<span style='font-size:0.72rem;color:#A78BFA'>120 km/h enabled | Speed→Lmin: 80→70, 100→85, 120→100 m</span>",unsafe_allow_html=True)
    
    min_length=min_length_expressway if expressway else min_length_standard
    available_speeds=all_speeds if expressway else standard_speeds
    
    st.markdown("---")
    st.markdown("##### Curve Type")
    curve_type = st.radio('Curve Type', ('Crest', 'Sag'), index=0, label_visibility='collapsed')
    
    st.markdown("---")
    st.markdown("##### Sight Distance Type")
    if curve_type == 'Crest':
        sd_type = st.radio(
            'Sight Distance Type',
            ('SSD','ISD','OSD'),
            index=1,
            label_visibility='collapsed'
        )
    else:
        sd_type = 'HSD'
        st.markdown("**HSD**")
    
    st.markdown("---")
    st.markdown("##### Design Speeds (km/h)")
    avail_for_sd=available_speeds if sd_type!='OSD' else [s for s in available_speeds if s >=OSD_MIN]
    defaults=[s for s in ([80,100,120] if expressway else [80,100]) if s in avail_for_sd]
    selected_speeds=st.multiselect('Speeds',avail_for_sd,default=defaults,format_func=lambda x:f'{x} km/h',label_visibility='collapsed')
    
    st.markdown("---")
    st.markdown("##### View")
    split_formulas = st.toggle('Formula Split', value=False)

    st.markdown("---")
    st.markdown("##### Options")
    show_min=st.checkbox('Min Length (Table 7.5)',value=True)
    show_env=st.checkbox('L = S Envelope',value=True)

    st.markdown("---")
    st.caption(f"IRC:73-2023 | {datetime.date.today().strftime('%d %b %Y')}")


# ----------------------------------------------------------------------
#  FORMULA STRINGS (display only)
# ----------------------------------------------------------------------
f1_crest = "L = (N·S²) / ( (√(2h₁) + √(2h₂))² )"
f2_crest = "L = 2S − ( (√(2h₁) + √(2h₂))² ) / N"

f1_sag = "L = (N·S²) / (2h₁ + 2S·tanα)"
f2_sag = "L = 2S − (2h₁ + 2S·tanα) / N"
# ----------------------------------------------------------------------
#  VIEW MODE
# ----------------------------------------------------------------------
view_mode = "🔬 Formula Analysis" if split_formulas else "📐 Design Chart"

# ----------------------------------------------------------------------
#  AUTO AXIS COMPUTATION
# ----------------------------------------------------------------------
def auto_axes(speeds, cv_type, sdt, L_cap=1200):
    """Compute xmax/ymax/xgrid/ygrid from actual curve data."""
    items = []
    for spd in speeds:
        if cv_type == 'Crest':
            if sdt not in sd_index: continue
            Sv = sd_table[spd][sd_index[sdt]]
            if Sv is None: continue
            h1_, h2_ = heights[sdt]
            dv = (np.sqrt(2*h1_)+np.sqrt(2*h2_))**2
        else:
            Sv = sd_table[spd][0]
            dv = sag_denom(Sv)
        items.append((spd, Sv, dv))

    if not items:
        return 0.16, 700, 0.02, 100

    # Strategy: anchor on the HIGHEST speed (largest S).
    # Its crossover is the smallest N_x (sits closest to origin).
    # We extend to show meaningful F1 slope beyond that crossover.
    # Low-speed crossovers sitting far right are NOT used for xmax —
    # they would blow the window out making high-speed curves unreadable.
    items_sorted = sorted(items, key=lambda x: x[1])  # sort by S ascending
    spd_top, Sv_top, dv_top = items_sorted[-1]         # highest S speed

    # Crossover of highest speed
    Nx_top = dv_top / Sv_top
    # Extend to show F1 reaching L_cap for that speed
    N_f1_cap = (L_cap * dv_top) / (Sv_top**2)
    xmax_raw = max(Nx_top * 3.5, N_f1_cap)
    xmax = min(round(xmax_raw / 0.005) * 0.005 + 0.005, 0.30)

    # ymax: evaluate all curves at xmax
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
#  DERIVED VALUES
# ----------------------------------------------------------------------
if curve_type == 'Crest':
    if sd_type in heights:
        h1_c,h2_c=heights[sd_type]
        denom_crest=(np.sqrt(2*h1_c)+np.sqrt(2*h2_c))**2
        h_note=formula_label[sd_type][0]
    else:
        h1_c,h2_c=None
        denom_crest=None
        h_note='HSD'
else:
    denom_crest = None
    h_note = f'h₁={SAG_H1}m, α={SAG_ALPHA}°'

N_arr=np.linspace(0.0005,xmax,2000)
f1 = f1_crest if curve_type == 'Crest' else f1_sag
f2 = f2_crest if curve_type == 'Crest' else f2_sag
fg_str='L = max(F₁,F₂), then max(L,Lmin)'
mode_label='Design Chart' if '📐' in view_mode else 'Formula Analysis'
expr_badge='<span class="expressway-badge">EXPRESSWAY</span>' if expressway else ''

# ----------------------------------------------------------------------
#  PLOT HELPERS (exactly as original)
# ----------------------------------------------------------------------
matplotlib.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

def style_ax(ax):
    ax.set_facecolor(COLORS['bg_plot'])
    ax.tick_params(labelsize=8.5, colors=COLORS['muted'])
    for s in ax.spines.values():
        s.set_edgecolor(COLORS['border'])

def apply_axes(ax):
    ax.set_xlim(0,xmax)
    ax.set_ylim(0,ymax)
    ax.set_xticks(np.arange(0,xmax+xgrid,xgrid))
    ax.set_yticks(np.arange(0,ymax+ygrid,ygrid))
    ax.grid(True, color=COLORS['grid_color'], linewidth=0.8, zorder=0)
    ax.set_xlabel('Deviation Angle   N', fontsize=9.5,
                  color=COLORS['axis_label_color'], labelpad=6)
    ax.set_ylabel('Length of Vertical Curve   L  (m)', fontsize=9.5,
                  color=COLORS['axis_label_color'], labelpad=6)

def draw_min_lines(ax,spds):
    if not show_min:
        return
    seen={}
    for s in spds:
        Lm=min_length.get(s)
        if Lm:
            seen.setdefault(Lm,[]).append(s)
    # Sort by Lmin value so stagger direction is predictable
    sorted_lmins = sorted(seen.items())
    for i,(Lm,ss) in enumerate(sorted_lmins):
        if 0<Lm<ymax:
            ax.axhline(Lm,color=COLORS['muted'],linewidth=0.8,linestyle='-.',alpha=0.50,zorder=2)
            # Stagger labels: alternate offset to avoid overlap on close values
            v_offset = ymax * 0.012 if i % 2 == 0 else -ymax * 0.022
            va = 'bottom' if i % 2 == 0 else 'top'
            ax.text(xmax*0.998, Lm+v_offset,
                    f'Lmin={Lm}m  ({", ".join(str(x) for x in ss)} km/h)',
                    fontsize=6,color=COLORS['muted'],ha='right',va=va,alpha=0.85)

def draw_envelope(ax,dfn):
    if not show_env:
        return None
    Sr=np.linspace(5,max(ymax*1.5,1500),6000)
    Ne=np.array([dfn(S)/S for S in Sr])
    mk=(Ne>0)&(Ne<xmax)&(Sr>0)&(Sr<ymax)
    if mk.any():
        ax.plot(Ne[mk],Sr[mk],color=COLORS['envelope_line'],linewidth=1.1,linestyle='--',alpha=0.80,zorder=5)
    return Ne,Sr,mk

def fin_legend(ax,spds,eh=None,el=None):
    if not spds:
        return
    h,l=ax.get_legend_handles_labels()
    if eh:
        h+=eh
        l+=el
    leg=ax.legend(handles=h,labels=l,fontsize=7.5,loc='upper left',
                  framealpha=0.90,facecolor=COLORS['bg_card'],
                  edgecolor=COLORS['border'],
                  ncol=2 if len(spds)>5 else 1)
    leg.get_frame().set_linewidth(0.8)
    for txt in leg.get_texts():
        txt.set_color('#C9D1D9')

def std_extra():
    eh=[Line2D([0],[0],color=COLORS['envelope_line'],linewidth=1.1,linestyle='--',label='L=S boundary')]
    el=['L=S boundary']
    if show_min:
        eh.append(Line2D([0],[0],color=COLORS['muted'],linewidth=0.9,linestyle='-.',label='Lmin (Table 7.5)'))
        el.append('Lmin (Table 7.5)')
    return eh,el

def plot_segs(ax,spd,S_val,dv,Lmin,col,lbl):
    Nx=dv/S_val
    vis_any=False
    labelled=False
    if Nx>=xmax:
        Lf2=np.maximum(2*S_val-dv/N_arr,Lmin)
        v=(Lf2>=0)&(Lf2<=ymax)
        if v.any():
            ax.plot(N_arr[v],Lf2[v],color=col,linewidth=1.8,solid_capstyle='round',zorder=3,label=lbl)
            labelled=vis_any=True
            Nt,Lt=N_arr[v][-1],Lf2[v][-1]
            if Lt<ymax*0.97:
                ax.annotate('',xy=(Nt+xmax*0.012,Lt),xytext=(Nt,Lt),arrowprops=dict(arrowstyle='->',color=col,lw=0.8))
    else:
        mf2=(N_arr>0)&(N_arr<=Nx+1e-9)
        Nf2=N_arr[mf2]
        if len(Nf2)>0:
            Lf2=np.maximum(2*S_val-dv/Nf2,Lmin)
            v=(Lf2>=0)&(Lf2<=ymax)
            if v.any():
                ax.plot(Nf2[v],Lf2[v],color=col,linewidth=1.8,solid_capstyle='round',zorder=3,label=lbl)
                labelled=vis_any=True
        mf1=(N_arr>=Nx-1e-9)
        Nf1=N_arr[mf1]
        if len(Nf1)>0:
            Lf1=np.maximum((Nf1*S_val**2)/dv,Lmin)
            v=(Lf1>=0)&(Lf1<=ymax)
            if v.any():
                ax.plot(Nf1[v],Lf1[v],color=col,linewidth=1.8,solid_capstyle='round',zorder=3,label='_nolegend_')
                vis_any=True
        if 0<S_val<ymax:
            ax.plot(Nx,S_val,'o',color=col,markersize=5,zorder=6,alpha=0.90,markeredgecolor='white',markeredgewidth=0.6)
    if not labelled:
        ax.plot([],[],color=col,linewidth=1.8,label=lbl)
    return vis_any

def add_env_annotation(ax,res):
    if show_env and res:
        Ne,Sr,mk=res
        if mk.any():
            mid=len(Ne[mk])//3
            ax.annotate('L = S',xy=(Ne[mk][mid],Sr[mk][mid]),xytext=(-38,18),textcoords='offset points',
                        fontsize=8,fontstyle='italic',color='#E6EDF3',fontweight='bold',
                        arrowprops=dict(arrowstyle='-',color='#8B949E',lw=0.6))

# ----------------------------------------------------------------------
#  PLOT FUNCTIONS (CACHED) — exactly as original
# ----------------------------------------------------------------------
@st.cache_data
def crest_design(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig,ax=plt.subplots(figsize=(14,7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    style_ax(ax)
    inv=[]
    for spd in selected_speeds:
        Sv=sd_table[spd][sd_index[sd_type]]
        if Sv is None:
            continue
        Lmin=min_length.get(spd,0)
        if not plot_segs(ax,spd,Sv,denom_crest,Lmin,spd_color[spd],f'{spd} km/h (S={Sv}m)'):
            inv.append(spd)
    add_env_annotation(ax,draw_envelope(ax,lambda S:denom_crest))
    draw_min_lines(ax,selected_speeds)
    if inv:
        ax.text(0.01,0.012,'Not visible: '+', '.join(f'{s} km/h' for s in inv),
                transform=ax.transAxes,fontsize=6.5,color=COLORS['muted'],style='italic',va='bottom')
    apply_axes(ax)
    ax.set_title('Design Chart  —  Crest Vertical Curve',
                 fontsize=9, fontweight='bold', color=COLORS['success'], pad=10)
    ax.text(0.975,0.965,'← F2  ·  crossover ●  ·  F1 →',
            transform=ax.transAxes,fontsize=7,ha='right',va='top',color=COLORS['success'],
            bbox=dict(boxstyle='round,pad=0.4',facecolor=COLORS['bg_card'],
                      edgecolor=COLORS['success'],linewidth=0.7,alpha=0.90))
    fig.patch.set_facecolor(COLORS['bg_card'])
    fin_legend(ax,selected_speeds,*std_extra())
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def crest_analysis(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(16,7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    for ax,fn in [(ax1,1),(ax2,2)]:
        style_ax(ax)
        for spd in selected_speeds:
            Sv=sd_table[spd][sd_index[sd_type]]
            if Sv is None:
                continue
            L=(N_arr*Sv**2)/denom_crest if fn==1 else 2*Sv-denom_crest/N_arr
            ax.plot(N_arr,L,color=spd_color[spd],linewidth=1.8,label=f'{spd} km/h (S={Sv}m)',solid_capstyle='round')
        res=draw_envelope(ax,lambda S:denom_crest)
        if show_env and res:
            Ne,Sr,mk=res
            if mk.any():
                sh='#1C4B8F' if fn==1 else '#8B1A1A'   # deep blue / deep red on dark
                if fn==1:
                    ax.fill_betweenx(Sr[mk],Ne[mk],xmax,color=sh,alpha=0.35,zorder=0)
                else:
                    ax.fill_betweenx(Sr[mk],0,Ne[mk],color=sh,alpha=0.35,zorder=0)
                mid=len(Ne[mk])//3
                off=(-38,18) if fn==1 else (-38,-18)
                lbl_col=COLORS['primary'] if fn==1 else COLORS['danger']
                ax.annotate('L > S' if fn==1 else 'L < S',xy=(Ne[mk][mid],Sr[mk][mid]),xytext=off,
                            textcoords='offset points',fontsize=8.5,fontstyle='italic',
                            color=lbl_col,fontweight='bold',
                            arrowprops=dict(arrowstyle='-',color='#8B949E',lw=0.6))
        for spd in selected_speeds:
            Sv=sd_table[spd][sd_index[sd_type]]
            if Sv and 0<Sv<ymax:
                ax.axhline(Sv,color=spd_color[spd],linewidth=0.4,linestyle='--',alpha=0.18)
        draw_min_lines(ax,selected_speeds)
        apply_axes(ax)
        cond='L ≥ S' if fn==1 else 'L ≤ S'
        tcol=COLORS['primary'] if fn==1 else COLORS['danger']
        ax.set_title(f'Formula {fn}  —  Valid when  {cond}',
                     fontsize=9,fontweight='bold',color=tcol,pad=10)
        bt='Valid  →  right of envelope' if fn==1 else 'Valid  →  left of envelope'
        bg=COLORS['bg_card']
        ax.text(0.975,0.965,bt,transform=ax.transAxes,fontsize=7,ha='right',va='top',color=tcol,
                bbox=dict(boxstyle='round,pad=0.4',facecolor=bg,edgecolor=tcol,linewidth=0.7,alpha=0.90))
        fin_legend(ax,selected_speeds,*std_extra())
    fig.patch.set_facecolor(COLORS['bg_card'])
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def sag_design(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig,ax=plt.subplots(figsize=(14,7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    style_ax(ax)
    inv=[]
    for spd in selected_speeds:
        Sv=hsd_table.get(spd)
        if Sv is None:
            continue
        Lmin=min_length.get(spd,0)
        ds=sag_denom(Sv)
        if not plot_segs(ax,spd,Sv,ds,Lmin,spd_color[spd],f'{spd} km/h (HSD={Sv}m)'):
            inv.append(spd)
    add_env_annotation(ax,draw_envelope(ax,sag_denom))
    draw_min_lines(ax,selected_speeds)
    if inv:
        ax.text(0.01,0.012,'Not visible: '+', '.join(f'{s} km/h' for s in inv),
                transform=ax.transAxes,fontsize=6.5,color=COLORS['muted'],style='italic',va='bottom')
    apply_axes(ax)
    ax.set_title('Design Chart  —  Sag Vertical Curve',
                 fontsize=9,fontweight='bold',color=COLORS['warning'],pad=10)
    ax.text(0.975,0.965,'← F2  ·  crossover ●  ·  F1 →',
            transform=ax.transAxes,fontsize=7,ha='right',va='top',color=COLORS['warning'],
            bbox=dict(boxstyle='round,pad=0.4',facecolor=COLORS['bg_card'],
                      edgecolor=COLORS['warning'],linewidth=0.7,alpha=0.90))
    fig.patch.set_facecolor(COLORS['bg_card'])
    fin_legend(ax,selected_speeds,*std_extra())
    plt.tight_layout(pad=2.0)
    return fig

@st.cache_data
def sag_analysis(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid):
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(16,7))
    fig.patch.set_facecolor(COLORS['bg_card'])
    for ax,fn in [(ax1,1),(ax2,2)]:
        style_ax(ax)
        for spd in selected_speeds:
            Sv=hsd_table.get(spd)
            if Sv is None:
                continue
            ds=sag_denom(Sv)
            L=(N_arr*Sv**2)/ds if fn==1 else 2*Sv-ds/N_arr
            ax.plot(N_arr,L,color=spd_color[spd],linewidth=1.8,label=f'{spd} km/h (HSD={Sv}m)',solid_capstyle='round')
        res=draw_envelope(ax,sag_denom)
        if show_env and res:
            Ne,Sr,mk=res
            if mk.any():
                sh='#1C4B8F' if fn==1 else '#8B1A1A'
                if fn==1:
                    ax.fill_betweenx(Sr[mk],Ne[mk],xmax,color=sh,alpha=0.35,zorder=0)
                else:
                    ax.fill_betweenx(Sr[mk],0,Ne[mk],color=sh,alpha=0.35,zorder=0)
                mid=len(Ne[mk])//3
                off=(-38,18) if fn==1 else (-38,-18)
                lbl_col=COLORS['primary'] if fn==1 else COLORS['danger']
                ax.annotate('L > S' if fn==1 else 'L < S',xy=(Ne[mk][mid],Sr[mk][mid]),xytext=off,
                            textcoords='offset points',fontsize=8.5,fontstyle='italic',
                            color=lbl_col,fontweight='bold',
                            arrowprops=dict(arrowstyle='-',color='#8B949E',lw=0.6))
        for spd in selected_speeds:
            Sv=hsd_table.get(spd)
            if Sv and 0<Sv<ymax:
                ax.axhline(Sv,color=spd_color[spd],linewidth=0.4,linestyle='--',alpha=0.18)
        draw_min_lines(ax,selected_speeds)
        apply_axes(ax)
        cond='L ≥ S' if fn==1 else 'L ≤ S'
        tcol=COLORS['primary'] if fn==1 else COLORS['danger']
        ax.set_title(f'Formula {fn}  —  Valid when  {cond}',
                     fontsize=9,fontweight='bold',color=tcol,pad=10)
        bt='Valid  →  right of envelope' if fn==1 else 'Valid  →  left of envelope'
        ax.text(0.975,0.965,bt,transform=ax.transAxes,fontsize=7,ha='right',va='top',color=tcol,
                bbox=dict(boxstyle='round,pad=0.4',facecolor=COLORS['bg_card'],edgecolor=tcol,linewidth=0.7,alpha=0.90))
        fin_legend(ax,selected_speeds,*std_extra())
    fig.patch.set_facecolor(COLORS['bg_card'])
    plt.tight_layout(pad=2.0)
    return fig

# ----------------------------------------------------------------------
#  MAIN CONTENT
# ----------------------------------------------------------------------
if curve_type == 'Crest':
    # ── Header ────────────────────────────────────────────────────────────
    expr_chip = '<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''
    st.markdown(f"""
    <div class="vc-header">
      <div class="vc-header-left">
        <h1>Vertical Curve Explorer</h1>
        <p>IRC:73-2023  ·  Crest Curve</p>
      </div>
      <div class="vc-header-right">
        <span class="chip chip-blue">{sd_type}</span>
        <span class="chip chip-muted">{h_note}</span>
        <span class="chip chip-green">{'Expressway' if expressway else 'Standard'}</span>
        {expr_chip}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Formula strip ─────────────────────────────────────────────────────
    if not split_formulas:
        st.markdown(f"""
        <div class="formula-strip">
          <span class="f-label">F1</span>
          <span class="f-eq f1">{f1_crest}</span>
          <span class="f-sub">valid  L ≥ S</span>
          <span class="divider">  |  </span>
          <span class="f-label">F2</span>
          <span class="f-eq f2">{f2_crest}</span>
          <span class="f-sub">valid  L ≤ S</span>
          <span class="divider">  |  </span>
          <span class="f-sub">governing = max(F1, F2) ≥ Lmin</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        cf1,cf2=st.columns(2)
        with cf1: st.markdown(f'<div class="formula-card">F1  —  {f1_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≥ S</span></div>',unsafe_allow_html=True)
        with cf2: st.markdown(f'<div class="formula-card red">F2  —  {f2_crest}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≤ S</span></div>',unsafe_allow_html=True)
    
    fc=crest_design(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid) if '📐' in view_mode else crest_analysis(selected_speeds, sd_type, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid)
    st.pyplot(fc,width="stretch")
    bc=io.BytesIO()
    fc.savefig(bc,format='png',dpi=180,bbox_inches='tight',facecolor=COLORS['bg_card'])
    bc.seek(0)
    st.download_button('⬇  Download Plot',data=bc,file_name=f'crest_{sd_type}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png',mime='image/png',key='dl_plot')
    plt.close(fc)
    
    if selected_speeds:
        st.markdown("---")
        st.markdown("**Quick Reference — Crest**")
        cols=st.columns(len(selected_speeds))
        for col,spd in zip(cols,selected_speeds):
            Sv=sd_table[spd][sd_index[sd_type]]
            Lmin=min_length.get(spd,0)
            if Sv:
                Nx=round(denom_crest/Sv,4)
                Lg=max((Nx*Sv**2)/denom_crest,2*Sv-denom_crest/Nx)
                Ld=round(max(Lg,Lmin),1)
            else:
                Nx=Ld='—'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (S)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>',unsafe_allow_html=True)

else:
    # ── Header ────────────────────────────────────────────────────────────
    expr_chip = '<span class="chip chip-purple">EXPRESSWAY</span>' if expressway else ''
    st.markdown(f"""
    <div class="vc-header">
      <div class="vc-header-left">
        <h1>Vertical Curve Explorer</h1>
        <p>IRC:73-2023  ·  Sag Curve</p>
      </div>
      <div class="vc-header-right">
        <span class="chip chip-amber">HSD</span>
        <span class="chip chip-muted">h₁={SAG_H1}m  ·  α={SAG_ALPHA}°</span>
        <span class="chip chip-green">{'Expressway' if expressway else 'Standard'}</span>
        {expr_chip}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Formula strip ─────────────────────────────────────────────────────
    if not split_formulas:
        st.markdown(f"""
        <div class="formula-strip">
          <span class="f-label">F1</span>
          <span class="f-eq f1">{f1_sag}</span>
          <span class="f-sub">valid  L ≥ S</span>
          <span class="divider">  |  </span>
          <span class="f-label">F2</span>
          <span class="f-eq f2">{f2_sag}</span>
          <span class="f-sub">valid  L ≤ S</span>
          <span class="divider">  |  </span>
          <span class="f-sub">governing = max(F1, F2) ≥ Lmin</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        sf1,sf2=st.columns(2)
        with sf1: st.markdown(f'<div class="formula-card">F1  —  {f1_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≥ S</span></div>',unsafe_allow_html=True)
        with sf2: st.markdown(f'<div class="formula-card red">F2  —  {f2_sag}<br><span style="color:#8B949E;font-size:0.68rem">Valid when  L ≤ S</span></div>',unsafe_allow_html=True)
    
    fs=sag_design(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid) if '📐' in view_mode else sag_analysis(selected_speeds, expressway, show_min, show_env, xmax, ymax, xgrid, ygrid)
    st.pyplot(fs,width="stretch")
    bs=io.BytesIO()
    fs.savefig(bs,format='png',dpi=180,bbox_inches='tight',facecolor=COLORS['bg_card'])
    bs.seek(0)
    st.download_button('⬇  Download Plot',data=bs,file_name=f'sag_HSD_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png',mime='image/png',key='dl_plot')
    plt.close(fs)
    
    if selected_speeds:
        st.markdown("---")
        st.markdown("**Quick Reference — Sag**")
        cols=st.columns(len(selected_speeds))
        for col,spd in zip(cols,selected_speeds):
            Sv=hsd_table.get(spd)
            Lmin=min_length.get(spd,0)
            if Sv:
                ds=sag_denom(Sv)
                Nx=round(ds/Sv,4)
                Lg=max((Nx*Sv**2)/ds,2*Sv-ds/Nx)
                Ld=round(max(Lg,Lmin),1)
            else:
                Nx=Ld='—'
            with col:
                st.markdown(f'<div class="metric-tile"><div class="label">{spd} km/h</div><div class="value">{Sv}<span class="unit">m (HSD)</span></div><div class="label" style="margin-top:4px">Crossover N={Nx}</div><div class="label">L at crossover={Ld}m</div><div class="label">Lmin={Lmin}m</div></div>',unsafe_allow_html=True)

# ----------------------------------------------------------------------
#  CALCULATOR SECTION (exactly as original)
# ----------------------------------------------------------------------
st.markdown("---")
st.markdown("<span style='font-family:JetBrains Mono,monospace;font-size:0.95rem;font-weight:600;color:#E6EDF3'>📋  Design Input Calculator</span>", unsafe_allow_html=True)
st.markdown("<span style='font-size:0.76rem;color:#8B949E'>Compute required lengths for a list of locations. Row-level <code>Curve_Type</code> and <code>SD_Type</code> override global sidebar. Sag rows always use HSD.</span>",unsafe_allow_html=True)

_tmpl=pd.DataFrame({'N':[0.045,0.072,0.031,0.055,0.038],'Speed_kmh':[60,80,100,65,80],'SD_Type':['SSD','ISD','','OSD',''],'Curve_Type':['Crest','Crest','Crest','Crest','Sag']})
_tb=io.StringIO()
_tmpl.to_csv(_tb,index=False)

tm,tb=st.tabs(['✏️  Manual Entry','📁  Batch Upload'])

def compute_row(N_in,spd_in,sdt_in,curve_type='crest',n_fmt='decimal'):
    try:
        spd=int(float(spd_in))
        N_v=float(N_in)
        if n_fmt=='percent':
            N_v/=100.0
        if N_v<=0:
            return {'error':'N must be > 0'}
        if spd==120 and not expressway:
            return {'error':'120 km/h applicable for Expressway only'}
        if spd not in sd_table:
            return {'error':f'Speed {spd} not in IRC table'}
        Lmn=min_length.get(spd,0)
        if curve_type=='sag':
            Sv=hsd_table.get(spd)
            if Sv is None:
                return {'error':f'HSD not defined for {spd} km/h'}
            den_=sag_denom(Sv)
            sd_used='HSD'
        else:
            sdt=str(sdt_in).strip().upper()
            if sdt not in ('SSD','ISD','OSD'):
                return {'error':f'SD type "{sdt}" invalid'}
            if sdt=='OSD' and spd<OSD_MIN:
                return {'error':f'OSD N/A for {spd} km/h (min {OSD_MIN} km/h)'}
            sdi=sd_index[sdt]
            Sv=sd_table[spd][sdi]
            if Sv is None:
                return {'error':f'{sdt} not defined for {spd} km/h'}
            h1_,h2_=heights[sdt]
            den_=(np.sqrt(2*h1_)+np.sqrt(2*h2_))**2
            sd_used=sdt
        L1=(N_v*Sv**2)/den_
        L2=2*Sv-den_/N_v
        Lg=max(L1,L2)
        Ld=max(Lg,Lmn)
        K=round(Ld/N_v,2)
        gov='F1 (L≥S)' if L1>=L2 else 'F2 (L≤S)'
        notes=[]
        if Lmn>Lg:
            notes.append('Lmin governs')
        if expressway:
            notes.append('Expressway Lmin')
        kn='' if L1>=L2 else ' [L<S]'
        return {'S (m)':Sv,'SD/HSD used':sd_used,'L1 (m)':round(L1,2),'L2 (m)':round(L2,2),'Governing':gov,'Lmin (m)':Lmn,'Required L (m)':round(Ld,2),'K=L/N':f'{K}{kn}','Notes':' | '.join(notes) if notes else '—','error':None}
    except Exception as e:
        return {'error':str(e)}

def results_from_df(df,n_fmt):
    rows=[]
    for i,row in df.iterrows():
        sdt_r=str(row.get('SD_Type','')).strip().upper()
        sdt_u=sdt_r if sdt_r in ('SSD','ISD','OSD') else sd_type
        ct_r=str(row.get('Curve_Type','')).strip().lower()
        ct_u='sag' if ct_r=='sag' else 'crest'
        r=compute_row(row['N'],row['Speed_kmh'],sdt_u,ct_u,n_fmt)
        base={'Row':i+1,'N (input)':row['N'],'Speed (km/h)':row['Speed_kmh'],'Curve Type':ct_u.capitalize(),'SD Type used':sdt_u if ct_u=='crest' else 'HSD'}
        if r.get('error'):
            base.update({'Required L (m)':'—','K=L/N':'—','Governing':'—','Lmin (m)':'—','Notes':f'⚠ {r["error"]}'})
        else:
            base.update({k:v for k,v in r.items() if k!='error'})
        rows.append(base)
    return pd.DataFrame(rows)

def plot_calc(res_df,nfmt):
    valid=res_df[~res_df['Notes'].str.startswith('⚠',na=False)].copy()
    if valid.empty:
        st.warning('No valid rows to plot.')
        return
    pspds=sorted(valid['Speed (km/h)'].astype(int).unique().tolist())
    nv=valid['N (input)'].astype(float)
    lv=valid['Required L (m)'].astype(float)
    if nfmt=='percent':
        nv/=100.0
    anmax=round(nv.max()*1.25+0.005,3)
    aymax=int(lv.max()*1.25/50+1)*50
    fig,ax=plt.subplots(figsize=(13,6))
    fig.patch.set_facecolor('#FFFFFF')
    style_ax(ax)
    Nbg=np.linspace(0.0005,anmax,2000)
    plotted=set()
    for spd in pspds:
        col=spd_color.get(spd,'#888888')
        Lmin=min_length.get(spd,0)
        rows=valid[valid['Speed (km/h)'].astype(int)==spd]
        for sdt in rows[rows['Curve Type']=='Crest']['SD Type used'].unique():
            if sdt=='HSD': continue
            h1_,h2_=heights[sdt]
            den_=(np.sqrt(2*h1_)+np.sqrt(2*h2_))**2
            Sv=sd_table[spd][sd_index[sdt]]
            if Sv is None: continue
            Ld=np.maximum(np.maximum((Nbg*Sv**2)/den_,2*Sv-den_/Nbg),Lmin)
            lbl=f'{spd} km/h Crest ({sdt})'
            ls='-' if sdt=='SSD' else ('--' if sdt=='ISD' else ':')
            ax.plot(Nbg,Ld,color=col,linewidth=1.5,linestyle=ls,alpha=0.5,zorder=2,label=lbl if lbl not in plotted else '_nolegend_')
            plotted.add(lbl)
        if len(rows[rows['Curve Type']=='Sag'])>0:
            Sv=hsd_table.get(spd)
            if Sv:
                ds=sag_denom(Sv)
                Ld=np.maximum(np.maximum((Nbg*Sv**2)/ds,2*Sv-ds/Nbg),Lmin)
                lbl=f'{spd} km/h Sag (HSD)'
                ax.plot(Nbg,Ld,color=col,linewidth=1.5,linestyle='-.',alpha=0.5,zorder=2,label=lbl if lbl not in plotted else '_nolegend_')
                plotted.add(lbl)
    for _,row in valid.iterrows():
        spd=int(row['Speed (km/h)'])
        n_in=float(row['N (input)'])
        if nfmt=='percent':
            n_in/=100.0
        l_out=float(row['Required L (m)'])
        col=spd_color.get(spd,'#888888')
        mk='o' if row['Curve Type']=='Crest' else 's'
        ax.plot(n_in,l_out,mk,color=col,markersize=7,zorder=6,markeredgecolor='white',markeredgewidth=0.8)
    ax.set_xlim(0,anmax)
    ax.set_ylim(0,aymax)
    ax.grid(True,color=COLORS['border'],linewidth=0.7,zorder=0)
    ax.set_xlabel('Deviation Angle   N',fontsize=10,color=COLORS['axis_label_color'],labelpad=6)
    ax.set_ylabel('Length of Vertical Curve   L  (m)',fontsize=10,color=COLORS['axis_label_color'],labelpad=6)
    ax.set_title(f'Calculated — {len(valid)} location(s) | ● Crest  ■ Sag | Background = governing curves',fontsize=9,fontweight='bold',color=COLORS['success'],pad=10)
    h_,l_=ax.get_legend_handles_labels()
    if h_:
        leg=ax.legend(handles=h_,labels=l_,fontsize=7.5,loc='upper left',framealpha=0.92,edgecolor=COLORS['border'],ncol=2 if len(h_)>4 else 1)
        leg.get_frame().set_linewidth(0.8)
    plt.tight_layout(pad=2.0)
    st.pyplot(fig,width="stretch")
    pb=io.BytesIO()
    fig.savefig(pb,format='png',dpi=180,bbox_inches='tight',facecolor=COLORS['bg_card'])
    pb.seek(0)
    st.download_button('⬇  Download Plot (PNG)',data=pb,file_name=f'vc_calc_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png',mime='image/png',key=f'dl_cp_{id(res_df)}')
    plt.close(fig)

with tm:
    st.markdown("<span style='font-size:0.8rem;color:#64748B'>Blank SD_Type uses sidebar. Blank Curve_Type → Crest.</span>",unsafe_allow_html=True)
    nfm=st.radio('N format',('Decimal (e.g. 0.045)','Percentage (e.g. 4.5)'),horizontal=True,key='nfmt_manual')
    nfmt_m='percent' if 'Percent' in nfm else 'decimal'
    dr=pd.DataFrame({'N':[0.045,0.072,0.031,0.038],'Speed_kmh':[60,80,100,80],'SD_Type':['','ISD','SSD',''],'Curve_Type':['Crest','Crest','Crest','Sag']})
    idf=st.data_editor(dr,num_rows='dynamic',width="stretch",column_config={
        'N':st.column_config.NumberColumn('N',min_value=0.0001,max_value=500.0,step=0.001,format='%.4f',required=True),
        'Speed_kmh':st.column_config.SelectboxColumn('Speed (km/h)',options=available_speeds,required=True),
        'SD_Type':st.column_config.SelectboxColumn('SD Type (blank=global)',options=['','SSD','ISD','OSD']),
        'Curve_Type':st.column_config.SelectboxColumn('Curve Type',options=['Crest','Sag'])},
        hide_index=True,key='manual_editor')
    
    if idf is not None and len(idf)>0:
        rdf=results_from_df(idf,nfmt_m)
        st.markdown("#### Results")
        st.dataframe(rdf,width="stretch",hide_index=True)
        co=io.StringIO()
        rdf.to_csv(co,index=False)
        st.download_button('⬇  Download Results (CSV)',data=co.getvalue(),file_name=f'vc_manual_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',mime='text/csv',key='dl_manual')
        st.markdown("#### Plot")
        plot_calc(rdf,nfmt_m)

with tb:
    c1,c2=st.columns([3,1])
    with c1:
        st.markdown('<div class="info-box"><b>CSV columns:</b> <code>N</code> · <code>Speed_kmh</code> · <code>SD_Type</code> (opt) · <code>Curve_Type</code> (Crest/Sag — blank=Crest)<br>Header required. Aliases accepted.</div>',unsafe_allow_html=True)
    with c2:
        st.download_button('⬇  Template',data=_tb.getvalue(),file_name='vc_template.csv',mime='text/csv',key='dl_tmpl')
    nfb=st.radio('N format in file',('Decimal (e.g. 0.045)','Percentage (e.g. 4.5)'),horizontal=True,key='nfmt_batch')
    nfmt_b='percent' if 'Percent' in nfb else 'decimal'
    up=st.file_uploader('Upload CSV',type=['csv'],label_visibility='collapsed',key='batch_uploader')
    
    if up is not None:
        try:
            rdf2=pd.read_csv(up)
            rdf2.columns=[c.strip() for c in rdf2.columns]
            cm={}
            for c in rdf2.columns:
                cl=c.lower().replace(' ','_')
                if cl in ('n','deviation_angle','dev_angle','angle'):
                    cm[c]='N'
                elif cl in ('speed_kmh','speed','design_speed','v'):
                    cm[c]='Speed_kmh'
                elif cl in ('sd_type','sd','sight_distance','type'):
                    cm[c]='SD_Type'
                elif cl in ('curve_type','curve','vc_type','vertical_curve'):
                    cm[c]='Curve_Type'
            rdf2=rdf2.rename(columns=cm)
            if 'N' not in rdf2.columns or 'Speed_kmh' not in rdf2.columns:
                st.error('CSV must have N and Speed_kmh columns.')
            else:
                if 'SD_Type' not in rdf2.columns:
                    rdf2['SD_Type']=''
                if 'Curve_Type' not in rdf2.columns:
                    rdf2['Curve_Type']='Crest'
                st.success(f'{len(rdf2):,} rows loaded.')
                with st.spinner('Computing...'):
                    res2=results_from_df(rdf2,nfmt_b)
                tot=len(res2)
                err=res2['Notes'].str.startswith('⚠').sum()
                lgov=res2['Notes'].str.contains('Lmin governs',na=False).sum()
                nc=(res2['Curve Type']=='Crest').sum()
                ns=(res2['Curve Type']=='Sag').sum()
                s1,s2,s3,s4,s5=st.columns(5)
                s1.metric('Total',f'{tot:,}')
                s2.metric('Crest',f'{nc:,}')
                s3.metric('Sag',f'{ns:,}')
                s4.metric('Lmin governs',f'{lgov:,}')
                s5.metric('Errors',f'{err:,}')
                st.markdown("#### Results")
                st.dataframe(res2,width="stretch",hide_index=True)
                co2=io.StringIO()
                res2.to_csv(co2,index=False)
                st.download_button('⬇  Download Results (CSV)',data=co2.getvalue(),file_name=f'vc_batch_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',mime='text/csv',key='dl_batch')
                st.markdown("#### Plot")
                plot_calc(res2,nfmt_b)
        except Exception as e:
            st.error(f'Error reading file: {e}')

# ----------------------------------------------------------------------
#  FOOTNOTE
# ----------------------------------------------------------------------
en='Expressway: Lmin 80→70, 100→85, 120→100m | ' if expressway else ''
st.markdown(f'<div class="footnote">* {en}Lmin IRC:73-2023 Table 7.5 | Crest: SSD/ISD/OSD | Sag: HSD (h₁={SAG_H1}m, α={SAG_ALPHA}°, denom=1.50+0.035S) | OSD≥{OSD_MIN}km/h | 120km/h Expressway only | K=L/N (verify IRC Table 7.4)</div>',unsafe_allow_html=True)