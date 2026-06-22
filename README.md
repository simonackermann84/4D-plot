# 4D Excel Plotter

A small Streamlit app that reads an Excel file and creates an interactive 3D scatter plot with a fourth variable shown by marker color.

## Expected Excel format

The uploaded `.xlsx` file must follow this structure:

| Row | Content |
| --- | --- |
| 1 | Plot title in the first cell |
| 2 | Axis and colorbar labels: X, Y, Z, Color |
| 3 onward | Numeric data: X, Y, Z, Color |

Example:

| Data example | | | |
| --- | --- | --- | --- |
| Data 1 | Data 2 | Multi | Plus |
| 0.1 | 0.2 | 0.02 | 0.3 |

## Local installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload these files to the repository root:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Go to Streamlit Community Cloud.
4. Create a new app from your GitHub repository.
5. Set the main file path to:

```text
app.py
```

6. Deploy the app.

## Notes

- The app accepts `.xlsx` files only.
- Axis limits and tick spacing are calculated automatically from the data.
- Invalid or non-numeric rows in the data section are dropped.
- The plot can be downloaded as an interactive HTML file.
