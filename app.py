import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math
import streamlit.components.v1 as components

# =====================================================
# Page Config
# =====================================================

st.set_page_config(
    page_title="PROCESS PIPING DESIGN TOOL",
    layout="wide"
)

# =====================================================
# Google Analytics
# =====================================================

GA_ID = "G-SCMMFH2S1Z"

components.html(
    f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>

    <script>
      window.dataLayer = window.dataLayer || [];

      function gtag(){{
        dataLayer.push(arguments);
      }}

      gtag('js', new Date());

      gtag(
        'config',
        '{GA_ID}'
      );
    </script>
    """,
    height=0
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

        "route": "ルート入力",

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

        "elbow45": "45°エルボ数",

        "show_detail": "詳細計算結果を表示",

        "show_node": "ノードデータを表示",

        "show_eq": "計算式を表示",
        
        "system_summary": "システムサマリー",

        "pressure_result": "圧力結果",

        "pipe_length": "総配管長 [m]",

        "auto_elbows": "自動検出エルボ",

        "flow_regime": "流動状態",

        "end_elevation": "終点標高 [m]",

        "total_loss": "総損失 [kPa]",
        
        "feedback": "フィードバック",
        
        "route_history": "ルート履歴",
        
        "csv_data": "CSVデータ",

        "csv_export": "CSV出力",

        "csv_import": "CSV読込",

        "import_route": "ルート読込",
                
        "node_data": "ノードデータ",

        "no_route_data": "ルートデータがありません",
                
    }

else:

    TXT = {

        "route": "Route Input",

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

        "elbow45": "45° Elbows",

        "show_detail": "Show Detailed Results",

        "show_node": "Show Node Data",

        "show_eq": "Show Equations",
        
        "system_summary": "SYSTEM SUMMARY",

        "pressure_result": "PRESSURE RESULT",

        "pipe_length": "PIPE LENGTH [m]",

        "auto_elbows": "AUTO ELBOWS",

        "flow_regime": "FLOW REGIME",

        "end_elevation": "END ELEVATION [m]",

        "total_loss": "TOTAL LOSS [kPa]",
        
        "feedback": "Feedback",
        
        "route_history": "Route History",
                
        "csv_data": "CSV Data",

        "csv_export": "CSV Export",

        "csv_import": "CSV Import",

        "import_route": "Import Route",
                
        "node_data": "Node Data",

        "no_route_data": "No Route Data",              

    }

# =====================================================
# Common Labels
# =====================================================

if language == "日本語":

    add_label = "ルート追加"

    delete_label = "最後を削除"

else:

    add_label = "Add Segment"

    delete_label = "Delete Last"

# =====================================================
# Session
# =====================================================

if "route_segments" not in st.session_state:

    st.session_state.route_segments = []

if "segment_id" not in st.session_state:

    st.session_state.segment_id = 1

# =====================================================
# Application Header
# =====================================================

st.markdown("""
<div style="
padding-bottom:10px;
">

<div style="
font-size:38px;
font-weight:700;
color:#1E3A8A;
letter-spacing:1px;
">
PROCESS PIPING DESIGN TOOL
</div>

<div style="
font-size:16px;
color:#64748B;
margin-top:4px;
">
Route-Based Pressure Calculation
</div>

<div style="
height:3px;
background:#2563EB;
margin-top:10px;
border-radius:2px;
">
</div>

</div>
""", unsafe_allow_html=True)
st.markdown("---")
    
# =====================================================
# Route Engine
# =====================================================

def build_points_from_segments(
    segments
):

    x = 0.0
    y = 0.0

    points = [(x, y)]

    for seg in segments:

        direction = seg["direction"]

        length = seg["length"]

        # ---------------------------------------------
        # X Direction
        # ---------------------------------------------

        if direction == "X+":

            x += length

        elif direction == "X-":

            x -= length
            
        # ---------------------------------------------
        # Y Direction
        # ---------------------------------------------
        
        elif direction == "Y+":

            x += length * 0.5
            y += length * 0.5

        elif direction == "Y-":

            x -= length * 0.5
            y -= length * 0.5
        
        # ---------------------------------------------
        # Z Direction
        # ---------------------------------------------

        elif direction == "Z+":

            y += length

        elif direction == "Z-":

            y -= length

        points.append(
            (x, y)
        )

    return points

# =====================================================
# Auto Elbow Recognition
# =====================================================

def count_auto_elbows(
    segments
):

    elbow90_count = 0

    for i in range(
        len(segments) - 1
    ):

        d1 = (
            segments[i]
            ["direction"]
        )

        d2 = (
            segments[i + 1]
            ["direction"]
        )

        if d1 != d2:

            elbow90_count += 1

    return elbow90_count

# =====================================================
# Route Data
# =====================================================

route_points = (
    build_points_from_segments(
        st.session_state.route_segments
    )
)

auto_elbow90 = (
    count_auto_elbows(
        st.session_state.route_segments
    )
)

# =====================================================
# Sidebar
# =====================================================

with st.sidebar:

    st.header(TXT["fluid"])

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

    st.header(TXT["pipe"])

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

    st.header(TXT["minor"])

    st.success(
        f"Auto 90° Elbows = {auto_elbow90}"
    )

    elbow45_count = st.number_input(
        TXT["elbow45"],
        value=0,
        step=1
    )

    k_expansion = 0.0
    k_contraction = 0.0
    k_valve = 0.0
    


# =====================================================
# Route Input
# =====================================================

st.markdown(f"""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-top:15px;
margin-bottom:8px;
border-left:4px solid #2563EB;
padding-left:10px;
">
{TXT["route"]}
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# Isometric Guide
# -----------------------------------------------------

if language == "日本語":

    st.info("""
アイソメルート入力

X = 水平方向

Y = 奥行方向

Z = 高低方向
""")

else:

    st.info("""
Isometric Route Input

X = Horizontal Direction

Y = Depth Direction

Z = Elevation Direction
""")

# -----------------------------------------------------
# Direction Input
# -----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

with c1:

    direction = st.selectbox(
        "Direction",
        [
            "→ X+",
            "← X-",
            "↗ Y+",
            "↙ Y-",
            "↑ Z+",
            "↓ Z-"
        ]
    )

with c2:

    segment_length = st.number_input(
        "Length [m]",
        value=10.0,
        min_value=0.0,
        step=1.0
    )

with c3:

    st.write("")
    st.write("")

    direction_code = direction[-2:]

    if st.button(
        add_label,
        use_container_width=True
    ):

        st.session_state.route_segments.append(
            {
                "id":
                st.session_state.segment_id,

                "direction":
                direction_code,

                "length":
                segment_length,

                "type":
                "PIPE"
            }
        )

        st.session_state.segment_id += 1

        st.rerun()

with c4:

    st.write("")
    st.write("")

    if st.button(
        delete_label,
        use_container_width=True
    ):

        if len(
            st.session_state.route_segments
        ) > 0:

            st.session_state.route_segments.pop()

            st.rerun()

st.markdown("---")

    
# =====================================================
# Graph Range
# =====================================================

all_x = [0]
all_y = [0]

for px, py in route_points:

    all_x.append(px)
    all_y.append(py)

graph_range = max(

    abs(max(all_x)),
    abs(min(all_x)),

    abs(max(all_y)),
    abs(min(all_y)),

    10
)

graph_range *= 1.5

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

    plot_title = "ルートプレビュー"

    plot_caption = (
        "Direction + Lengthから生成"
    )

else:

    plot_title = "Route Preview"

    plot_caption = (
        "Generated from Direction + Length"
    )

title_col, compass_col = st.columns([8, 1])

with title_col:

    st.markdown(f"""
    <div style="
    font-size:18px;
    font-weight:600;
    color:#475569;
    margin-top:20px;
    margin-bottom:8px;
    border-left:4px solid #2563EB;
    padding-left:10px;
    ">
    {plot_title}
    </div>
    """, unsafe_allow_html=True)

    st.caption(plot_caption)

with compass_col:

    st.image(
        "assets/axis_compass.png",
        width=100
    )

fig = go.Figure()

fig.update_xaxes(

    range=[
        -graph_range,
        graph_range
    ],

    dtick=major_tick,

    showgrid=True,

    gridcolor=
    "rgba(148,163,184,0.20)",

    zeroline=True,

    zerolinewidth=2,

    zerolinecolor="#CBD5E1"
)

fig.update_yaxes(

    range=[
        -graph_range,
        graph_range
    ],

    dtick=major_tick,

    showgrid=True,

    gridcolor=
    "rgba(148,163,184,0.20)",

    zeroline=True,

    zerolinewidth=2,

    zerolinecolor="#CBD5E1",

    scaleanchor="x"
)

if len(route_points) > 1:

    xs = [
        p[0]
        for p in route_points
    ]

    ys = [
        p[1]
        for p in route_points
    ]

    fig.add_trace(

        go.Scatter(

            x=xs,
            y=ys,

            mode=
            "lines+markers",

            line=dict(
                width=5,
                color="#1E40AF"
            ),

            marker=dict(
                size=6,
                color="#64748B",
                line=dict(
                    width=1,
                    color="#334155"
                )
            )

        )

    )
    

# =====================================================
# Axis Compass Image
# =====================================================

fig.add_annotation(

    x=graph_range * 0.6,

    y=graph_range * 0.8,

    text=
    f"""
    Segments

    {len(st.session_state.route_segments)}

    Auto 90° Elbows

    {auto_elbow90}
    """,

    showarrow=False,

    bgcolor="white",

    bordercolor="#CBD5E1",

    borderwidth=1
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
# Route History
# =====================================================

with st.expander(
    TXT["route_history"],
    expanded=False
):

    if len(
        st.session_state.route_segments
    ) > 0:

        seg_df = pd.DataFrame(

            [
                {
                    "Direction":

                    {
                        "X+": "→ X+",
                        "X-": "← X-",
                        "Y+": "↗ Y+",
                        "Y-": "↙ Y-",
                        "Z+": "↑ Z+",
                        "Z-": "↓ Z-"
                    }.get(
                        seg["direction"],
                        seg["direction"]
                    ),

                    "Length [m]":
                    seg["length"]
                }

                for seg

                in st.session_state.route_segments
            ]

        )

        st.dataframe(

            seg_df,

            use_container_width=True,

            hide_index=True

        )

    else:

        if language == "日本語":

            st.info(
                "ルートデータがありません"
            )

        else:

            st.info(
                "No Route Segments"
            )


# =====================================================
# Pipe Length
# =====================================================

total_length_m = sum(

    seg["length"]

    for seg

    in st.session_state.route_segments

)

# =====================================================
# Auto Elevation
# =====================================================

calculated_end_elevation = (
    start_elevation_m
)

for seg in (
    st.session_state.route_segments
):

    if (
        seg["direction"]
        == "Z+"
    ):

        calculated_end_elevation += (
            seg["length"]
        )

    elif (
        seg["direction"]
        == "Z-"
    ):

        calculated_end_elevation -= (
            seg["length"]
        )

if auto_elevation:

    end_elevation_m = (
        calculated_end_elevation
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

area = 0.0

if pipe_diameter_m > 0:

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

                    (

                        3.7

                        * pipe_diameter_m

                    )

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

            (

                2 * g

            )

        )

    )

# =====================================================
# Minor Loss
# =====================================================

K90 = 0.9

K45 = 0.4

minor_k = (

    auto_elbow90 * K90

    +

    elbow45_count * K45

    +

    k_expansion

    +

    k_contraction

    +

    k_valve

)

minor_loss_m = (

    minor_k

    * (

        velocity ** 2

        /

        (

            2 * g

        )

    )

)

# =====================================================
# Total Loss
# =====================================================

total_loss_m = (

    major_loss_m

    +

    minor_loss_m

    +

    static_head_m

)

pressure_loss_kpa = (

    fluid_density

    * g

    * total_loss_m

) / 1000.0

end_pressure_kpa = (

    start_pressure_kpa

    -

    pressure_loss_kpa

)

if language == "日本語":

    flow_regime = (

        "層流"

        if reynolds <= 4000

        else "乱流"

    )

else:

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

) / 1000.0

other_pressure_loss_kpa = (

    fluid_density

    * g

    * (

        minor_loss_m

        +

        static_head_m

    )

) / 1000.0

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

        "subtitle": "Key Pressure Information",

        "start": "Start Pressure [kPa]",

        "end": "End Pressure [kPa]",

        "pipe": "Pipe Loss [kPa]",

        "other": "Other Loss [kPa]"
    }

# =====================================================
# Quick Results
# =====================================================

def result_card(
    title,
    value,
    color="#2563EB"
):

    st.markdown(
        f"""
        <div style="
        border-left:6px solid {color};
        background:#FFFFFF;
        padding:15px;
        border-radius:8px;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);
        margin-bottom:12px;
        ">

        <div style="
        font-size:12px;
        color:#64748B;
        margin-bottom:5px;
        ">
        {title}
        </div>

        <div style="
        font-size:28px;
        font-weight:700;
        color:#0F172A;
        ">
        {value}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def detail_header(title):

    st.markdown(
        f"""
        <div style="
        font-size:15px;
        font-weight:600;
        color:#475569;
        margin-top:15px;
        margin-bottom:10px;
        border-left:3px solid #94A3B8;
        padding-left:8px;
        ">
        {title}
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(f"""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-top:20px;
margin-bottom:12px;
border-left:4px solid #2563EB;
padding-left:10px;
">
{TXT["system_summary"]}
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:

    result_card(
        TXT["pipe_length"],
        f"{total_length_m:.1f}"
    )

    result_card(
        TXT["auto_elbows"],
        str(auto_elbow90)
    )

with c2:

    result_card(
        TXT["end_elevation"],
        f"{end_elevation_m:.1f}"
    )

    result_card(
        TXT["flow_regime"],
        flow_regime
    )

st.markdown("---")

st.markdown(f"""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-top:20px;
margin-bottom:12px;
border-left:4px solid #2563EB;
padding-left:10px;
">
{TXT["pressure_result"]}
</div>
""", unsafe_allow_html=True)

c3, c4, c5 = st.columns(3)

with c3:

    result_card(
        TXT["start_pressure"],
        f"{start_pressure_kpa:.1f}",
        "#2563EB"
    )

with c4:

    result_card(
        TXT["total_loss"],
        f"{pressure_loss_kpa:.1f}",
        "#DC2626"
    )

with c5:

    result_card(
        QUICK["end"],
        f"{end_pressure_kpa:.1f}",
        "#16A34A"
    )
    
# =====================================================
# Detailed Results
# =====================================================

with st.expander(
    TXT["show_detail"],
    expanded=False
):

    detail_header(
        "流体特性"
        if language == "日本語"
        else
        "Flow Characteristics"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "総配管長 [m]"
            if language == "日本語"
            else
            "Total Length [m]",
            f"{total_length_m:.2f}"
        )

    with c2:

        st.metric(
            "流速 [m/s]"
            if language == "日本語"
            else
            "Velocity [m/s]",
            f"{velocity:.2f}"
        )

    with c3:

        st.metric(
            "流動状態"
            if language == "日本語"
            else
            "Flow Regime",
            flow_regime
        )

    with c4:

        st.metric(
            "レイノルズ数"
            if language == "日本語"
            else
            "Reynolds Number",
            f"{reynolds:.0f}"
        )

    detail_header(
        "ルート情報"
        if language == "日本語"
        else
        "Route Information"
    )

    c5, c6, c7, c8 = st.columns(4)

    with c5:

        st.metric(
            "セグメント数"
            if language == "日本語"
            else
            "Segments",
            len(
                st.session_state.route_segments
            )
        )

    with c6:

        st.metric(
            "自動90°エルボ"
            if language == "日本語"
            else
            "Auto 90° Elbows",
            auto_elbow90
        )

    with c7:

        st.metric(
            "始点標高 [m]"
            if language == "日本語"
            else
            "Start Elevation [m]",
            f"{start_elevation_m:.2f}"
        )

    with c8:

        st.metric(
            "終点標高 [m]"
            if language == "日本語"
            else
            "End Elevation [m]",
            f"{end_elevation_m:.2f}"
        )

    detail_header(
        "損失解析"
        if language == "日本語"
        else
        "Loss Analysis"
    )

    c9, c10, c11, c12 = st.columns(4)

    with c9:

        st.metric(
            "摩擦損失 [m]"
            if language == "日本語"
            else
            "Major Loss [m]",
            f"{major_loss_m:.2f}"
        )

    with c10:

        st.metric(
            "局部損失 [m]"
            if language == "日本語"
            else
            "Minor Loss [m]",
            f"{minor_loss_m:.2f}"
        )

    with c11:

        st.metric(
            "静水頭 [m]"
            if language == "日本語"
            else
            "Static Head [m]",
            f"{static_head_m:.2f}"
        )

    with c12:

        st.metric(
            "総損失 [m]"
            if language == "日本語"
            else
            "Total Loss [m]",
            f"{total_loss_m:.2f}"
        )

    detail_header(
        "圧力解析"
        if language == "日本語"
        else
        "Pressure Analysis"
    )

    c13, c14, c15, c16 = st.columns(4)

    with c13:

        st.metric(
            "摩擦係数"
            if language == "日本語"
            else
            "Friction Factor",
            f"{friction_factor:.4f}"
        )

    with c14:

        st.metric(
            "圧力損失 [kPa]"
            if language == "日本語"
            else
            "Pressure Loss [kPa]",
            f"{pressure_loss_kpa:.2f}"
        )

    with c15:

        st.metric(
            "始点圧力 [kPa]"
            if language == "日本語"
            else
            "Start Pressure [kPa]",
            f"{start_pressure_kpa:.2f}"
        )

    with c16:

        st.metric(
            "終点圧力 [kPa]"
            if language == "日本語"
            else
            "End Pressure [kPa]",
            f"{end_pressure_kpa:.2f}"
        )
        
# =====================================================
# Node Data
# =====================================================

with st.expander(
    TXT["show_node"],
    expanded=False
):

    if len(
        st.session_state.route_segments
    ) > 0:

        node_df = pd.DataFrame(

            [
                {
                    "No":
                    i + 1,

                    "Direction":

                    {
                        "X+": "→ X+",
                        "X-": "← X-",
                        "Y+": "↗ Y+",
                        "Y-": "↙ Y-",
                        "Z+": "↑ Z+",
                        "Z-": "↓ Z-"
                    }.get(
                        seg["direction"],
                        seg["direction"]
                    ),

                    "Length [m]":
                    seg["length"]
                }

                for i, seg in enumerate(
                    st.session_state.route_segments
                )
            ]

        )

        st.dataframe(

            node_df,

            use_container_width=True,

            hide_index=True

        )

        if language == "日本語":

            st.caption(
                f"セグメント数 : {len(st.session_state.route_segments)}"
            )

        else:

            st.caption(
                f"Segments : {len(st.session_state.route_segments)}"
            )

    else:

        st.info(
            TXT["no_route_data"]
        )
        
# =====================================================
# CSV Import / Export
# =====================================================

st.markdown(f"""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-top:20px;
margin-bottom:12px;
border-left:4px solid #2563EB;
padding-left:10px;
">
{TXT["csv_data"]}
</div>
""", unsafe_allow_html=True)

csv_df = pd.DataFrame(

    [
        {
            "Direction":
            seg["direction"],

            "Length [m]":
            seg["length"]
        }

        for seg

        in st.session_state.route_segments
    ]

)

csv_data = csv_df.to_csv(
    index=False
).encode(
    "utf-8-sig"
)

c1, c2 = st.columns(2)

with c1:

    st.download_button(

        TXT["csv_export"],

        csv_data,

        file_name=
        "pipe_route_v4.csv",

        mime="text/csv",

        use_container_width=True
    )

with c2:

    uploaded_csv = st.file_uploader(

        TXT["csv_import"],

        type=["csv"]

    )

    if uploaded_csv is not None:

        if st.button(
            TXT["import_route"],
            use_container_width=True
        ):

            try:

                df_import = (
                    pd.read_csv(
                        uploaded_csv
                    )
                )

                st.session_state.route_segments = []

                st.session_state.segment_id = 1

                for _, row in (
                    df_import.iterrows()
                ):

                    st.session_state.route_segments.append(
                        {

                            "id":
                            st.session_state.segment_id,

                            "direction":
                            row["Direction"],

                            "length":
                            float(
                                row["Length [m]"]
                            ),

                            "type":
                            "PIPE"
                        }
                    )

                    st.session_state.segment_id += 1

                st.rerun()

            except Exception as e:

                st.error(
                    f"Import Error : {e}"
                )
                
# =====================================================
# Calculation Method
# =====================================================

with st.expander(
    TXT["show_eq"],
    expanded=False
):

    st.markdown(
        "### Route Engine"
    )

    st.markdown("""
- Route is defined by Direction + Length
- X = Horizontal
- Y = Depth
- Z = Elevation
- Total Length = Sum of all segment lengths
- Elevation is calculated automatically from Z segments
- 90° Elbows are detected automatically when direction changes
""")

    st.markdown(
        "### Reynolds Number"
    )

    st.latex(
        r"Re=\frac{VD}{\nu}"
    )

    st.markdown(
        "### Laminar Flow"
    )

    st.latex(
        r"f=\frac{64}{Re}"
    )

    st.markdown(
        "### Turbulent Flow (Swamee-Jain)"
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
        "### Darcy-Weisbach"
    )

    st.latex(
        r"h_f=f\frac{L}{D}\frac{V^2}{2g}"
    )

    st.markdown(
        "### Minor Loss"
    )

    st.latex(
        r"h_m=K\frac{V^2}{2g}"
    )

    st.markdown(
        "### Static Head"
    )

    st.latex(
        r"h_z=z_{end}-z_{start}"
    )

    st.markdown(
        "### Total Loss"
    )

    st.latex(
        r"h_t=h_f+h_m+h_z"
    )

    st.markdown(
        "### Pressure Loss"
    )

    st.latex(
        r"\Delta P=\rho g h_t"
    )

# =====================================================
# Feedback
# =====================================================

if language == "日本語":

    feedback_text = (
        "バグ報告・機能追加要望・UI改善案をお待ちしています"
    )

    feedback_button = (
        "Googleフォームを開く"
    )

else:

    feedback_text = (
        "Bug Reports / Feature Requests / UI Suggestions Welcome"
    )

    feedback_button = (
        "Send Feedback"
    )

st.markdown(f"""
<div style="
font-size:18px;
font-weight:600;
color:#475569;
margin-top:20px;
margin-bottom:12px;
border-left:4px solid #2563EB;
padding-left:10px;
">
💬 {TXT["feedback"]}
</div>
""", unsafe_allow_html=True)

st.info(
    feedback_text
)

st.link_button(
    feedback_button,
    "https://docs.google.com/forms/d/e/1FAIpQLSfVi4i5Pz9i_nr0vDCnT2RjvJmdhO-kGBAej4Du1CkAGhRgig/viewform"
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

    Version 4.0<br>

    Created by Kyotaro.H<br><br>

    Isometric Route Engine Enabled<br>

    Route Length / Elevation / Elbow Detection<br><br>

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

    Version 4.0<br>

    Created by Kyotaro.H<br><br>

    Isometric Route Engine Enabled<br>

    Route Length / Elevation / Elbow Detection<br><br>

    Feedback Welcome

    </div>
    """

st.markdown(
    footer_text,
    unsafe_allow_html=True
)
