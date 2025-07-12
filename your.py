# analysis_functions.py
import re
import nltk
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Download NLTK data
nltk.download('punkt', quiet=True)

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

def count_syllables(word):
    word = word.lower()
    if word.endswith(('es', 'ed')):
        word = word[:-2]
    vowels = "aeiou"
    return sum(1 for char in word if char in vowels)

def count_personal_pronouns(text):
    pronouns = ['i', 'we', 'my', 'ours', 'us']
    pattern = r'\b(' + '|'.join(pronouns) + r')\b'
    return len(re.findall(pattern, text, flags=re.IGNORECASE))

def scrape_content(url):
    try:
        # Create WebDriver instance
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(3)  # Allow page to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else ""
        
        # Extract content
        article = ""
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            article += p.get_text(strip=True) + " "
        
        return title, article.strip()
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return "", ""

def analyze_url(url):
    """Main analysis function - processes URL and returns all 14 metrics"""
    try:
        title, content = scrape_content(url)
        
        if not content:
            return {'error': "No content found at URL"}
        
        # Perform all text analysis
        blob = TextBlob(title + " " + content)
        
        # Sentiment analysis
        positive_score = blob.sentiment.polarity if blob.sentiment.polarity > 0 else 0
        negative_score = -blob.sentiment.polarity if blob.sentiment.polarity < 0 else 0
        polarity_score = blob.sentiment.polarity
        subjectivity_score = blob.sentiment.subjectivity
        
        # Sentence and word analysis
        sentences = nltk.sent_tokenize(content)
        words = nltk.word_tokenize(content)
        word_count = len(words)
        
        # Calculate sentence length
        avg_sentence_length = len(words)/len(sentences) if sentences else 0
        
        # Complex words and syllables
        complex_words = [word for word in words if count_syllables(word) > 2]
        complex_word_count = len(complex_words)
        percentage_of_complex_words = len(complex_words)/len(words) if words else 0
        
        # Syllable count
        total_syllables = sum(count_syllables(word) for word in words)
        avg_syllable_word_counts = total_syllables/len(words) if words else 0
        
        # Personal pronouns
        pp_count = count_personal_pronouns(content)
        
        # Average word length
        total_chars = sum(len(word) for word in words)
        average_word_length = total_chars/len(words) if words else 0
        
        # Fog Index
        fog_index = 0.4 * (avg_sentence_length + percentage_of_complex_words)
        
        return {
            'url': url,
            'title': title,
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'positive_score': round(positive_score, 3),
            'negative_score': round(negative_score, 3),
            'polarity_score': round(polarity_score, 3),
            'subjectivity_score': round(subjectivity_score, 3),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'percentage_of_complex_words': round(percentage_of_complex_words, 3),
            'fog_index': round(fog_index, 2),
            'complex_word_count': complex_word_count,
            'word_count': word_count,
            'avg_syllable_word_counts': round(avg_syllable_word_counts, 2),
            'pp_count': pp_count,
            'average_word_length': round(average_word_length, 2)
        }
    except Exception as e:
        return {'error': str(e)}