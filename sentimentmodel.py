import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon if not already downloaded
#nltk.download('vader_lexicon')

def sentimentfunc(text):
    try:
        # Create a Sentiment Intensity Analyzer object
        sia = SentimentIntensityAnalyzer()
    
        scores = sia.polarity_scores(text)
    
        result = ''
        if scores['compound'] >= 0.05:
            result = 'Positive'
        elif scores['compound'] < 0.05:
            result = 'Negative'
        else:
            raise Exception("scores invalid")
        return result
    except Exception as e:
        return "ERROR: {}".format(e)
    
    
def main():
    text = "I hate you."
    output = sentimentfunc(text)
    if not output:
        print("ERROR")
    else:
        print("SUCCESS: " + output + ".")
    
    
if __name__ == "__main__":
    main()