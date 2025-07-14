# app.py
# Fix for pkgutil.ImpImporter
try:
    import fix_importer
except ImportError:
    pass

from flask import Flask, render_template, request, send_file
from your import analyze_url
import pandas as pd
import io

app = Flask(__name__)

# Metric definitions for the homepage
METRIC_DEFINITIONS = {
    'positive_score': "How much happy, good, or positive feeling is in the text.",
    'negative_score': "How much sad, bad, or negative feeling is in the text.",
    'polarity_score': "The overall emotion balance of the text, from very negative to very positive.",
    'subjectivity_score': "How much the text contains personal opinions versus factual information.",
    'avg_sentence_length': "The average number of words in each sentence.",
    'percentage_of_complex_words': "How many words in the text are difficult to read or understand.",
    'fog_index': "How hard the text is to read and understand (higher = more difficult).",
    'complex_word_count': "Total number of difficult words in the text.",
    'word_count': "Total number of words in the text",
    'avg_syllable_word_counts': "How many sound parts (syllables) each word has on average.",
    'pp_count': "Frequency of personal pronouns (I, we, my, ours, us)",
    'average_word_length': "Average character count per word"
}

@app.route('/')
def home():
    return render_template('index.html', definitions=METRIC_DEFINITIONS)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Analyze the URL using your Jupyter logic
    results = analyze_url(url)
    
    if 'error' in results:
        return render_template('error.html', error=results['error'])
    
    return render_template('results.html', results=results)

@app.route('/download', methods=['POST'])
def download():
    # Get results from form data
    results = {}
    for key in request.form:
        if key == 'download':
            continue
        try:
            # Convert numeric values back to float
            results[key] = float(request.form[key])
        except:
            results[key] = request.form[key]
    
    # Create DataFrame with the same structure as your Jupyter output
    df = pd.DataFrame([results])
    
    # Reorder columns to match your 14-column structure
    column_order = [
        'url', 'title', 'positive_score', 'negative_score', 'polarity_score',
        'subjectivity_score', 'avg_sentence_length', 'percentage_of_complex_words',
        'fog_index', 'complex_word_count', 'word_count', 'avg_syllable_word_counts',
        'pp_count', 'average_word_length'
    ]
    df = df[column_order]
    
    # Rename columns to match your Excel structure
    column_mapping = {
        'url': 'URL',
        'title': 'Title',
        'positive_score': 'POSITIVE SCORE',
        'negative_score': 'NEGATIVE SCORE',
        'polarity_score': 'POLARITY SCORE',
        'subjectivity_score': 'SUBJECTIVITY SCORE',
        'avg_sentence_length': 'AVG SENTENCE LENGTH',
        'percentage_of_complex_words': 'PERCENTAGE OF COMPLEX WORDS',
        'fog_index': 'FOG INDEX',
        'complex_word_count': 'COMPLEX WORD COUNT',
        'word_count': 'WORD COUNT',
        'avg_syllable_word_counts': 'SYLLABLE PER WORD',
        'pp_count': 'PERSONAL PRONOUNS',
        'average_word_length': 'AVG WORD LENGTH'
    }
    df = df.rename(columns=column_mapping)
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Send file
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='text_analysis_results.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)