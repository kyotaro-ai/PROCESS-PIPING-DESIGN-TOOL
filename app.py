import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# =====================================================
# Page Config
# =====================================================

st.set_page_config(
    page_title="PROCESS PIPING DESIGN TOOL",
    layout="wide"
)

# =====================================================
# Language
# =====================================================

with st.sidebar:

    language = st.radio(
        "🌐 Language",
        ["日本語", "English"]
    )

# =====================================================
# Text Dictionary
# =====================================================

if language == "日本語":

    TXT = {

        "fluid": "流体条件",
        "pipe": "配管条件",
        "minor": "局部損失",

        "start_pressure": "始点圧力 [kPa]",
        "flowrate": "流量 [m³/h]",
        "density": "密度 [kg/m³]",
        "viscosity": "動粘度 [m²/s]",

        "pipe_id": "管内径 [mm]",
        "roughness": "管内面粗さ ε [mm]",

        "start_elevation": "始点標高 [m]",
        "end_elevation": "終点標高 [m]",

        "elbow90": "90°エルボ数",
        "elbow45": "45°エルボ数",

        "route": "ルート入力",

        "results": "計算結果",

        "detail": "詳細計算結果",

        "node": "ノードデータ",

        "equation": "計算式",

        "feedback": "ご意見・改善提案",

        "show_detail": "詳細計算結果を表示",

        "show_node": "ノードデータを表示",

        "show_eq": "計算式を表示"
    }

else:

    TXT = {

        "fluid": "Fluid Conditions",

        "pipe": "Pipe Specifications",

        "minor": "Minor Loss Elements",

        "start_pressure": "Start Pressure [kPa]",

        "flowrate": "Flow Rate [m³/h]",

        "density": "Density [kg/m³]",

        "viscosity": "Kinematic Viscosity [m²/s]",

        "pipe_id": "Pipe ID [mm]",

        "roughness": "Pipe Roughness ε [mm]",

        "start_elevation": "Start Elevation [m]",

        "end_elevation": "End Elevation [m]",

        "elbow90": "90° Elbows",

        "elbow45": "45° Elbows",

        "route": "Route Input",

        "results": "Results",

        "detail": "Detailed Results",

        "node": "Node Data",

        "equation": "Calculation Method",

        "feedback": "Feedback",

        "show_detail": "Show Detailed Results",

        "show_node": "Show Node Data",

        "show_eq": "Show Equations"
    }

# =====================================================
# Session
# =====================================================

if "points" not in st.session_state:
    st.session_state.points = []
    
# =====================================================
# Apple Style CSS
# =====================================================

st.markdown("""
<style>

/* Main spacing */

.block-container{
    padding-top:2rem;
}

/* KPI Cards */

[data-testid="stMetric"]{

    border-radius:18px;

    padding:18px;

    border:1px solid rgba(148,163,184,0.25);

    border-left:4px solid #2563EB;

    background-color:rgba(148,163,184,0.05);

}

/* KPI Label */

[data-testid="stMetricLabel"]{

    font-size:0.9rem;

}

/* KPI Value */

[data-testid="stMetricValue"]{

    font-weight:700;

    font-size:1.6rem;

}

/* Expander */

.streamlit-expanderHeader{

    font-weight:600;

}

</style>
""", unsafe_allow_html=True)


# =====================================================
# Header
# =====================================================

st.markdown(
    """
    <h1 style="
    color:#2563EB;
    font-size:42px;
    font-weight:800;
    margin-bottom:0px;
    ">
    PROCESS PIPING DESIGN TOOL
    </h1>

    <p style="
    color:#94A3B8;
    font-size:14px;
    margin-top:0px;
    margin-bottom:0px;
    ">
    Version 3.0
    </p>

    <p style="
    color:#64748B;
    font-size:16px;
    margin-top:5px;
    ">
    Created by Kyotaro.H
    </p>
    """,
    unsafe_allow_html=True
)

# =====================================================
# Sidebar
# =====================================================

with st.sidebar:

    # -------------------------------------------------
    # Fluid Conditions
    # -------------------------------------------------

    st.header(TXT["fluid"])

    if language == "日本語":

        st.caption(
            "圧力・流量・流体物性"
        )

    else:

        st.caption(
            "Pressure, Flow Rate and Fluid Properties"
        )

    start_pressure_kpa = st.number_input(
        TXT["start_pressure"],
        value=300.0,
        min_value=0.0
    )

    flow_rate_m3h = st.number_input(
        TXT["flowrate"],
        value=10.0,
        min_value=0.0
    )

    fluid_density = st.number_input(
        TXT["density"],
        value=998.0
    )

    kinematic_viscosity = st.number_input(
        TXT["viscosity"],
        value=1.0e-6,
        format="%e"
    )

    st.divider()

    # -------------------------------------------------
    # Pipe Specifications
    # -------------------------------------------------

    st.header(TXT["pipe"])

    if language == "日本語":

        st.caption(
            "配管寸法と標高差"
        )

    else:

        st.caption(
            "Pipe Geometry and Elevation"
        )

    pipe_diameter_mm = st.number_input(
        TXT["pipe_id"],
        value=52.5,
        min_value=1.0
    )

    roughness_mm = st.number_input(
        TXT["roughness"],
        value=0.045
    )

    start_elevation_m = st.number_input(
        TXT["start_elevation"],
        value=0.0
    )

    auto_elevation = st.checkbox(
        "Auto Elevation",
        value=True
    )

    end_elevation_m = st.number_input(
        TXT["end_elevation"],
        value=0.0,
        disabled=auto_elevation
    )

    st.divider()

    # -------------------------------------------------
    # Minor Loss Elements
    # -------------------------------------------------

    st.header(TXT["minor"])

    if language == "日本語":

        st.caption(
            "エルボ・拡大縮小・バルブ"
        )

    else:

        st.caption(
            "Elbows, Reducers and Valves"
        )

    elbow90_count = st.number_input(
        TXT["elbow90"],
        value=0,
        step=1
    )

    elbow45_count = st.number_input(
        TXT["elbow45"],
        value=0,
        step=1
    )

    # =================================================
    # Expansion Loss
    # =================================================

    with st.expander("Expansion Loss"):

        expansion_count = st.number_input(
            "Expansion Count",
            value=0,
            step=1
        )

        k_expansion = 0.0

        if expansion_count > 0:

            expansion_d1_mm = st.number_input(
                "ID Before Expansion [mm]",
                value=50.0
            )

            expansion_d2_mm = st.number_input(
                "ID After Expansion [mm]",
                value=80.0
            )

            area1 = (
                math.pi
                * (expansion_d1_mm / 1000) ** 2
                / 4
            )

            area2 = (
                math.pi
                * (expansion_d2_mm / 1000) ** 2
                / 4
            )

            if area2 > 0:

                k_expansion = (
                    (1 - area1 / area2) ** 2
                ) * expansion_count

            st.caption(
                f"K = {k_expansion:.3f}"
            )

    # =================================================
    # Contraction Loss
    # =================================================

    with st.expander("Contraction Loss"):

        contraction_count = st.number_input(
            "Contraction Count",
            value=0,
            step=1
        )

        k_contraction = 0.0

        if contraction_count > 0:

            contraction_d1_mm = st.number_input(
                "ID Before Contraction [mm]",
                value=80.0
            )

            contraction_d2_mm = st.number_input(
                "ID After Contraction [mm]",
                value=50.0
            )

            area1 = (
                math.pi
                * (contraction_d1_mm / 1000) ** 2
                / 4
            )

            area2 = (
                math.pi
                * (contraction_d2_mm / 1000) ** 2
                / 4
            )

            if area1 > 0:

                k_contraction = (
                    0.5
                    * (1 - area2 / area1)
                ) * contraction_count

            st.caption(
                f"K = {k_contraction:.3f}"
            )

    # =================================================
    # Valve Loss
    # =================================================

    with st.expander("Valve Loss"):

        valve_rows = st.number_input(
            "Valve Types",
            value=0,
            step=1
        )

        k_valve = 0.0

        for i in range(valve_rows):

            st.markdown(
                f"##### Valve {i+1}"
            )

            valve_type = st.selectbox(
                f"Valve Type {i+1}",
                [
                    "Ball Valve",
                    "Gate Valve",
                    "Butterfly Valve",
                    "Globe Valve"
                ],
                key=f"valve_type_{i}"
            )

            valve_quantity = st.number_input(
                f"Quantity {i+1}",
                value=1,
                step=1,
                key=f"valve_qty_{i}"
            )

            opening_percent = st.slider(
                f"Opening {i+1} [%]",
                min_value=10,
                max_value=100,
                value=100,
                step=5,
                key=f"valve_open_{i}"
            )

            full_open_k = {
                "Ball Valve": 0.05,
                "Gate Valve": 0.15,
                "Butterfly Valve": 0.70,
                "Globe Valve": 10.0
            }

            base_k = full_open_k[valve_type]

            valve_k = (
                base_k
                * (100 / opening_percent) ** 2
                * valve_quantity
            )

            k_valve += valve_k

            st.caption(
                f"K = {valve_k:.3f}"
            )

        st.success(
            f"Total Valve K = {k_valve:.3f}"
        )
        
# =====================================================
# Route Input
# =====================================================

st.markdown(f"""
<h2 style="
margin-top:25px;
margin-bottom:10px;
font-weight:700;
">
{TXT["route"]}
</h2>
""", unsafe_allow_html=True)

if language == "日本語":

    st.caption(
        "X-Y座標で配管ルートを作成します"
    )

    x_label = "X 座標 [m]"
    y_label = "Y 座標 [m]"

    add_label = "ポイント追加"
    delete_label = "最後を削除"

else:

    st.caption(
        "Draw your piping route using X-Y coordinates"
    )

    x_label = "X Coordinate [m]"
    y_label = "Y Coordinate [m]"

    add_label = "Add Point"
    delete_label = "Delete Last"


c1, c2, c3, c4 = st.columns(4)

with c1:

    x = st.number_input(
        x_label,
        value=0.0,
        step=1.0
    )

with c2:

    y = st.number_input(
        y_label,
        value=0.0,
        step=1.0
    )

with c3:

    st.write("")
    st.write("")

    if st.button(
        add_label,
        use_container_width=True
    ):

        st.session_state.points.append(
            (x, y)
        )

        st.rerun()

with c4:

    st.write("")
    st.write("")

    if st.button(
        delete_label,
        use_container_width=True
    ):

        if len(st.session_state.points) > 0:

            st.session_state.points.pop()

            st.rerun()


st.markdown("---")

# =====================================================
# Graph Range
# =====================================================

all_x = [x]
all_y = [y]

for px, py in st.session_state.points:

    all_x.append(px)
    all_y.append(py)

# -------------------------------------------------
# Auto Scale
# -------------------------------------------------

graph_range = max(
    max(all_x),
    max(all_y),
    10
)

# Add margin

graph_range *= 1.2


# -------------------------------------------------
# Tick Spacing
# -------------------------------------------------

if graph_range <= 10:

    major_tick = 1
    minor_tick = 0.2

elif graph_range <= 50:

    major_tick = 5
    minor_tick = 1

elif graph_range <= 100:

    major_tick = 10
    minor_tick = 2

elif graph_range <= 500:

    major_tick = 50
    minor_tick = 10

else:

    major_tick = 100
    minor_tick = 20
    
# =====================================================
# Route Plot
# =====================================================

if language == "日本語":

    plot_title = "配管ルート"

    plot_caption = (
        "入力したルートを表示"
    )

else:

    plot_title = "Route Plot"

    plot_caption = (
        "Visualization of piping route"
    )

st.markdown(f"""
<h2 style="
margin-top:25px;
margin-bottom:10px;
font-weight:700;
">
{plot_title}
</h2>
""", unsafe_allow_html=True)

st.caption(plot_caption)

fig = go.Figure()

fig.update_xaxes(
    range=[0, graph_range],
    dtick=major_tick,
    showgrid=True,
    gridcolor="rgba(148,163,184,0.35)",
    tickfont=dict(
        size=12
    ),
    minor=dict(
        showgrid=True,
        dtick=minor_tick,
        gridcolor="rgba(148,163,184,0.10)"
    )
)

fig.update_yaxes(
    range=[0, graph_range],
    dtick=major_tick,
    showgrid=True,
    gridcolor="rgba(148,163,184,0.35)",
    tickfont=dict(
        size=12
    ),
    minor=dict(
        showgrid=True,
        dtick=minor_tick,
        gridcolor="rgba(148,163,184,0.10)"
    ),
    scaleanchor="x"
)

if len(st.session_state.points) > 0:

    xs = [p[0] for p in st.session_state.points]
    ys = [p[1] for p in st.session_state.points]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",

            line=dict(
                width=8,
                color="#2563EB"
            ),

            marker=dict(
                size=10,
                color="#EA580C"
            )
        )
    )

fig.update_layout(

    height=500,

    showlegend=False,

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),

    plot_bgcolor="#F8FAFC",

    paper_bgcolor="#FFFFFF"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# Pipe Length Calculation
# =====================================================

total_length_m = 0.0

for i in range(
    len(st.session_state.points) - 1
):

    x1, y1 = st.session_state.points[i]

    x2, y2 = (
        st.session_state.points[i + 1]
    )

    segment_length = math.sqrt(
        (x2 - x1) ** 2
        +
        (y2 - y1) ** 2
    )

    total_length_m += (
        segment_length
    )

# =====================================================
# Auto End Elevation
# =====================================================

calculated_end_elevation = (
    start_elevation_m
)

for i in range(
    len(st.session_state.points) - 1
):

    x1, y1 = st.session_state.points[i]

    x2, y2 = (
        st.session_state.points[i + 1]
    )

    # Vertical Segment Only

    if x1 == x2:

        calculated_end_elevation += (
            y2 - y1
        )

if auto_elevation:

    end_elevation_m = (
        calculated_end_elevation
    )

    st.info(
        f"Auto End Elevation = "
        f"{end_elevation_m:.2f} m"
    )


# =====================================================
# Static Head
# =====================================================

static_head_m = (
    end_elevation_m
    -
    start_elevation_m
)

# =====================================================
# Darcy-Weisbach Calculation
# =====================================================

g = 9.80665

# -------------------------------------------------
# Unit Conversion
# -------------------------------------------------

pipe_diameter_m = (
    pipe_diameter_mm / 1000.0
)

roughness_m = (
    roughness_mm / 1000.0
)

flow_rate_m3s = (
    flow_rate_m3h / 3600.0
)

# -------------------------------------------------
# Pipe Cross Section
# -------------------------------------------------

area = (
    math.pi
    * pipe_diameter_m ** 2
    / 4.0
)

# -------------------------------------------------
# Velocity
# -------------------------------------------------

velocity = 0.0

if area > 0:

    velocity = (
        flow_rate_m3s
        / area
    )

# -------------------------------------------------
# Reynolds Number
# -------------------------------------------------

reynolds = 0.0

if kinematic_viscosity > 0:

    reynolds = (
        velocity
        * pipe_diameter_m
        / kinematic_viscosity
    )

# -------------------------------------------------
# Friction Factor
# -------------------------------------------------

friction_factor = 0.0

# Swamee-Jain

if (
    reynolds > 4000
    and pipe_diameter_m > 0
):

    friction_factor = (
        0.25
        /
        (
            math.log10(
                (
                    roughness_m
                    /
                    (3.7 * pipe_diameter_m)
                )
                +
                (
                    5.74
                    /
                    (
                        reynolds ** 0.9
                    )
                )
            )
        ) ** 2
    )

# Laminar

elif reynolds > 0:

    friction_factor = (
        64
        / reynolds
    )
    
# =====================================================
# Major Loss
# =====================================================

major_loss_m = 0.0

if pipe_diameter_m > 0:

    major_loss_m = (

        friction_factor

        * (
            total_length_m
            /
            pipe_diameter_m
        )

        * (
            velocity ** 2
            /
            (2 * g)
        )

    )


# =====================================================
# Minor Loss
# =====================================================

# -------------------------------------------------
# Loss Coefficients
# -------------------------------------------------

K90 = 0.9
K45 = 0.4

# -------------------------------------------------
# Total K Value
# -------------------------------------------------

minor_k = (

    elbow90_count * K90

    +

    elbow45_count * K45

    +

    k_expansion

    +

    k_contraction

    +

    k_valve

)

# -------------------------------------------------
# Minor Loss
# -------------------------------------------------

minor_loss_m = (

    minor_k

    *

    (
        velocity ** 2
        /
        (2 * g)
    )

)

# =====================================================
# Total Loss
# =====================================================

# -------------------------------------------------
# Total Head Loss
# -------------------------------------------------

total_loss_m = (

    major_loss_m

    +

    minor_loss_m

    +

    static_head_m

)

# -------------------------------------------------
# Pressure Loss
# -------------------------------------------------

pressure_loss_kpa = (

    fluid_density

    * g

    * total_loss_m

) / 1000.0

# -------------------------------------------------
# End Pressure
# -------------------------------------------------

end_pressure_kpa = (

    start_pressure_kpa

    -

    pressure_loss_kpa

)

# -------------------------------------------------
# Flow Regime
# -------------------------------------------------

flow_regime = (

    "Laminar"

    if reynolds <= 4000

    else "Turbulent"

)

# =====================================================
# Quick Results Calculation
# =====================================================

pipe_pressure_loss_kpa = (
    fluid_density
    * g
    * major_loss_m
) / 1000

other_pressure_loss_kpa = (
    fluid_density
    * g
    * (
        minor_loss_m
        + static_head_m
    )
) / 1000


# =====================================================
# Quick Result Labels
# =====================================================

if language == "日本語":

    QUICK = {

        "title": "結果",

        "subtitle": "圧力計算結果",

        "start": "始点圧力 [kPa]",

        "end": "終点圧力 [kPa]",

        "pipe": "配管圧力損失 [kPa]",

        "other": "局部損失＋高低差 [kPa]"
    }

else:

    QUICK = {

        "title": "Quick Results",

        "subtitle": "Key pressure information",

        "start": "Start Pressure [kPa]",

        "end": "End Pressure [kPa]",

        "pipe": "Pipe Loss [kPa]",

        "other": "Other Loss [kPa]"
    }


# =====================================================
# Quick Results
# =====================================================

st.markdown(f"""
<h2 style="
margin-top:30px;
margin-bottom:5px;
font-weight:700;
">
{QUICK["title"]}
</h2>
""", unsafe_allow_html=True)

st.caption(
    QUICK["subtitle"]
)

q1, q2, q3, q4 = st.columns(4)

with q1:

    st.metric(
        QUICK["start"],
        f"{start_pressure_kpa:.1f}"
    )

with q2:

    st.metric(
        QUICK["end"],
        f"{end_pressure_kpa:.1f}"
    )

with q3:

    st.metric(
        QUICK["pipe"],
        f"{pipe_pressure_loss_kpa:.1f}"
    )

with q4:

    st.metric(
        QUICK["other"],
        f"{other_pressure_loss_kpa:.1f}"
    )
    
# =====================================================
# Detailed Results
# =====================================================

with st.expander(
    TXT["show_detail"],
    expanded=False
):

    st.markdown("### Flow Characteristics")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Length [m]",
            f"{total_length_m:.2f}"
        )

    with c2:

        st.metric(
            "Velocity [m/s]",
            f"{velocity:.2f}"
        )

    with c3:

        st.metric(
            "Flow Regime",
            flow_regime
        )

    with c4:

        st.metric(
            "Reynolds Number",
            f"{reynolds:.0f}"
        )

    st.markdown("### Loss Analysis")

    c5, c6, c7, c8 = st.columns(4)

    with c5:

        st.metric(
            "Major Loss [m]",
            f"{major_loss_m:.2f}"
        )

    with c6:

        st.metric(
            "Minor Loss [m]",
            f"{minor_loss_m:.2f}"
        )

    with c7:

        st.metric(
            "Static Head [m]",
            f"{static_head_m:.2f}"
        )

    with c8:

        st.metric(
            "Total Loss [m]",
            f"{total_loss_m:.2f}"
        )

    st.markdown("### Pressure Analysis")

    c9, c10, c11, c12 = st.columns(4)

    with c9:

        st.metric(
            "Friction Factor",
            f"{friction_factor:.4f}"
        )

    with c10:

        st.metric(
            "Pressure Loss [kPa]",
            f"{pressure_loss_kpa:.2f}"
        )

    with c11:

        st.metric(
            "Start Pressure [kPa]",
            f"{start_pressure_kpa:.2f}"
        )

    with c12:

        st.metric(
            "End Pressure [kPa]",
            f"{end_pressure_kpa:.2f}"
        )
        
# =====================================================
# Calculation Method
# =====================================================

with st.expander(
    TXT["show_eq"],
    expanded=False
):

    st.markdown("### Reynolds Number")

    st.latex(
        r"Re=\frac{VD}{\nu}"
    )

    st.markdown("### Flow Regime")

    st.markdown("""
- Re ≤ 4000 : Laminar Flow
- Re > 4000 : Turbulent Flow
""")

    st.markdown("### Laminar Flow")

    st.latex(
        r"f=\frac{64}{Re}"
    )

    st.markdown(
        "### Turbulent Flow (Swamee-Jain Equation)"
    )

    st.latex(
        r"f=\frac{0.25}"
        r"{\left[\log_{10}\left("
        r"\frac{\varepsilon}{3.7D}"
        r"+"
        r"\frac{5.74}{Re^{0.9}}"
        r"\right)\right]^2}"
    )

    st.markdown(
        "### Darcy-Weisbach Equation"
    )

    st.latex(
        r"h_f=f\frac{L}{D}\frac{V^2}{2g}"
    )

    st.markdown("### Minor Loss")

    st.latex(
        r"h_m=K\frac{V^2}{2g}"
    )

    st.markdown("### Loss Coefficient")

    st.latex(
        r"K=K_{90}+K_{45}+K_{exp}+K_{con}+K_{valve}"
    )

    st.markdown("### Static Head")

    st.latex(
        r"h_z=z_{end}-z_{start}"
    )

    st.markdown("### Total Loss")

    st.latex(
        r"h_t=h_f+h_m+h_z"
    )

    st.markdown("### Pressure Loss")

    st.latex(
        r"\Delta P=\rho g h_t"
    )

    st.markdown("### End Pressure")

    st.latex(
        r"P_2=P_1-\Delta P"
    )

    st.markdown("### Symbols")

    st.markdown("""
- **P** : Pressure [kPa]
- **D** : Pipe Diameter [m]
- **L** : Pipe Length [m]
- **V** : Velocity [m/s]
- **ρ** : Fluid Density [kg/m³]
- **ν** : Kinematic Viscosity [m²/s]
- **g** : Gravitational Acceleration [m/s²]
- **K** : Minor Loss Coefficient
""")
                
# =====================================================
# Node Data
# =====================================================

with st.expander(
    TXT["show_node"],
    expanded=False
):

    if language == "日本語":

        st.caption(
            "入力されたノード座標一覧"
        )

        columns = [
            "X 座標 [m]",
            "Y 座標 [m]"
        ]

    else:

        st.caption(
            "Input route coordinates"
        )

        columns = [
            "X [m]",
            "Y [m]"
        ]

    df = pd.DataFrame(
        st.session_state.points,
        columns=columns
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Node Count : {len(st.session_state.points)}"
    )
    
# =====================================================
# CSV Import / Export
# =====================================================

if language == "日本語":

    csv_title = "CSVデータ"

    export_label = "CSVエクスポート"

    import_label = "CSVインポート"

    import_button = "ルートを読込"

else:

    csv_title = "CSV Data"

    export_label = "CSV Export"

    import_label = "CSV Import"

    import_button = "Import Route"


st.markdown(f"""
<h2 style="
margin-top:25px;
margin-bottom:10px;
font-weight:700;
">
{csv_title}
</h2>
""", unsafe_allow_html=True)


csv_df = pd.DataFrame(
    st.session_state.points,
    columns=["X [m]", "Y [m]"]
)

csv_data = csv_df.to_csv(
    index=False
).encode("utf-8-sig")


c1, c2 = st.columns(2)

with c1:

    st.download_button(
        export_label,
        csv_data,
        file_name="pipe_route_v3.csv",
        mime="text/csv",
        use_container_width=True
    )

with c2:

    uploaded_csv = st.file_uploader(
        import_label,
        type=["csv"]
    )

    if uploaded_csv is not None:

        if st.button(
            import_button,
            use_container_width=True
        ):

            try:

                df_import = pd.read_csv(
                    uploaded_csv
                )

                st.session_state.points = list(
                    zip(
                        df_import.iloc[:, 0],
                        df_import.iloc[:, 1]
                    )
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Import Error : {e}"
                )
                
# =====================================================
# Feedback & Support
# =====================================================

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfVi4i5Pz9i_nr0vDCnT2RjvJmdhO-kGBAej4Du1CkAGhRgig/viewform?usp=publish-editor"

if language == "日本語":

    feedback_title = "Feedback & Support"

    feedback_caption = (
        "不具合報告・改善提案・新機能要望"
    )

    category_label = "カテゴリー"

    comment_label = "コメント"

    categories = [
        "不具合",
        "UI改善",
        "計算ロジック",
        "新機能要望"
    ]

    form_button = "フィードバックフォームを開く"

else:

    feedback_title = "Feedback & Support"

    feedback_caption = (
        "Bug Reports, Improvements and Feature Requests"
    )

    category_label = "Category"

    comment_label = "Comment"

    categories = [
        "Bug",
        "UI",
        "Calculation",
        "Feature Request"
    ]

    form_button = "Open Feedback Form"


st.markdown(f"""
<h2 style="
margin-top:25px;
margin-bottom:10px;
font-weight:700;
">
{feedback_title}
</h2>
""", unsafe_allow_html=True)

st.caption(
    feedback_caption
)

feedback_category = st.selectbox(
    category_label,
    categories
)

feedback_comment = st.text_area(
    comment_label,
    height=150,
    placeholder=""
)

st.link_button(
    form_button,
    FORM_URL,
    use_container_width=True
)

# =====================================================
# Footer
# =====================================================

st.markdown("---")

if language == "日本語":

    footer_text = """
    <div style="
    text-align:center;
    padding:25px;
    color:#64748B;
    font-size:14px;
    ">

    <b>PROCESS PIPING DESIGN TOOL</b><br>

    Version 3.0<br>

    Created by Kyotaro.H<br><br>

    Beginner-Friendly Process Engineering Tool<br>

    Feedback Welcome

    </div>
    """

else:

    footer_text = """
    <div style="
    text-align:center;
    padding:25px;
    color:#64748B;
    font-size:14px;
    ">

    <b>PROCESS PIPING DESIGN TOOL</b><br>

    Version 3.0<br>

    Created by Kyotaro.H<br><br>

    Beginner-Friendly Process Engineering Tool<br>

    Feedback Welcome

    </div>
    """

st.markdown(
    footer_text,
    unsafe_allow_html=True
)