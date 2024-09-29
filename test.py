from textblob import TextBlob
import pandas as pd
import streamlit as st
import cleantext
import os

st.header('Twitter Sentiment Analysis')

# Text Analysis
with st.expander('Analyze Text'):
    text = st.text_input('Text here: ')
    if text:
        blob = TextBlob(text)
        st.write('Polarity: ', round(blob.sentiment.polarity, 2))
        st.write('Subjectivity: ', round(blob.sentiment.subjectivity, 2))

    pre = st.text_input('Clean Text: ')
    if pre:
        st.write(cleantext.clean(pre, clean_all=False, extra_spaces=True, stopwords=True, lowercase=True, numbers=True, punct=True))

# CSV and Excel Analysis
with st.expander('Analyze CSV or Excel'):
    upl = st.file_uploader('Upload file', type=['xls', 'xlsx', 'xlsm', 'csv'])

    def score(x):
        blob1 = TextBlob(x)
        return blob1.sentiment.polarity

    def analyze(x):
        if x >= 0.5:
            return 'Positive'
        elif x <= -0.5:
            return 'Negative'
        else:
            return 'Neutral'

    if upl:
        # Get the file extension
        file_extension = os.path.splitext(upl.name)[1]
        st.write("File extension detected:", file_extension)  # Debugging output

        try:
            if file_extension == '.xls':
                df = pd.read_excel(upl, engine='xlrd')
            elif file_extension in ['.xlsx', '.xlsm']:
                df = pd.read_excel(upl, engine='openpyxl')
            elif file_extension == '.csv':
                df = pd.read_csv(upl)
            else:
                st.error("Unsupported file format. Please upload an .xls, .xlsx, or .csv file.")
                df = None

            if df is not None:
                st.write("Available columns:", df.columns.tolist())
                selected_column = st.selectbox("Select the column containing the text:", df.columns)

                if selected_column:
                    if not df[selected_column].empty:
                        df['score'] = df[selected_column].apply(score)
                        df['analysis'] = df['score'].apply(analyze)
                        st.write(df.head(10))

                        @st.cache
                        def convert_df(df):
                            return df.to_csv().encode('utf-8')

                        csv = convert_df(df)

                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name='twitter_sentiment.csv',
                            mime='text/csv',
                        )
                    else:
                        st.error("The selected column is empty.")
        except Exception as e:
            st.error(f"Error reading the file: {e}")
