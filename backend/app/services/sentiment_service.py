from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score(text: str) -> float:
    """Return compound sentiment score in [-1, 1]. Positive > 0.05, Negative < -0.05."""
    return _analyzer.polarity_scores(text)["compound"]


def label(score_val: float) -> str:
    if score_val >= 0.05:
        return "positive"
    if score_val <= -0.05:
        return "negative"
    return "neutral"
