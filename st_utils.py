import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64
import os
import json
import pickle


def download_button(
    object_to_download, download_filename, button_text, pickle_it=False
):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    dl_link = f"""
        <html>
        <head>
        <title>Start Auto Download file</title>
        <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
        <script>
        $(function() {{
        $('a[data-auto-download]').each(function(){{
        var $this = $(this);
        setTimeout(function() {{
        window.location = $this.attr('href');
        }}, 500);
        }});
        }});
        </script>
        </head>
        <body>
        <div class="wrapper">
        <a data-auto-download href="data:text/csv;base64,{b64}"></a>
        </div>
        </body>
        </html>"""

    return dl_link


def plan_downloader(df):
    def download_df():
        filename = "my-dataframe.csv"
        components.html(
            download_button(
                df, filename, f"Click here to download {filename}", pickle_it=False
            ),
            height=0,
        )

    return download_df
