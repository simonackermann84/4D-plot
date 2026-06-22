import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="4D Excel Plotter",
    page_icon="📊",
    layout="wide",
)


def nice_tick_step(vmin, vmax, target_ticks=6):
    """Return a human-friendly tick step for a numeric range."""
    data_range = vmax - vmin

    if not np.isfinite(data_range) or data_range <= 0:
        return 1.0

    raw_step = data_range / target_ticks
    magnitude = 10 ** np.floor(np.log10(raw_step))
    residual = raw_step / magnitude

    if residual <= 1:
        nice = 1
    elif residual <= 2:
        nice = 2
    elif residual <= 5:
        nice = 5
    else:
        nice = 10

    return nice * magnitude


def make_tick_values(vmin, vmax, step):
    """Create tick values that cover the full axis range."""
    if not np.isfinite(step) or step <= 0:
        return None

    tick_start = np.floor(vmin / step) * step
    tick_end = np.ceil(vmax / step) * step
    return np.arange(tick_start, tick_end + 0.5 * step, step)


def add_margin(vmin, vmax, margin_fraction=0.05):
    """Add a small margin around an axis range."""
    data_range = vmax - vmin

    if not np.isfinite(data_range) or data_range == 0:
        margin = 0.5 if vmin == 0 else abs(vmin) * margin_fraction
        return vmin - margin, vmax + margin

    margin = margin_fraction * data_range
    return vmin - margin, vmax + margin


def read_excel_4d(uploaded_file):
    """
    Read an Excel file with this expected structure:
    row 1: plot title
    row 2: x label, y label, z label, colorbar label
    row 3 onward: x, y, z, color values
    """
    title_df = pd.read_excel(uploaded_file, header=None, nrows=1, engine="openpyxl")
    uploaded_file.seek(0)

    header_df = pd.read_excel(uploaded_file, header=None, skiprows=1, nrows=1, engine="openpyxl")
    uploaded_file.seek(0)

    data = pd.read_excel(uploaded_file, header=None, skiprows=2, engine="openpyxl")

    if title_df.empty or header_df.empty:
        raise ValueError("The Excel file must contain at least two rows: title row and axis-label row.")

    if data.shape[1] < 4:
        raise ValueError("The Excel file must contain at least four data columns: X, Y, Z, and color.")

    plot_title = str(title_df.iloc[0, 0])
    headers = header_df.iloc[0]

    x_axis_label = str(headers.iloc[0])
    y_axis_label = str(headers.iloc[1])
    z_axis_label = str(headers.iloc[2])
    c_bar_label = str(headers.iloc[3])

    numeric_data = data.iloc[:, :4].apply(pd.to_numeric, errors="coerce")
    numeric_data = numeric_data.dropna(how="any")

    if numeric_data.empty:
        raise ValueError("No valid numeric data was found in rows 3 onward.")

    return {
        "plot_title": plot_title,
        "x_axis_label": x_axis_label,
        "y_axis_label": y_axis_label,
        "z_axis_label": z_axis_label,
        "c_bar_label": c_bar_label,
        "data": numeric_data,
    }


def build_figure(
    parsed,
    marker_size=4.5,
    colorscale="Plasma",
    target_ticks=6,
    margin_fraction=0.05,
    width_cm=15,
    height_cm=15,
    camera_x=1.6,
    camera_y=-4.0,
    camera_z=0.7,
):
    data = parsed["data"]

    x_values = data.iloc[:, 0].to_numpy(dtype=float)
    y_values = data.iloc[:, 1].to_numpy(dtype=float)
    z_values = data.iloc[:, 2].to_numpy(dtype=float)
    c_values = data.iloc[:, 3].to_numpy(dtype=float)

    x_min, x_max = add_margin(np.nanmin(x_values), np.nanmax(x_values), margin_fraction)
    y_min, y_max = add_margin(np.nanmin(y_values), np.nanmax(y_values), margin_fraction)
    z_min, z_max = add_margin(np.nanmin(z_values), np.nanmax(z_values), margin_fraction)

    c_min = np.nanmin(c_values)
    c_max = np.nanmax(c_values)

    x_tick_step = nice_tick_step(x_min, x_max, target_ticks)
    y_tick_step = nice_tick_step(y_min, y_max, target_ticks)
    z_tick_step = nice_tick_step(z_min, z_max, target_ticks)
    c_tick_step = nice_tick_step(c_min, c_max, target_ticks)

    x_tickvals = make_tick_values(x_min, x_max, x_tick_step)
    y_tickvals = make_tick_values(y_min, y_max, y_tick_step)
    z_tickvals = make_tick_values(z_min, z_max, z_tick_step)
    c_tickvals = make_tick_values(c_min, c_max, c_tick_step)

    trace_main = go.Scatter3d(
        x=x_values,
        y=y_values,
        z=z_values,
        mode="markers",
        marker=dict(
            size=marker_size,
            color=c_values,
            colorscale=colorscale,
            cmin=c_min,
            cmax=c_max,
            opacity=1.0,
            colorbar=dict(
                title=parsed["c_bar_label"],
                tickvals=c_tickvals,
                ticktext=[f"{t:.3g}" for t in c_tickvals] if c_tickvals is not None else None,
                len=0.8,
            ),
            line=dict(width=0),
        ),
        name="",
    )

    camera = dict(eye=dict(x=camera_x, y=camera_y, z=camera_z))

    fig = go.Figure(data=[trace_main])
    fig.update_layout(
        title=dict(
            text=parsed["plot_title"],
            font=dict(family="DejaVu Sans", size=16),
        ),
        width=int(width_cm / 2.54 * 96),
        height=int(height_cm / 2.54 * 96),
        paper_bgcolor="white",
        scene=dict(
            xaxis=dict(
                title=parsed["x_axis_label"],
                range=[x_min, x_max],
                tickmode="array",
                tickvals=x_tickvals,
                tickformat=".3g",
                showbackground=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                linecolor="black",
            ),
            yaxis=dict(
                title=parsed["y_axis_label"],
                range=[y_min, y_max],
                tickmode="array",
                tickvals=y_tickvals,
                tickformat=".3g",
                showbackground=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                linecolor="black",
            ),
            zaxis=dict(
                title=parsed["z_axis_label"],
                range=[z_min, z_max],
                tickmode="array",
                tickvals=z_tickvals,
                tickformat=".3g",
                showbackground=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                linecolor="black",
            ),
            camera=camera,
        ),
        font=dict(
            family="DejaVu Sans",
            size=12,
            color="black",
        ),
        margin=dict(l=0, r=0, b=0, t=50),
    )

    return fig


st.title("4D Excel Plotter")
st.write(
    """Upload an `.xlsx` file where row 1 contains the plot title, row 2 contains the
    axis/colorbar labels, and row 3 onward contains the numeric X, Y, Z, and color data.
    
    Example format in Excel:
    
      | A           | B           | C           | D           |
      
    1 | Title       |
    
    2 | x-axis name | y-axis name | z-axis name | c-axis name |
    
    3 | 1.7         | 0.9         | 1.53        | 2.6         |"""
)

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

with st.sidebar:
    st.header("Plot settings")
    marker_size = st.slider("Marker size", 1.0, 12.0, 4.5, 0.5)
    colorscale = st.selectbox(
        "Color scale",
        ["Plasma", "Viridis", "Cividis", "Inferno", "Magma", "Turbo", "Jet"],
        index=0,
    )
    target_ticks = st.slider("Approximate number of ticks", 3, 12, 6, 1)
    margin_fraction = st.slider("Axis margin", 0.0, 0.20, 0.05, 0.01)
    width_cm = st.slider("Figure width [cm]", 8, 30, 15, 1)
    height_cm = st.slider("Figure height [cm]", 8, 30, 15, 1)

    st.header("Camera")
    camera_x = st.slider("Camera X", -5.0, 5.0, 1.6, 0.1)
    camera_y = st.slider("Camera Y", -5.0, 5.0, -4.0, 0.1)
    camera_z = st.slider("Camera Z", -5.0, 5.0, 0.7, 0.1)

if uploaded_file is None:
    st.info("Upload an Excel file to create the 4D plot.")
else:
    try:
        parsed = read_excel_4d(uploaded_file)
        fig = build_figure(
            parsed,
            marker_size=marker_size,
            colorscale=colorscale,
            target_ticks=target_ticks,
            margin_fraction=margin_fraction,
            width_cm=width_cm,
            height_cm=height_cm,
            camera_x=camera_x,
            camera_y=camera_y,
            camera_z=camera_z,
        )

        st.subheader(parsed["plot_title"])
        st.plotly_chart(fig, use_container_width=True)

        html = fig.to_html(include_plotlyjs="cdn")
        st.download_button(
            label="Download interactive HTML plot",
            data=html,
            file_name=f"{parsed['plot_title']}.html",
            mime="text/html",
        )

        with st.expander("Preview loaded data"):
            preview = parsed["data"].copy()
            preview.columns = [
                parsed["x_axis_label"],
                parsed["y_axis_label"],
                parsed["z_axis_label"],
                parsed["c_bar_label"],
            ]
            st.dataframe(preview, use_container_width=True)

    except Exception as exc:
        st.error(f"Could not read or plot the uploaded file: {exc}")
