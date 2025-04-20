import re
import pandas as pd
from collections import Counter

class SimpleAIWordHighlighter:
    def __init__(self):
        """Initialize with a default set of common AI words and phrases"""
        # Common AI words with their frequency rankings
        self.ai_words = {
            # Words identified from multiple sources as common in AI text
            "delve": 10,
            "whilst": 9,
            "furthermore": 8,
            "navigate": 8,
            "indeed": 7,
            "utilize": 7,
            "leverage": 7,
            "robust": 7,
            "optimal": 7,
            "showcase": 6,
            "essentially": 6,
            "ultimately": 6,
            "myriad": 6,
            "seamless": 6,
            "plethora": 6,
            "harness": 6,
            "elevate": 10,
            "tapestry": 9,
            "captivate": 8,
            "testament": 8,
            "nuanced": 7,
            "enhance": 7,
            "facilitate": 7,
            "comprehensive": 7,
            "innovative": 6,
            "streamline": 6,
            "synergy": 6,
            "paradigm": 6,
            "empower": 6,
            "revolutionize": 6,
            "transformative": 6,
            "ecosystem": 5,
            "unprecedented": 5,
            "cultivate": 5,
            "catalyst": 5,
            "disrupt": 5,
            "holistic": 5,
            "cutting-edge": 5,
            "sustainable": 5,
            "strategic": 5,
            "foster": 5,
            "streamlined": 5,
            "implementation": 5,
            "integration": 5,
            "methodology": 5,
            "functionality": 5,
            "optimization": 5,
            "infrastructure": 5,
            "initiative": 5,
        }
        
        # Common AI phrases with their frequency rankings
        self.ai_phrases = {
            "in this article": 10,
            "delve into": 9,
            "it's important to note": 9,
            "on the other hand": 8,
            "in the realm of": 8,
            "a wide range of": 8,
            "it is worth mentioning": 7,
            "plays a crucial role": 7,
            "in conclusion": 7,
            "in summary": 7,
            "to summarize": 6,
            "as we have seen": 6,
            "moving forward": 6,
            "when it comes to": 6,
            "as mentioned earlier": 6,
            "in the context of": 6,
            "it goes without saying": 5,
            "it is essential to": 5,
            "needless to say": 5,
            "it's worth noting that": 5,
            "a plethora of": 9,
            "treasure trove of": 8,
            "in today's fast-paced world": 8,
            "in the digital age": 7,
            "embark on a journey": 7,
            "unlock the potential": 7,
            "harness the power": 6,
            "foster a culture of": 6,
            "curated collection": 6,
            "seamless integration": 6,
            "rich tapestry": 5,
            "paradigm shift": 5,
            "as an AI language model": 10,
            "I don't have access to": 9,
            "as of my last update": 9,
            "I cannot provide": 8,
            "I cannot browse the internet": 8,
        }

    def add_word(self, word, frequency=5):
        """Add a new AI word to the dictionary"""
        self.ai_words[word.lower()] = frequency

    def add_phrase(self, phrase, frequency=5):
        """Add a new AI phrase to the dictionary"""
        self.ai_phrases[phrase.lower()] = frequency

    def remove_word(self, word):
        """Remove a word from the dictionary"""
        if word.lower() in self.ai_words:
            del self.ai_words[word.lower()]
            return True
        return False

    def remove_phrase(self, phrase):
        """Remove a phrase from the dictionary"""
        if phrase.lower() in self.ai_phrases:
            del self.ai_phrases[phrase.lower()]
            return True
        return False

    def get_all_words(self):
        """Get all AI words"""
        return sorted(self.ai_words.items(), key=lambda x: x[1], reverse=True)

    def get_all_phrases(self):
        """Get all AI phrases"""
        return sorted(self.ai_phrases.items(), key=lambda x: x[1