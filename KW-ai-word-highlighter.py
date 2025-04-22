# streamlit run xxxx
import re
import sqlite3
import pandas as pd
from collections import Counter
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

class AIWordHighlighter:
    def __init__(self, db_path="ai_words.db"):
        """Initialize with database path (default is file in current directory)"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        
        # Only load default words if the database is empty
        self.cursor.execute('SELECT COUNT(*) FROM ai_words')
        word_count = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT COUNT(*) FROM ai_phrases')
        phrase_count = self.cursor.fetchone()[0]
        
        if word_count == 0 and phrase_count == 0:
            self.load_default_words()

    def initialize_database(self):
        """Create the necessary tables if they don't exist"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_words (
            id INTEGER PRIMARY KEY,
            word TEXT NOT NULL,
            frequency INTEGER DEFAULT 1,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'default'
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_phrases (
            id INTEGER PRIMARY KEY,
            phrase TEXT NOT NULL,
            frequency INTEGER DEFAULT 1,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'default'
        )
        ''')
        
        # Create indices for faster lookups
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON ai_words(word)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrase ON ai_phrases(phrase)')
        self.conn.commit()

    def load_default_words(self):
        """Load a default set of commonly used AI words and phrases"""
        # Common words from various sources
        default_words = [
            # Words identified from multiple sources as common in AI text
            ("delve", 10, "verb", "GPTZero"),
            ("whilst", 9, "conjunction", "ZeroGPT"),
            ("furthermore", 8, "conjunction", "ZeroGPT"),
            ("navigate", 8, "verb", "GPTZero"),
            ("indeed", 7, "adverb", "ZeroGPT"),
            ("utilize", 7, "verb", "ZeroGPT"),
            ("leverage", 7, "verb", "ZeroGPT"),
            ("robust", 7, "adjective", "ZeroGPT"),
            ("optimal", 7, "adjective", "ZeroGPT"),
            ("showcase", 6, "verb", "ZeroGPT"),
            ("essentially", 6, "adverb", "ZeroGPT"),
            ("ultimately", 6, "adverb", "ZeroGPT"),
            ("myriad", 6, "adjective", "ZeroGPT"),
            ("seamless", 6, "adjective", "ZeroGPT"),
            ("plethora", 6, "noun", "ZeroGPT"),
            ("harness", 6, "verb", "ZeroGPT"),
            ("elevate", 10, "verb", "GPTZero"),
            ("tapestry", 9, "noun", "GPTZero"),
            ("captivate", 8, "verb", "GPTZero"),
            ("testament", 8, "noun", "GPTZero"),
            ("nuanced", 7, "adjective", "GPTZero"),
            ("enhance", 7, "verb", "ZeroGPT"),
            ("facilitate", 7, "verb", "ZeroGPT"),
            ("comprehensive", 7, "adjective", "ZeroGPT"),
            ("innovative", 6, "adjective", "ZeroGPT"),
            ("streamline", 6, "verb", "ZeroGPT"),
            ("synergy", 6, "noun", "ZeroGPT"),
            ("paradigm", 6, "noun", "ZeroGPT"),
            ("empower", 6, "verb", "ZeroGPT"),
            ("revolutionize", 6, "verb", "ZeroGPT"),
            ("transformative", 6, "adjective", "ZeroGPT"),
            ("ecosystem", 5, "noun", "ZeroGPT"),
            ("unprecedented", 5, "adjective", "ZeroGPT"),
            ("cultivate", 5, "verb", "ZeroGPT"),
            ("catalyst", 5, "noun", "ZeroGPT"),
            ("disrupt", 5, "verb", "ZeroGPT"),
            ("holistic", 5, "adjective", "ZeroGPT"),
            ("cutting-edge", 5, "adjective", "ZeroGPT"),
            ("sustainable", 5, "adjective", "ZeroGPT"),
            ("innovative", 5, "adjective", "ZeroGPT"),
            ("strategic", 5, "adjective", "ZeroGPT"),
            ("foster", 5, "verb", "ZeroGPT"),
            ("streamlined", 5, "adjective", "ZeroGPT"),
            ("implementation", 5, "noun", "ZeroGPT"),
            ("integration", 5, "noun", "ZeroGPT"),
            ("methodology", 5, "noun", "ZeroGPT"),
            ("functionality", 5, "noun", "ZeroGPT"),
            ("optimization", 5, "noun", "ZeroGPT"),
            ("infrastructure", 5, "noun", "ZeroGPT"),
            ("initiative", 5, "noun", "ZeroGPT"),
        ]
        
        # Common phrases from various sources
        default_phrases = [
            # ("in this article", 10, "introduction", "ZeroGPT"),
            ("in this article", 1, "general", "user"),
            ("i don't have access to", 1, "general", "user"),
            ("delve", 1, "general", "user"),
            ("elevate", 1, "general", "user"),
            ("whilst", 1, "general", "user"),
            ("tapestry", 1, "general", "user"),
            ("furthermore", 1, "general", "user"),
            ("navigate", 1, "general", "user"),
            ("captivate", 1, "general", "user"),
            ("testament", 1, "general", "user"),
            ("indeed", 1, "general", "user"),
            ("utilize", 1, "general", "user"),
            ("leverage", 1, "general", "user"),
            ("robust", 1, "general", "user"),
            ("optimal", 1, "general", "user"),
            ("nuanced", 1, "general", "user"),
            ("enhance", 1, "general", "user"),
            ("facilitate", 1, "general", "user"),
            ("comprehensive", 1, "general", "user"),
            ("showcase", 1, "general", "user"),
            ("essentially", 1, "general", "user"),
            ("ultimately", 1, "general", "user"),
            ("myriad", 1, "general", "user"),
            ("seamless", 1, "general", "user"),
            ("plethora", 1, "general", "user"),
            ("harness", 1, "general", "user"),
            ("innovative", 1, "general", "user"),
            ("streamline", 1, "general", "user"),
            ("synergy", 1, "general", "user"),
            ("paradigm", 1, "general", "user"),
            ("empower", 1, "general", "user"),
            ("revolutionize", 1, "general", "user"),
            ("transformative", 1, "general", "user"),
            ("ecosystem", 1, "general", "user"),
            ("unprecedented", 1, "general", "user"),
            ("cultivate", 1, "general", "user"),
            ("catalyst", 1, "general", "user"),
            ("disrupt", 1, "general", "user"),
            ("holistic", 1, "general", "user"),
            ("cutting-edge", 1, "general", "user"),
            ("sustainable", 1, "general", "user"),
            ("innovative", 1, "general", "user"),
            ("strategic", 1, "general", "user"),
            ("foster", 1, "general", "user"),
            ("streamlined", 1, "general", "user"),
            ("implementation", 1, "general", "user"),
            ("integration", 1, "general", "user"),
            ("methodology", 1, "general", "user"),
            ("functionality", 1, "general", "user"),
            ("optimization", 1, "general", "user"),
            ("infrastructure", 1, "general", "user"),
            ("initiative", 1, "general", "user"),
            ("in this article", 1, "general", "user"),
            ("as an AI language model", 1, "general", "user"),
            ("delve into", 1, "general", "user"),
            ("it's important to note", 1, "general", "user"),
            ("a plethora of", 1, "general", "user"),
            ("I don't have access to", 1, "general", "user"),
            ("as of my last update", 1, "general", "user"),
            ("on the other hand", 1, "general", "user"),
            ("in the realm of", 1, "general", "user"),
            ("a wide range of", 1, "general", "user"),
            ("treasure trove of", 1, "general", "user"),
            ("in today's fast-paced world", 1, "general", "user"),
            ("I cannot provide", 1, "general", "user"),
            ("I cannot browse the internet", 1, "general", "user"),
            ("it is worth mentioning", 1, "general", "user"),
            ("plays a crucial role", 1, "general", "user"),
            ("in conclusion", 1, "general", "user"),
            ("in summary", 1, "general", "user"),
            ("in the digital age", 1, "general", "user"),
            ("embark on a journey", 1, "general", "user"),
            ("unlock the potential", 1, "general", "user"),
            ("to summarize", 1, "general", "user"),
            ("as we have seen", 1, "general", "user"),
            ("moving forward", 1, "general", "user"),
            ("when it comes to", 1, "general", "user"),
            ("as mentioned earlier", 1, "general", "user"),
            ("in the context of", 1, "general", "user"),
            ("harness the power", 1, "general", "user"),
            ("foster a culture of", 1, "general", "user"),
            ("curated collection", 1, "general", "user"),
            ("seamless integration", 1, "general", "user"),
            ("it goes without saying", 1, "general", "user"),
            ("it is essential to", 1, "general", "user"),
            ("needless to say", 1, "general", "user"),
            ("it's worth noting that", 1, "general", "user"),
            ("rich tapestry", 1, "general", "user"),
            ("paradigm shift", 1, "general", "user"),
            ("provide valuable insights", 1, "general", "user"),
            ("gain valuable insights", 1, "general", "user"),
            ("casting long shadows", 1, "general", "user"),
            ("provides valuable insights", 1, "general", "user"),
            ("gain a comprehensive understanding", 1, "general", "user"),
            ("study provides a valuable", 1, "general", "user"),
            ("left an indelible mark", 1, "general", "user"),
            ("offers valuable insights", 1, "general", "user"),
            ("an indelible mark", 1, "general", "user"),
            ("an unwavering commitment", 1, "general", "user"),
            ("plays a crucial role in shaping", 1, "general", "user"),
            ("plays a crucial role in understanding", 1, "general", "user"),
            ("played a significant role in shaping", 1, "general", "user"),
            ("left an indelible", 1, "general", "user"),
            ("valuable insights", 1, "general", "user"),
            ("a rich tapestry", 1, "general", "user"),
            ("offers valuable insights", 1, "general", "user"),
            ("opens new avenues", 1, "general", "user"),
            ("help to feel a sense", 1, "general", "user"),
            ("adds a layer of complexity", 1, "general", "user"),
            ("significant contributions to the field", 1, "general", "user"),
            ("plays a crucial role in shaping", 1, "general", "user"),
            ("research needed to explore", 1, "general", "user"),
            ("the intricate relationship", 1, "general", "user"),
            ("findings contribute to", 1, "general", "user"),
            ("continue to inspire", 1, "general", "user"),
            ("a stark reminder", 1, "general", "user"),
            ("hung heavy", 1, "general", "user"),
            ("crucial role in understanding", 1, "general", "user"),
            ("fostering a sense", 1, "general", "user"),
            ("significant attention in recent years", 1, "general", "user"),
            ("needed to fully understand", 1, "general", "user"),
            ("pivotal role in shaping", 1, "general", "user"),
            ("gain a deeper understanding", 1, "general", "user"),
            ("study sheds light on", 1, "general", "user"),
            ("continues to inspire", 1, "general", "user"),
            ("implications of various", 1, "general", "user"),
            ("highlights the importance of considering", 1, "general", "user"),
            ("let us delve", 1, "general", "user"),
            ("holds a significant", 1, "general", "user"),
            ("garnered a significant", 1, "general", "user"),
            ("advancing the understanding", 1, "general", "user"),
            ("voice dripping with sarcasm", 1, "general", "user"),
            ("conclusion of the study provides", 1, "general", "user"),
            ("It's important to note", 1, "general", "user"),
            ("Delve into", 1, "general", "user"),
            ("In conclusion", 1, "general", "user"),
            ("As we have seen", 1, "general", "user"),
            ("It's crucial to understand", 1, "general", "user"),
            ("To sum up", 1, "general", "user"),
            ("In the fast-paced world", 1, "general", "user"),
            ("A wide range of", 1, "general", "user"),
            ("This highlights the need", 1, "general", "user"),
            ("With regard to", 1, "general", "user"),
            ("On the other hand", 1, "general", "user"),
            ("The findings suggest", 1, "general", "user"),
            ("To better understand", 1, "general", "user"),
            ("This underscores the importance of", 1, "general", "user"),
            ("In other words", 1, "general", "user"),
            ("It's worth mentioning that", 1, "general", "user"),
            ("Given the context", 1, "general", "user"),
            ("Navigating the complexities", 1, "general", "user"),
            ("This approach allows for", 1, "general", "user"),
            ("An important consideration is", 1, "general", "user"),
            ("That being said", 1, "general", "user"),
            ("At its core", 1, "general", "user"),
            ("To put it simply", 1, "general", "user"),
            ("This underscores the importance of", 1, "general", "user"),
            ("A key takeaway is", 1, "general", "user"),
            ("From a broader perspective", 1, "general", "user"),
            ("Delve", 1, "general", "user"),
            ("Underscore", 1, "general", "user"),
            ("Pivotal", 1, "general", "user"),
            ("Realm", 1, "general", "user"),
            ("Harness", 1, "general", "user"),
            ("Illuminate", 1, "general", "user"),
            ("Shed light on", 1, "general", "user"),
            ("Facilitate", 1, "general", "user"),
            ("Refine", 1, "general", "user"),
            ("Bolster", 1, "general", "user"),
            ("Differentiate", 1, "general", "user"),
            ("Streamline", 1, "general", "user"),
            ("Multifaceted", 1, "general", "user"),
            ("Comprehensive", 1, "general", "user"),
            ("Testament", 1, "general", "user"),
            ("Paramount", 1, "general", "user"),
            ("Profound", 1, "general", "user"),
            ("Ultimately", 1, "general", "user"),
            ("Robust", 1, "general", "user"),
            ("Myriad", 1, "general", "user"),
            ("Plethora", 1, "general", "user"),
            ("Utilize", 1, "general", "user"),
            ("Paradigm", 1, "general", "user"),
            ("Revolutionize", 1, "general", "user"),
            ("Innovative", 1, "general", "user"),
            ("Cutting-edge", 1, "general", "user"),
            ("Game-changing", 1, "general", "user"),
            ("Transformative", 1, "general", "user"),
            ("Seamless integration", 1, "general", "user"),
            ("Scalable solution", 1, "general", "user"),
            ("Leverage", 1, "general", "user"),
            ("Optimize", 1, "general", "user"),
            ("Framework", 1, "general", "user"),
            ("Dynamic", 1, "general", "user"),
            ("Robust", 1, "general", "user"),
            ("Elevate", 1, "general", "user"),
            ("Journey", 1, "general", "user"),
            ("Resonate", 1, "general", "user"),
            ("Explore", 1, "general", "user"),
            ("Enrich", 1, "general", "user"),
            ("Seamless", 1, "general", "user"),
            ("Foster", 1, "general", "user"),
            ("Navigate", 1, "general", "user"),
            ("Landscape", 1, "general", "user"),
            ("Supercharge", 1, "general", "user"),
            ("Evolve", 1, "general", "user"),
            ("Reimagine", 1, "general", "user"),
            ("Align", 1, "general", "user"),
            ("Orchestrate", 1, "general", "user"),
            ("Generally speaking", 1, "general", "user"),
            ("Typically", 1, "general", "user"),
            ("Tends to", 1, "general", "user"),
            ("Arguably", 1, "general", "user"),
            ("To some extent", 1, "general", "user"),
            ("Broadly speaking", 1, "general", "user"),
            ("It can be argued", 1, "general", "user"),
            ("In many cases", 1, "general", "user"),
            ("One might consider", 1, "general", "user"),
            ("It stands to reason", 1, "general", "user"),
            ("In the event that", 1, "general", "user"),
            ("Crucial", 1, "general", "user"),
            ("Significant", 1, "general", "user"),
            ("Vital", 1, "general", "user"),
            ("Essential", 1, "general", "user"),
            ("Fundamentally", 1, "general", "user"),
            ("It is important to note", 1, "general", "user"),
            ("Crucially", 1, "general", "user"),
            ("Significantly", 1, "general", "user"),
            ("Undoubtedly", 1, "general", "user"),
            ("Despite the challenge faced", 1, "general", "user"),
            ("Today in the digital age", 1, "general", "user"),
            ("Today the fast pace of the world", 1, "general", "user"),
            ("Pave the way for the future", 1, "general", "user"),
            ("Finding an important implication", 1, "general", "user"),
            ("Make an informed decision in regard to", 1, "general", "user"),
            ("Require a careful consideration", 1, "general", "user"),
            ("Tapestry", 1, "general", "user"),
            ("Symphony", 1, "general", "user"),
            ("Beacon", 1, "general", "user"),
            ("Landscape", 1, "general", "user"),
            ("Realm", 1, "general", "user"),
            ("Treasure trove", 1, "general", "user"),
            ("In the annals of", 1, "general", "user"),
            ("Embark", 1, "general", "user"),
            ("Navigate", 1, "general", "user"),
            ("Unlock", 1, "general", "user"),
            ("In light of", 1, "general", "user"),
            ("It is worth noting", 1, "general", "user"),
            ("Provide a framework to understand", 1, "general", "user"),
            ("Present a unique challenge", 1, "general", "user"),
            ("Highlight the significance", 1, "general", "user"),
            ("Underscore the need", 1, "general", "user"),
            ("Enhance the understanding", 1, "general", "user"),
            ("Essential to recognize", 1, "general", "user"),
            ("Address the root cause", 1, "general", "user"),
            ("Contribute to understanding", 1, "general", "user"),
            ("Furthermore", 1, "general", "user"),
            ("Moreover", 1, "general", "user"),
            ("Additionally", 1, "general", "user"),
            ("Specifically", 1, "general", "user"),
            ("Consequently", 1, "general", "user"),
            ("Importantly", 1, "general", "user"),
            ("Similarly", 1, "general", "user"),
            ("Nonetheless", 1, "general", "user"),
            ("As a result", 1, "general", "user"),
            ("Indeed", 1, "general", "user"),
            ("Thus", 1, "general", "user"),
            ("Alternatively", 1, "general", "user"),
            ("Notably", 1, "general", "user"),
            ("Ensure", 1, "general", "user"),
            ("Context", 1, "general", "user"),
            ("Insight", 1, "general", "user"),
            ("Nuanced", 1, "general", "user"),
            ("Perspective", 1, "general", "user"),
            ("Framework", 1, "general", "user"),
            ("Facet", 1, "general", "user"),
            ("Intricacies", 1, "general", "user"),
            ("Holistic", 1, "general", "user"),
            ("Iterative", 1, "general", "user"),
            ("Synergy", 1, "general", "user"),
            ("Confluence", 1, "general", "user"),
            ("Trajectory", 1, "general", "user"),
            ("Meticulous", 1, "general", "user"),
            ("Esteemed", 1, "general", "user"),
            ("Whimsical", 1, "general", "user"),
            ("Bespoke", 1, "general", "user"),
            ("Captivate", 1, "general", "user"),
            ("Indelible", 1, "general", "user"),
            ("Enigma", 1, "general", "user"),
            ("Studies have shown", 1, "general", "user"),
            ("Experts agree", 1, "general", "user"),
            ("It is widely accepted", 1, "general", "user"),
            ("Research indicates", 1, "general", "user"),
            ("In conclusion", 1, "general", "user"),
            ("To sum up", 1, "general", "user"),
            ("All things considered", 1, "general", "user"),
            ("Ultimately", 1, "general", "user"),
            ("provide a valuable insight", 1, "general", "user"),
            ("left an indelible mark", 1, "general", "user"),
            ("play a significant role in shaping", 1, "general", "user"),
            ("an unwavering commitment", 1, "general", "user"),
            ("open a new avenue", 1, "general", "user"),
            ("a stark reminder", 1, "general", "user"),
            ("play a crucial role in determining", 1, "general", "user"),
            ("finding a contribution", 1, "general", "user"),
            ("crucial role in understanding", 1, "general", "user"),
            ("finding a shed light", 1, "general", "user"),
            ("gain a comprehensive understanding", 1, "general", "user"),
            ("conclusion of the study provides", 1, "general", "user"),
            ("a nuanced understanding", 1, "general", "user"),
            ("hold a significant", 1, "general", "user"),
            ("gain significant attention", 1, "general", "user"),
            ("continue to inspire", 1, "general", "user"),
            ("provide a comprehensive overview", 1, "general", "user"),
            ("finding the highlight the importance", 1, "general", "user"),
            ("endure a legacy", 1, "general", "user"),
            ("mark a significant", 1, "general", "user"),
            ("gain a deeper understanding", 1, "general", "user"),
            ("the multifaceted nature", 1, "general", "user"),
            ("the complex interplay", 1, "general", "user"),
            ("study shed light on", 1, "general", "user"),
            ("need to fully understand", 1, "general", "user"),
            ("navigate the complex", 1, "general", "user"),
            ("a serf reminder", 1, "general", "user"),
            ("the potential to revolutionize", 1, "general", "user"),
            ("the relentless pursuit", 1, "general", "user"),
            ("offer a valuable", 1, "general", "user"),
            ("underscore the importance", 1, "general", "user"),
            ("a complex multifaceted", 1, "general", "user"),
            ("the transformative power", 1, "general", "user"),
            ("today the fast pace of the world", 1, "general", "user"),
            ("a significant milestone", 1, "general", "user"),
            ("delve deeper into", 1, "general", "user"),
            ("provide an insight", 1, "general", "user"),
            ("navigate the challenge", 1, "general", "user"),
            ("highlight the potential", 1, "general", "user"),
            ("pose a significant challenge", 1, "general", "user"),
            ("a unique blend", 1, "general", "user"),
            ("a crucial development", 1, "general", "user"),
            ("various fields include", 1, "general", "user"),
            ("commitment to excellence", 1, "general", "user"),
            ("sent shockwaves through", 1, "general", "user"),
            ("emphasize the need", 1, "general", "user"),
            ("despite the face", 1, "general", "user"),
            ("understanding the fundamental", 1, "general", "user"),
            ("leave a lasting", 1, "general", "user"),
            ("gain a valuable", 1, "general", "user"),
            ("understand the behavior", 1, "general", "user"),
            ("broad implications", 1, "general", "user"),
            ("a prominent figure", 1, "general", "user"),
            ("study highlights the importance", 1, "general", "user"),
            ("a significant turning point", 1, "general", "user"),
            ("curiosity piques", 1, "general", "user"),
            ("today in the digital age", 1, "general", "user"),
            ("implication to understand", 1, "general", "user"),
            ("a beacon of hope", 1, "general", "user"),
            ("pave the way for the future", 1, "general", "user"),
            ("finding an important implication", 1, "general", "user"),
            ("understand the complexity", 1, "general", "user"),
            ("meticulous attention to", 1, "general", "user"),
            ("add a layer", 1, "general", "user"),
            ("the legacy of life", 1, "general", "user"),
            ("identify the area of improvement", 1, "general", "user"),
            ("aim to explore", 1, "general", "user"),
            ("highlight the need", 1, "general", "user"),
            ("provide the text", 1, "general", "user"),
            ("conclusion of the study demonstrates", 1, "general", "user"),
            ("a multifaceted approach", 1, "general", "user"),
            ("provide a framework to understand", 1, "general", "user"),
            ("present a unique challenge", 1, "general", "user"),
            ("highlight the significance", 1, "general", "user"),
            ("add depth to", 1, "general", "user"),
            ("a significant stride", 1, "general", "user"),
            ("gain an insight", 1, "general", "user"),
            ("underscore the need", 1, "general", "user"),
            ("the importance to consider", 1, "general", "user"),
            ("offer a unique perspective", 1, "general", "user"),
            ("contribute to understanding", 1, "general", "user"),
            ("a significant implication", 1, "general", "user"),
            ("despite the challenge faced", 1, "general", "user"),
            ("enhances the understanding", 1, "general", "user"),
            ("make an informed decision in regard to", 1, "general", "user"),
            ("the target intervention", 1, "general", "user"),
            ("require a careful consideration", 1, "general", "user"),
            ("essential to recognize", 1, "general", "user"),
            ("validate the finding", 1, "general", "user"),
            ("vital role in shaping", 1, "general", "user"),
            ("sense of camaraderie", 1, "general", "user"),
            ("influence various factors", 1, "general", "user"),
            ("make a challenge", 1, "general", "user"),
            ("unwavering support", 1, "general", "user"),
            ("importance of the address", 1, "general", "user"),
            ("a significant step forward", 1, "general", "user"),
            ("add an extra layer", 1, "general", "user"),
            ("address the root cause", 1, "general", "user"),
            ("a profound implication", 1, "general", "user"),
            ("contributes to understanding", 1, "general", "user"),
            ("It's important to note", 1, "general", "user"),
            ("Tapestry", 1, "general", "user"),
            ("Bustling", 1, "general", "user"),
            ("In summary", 1, "general", "user"),
            ("Remember that", 1, "general", "user"),
            ("Take a dive into", 1, "general", "user"),
            ("Navigating", 1, "general", "user"),
            ("Landscape", 1, "general", "user"),
            ("Testament", 1, "general", "user"),
            ("In the world of", 1, "general", "user"),
            ("Realm", 1, "general", "user"),
            ("Embark", 1, "general", "user"),
            ("Analogies to being a conductor or to music", 1, "general", "user"),
            ("Colons", 1, "general", "user"),
            ("Vibrant", 1, "general", "user"),
            ("Metropolis", 1, "general", "user"),
            ("Firstly", 1, "general", "user"),
            ("Moreover", 1, "general", "user"),
            ("Crucial", 1, "general", "user"),
            ("To consider", 1, "general", "user"),
            ("Essential", 1, "general", "user"),
            ("There are a few considerations", 1, "general", "user"),
            ("Ensure", 1, "general", "user"),
            ("It's essential to", 1, "general", "user"),
            ("Furthermore", 1, "general", "user"),
            ("Vital", 1, "general", "user"),
            ("Keen", 1, "general", "user"),
            ("Fancy", 1, "general", "user"),
            ("As a professional", 1, "general", "user"),
            ("However", 1, "general", "user"),
            ("Therefore", 1, "general", "user"),
            ("Additionally", 1, "general", "user"),
            ("Specifically", 1, "general", "user"),
            ("Generally", 1, "general", "user"),
            ("Consequently", 1, "general", "user"),
            ("Importantly", 1, "general", "user"),
            ("Similarly", 1, "general", "user"),
            ("Nonetheless", 1, "general", "user"),
            ("As a result", 1, "general", "user"),
            ("Indeed", 1, "general", "user"),
            ("Thus", 1, "general", "user"),
            ("Alternatively", 1, "general", "user"),
            ("Notably", 1, "general", "user"),
            ("As well as", 1, "general", "user"),
            ("Despite", 1, "general", "user"),
            ("Essentially", 1, "general", "user"),
            ("While", 1, "general", "user"),
            ("Unless", 1, "general", "user"),
            ("Also", 1, "general", "user"),
            ("Even though", 1, "general", "user"),
            ("Because", 1, "general", "user"),
            ("In contrast", 1, "general", "user"),
            ("Although", 1, "general", "user"),
            ("In order to", 1, "general", "user"),
            ("Due to", 1, "general", "user"),
            ("Even if", 1, "general", "user"),
            ("Given that", 1, "general", "user"),
            ("Arguably", 1, "general", "user"),
            ("You may want to", 1, "general", "user"),
            ("This is not an exhaustive list", 1, "general", "user"),
            ("You could consider", 1, "general", "user"),
            ("On the other hand", 1, "general", "user"),
            ("As previously mentioned", 1, "general", "user"),
            ("It's worth noting that", 1, "general", "user"),
            ("To summarize", 1, "general", "user"),
            ("Ultimately", 1, "general", "user"),
            ("To put it simply", 1, "general", "user"),
            ("Pesky", 1, "general", "user"),
            ("Promptly", 1, "general", "user"),
            ("Dive into", 1, "general", "user"),
            ("In today's digital era", 1, "general", "user"),
            ("Reverberate", 1, "general", "user"),
            ("Enhance", 1, "general", "user"),
            ("Emphasise", 1, "general", "user"),
            ("Hustle and bustle", 1, "general", "user"),
            ("Revolutionize", 1, "general", "user"),
            ("Foster", 1, "general", "user"),
            ("Labyrinthine", 1, "general", "user"),
            ("Moist", 1, "general", "user"),
            ("Remnant", 1, "general", "user"),
            ("Subsequently", 1, "general", "user"),
            ("Nestled", 1, "general", "user"),
            ("Game changer", 1, "general", "user"),
            ("Labyrinth", 1, "general", "user"),
            ("Gossamer", 1, "general", "user"),
            ("Enigma", 1, "general", "user"),
            ("Whispering", 1, "general", "user"),
            ("Sights unseen", 1, "general", "user"),
            ("Sounds unheard", 1, "general", "user"),
            ("Dance", 1, "general", "user"),
            ("Metamorphosis", 1, "general", "user"),
            ("Indelible", 1, "general", "user"),
            ("My friend", 1, "general", "user"),
            ("In conclusion", 1, "general", "user"),
            # ("I cannot browse the internet", 8, "limitation", "Various"),
        ]
        
        # Clear existing data
        self.cursor.execute('DELETE FROM ai_words')
        self.cursor.execute('DELETE FROM ai_phrases')
        
        # Insert words
        self.cursor.executemany(
            'INSERT INTO ai_words (word, frequency, category, source) VALUES (?, ?, ?, ?)',
            default_words
        )
        
        # Insert phrases
        self.cursor.executemany(
            'INSERT INTO ai_phrases (phrase, frequency, category, source) VALUES (?, ?, ?, ?)',
            default_phrases
        )
        
        self.conn.commit()

    def add_word(self, word, frequency=1, category="general", source="user"):
        """Add a new AI word to the database"""
        self.cursor.execute(
            'INSERT INTO ai_words (word, frequency, category, source) VALUES (?, ?, ?, ?)',
            (word.lower(), frequency, category, source)
        )
        self.conn.commit()

    def add_phrase(self, phrase, frequency=1, category="general", source="user"):
        """Add a new AI phrase to the database"""
        self.cursor.execute(
            'INSERT INTO ai_phrases (phrase, frequency, category, source) VALUES (?, ?, ?, ?)',
            (phrase.lower(), frequency, category, source)
        )
        self.conn.commit()

    def get_all_words(self):
        """Get all AI words from the database"""
        self.cursor.execute('SELECT word, frequency, category, source FROM ai_words ORDER BY frequency DESC')
        return self.cursor.fetchall()

    def get_all_phrases(self):
        """Get all AI phrases from the database"""
        self.cursor.execute('SELECT phrase, frequency, category, source FROM ai_phrases ORDER BY frequency DESC')
        return self.cursor.fetchall()

    def import_words_from_csv(self, file_path):
        """Import words from a CSV file"""
        try:
            df = pd.read_csv(file_path)
            required_columns = ['word', 'frequency', 'category', 'source']
            
            # Check if all required columns exist
            if all(col in df.columns for col in required_columns):
                for index, row in df.iterrows():
                    self.add_word(row['word'], row['frequency'], row['category'], row['source'])
                return True, f"Successfully imported {len(df)} words"
            else:
                return False, "CSV must have columns: word, frequency, category, source"
        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"

    def import_phrases_from_csv(self, file_path):
        """Import phrases from a CSV file"""
        try:
            df = pd.read_csv(file_path)
            required_columns = ['phrase', 'frequency', 'category', 'source']
            
            # Check if all required columns exist
            if all(col in df.columns for col in required_columns):
                for index, row in df.iterrows():
                    self.add_phrase(row['phrase'], row['frequency'], row['category'], row['source'])
                return True, f"Successfully imported {len(df)} phrases"
            else:
                return False, "CSV must have columns: phrase, frequency, category, source"
        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"

    def highlight_text(self, text):
        """Highlight AI words and phrases in the given text"""
        # Get all words and phrases
        words = self.get_all_words()
        phrases = self.get_all_phrases()
        print(f"Words from database: {len(words)}, sample: {words[:5] if words else 'none'}")
        print(f"Phrases from database: {len(phrases)}, sample: {phrases[:5] if phrases else 'none'}")

        # Create a copy of the text for highlighting
        highlighted_text = text
        found_items = []
        
        # First detect phrases (to avoid highlighting parts of phrases as individual words)
        for phrase, frequency, category, source in phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                found_items.append(("phrase", phrase, match.start(), match.end(), frequency, category, source))
        
        # After the phrase detection loop:
        # print(f"Detected {len(found_items)} phrases")

        # Then detect individual words
        for word, frequency, category, source in words:
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Check if this word is part of a detected phrase
                is_part_of_phrase = False
                for item_type, item_text, start, end, _, _, _ in found_items:
                    if item_type == "phrase" and start <= match.start() and match.end() <= end:
                        is_part_of_phrase = True
                        break
                
                if not is_part_of_phrase:
                    found_items.append(("word", word, match.start(), match.end(), frequency, category, source))
        
        # Sort found items by position (start index) in reverse order
        # This way we can replace from end to beginning without affecting positions
        found_items.sort(key=lambda x: x[2], reverse=True)
        
        # Replace matches with highlighted versions
        for item_type, item_text, start, end, frequency, category, source in found_items:
            original_text = text[start:end]
            # highlighted = f"**{original_text}**"  # Bold for Markdown
            # highlighted = f"<span style='color:red;font-weight:bold;'>{original_text}</span>"  # Red bold for HTML
            # And then make sure to use st.markdown(highlighted_text, unsafe_allow_html=True) when displaying the text in Streamlit.
            highlighted = f"<span style='color:red'>{original_text}</span>"  # Red bold for Streamlit Markdown
            highlighted_text = highlighted_text[:start] + highlighted + highlighted_text[end:]
        
        return highlighted_text, found_items

    def analyze_text(self, text):
        """Analyze the text and return statistics"""
        highlighted_text, found_items = self.highlight_text(text)
        # print(f"Found items: {found_items}")
        
        # Count word frequencies
        word_counts = Counter()
        phrase_counts = Counter()
        source_counts = Counter()
        category_counts = Counter()
        
        # Track AI words count
        ai_word_count = 0
        
        for item in found_items:
            # print(f"Processing item: {item}")
            item_type, item_text, _, _, frequency, category, source = item
            
            if item_type == "word":
                word_counts[item_text] += 1
                ai_word_count += 1
                # print(f"Added word: {item_text}, current word_counts: {word_counts}")
            else:
                phrase_counts[item_text] += 1
                # print(f"Added phrase: {item_text}, current phrase_counts: {phrase_counts}")
            
            source_counts[source] += 1
            category_counts[category] += 1
        
        # print(f"Final word_counts: {word_counts}")
        # print(f"Final phrase_counts: {phrase_counts}")
        # print(f"Final source_counts: {source_counts}")
        # print(f"Final category_counts: {category_counts}")
        
        # Calculate statistics
        total_words = len(re.findall(r'\b\w+\b', text))
        # print(f"Total words in text: {total_words}")
        
        unique_words = len(set(re.findall(r'\b\w+\b', text.lower())))
        # print(f"Unique words in text: {unique_words}")
        
        ai_markers = len(found_items)
        # print(f"AI markers found: {ai_markers}")
        
        # print(f"AI word count: {ai_word_count}")
        
        ai_word_percentage = (ai_word_count / total_words) * 100 if total_words > 0 else 0
        # print(f"AI word percentage calculation: ({ai_word_count} / {total_words}) * 100 = {ai_word_percentage}%")
        
        # Prepare results
        results = {
            "total_words": total_words,
            "unique_words": unique_words,
            "ai_markers": ai_markers,
            "ai_word_percentage": ai_word_percentage,
            "word_counts": word_counts,
            "phrase_counts": phrase_counts,
            "source_counts": source_counts,
            "category_counts": category_counts
        }
        
        # print(f"Final results dictionary: {results}")
        
        return results
    
    def export_words_to_csv(self, file_path):
        """Export words to a CSV file"""
        words = self.get_all_words()
        df = pd.DataFrame(words, columns=['word', 'frequency', 'category', 'source'])
        df.to_csv(file_path, index=False)
        
    def export_phrases_to_csv(self, file_path):
        """Export phrases to a CSV file"""
        phrases = self.get_all_phrases()
        df = pd.DataFrame(phrases, columns=['phrase', 'frequency', 'category', 'source'])
        df.to_csv(file_path, index=False)
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()


def create_streamlit_app():
    """Create a Streamlit app for the AI Word Highlighter"""
    st.title("AI Word and Phrase Highlighter")
    st.markdown("This tool helps identify common words and phrases used in AI-generated content.")
    
    # Initialize the highlighter
    highlighter = AIWordHighlighter()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Highlight Text", "Manage Words & Phrases", "About"])
    
    with tab1:
        st.header("Text Analysis")
        
        # Input text area
        input_text = st.text_area("Enter text to analyze", height=200)
        
        if st.button("Analyze Text"):
            if not input_text:
                st.warning("Please enter some text to analyze.")
            else:
                # Highlight and analyze text
                highlighted_text, found_items = highlighter.highlight_text(input_text)
                results = highlighter.analyze_text(input_text)
                
                # Display results
                st.subheader("Highlighted Text")
                # st.markdown(highlighted_text)
                st.markdown(highlighted_text, unsafe_allow_html=True)

                
                st.subheader("Analysis Results")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Words", results["total_words"])
                col2.metric("Unique Words", results["unique_words"])
                col3.metric("AI Markers Found", results["ai_markers"])
                col4.metric("AI Word %", f"{results['ai_word_percentage']:.2f}%")
                
                # Display top detected words and phrases
                if results["word_counts"]:
                    st.subheader("Top AI Words Detected")
                    top_words = dict(results["word_counts"].most_common(10))
                    
                    # Create DataFrame for the table
                    word_df = pd.DataFrame({
                        "Word": list(top_words.keys()),
                        "Count": list(top_words.values())
                    })
                    st.table(word_df)
                    
                    # Bar chart for word counts
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x=list(top_words.keys()), y=list(top_words.values()), ax=ax)
                    plt.title("Top AI Words Detected")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig)
                
                if results["phrase_counts"]:
                    st.subheader("Top AI Phrases Detected")
                    top_phrases = dict(results["phrase_counts"].most_common(10))
                    
                    # Create DataFrame for the table
                    phrase_df = pd.DataFrame({
                        "Phrase": list(top_phrases.keys()),
                        "Count": list(top_phrases.values())
                    })
                    st.table(phrase_df)
                    
                    # Bar chart for phrase counts
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x=list(top_phrases.keys()), y=list(top_phrases.values()), ax=ax)
                    plt.title("Top AI Phrases Detected")
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig)
                
                if not results["word_counts"] and not results["phrase_counts"]:
                    st.info("No AI markers were detected in the text.")
    
    with tab2:
        st.header("Manage AI Words and Phrases")
        
        # Display words and phrases
        st.subheader("AI Words in Database")
        words = highlighter.get_all_words()
        if words:
            word_df = pd.DataFrame(words, columns=["Word", "Frequency", "Category", "Source"])
            st.dataframe(word_df)
        else:
            st.info("No AI words in the database.")
        
        st.subheader("AI Phrases in Database")
        phrases = highlighter.get_all_phrases()
        if phrases:
            phrase_df = pd.DataFrame(phrases, columns=["Phrase", "Frequency", "Category", "Source"])
            st.dataframe(phrase_df)
        else:
            st.info("No AI phrases in the database.")
        
        # Add new word or phrase
        st.subheader("Add New Word/Phrase")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add Word")
            new_word = st.text_input("New Word")
            word_freq = st.slider("Word Frequency", 1, 10, 5, key="word_freq")
            word_category = st.text_input("Category", "general", key="word_cat")
            word_source = st.text_input("Source", "user", key="word_source")
            
            if st.button("Add Word"):
                if new_word:
                    highlighter.add_word(new_word, word_freq, word_category, word_source)
                    st.success(f"Added word: {new_word}")
                    st.experimental_rerun()
                else:
                    st.warning("Please enter a word.")
        
        with col2:
            st.markdown("#### Add Phrase")
            new_phrase = st.text_input("New Phrase")
            phrase_freq = st.slider("Phrase Frequency", 1, 10, 5, key="phrase_freq")
            phrase_category = st.text_input("Category", "general", key="phrase_cat")
            phrase_source = st.text_input("Source", "user", key="phrase_source")
            
            if st.button("Add Phrase"):
                if new_phrase:
                    highlighter.add_phrase(new_phrase, phrase_freq, phrase_category, phrase_source)
                    st.success(f"Added phrase: {new_phrase}")
                    st.experimental_rerun()
                else:
                    st.warning("Please enter a phrase.")
        
        # Import/Export
        st.subheader("Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Import")
            import_type = st.selectbox("Import Type", ["Words", "Phrases"])
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            
            if st.button("Import"):
                if uploaded_file is not None:
                    if import_type == "Words":
                        success, message = highlighter.import_words_from_csv(uploaded_file)
                    else:
                        success, message = highlighter.import_phrases_from_csv(uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please upload a CSV file.")
        
        with col2:
            st.markdown("#### Export")
            export_type = st.selectbox("Export Type", ["Words", "Phrases"])
            export_filename = st.text_input("Filename", "ai_words.csv" if export_type == "Words" else "ai_phrases.csv")
            
            if st.button("Export"):
                if export_type == "Words":
                    highlighter.export_words_to_csv(export_filename)
                else:
                    highlighter.export_phrases_to_csv(export_filename)
                st.success(f"Exported to {export_filename}")
    
    with tab3:
        st.header("About this Tool")
        st.markdown("""
        The AI Word and Phrase Highlighter is designed to detect common words and phrases frequently used in AI-generated content.
        
        ### How it works
        
        1. The tool maintains a database of words and phrases commonly used by AI systems like ChatGPT, Claude, and others.
        2. When you input text, it scans for these markers and highlights them.
        3. It also provides statistics on the frequency of these markers in your text.
        
        ### Use cases
        
        - Writers can use this to reduce AI-like patterns in their writing
        - Content reviewers can quickly identify potential AI-generated content
        - Students and educators can ensure original work
        - SEO specialists can improve content to avoid AI detection penalties
        
        ### Sources
        
        The default database includes words and phrases identified by various AI detection tools including:
        
        - ZeroGPT
        - GPTZero
        - Originality.ai
        - And various research studies on AI-generated text patterns
        
        You can extend the database with your own observations or from other sources.
        """)

    # Close the database connection when done
    highlighter.close()

# Run the Streamlit app if this script is run directly
if __name__ == "__main__":
    create_streamlit_app()
