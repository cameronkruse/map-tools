import streamlit as st
import numpy as np
import pandas as pd
import math

st.set_page_config(page_title="Raster Tile Helper", page_icon="🌍", layout="centered")

st.title("🌍 Raster Tile Helper")
st.write(
    """
This page is a series tools that can help you as a user prepare to tile your raster data. This assumes the usage of the gdal2tiles package that you will run on your local machine or in the cloud. These tools are meant to help dial in the settings and make decisions about zoom levels, resampling, and other options.
"""
)

st.write(
    """
        ## Calculate Zoom Levels for Raster Tiles
        This part of the tool calculates the maximum suitable zoom level for XYZ tiles based on your raster's resolution. You can always cut tiles at higher zoom levels, but it won't result in higher resolution and it will waste time and storage.
        Enter your pixel size in degrees (longitude/latitude) or meters.
    """
)
tab1, tab2 = st.tabs(["Degrees (Lat/Lon)", "Meters (Projected)"])

with tab1:
    st.subheader("Resolution in Degrees")
    col1, col2 = st.columns(2)

    with col1:
        pixel_size_lon = st.number_input(
            "Pixel Size (Longitude)",
            min_value=0.000000001,
            max_value=180.0,
            value=0.008333333,
            format="%.12f",
            help="Pixel size in the X direction (longitude) in degrees",
        )

    with col2:
        pixel_size_lat = st.number_input(
            "Pixel Size (Latitude)",
            min_value=0.000000001,
            max_value=180.0,
            value=0.008333333,
            format="%.12f",
            help="Pixel size in the Y direction (latitude) in degrees. Use absolute value if negative.",
        )

    if st.button("Calculate Zoom Level (Degrees)", key="calc_deg"):
        # Ensure we're using the absolute value of pixel size
        pixel_size_lon_abs = abs(pixel_size_lon)
        pixel_size_lat_abs = abs(pixel_size_lat)

        # Use the smaller of the two dimensions to ensure we don't lose resolution
        pixel_size_deg = min(pixel_size_lon_abs, pixel_size_lat_abs)

        # Web Mercator tile size at the equator for zoom level 0 is 360 degrees
        # Each zoom level divides this by 2
        max_zoom = math.log2(360 / (pixel_size_deg * 256))

        st.success(f"Recommended maximum zoom level: **{int(max_zoom)}**")
        st.write("### Example GDAL2Tiles Command")
        st.code(
            f"""
            gdal2tiles.py -z 0-{int(max_zoom)} -p raster -w none -r average INPUT_FILE.tif OUTPUT_DIRECTORY
            """
        )
        print ("hello wold")

        # write me a function thqat takes geocoordinates and returns the zoom level
        


        st.write("### Zoom Level Details")
        st.write("Here are the resolutions at different zoom levels:")

        zoom_df_data = []
        for zoom in range(max(0, int(max_zoom) - 2), int(max_zoom) + 3):
            # Resolution in degrees per pixel at this zoom level
            resolution_deg = 360 / (256 * (2**zoom))
            # Convert to meters at equator (very approximate)
            resolution_m_equator = resolution_deg * 111319.5

            status = ""
            if zoom <= int(max_zoom):
                status = "✅ Suitable"
            else:
                status = "❌ May appear pixelated"

            zoom_df_data.append(
                {
                    "Zoom Level": zoom,
                    "Resolution (degrees/pixel)": f"{resolution_deg:.12f}°",
                    "Resolution at Equator (m/pixel)": f"{resolution_m_equator:.2f}m",
                    "Status": status,
                }
            )

        st.table(zoom_df_data)

with tab2:
    st.subheader("Resolution in Meters")
    pixel_size_m = st.number_input(
        "Pixel Size (meters)",
        min_value=0.001,
        max_value=10000.0,
        value=30.0,
        help="Pixel size in meters (for projected coordinate systems)",
    )

    if st.button("Calculate Zoom Level (Meters)", key="calc_m"):
        # Earth's circumference at the equator is approximately 40,075 km
        earth_circumference = 40075016.686  # meters

        # Size of the entire world at zoom level 0 is 256 pixels
        # So resolution at zoom 0 is:
        resolution_z0 = earth_circumference / 256  # meters per pixel

        # Calculate max zoom
        max_zoom = math.log2(resolution_z0 / pixel_size_m)

        st.success(f"Recommended maximum zoom level: **{int(max_zoom)}**")

        st.write("### Zoom Level Details")
        st.write("Here are the resolutions at different zoom levels:")

        zoom_df_data = []
        for zoom in range(max(0, int(max_zoom) - 2), int(max_zoom) + 3):
            # Resolution in meters per pixel at this zoom level (at equator)
            resolution_m = resolution_z0 / (2**zoom)

            zoom_df_data.append(
                {
                    "Zoom Level": zoom,
                    "Resolution (m/pixel)": f"{resolution_m:.2f}m",
                    "Status": status,
                }
            )

        st.table(zoom_df_data)

st.info(
    """
        **More Info:**

        1. For degrees: The formula calculates how many zoom levels are needed to reach your pixel resolution, given that zoom level 0 is 360° wide with 256 pixels.
        2. For meters: Uses the Earth's circumference at the equator (~40,075 km) and applies the same logic.
        **Note:** Keep in mind that web tile systems use Web Mercator projection, which distorts sizes as you move away from the equator.
    """
)

st.write(
    """
        ## Resampling Methods
        When tiling raster data, you can choose different resampling methods to affect how the output tiles look when a user is zoomed out enough where the original pixel size is smaller than the tiles pixel size. To resolve this the resampling method is used to determine how to combine the pixels into a single pixel. If you are tiling satellite imagery you will likely want to choose nearest or average resampling, but for other types of data here are all the methods gdal2tiles supports:
        - **Nearest Neighbor**: Fastest, but can result in a pixelated image. Best for categorical data. `near`
        - **Bilinear**: Smooths the image by averaging the four nearest pixels. Good for continuous data. 
        - **Cubic**: More advanced smoothing, uses 16 pixels. Slower but better quality.
        - **Average**: Averages all pixels in the resampling window. Good for reducing noise.
        - **Maximum**: Takes the maximum value in the resampling window. Good for highlighting maximum features.
        - **Minimum**: Takes the minimum value in the resampling window. Good for highlighting minimum features.
        - **Median**: Uses the median value in the resampling window. Can be good for reducing noise.
        - **Mode**: Uses the most common value in the resampling window. Good for categorical data.
        - **Cubic Spline**: Advanced smoothing, slower but better quality than cubic.
        - **Lanczos**: High-quality resampling, best for preserving details. Slowest.
    """
)
st.write("""
When tiling raster data, you need to choose a resampling method that affects how output tiles appear when users zoom out to levels where the original pixel size is smaller than the tile's pixel size. 
The resampling method determines how to combine multiple pixels into a single pixel.
""")

# Create dataframe with all methods
resampling_data = {
    'Resampling Method': [
        'Average', 
        'Nearest Neighbor',
        'Bilinear',
        'Cubic',
        'Cubic Spline',
        'Lanczos',
        'Antialias',
        'Mode',
        'Maximum',
        'Minimum',
        'Median',
        'First Quartile (Q1)',
        'Third Quartile (Q3)'
    ],
    'Description': [
        'Averages all pixels in the resampling window. Good for reducing noise in continuous data.',
        'Fastest method that selects the value of the nearest pixel. Best for categorical/discrete data where interpolation would create invalid values.',
        'Smooths the image by interpolating between the four nearest pixels. Good for continuous data like elevation.',
        'More advanced smoothing using 16 surrounding pixels. Better quality than bilinear but slower.',
        'Advanced smoothing using cubic spline algorithm. Produces smoother results than cubic but more computationally intensive.',
        'High-quality resampling that preserves more detail. One of the slowest methods but produces excellent results for visual data.',
        'Specialized anti-aliasing resampling that reduces artifacts when downsampling. Good for imagery intended for visual display.',
        'Uses the most common value in the resampling window. Excellent for categorical data where you want to preserve the dominant class.',
        'Takes the maximum value in the resampling window. Useful for highlighting peak features or preserving maxima in the data.',
        'Takes the minimum value in the resampling window. Useful for highlighting minimum features or preserving minima in the data.',
        'Uses the middle value (50th percentile) in the resampling window. Good for reducing outlier effects while preserving typical values.',
        'Uses the 25th percentile value in the resampling window. Useful for statistical analysis emphasizing lower values.',
        'Uses the 75th percentile value in the resampling window. Useful for statistical analysis emphasizing higher values.'
    ],
    'GDAL2Tiles Command': [
        '`average`',
        '`near`',
        '`bilinear`',
        '`cubic`',
        '`cubicspline`',
        '`lanczos`',
        '`antialias`',
        '`mode`',
        '`max`',
        '`min`',
        '`med`',
        '`q1`',
        '`q3`'
    ]
}

# Create and display the dataframe
df = pd.DataFrame(resampling_data)

# Add note about default
st.write("**Note:** The default resampling method in gdal2tiles is 'average'.")

# Display the dataframe with improved styling
st.dataframe(
    df,
    column_config={
        "Resampling Method": st.column_config.TextColumn("Resampling Method"),
        "Description": st.column_config.TextColumn("Description", width="large"),
        "GDAL2Tiles Command": st.column_config.TextColumn("GDAL2Tiles Command", help="Use this value with the -r parameter")
    },
    use_container_width=True,
    hide_index=True
)

# Add usage example
st.subheader("Usage Example")
st.code("""
# Example gdal2tiles.py command with resampling method
gdal2tiles.py -r lanczos -z 8-12 input_raster.tif output_folder/
""")

# Add tips section
st.subheader("Choosing the Right Resampling Method")
st.write("""
- **For satellite imagery**: `near` or `average` is usually recommended
- **For continuous data** (elevation, temperature): `bilinear`, `cubic`, or `cubicspline`
- **For categorical data** (land use, soil types): `mode`, `max`, `min`, or `median` 
- **For visual quality**: `lanczos` or `antialias`
- **For statistical analysis**: Consider `med`, `q1`, `q3` depending on your focus
""")