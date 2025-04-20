import re
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import argparse
import sys
import os
import json
from datetime import datetime

class AIContentAnalyzer:
    """
    A comprehensive tool for analyzing text to detect AI-generated content
    patterns and provide SEO optimization suggestions.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize the AI Content Analyzer.
        
        Args:
            db_path (str): Path to the SQLite database (default: ai_words.db in current directory)
        """
        if db_path is None:
            # Use a default database in the current directory
            db_path = os.path.join(os.getcwd(), "ai_words.db")
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect_database()
    
    def connect_database(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.setup_database()
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def setup_database(self):
        """Create necessary tables if they don't exist"""
        # Create table for AI words
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_words (
            id INTEGER PRIMARY KEY,
            word TEXT UNIQUE NOT NULL,
            frequency INTEGER DEFAULT 1,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'default'
        )
        ''')
        
        # Create table for AI phrases
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_phrases (
            id INTEGER PRIMARY KEY,
            phrase TEXT UNIQUE NOT NULL,
            frequency INTEGER DEFAULT 1,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'default'
        )
        ''')
        
        # Create indices for faster lookups
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON ai_words(word)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrase ON ai_phrases(phrase)')
        
        # Create table for analysis history
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY,
            text_hash TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_words INTEGER,
            ai_markers INTEGER,
            ai_percentage REAL,
            results TEXT  -- JSON string of analysis results
        )
        ''')
        
        self.conn.commit()
        
        # Check if we need to populate default data
        self.cursor.execute('SELECT COUNT(*) FROM ai_words')
        word_count = self.cursor.fetchone()[0]
        
        if word_count == 0:
            self.populate_default_data()
    
    def populate_default_data(self):
        """Populate the database with default AI words and phrases"""
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
            ("in this article", 10, "introduction", "ZeroGPT"),
            ("delve into", 9, "verb phrase", "GPTZero"),
            ("it's important to note", 9, "transition", "ZeroGPT"),
            ("on the other hand", 8, "transition", "ZeroGPT"),
            ("in the realm of", 8, "preposition", "ZeroGPT"),
            ("a wide range of", 8, "description", "ZeroGPT"),
            ("it is worth mentioning", 7, "transition", "ZeroGPT"),
            ("plays a crucial role", 7, "emphasis", "ZeroGPT"),
            ("in conclusion", 7, "conclusion", "ZeroGPT"),
            ("in summary", 7, "conclusion", "ZeroGPT"),
            ("to summarize", 6, "conclusion", "ZeroGPT"),
            ("as we have seen", 6, "conclusion", "ZeroGPT"),
            ("moving forward", 6, "transition", "ZeroGPT"),
            ("when it comes to", 6, "transition", "ZeroGPT"),
            ("as mentioned earlier", 6, "reference", "ZeroGPT"),
            ("in the context of", 6, "context", "ZeroGPT"),
            ("it goes without saying", 5, "emphasis", "ZeroGPT"),
            ("it is essential to", 5, "emphasis", "ZeroGPT"),
            ("needless to say", 5, "emphasis", "ZeroGPT"),
            ("it's worth noting that", 5, "transition", "ZeroGPT"),
            ("a plethora of", 9, "description", "GPTZero"),
            ("treasure trove of", 8, "description", "GPTZero"),
            ("in today's fast-paced world", 8, "context", "GPTZero"),
            ("in the digital age", 7, "context", "GPTZero"),
            ("embark on a journey", 7, "verb phrase", "GPTZero"),
            ("unlock the potential", 7, "verb phrase", "GPTZero"),
            ("harness the power", 6, "verb phrase", "GPTZero"),
            ("foster a culture of", 6, "verb phrase", "GPTZero"),
            ("curated collection", 6, "description", "GPTZero"),
            ("seamless integration", 6, "description", "GPTZero"),
            ("rich tapestry", 5, "description", "GPTZero"),
            ("paradigm shift", 5, "description", "GPTZero"),
            ("as an AI language model", 10, "disclaimer", "Various"),
            ("I don't have access to", 9, "limitation", "Various"),
            ("as of my last update", 9, "limitation", "Various"),
            ("I cannot provide", 8, "limitation", "Various"),
            ("I cannot browse the internet", 8, "limitation", "Various"),
        ]
        
        # Insert words
        self.cursor.executemany(
            'INSERT OR IGNORE INTO ai_words (word, frequency, category, source) VALUES (?, ?, ?, ?)',
            default_words
        )
        
        # Insert phrases
        self.cursor.executemany(
            'INSERT OR IGNORE INTO ai_phrases (phrase, frequency, category, source) VALUES (?, ?, ?, ?)',
            default_phrases
        )
        
        self.conn.commit()
        print(f"Added {len(default_words)} words and {len(default_phrases)} phrases to the database")
    
    def add_word(self, word, frequency=1, category="general", source="user"):
        """Add a new AI word to the database"""
        try:
            self.cursor.execute(
                'INSERT OR REPLACE INTO ai_words (word, frequency, category, source) VALUES (?, ?, ?, ?)',
                (word.lower(), frequency, category, source)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False

    def add_phrase(self, phrase, frequency=1, category="general", source="user"):
        """Add a new AI phrase to the database"""
        try:
            self.cursor.execute(
                'INSERT OR REPLACE INTO ai_phrases (phrase, frequency, category, source) VALUES (?, ?, ?, ?)',
                (phrase.lower(), frequency, category, source)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding phrase: {e}")
            return False

    def get_all_words(self, category=None, source=None, min_frequency=None):
        """Get all AI words with optional filtering"""
        query = 'SELECT word, frequency, category, source FROM ai_words'
        params = []
        
        conditions = []
        if category:
            conditions.append('category = ?')
            params.append(category)
        if source:
            conditions.append('source = ?')
            params.append(source)
        if min_frequency:
            conditions.append('frequency >= ?')
            params.append(min_frequency)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY frequency DESC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_all_phrases(self, category=None, source=None, min_frequency=None):
        """Get all AI phrases with optional filtering"""
        query = 'SELECT phrase, frequency, category, source FROM ai_phrases'
        params = []
        
        conditions = []
        if category:
            conditions.append('category = ?')
            params.append(category)
        if source:
            conditions.append('source = ?')
            params.append(source)
        if min_frequency:
            conditions.append('frequency >= ?')
            params.append(min_frequency)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY frequency DESC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def highlight_text(self, text, output_format='html', highlight_threshold=1):
        """
        Highlight AI words and phrases in the given text.
        
        Args:
            text (str): The text to analyze
            output_format (str): Output format - 'html', 'markdown', or 'plain'
            highlight_threshold (int): Minimum frequency to highlight (1-10)
            
        Returns:
            tuple: (highlighted text, list of found AI markers)
        """
        # Get all words and phrases
        words = self.get_all_words(min_frequency=highlight_threshold)
        phrases = self.get_all_phrases(min_frequency=highlight_threshold)
        
        # Create a copy of the text for highlighting
        highlighted_text = text
        found_items = []
        
        # First detect phrases (to avoid highlighting parts of phrases as individual words)
        for phrase, frequency, category, source in phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                found_items.append({
                    "type": "phrase",
                    "text": phrase,
                    "original_text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "frequency": frequency,
                    "category": category,
                    "source": source
                })
        
        # Then detect individual words
        for word, frequency, category, source in words:
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Check if this word is part of a detected phrase
                is_part_of_phrase = False
                for item in found_items:
                    if item["type"] == "phrase" and item["start"] <= match.start() and match.end() <= item["end"]:
                        is_part_of_phrase = True
                        break
                
                if not is_part_of_phrase:
                    found_items.append({
                        "type": "word",
                        "text": word,
                        "original_text": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                        "frequency": frequency,
                        "category": category,
                        "source": source
                    })
        
        # Sort found items by position (start index) in reverse order
        found_items.sort(key=lambda x: x["start"], reverse=True)
        
        # Replace matches with highlighted versions
        for item in found_items:
            original_text = item["original_text"]
            
            if output_format == 'html':
                frequency_class = f"ai-freq-{item['frequency']}"
                highlighted = f'<span class="ai-marker {frequency_class}" title="{item["text"]} ({item["category"]}, freq: {item["frequency"]})">{original_text}</span>'
            elif output_format == 'markdown':
                highlighted = f"**{original_text}**"
            else:  # plain
                highlighted = f"[AI:{original_text}]"
            
            highlighted_text = highlighted_text[:item["start"]] + highlighted + highlighted_text[item["end"]:]
        
        return highlighted_text, found_items

    def analyze_text(self, text, min_frequency=1):
        """
        Analyze text for AI patterns and provide detailed statistics.
        
        Args:
            text (str): The text to analyze
            min_frequency (int): Minimum frequency to consider (1-10)
            
        Returns:
            dict: Analysis results
        """
        # Highlight and find AI markers
        _, found_items = self.highlight_text(text, highlight_threshold=min_frequency)
        
        # Count total words and sentences
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        total_sentences = len(sentences)
        
        # Word frequency analysis
        word_freq = Counter(words)
        
        # AI marker statistics
        word_counts = Counter()
        phrase_counts = Counter()
        category_counts = Counter()
        source_counts = Counter()
        
        for item in found_items:
            if item["type"] == "word":
                word_counts[item["text"]] += 1
            else:
                phrase_counts[item["text"]] += 1
            
            category_counts[item["category"]] += 1
            source_counts[item["source"]] += 1
        
        # AI detection score
        ai_word_percentage = (len([i for i in found_items if i["type"] == "word"]) / total_words) * 100 if total_words > 0 else 0
        ai_phrase_percentage = (len([i for i in found_items if i["type"] == "phrase"]) / total_sentences) * 100 if total_sentences > 0 else 0
        
        # Calculate weighted AI score based on frequency of found markers
        weighted_score = 0
        for item in found_items:
            weighted_score += item["frequency"]
        
        weighted_ai_score = (weighted_score / (total_words + total_sentences)) * 10 if (total_words + total_sentences) > 0 else 0
        
        # Readability statistics
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        
        # Prepare results
        results = {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "unique_words": len(set(word.lower() for word in words)),
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "ai_markers": len(found_items),
            "ai_word_markers": len([i for i in found_items if i["type"] == "word"]),
            "ai_phrase_markers": len([i for i in found_items if i["type"] == "phrase"]),
            "ai_word_percentage": ai_word_percentage,
            "ai_phrase_percentage": ai_phrase_percentage,
            "weighted_ai_score": weighted_ai_score,
            "word_counts": dict(word_counts),
            "phrase_counts": dict(phrase_counts),
            "category_counts": dict(category_counts),
            "source_counts": dict(source_counts),
            "found_items": found_items
        }
        
        # Save analysis to history
        self.save_analysis(text, results)
        
        return results
    
    def save_analysis(self, text, results):
        """Save analysis results to the database"""
        import hashlib
        
        # Create a hash of the text to use as an identifier
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert results to JSON
        results_json = json.dumps({
            k: v for k, v in results.items() if k != 'found_items'
        })
        
        # Current timestamp
        timestamp = datetime.now().isoformat()
        
        try:
            self.cursor.execute(
                'INSERT INTO analysis_history (text_hash, timestamp, total_words, ai_markers, ai_percentage, results) VALUES (?, ?, ?, ?, ?, ?)',
                (
                    text_hash,
                    timestamp,
                    results["total_words"],
                    results["ai_markers"],
                    results["ai_word_percentage"],
                    results_json
                )
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error saving analysis: {e}")

    def get_analysis_history(self, limit=10):
        """Get recent analysis history"""
        self.cursor.execute(
            'SELECT timestamp, total_words, ai_markers, ai_percentage, results FROM analysis_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        return self.cursor.fetchall()

    def generate_suggestions(self, analysis_results):
        """
        Generate SEO and humanization suggestions based on analysis results.
        
        Args:
            analysis_results (dict): The analysis results from analyze_text()
            
        Returns:
            dict: Suggestions and improvements
        """
        suggestions = {
            "general": [],
            "word_replacements": {},
            "phrase_replacements": {},
            "structure": [],
            "seo": []
        }
        
        # General suggestions
        ai_score = analysis_results["weighted_ai_score"]
        
        if ai_score > 8:
            suggestions["general"].append("Text has a very high AI signature. Consider significant rewrites.")
        elif ai_score > 5:
            suggestions["general"].append("Text has a moderate AI signature. Some edits recommended.")
        else:
            suggestions["general"].append("Text has a low AI signature. Only minor adjustments needed.")
        
        # Word replacement suggestions
        for word, count in analysis_results["word_counts"].items():
            if word in self.get_word_replacements():
                suggestions["word_replacements"][word] = self.get_word_replacements()[word]
        
        # Phrase replacement suggestions
        for phrase, count in analysis_results["phrase_counts"].items():
            if phrase in self.get_phrase_replacements():
                suggestions["phrase_replacements"][phrase] = self.get_phrase_replacements()[phrase]
        
        # Structure suggestions
        avg_sentence_length = analysis_results["avg_sentence_length"]
        if avg_sentence_length > 25:
            suggestions["structure"].append("Sentences are quite long. Consider breaking them up for better readability.")
        
        # SEO suggestions
        if analysis_results["ai_word_percentage"] > 20:
            suggestions["seo"].append("High AI word percentage might impact SEO. Revise the most commonly flagged words.")
        
        return suggestions
    
    def get_word_replacements(self):
        """Dictionary of common AI words and suggested replacements"""
        return {
            "delve": ["explore", "examine", "investigate", "look into"],
            "whilst": ["while", "as", "during", "when"],
            "furthermore": ["also", "besides", "plus", "in addition"],
            "utilize": ["use", "apply", "employ"],
            "leverage": ["use", "apply", "employ", "harness"],
            "robust": ["strong", "solid", "durable", "powerful"],
            "optimal": ["best", "ideal", "perfect", "prime"],
            "essentially": ["basically", "mainly", "primarily", "at heart"],
            "ultimately": ["finally", "in the end", "eventually", "in conclusion"],
            "myriad": ["many", "numerous", "countless", "various"],
            "seamless": ["smooth", "flawless", "perfect", "uninterrupted"],
            "plethora": ["abundance", "wealth", "excess", "plenty"],
            "harness": ["use", "utilize", "channel", "direct"],
            "elevate": ["raise", "lift", "boost", "improve"],
            "tapestry": ["mixture", "blend", "fabric", "collection"],
            "captivate": ["engage", "entrance", "fascinate", "charm"],
            "testament": ["proof", "evidence", "example", "demonstration"]
        }
    
    def get_phrase_replacements(self):
        """Dictionary of common AI phrases and suggested replacements"""
        return {
            "in this article": ["here", "in these pages", "below", "in what follows"],
            "delve into": ["explore", "examine", "look at", "investigate"],
            "it's important to note": ["note that", "remember", "keep in mind", "be aware"],
            "on the other hand": ["however", "conversely", "in contrast", "alternatively"],
            "in the realm of": ["in", "within", "concerning", "regarding"],
            "a wide range of": ["many", "various", "diverse", "different"],
            "it is worth mentioning": ["notably", "interestingly", "remarkably"],
            "plays a crucial role": ["is important for", "is vital to", "is key to"],
            "in conclusion": ["to wrap up", "finally", "to sum up", "in closing"],
            "in summary": ["in short", "to recap", "in brief", "to summarize briefly"],
            "when it comes to": ["regarding", "about", "concerning", "on the topic of"],
            "as mentioned earlier": ["as I said", "as noted", "as stated above"]
        }
    
    def export_analysis_to_html(self, text, analysis_results, filename=None):
        """
        Export text analysis to an HTML file with highlighting.
        
        Args:
            text (str): The original text
            analysis_results (dict): Analysis results
            filename (str): Output filename (default: analysis_YYYY-MM-DD.html)
            
        Returns:
            str: Path to the HTML file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"analysis_{timestamp}.html"
        
        # Generate highlighted text
        highlighted_text, _ = self.highlight_text(text, output_format='html')
        
        # Create HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Content Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .text-container {{ margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .stats-container {{ display: flex; flex-wrap: wrap; margin-bottom: 20px; }}
                .stat-box {{ background-color: #f5f5f5; border-radius: 5px; padding: 10px; margin-right: 10px; margin-bottom: 10px; }}
                .ai-marker {{ background-color: #FFECB3; border-radius: 3px; padding: 0 2px; }}
                .ai-freq-10 {{ background-color: #FFCCBC; }}
                .ai-freq-9 {{ background-color: #FFD8B2; }}
                .ai-freq-8 {{ background-color: #FFE3B2; }}
                .ai-freq-7 {{ background-color: #FFECB3; }}
                .ai-freq-6 {{ background-color: #FFF59D; }}
                .ai-freq-5 {{ background-color: #FFF9C4; }}
                .ai-freq-4 {{ background-color: #FFFDE7; }}
                .ai-freq-3 {{ background-color: #E8F5E9; }}
                .ai-freq-2 {{ background-color: #E3F2FD; }}
                .ai-freq-1 {{ background-color: #EDE7F6; }}
                .suggestions {{ margin-top: 20px; padding: 15px; background-color: #e8f5e9; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 15px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h1, h2, h3 {{ color: #333; }}
                .legend {{ display: flex; flex-wrap: wrap; margin-bottom: 10px; }}
                .legend-item {{ display: flex; align-items: center; margin-right: 15px; margin-bottom: 5px; }}
                .legend-color {{ width: 20px; height: 20px; margin-right: 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Content Analysis</h1>
                
                <div class="stats-container">
                    <div class="stat-box">
                        <h3>Word Count</h3>
                        <p>{analysis_results["total_words"]}</p>
                    </div>
                    <div class="stat-box">
                        <h3>AI Markers</h3>
                        <p>{analysis_results["ai_markers"]}</p>
                    </div>
                    <div class="stat-box">
                        <h3>AI Word %</h3>
                        <p>{analysis_results["ai_word_percentage"]:.2f}%</p>
                    </div>
                    <div class="stat-box">
                        <h3>AI Score</h3>
                        <p>{analysis_results["weighted_ai_score"]:.2f}/10</p>
                    </div>
                </div>
                
                <h2>Highlighted Text</h2>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color ai-freq-10"></div>
                        <span>Very High (9-10)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color ai-freq-7"></div>
                        <span>High (7-8)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color ai-freq-5"></div>
                        <span>Medium (5-6)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color ai-freq-3"></div>
                        <span>Low (3-4)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color ai-freq-1"></div>
                        <span>Very Low (1-2)</span>
                    </div>
                </div>
                <div class="text-container">
                    {highlighted_text}
                </div>
                
                <h2>AI Words Detected</h2>
                <table>
                    <tr>
                        <th>Word</th>
                        <th>Count</th>
                        <th>Frequency Score</th>
                        <th>Category</th>
                    </tr>
        """
        
        # Add word rows
        for item in sorted(analysis_results["found_items"], key=lambda x: x["frequency"], reverse=True):
            if item["type"] == "word":
                html += f"""
                    <tr>
                        <td>{item["text"]}</td>
                        <td>{analysis_results["word_counts"][item["text"]]}</td>
                        <td>{item["frequency"]}</td>
                        <td>{item["category"]}</td>
                    </tr>
                """
        
        html += """
                </table>
                
                <h2>AI Phrases Detected</h2>
                <table>
                    <tr>
                        <th>Phrase</th>
                        <th>Count</th>
                        <th>Frequency Score</th>
                        <th>Category</th>
                    </tr>
        """
        
        # Add phrase rows
        for item in sorted(analysis_results["found_items"], key=lambda x: x["frequency"], reverse=True):
            if item["type"] == "phrase":
                html += f"""
                    <tr>
                        <td>{item["text"]}</td>
                        <td>{analysis_results["phrase_counts"].get(item["text"], 0)}</td>
                        <td>{item["frequency"]}</td>
                        <td>{item["category"]}</td>
                    </tr>
                """
        
        # Generate suggestions
        suggestions = self.generate_suggestions(analysis_results)
        
        html += """
                </table>
                
                <h2>Suggestions</h2>
                <div class="suggestions">
        """
        
        # Add general suggestions
        if suggestions["general"]:
            html += "<h3>General</h3><ul>"
            for suggestion in suggestions["general"]:
                html += f"<li>{suggestion}</li>"
            html += "</ul>"
        
        # Add SEO suggestions
        if suggestions["seo"]:
            html += "<h3>SEO</h3><ul>"
            for suggestion in suggestions["seo"]:
                html += f"<li>{suggestion}</li>"
            html += "</ul>"
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename

    def export_analysis_to_csv(self, analysis_results, filename=None):
        """
        Export analysis results to a CSV file.
        
        Args:
            analysis_results (dict): Analysis results
            filename (str): Output filename (default: analysis_YYYY-MM-DD.csv)
            
        Returns:
            str: Path to the CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"analysis_{timestamp}.csv"
        
        # Prepare data for CSV
        data = {
            "Metric": [
                "Total Words",
                "Total Sentences",
                "Unique Words",
                "Average Word Length",
                "Average Sentence Length",
                "AI Markers",
                "AI Word Markers",
                "AI Phrase Markers",
                "AI Word Percentage",
                "AI Phrase Percentage",
                "Weighted AI Score"
            ],
            "Value": [
                analysis_results["total_words"],
                analysis_results["total_sentences"],
                analysis_results["unique_words"],
                analysis_results["avg_word_length"],
                analysis_results["avg_sentence_length"],
                analysis_results["ai_markers"],
                analysis_results["ai_word_markers"],
                analysis_results["ai_phrase_markers"],
                analysis_results["ai_word_percentage"],
                analysis_results["ai_phrase_percentage"],
                analysis_results["weighted_ai_score"]
            ]
        }
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        
        # Additional CSVs for detailed data
        word_counts_df = pd.DataFrame([
            {"Word": word, "Count": count}
            for word, count in analysis_results["word_counts"].items()
        ])
        if not word_counts_df.empty:
            word_counts_filename = filename.replace('.csv', '_word_counts.csv')
            word_counts_df.to_csv(word_counts_filename, index=False)
        
        phrase_counts_df = pd.DataFrame([
            {"Phrase": phrase, "Count": count}
            for phrase, count in analysis_results["phrase_counts"].items()
        ])
        if not phrase_counts_df.empty:
            phrase_counts_filename = filename.replace('.csv', '_phrase_counts.csv')
            phrase_counts_df.to_csv(phrase_counts_filename, index=False)
        
        return filename

    def visualize_analysis(self, analysis_results, output_dir=None):
        """
        Create visualization charts for the analysis results.
        
        Args:
            analysis_results (dict): Analysis results
            output_dir (str): Directory to save visualizations (default: current directory)
            
        Returns:
            list: Paths to visualization files
        """
        if output_dir is None:
            output_dir = os.getcwd()
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        visualization_files = []
        
        # Set style for all plots
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 1. AI Score Gauge Chart
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Create a gauge chart using a half donut
        ai_score = analysis_results["weighted_ai_score"]
        max_score = 10
        
        # Colors based on score
        if ai_score < 3:
            color = 'green'
        elif ai_score < 7:
            color = 'orange'
        else:
            color = 'red'
        
        # Plot the gauge
        ax.pie(
            [ai_score, max_score - ai_score],
            colors=[color, '#f0f0f0'],
            startangle=90,
            counterclock=False,
            wedgeprops={'width': 0.4}
        )
        
        # Add a circle at the center to make it look like a gauge
        centre_circle = plt.Circle((0, 0), 0.25, fc='white')
        ax.add_patch(centre_circle)
        
        # Add text
        ax.text(0, 0, f"{ai_score:.1f}", ha='center', va='center', fontsize=36)
        ax.text(0, -0.15, "AI Score", ha='center', va='center', fontsize=16)
        
        # Add score labels
        ax.text(-0.8, -0.1, "Low", fontsize=12)
        ax.text(0, 0.8, "Medium", fontsize=12)
        ax.text(0.8, -0.1, "High", fontsize=12)
        
        ax.set_title("AI Content Detection Score", fontsize=18, pad=20)
        ax.axis('equal')
        
        gauge_chart_path = os.path.join(output_dir, f"ai_score_gauge_{timestamp}.png")
        plt.savefig(gauge_chart_path, bbox_inches='tight')
        plt.close()
        visualization_files.append(gauge_chart_path)
        
        # 2. Word and Phrase Counts Bar Chart
        if analysis_results["word_counts"] or analysis_results["phrase_counts"]:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
            
            # Word counts
            if analysis_results["word_counts"]:
                top_words = dict(sorted(analysis_results["word_counts"].items(), key=lambda x: x[1], reverse=True)[:10])
                
                sns.barplot(x=list(top_words.values()), y=list(top_words.keys()), palette="Blues_d", ax=ax1)
                ax1.set_title("Top AI Words Detected", fontsize=14)
                ax1.set_xlabel("Count", fontsize=12)
                ax1.set_ylabel("Word", fontsize=12)
            
            # Phrase counts
            if analysis_results["phrase_counts"]:
                top_phrases = dict(sorted(analysis_results["phrase_counts"].items(), key=lambda x: x[1], reverse=True)[:10])
                
                sns.barplot(x=list(top_phrases.values()), y=list(top_phrases.keys()), palette="Greens_d", ax=ax2)
                ax2.set_title("Top AI Phrases Detected", fontsize=14)
                ax2.set_xlabel("Count", fontsize=12)
                ax2.set_ylabel("Phrase", fontsize=12)
            
            plt.tight_layout()
            
            counts_chart_path = os.path.join(output_dir, f"ai_word_phrase_counts_{timestamp}.png")
            plt.savefig(counts_chart_path, bbox_inches='tight')
            plt.close()
            visualization_files.append(counts_chart_path)
        
        # 3. Category Distribution Pie Chart
        if analysis_results["category_counts"]:
            fig, ax = plt.subplots(figsize=(8, 8))
            
            categories = list(analysis_results["category_counts"].keys())
            counts = list(analysis_results["category_counts"].values())
            
            ax.pie(
                counts,
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.Paired(np.linspace(0, 1, len(categories)))
            )
            ax.axis('equal')
            
            ax.set_title("AI Marker Categories", fontsize=16)
            
            categories_chart_path = os.path.join(output_dir, f"ai_categories_{timestamp}.png")
            plt.savefig(categories_chart_path, bbox_inches='tight')
            plt.close()
            visualization_files.append(categories_chart_path)
        
        return visualization_files

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None


def main():
    """Main function to run the AI Content Analyzer from the command line"""
    parser = argparse.ArgumentParser(description='AI Content Analyzer - Detect and analyze AI-generated content patterns')
    
    # Input options
    parser.add_argument('--text', help='Text content to analyze')
    parser.add_argument('--file', help='Path to a text file to analyze')
    
    # Output options
    parser.add_argument('--output', help='Output directory for results', default='.')
    parser.add_argument('--format', choices=['text', 'csv', 'html', 'all'], default='text', help='Output format')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization charts')
    
    # Analysis options
    parser.add_argument('--min-freq', type=int, default=1, help='Minimum frequency threshold (1-10)')
    parser.add_argument('--db', help='Path to custom database file')
    
    # Database management options
    parser.add_argument('--add-word', help='Add a new AI word to the database')
    parser.add_argument('--add-phrase', help='Add a new AI phrase to the database')
    parser.add_argument('--frequency', type=int, default=5, help='Frequency for new word/phrase (1-10)')
    parser.add_argument('--category', default='general', help='Category for new word/phrase')
    parser.add_argument('--source', default='user', help='Source for new word/phrase')
    
    args = parser.parse_args()
    
    # Initialize the analyzer
    analyzer = AIContentAnalyzer(db_path=args.db)
    
    # Handle database management commands
    if args.add_word:
        success = analyzer.add_word(args.add_word, args.frequency, args.category, args.source)
        if success:
            print(f"Word '{args.add_word}' added to database")
        else:
            print(f"Failed to add word '{args.add_word}'")
        return
    
    if args.add_phrase:
        success = analyzer.add_phrase(args.add_phrase, args.frequency, args.category, args.source)
        if success:
            print(f"Phrase '{args.add_phrase}' added to database")
        else:
            print(f"Failed to add phrase '{args.add_phrase}'")
        return
    
    # Get text to analyze
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
    else:
        print("Please provide text to analyze using --text or --file")
        return
    
    # Analyze the text
    results = analyzer.analyze_text(text, min_frequency=args.min_freq)
    
    # Generate output based on format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    if args.format == 'text' or args.format == 'all':
        # Print analysis to console
        print("\n" + "="*50)
        print(" "*15 + "AI CONTENT ANALYSIS")
        print("="*50)
        
        print(f"\nTotal Words: {results['total_words']}")
        print(f"Total Sentences: {results['total_sentences']}")
        print(f"Unique Words: {results['unique_words']}")
        print(f"AI Markers Found: {results['ai_markers']}")
        print(f"AI Word Percentage: {results['ai_word_percentage']:.2f}%")
        print(f"AI Phrase Percentage: {results['ai_phrase_percentage']:.2f}%")
        print(f"Weighted AI Score: {results['weighted_ai_score']:.2f}/10")
        
        if results['word_counts']:
            print("\nTop AI Words Detected:")
            for word, count in sorted(results['word_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {word}: {count}")
        
        if results['phrase_counts']:
            print("\nTop AI Phrases Detected:")
            for phrase, count in sorted(results['phrase_counts'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {phrase}: {count}")
        
        # Generate and print suggestions
        suggestions = analyzer.generate_suggestions(results)
        
        print("\nSuggestions:")
        
        if suggestions['general']:
            print("\nGeneral:")
            for suggestion in suggestions['general']:
                print(f"  - {suggestion}")
        
        if suggestions['word_replacements']:
            print("\nWord Replacements:")
            for word, replacements in suggestions['word_replacements'].items():
                print(f"  - {word} → {', '.join(replacements)}")
        
        if suggestions['phrase_replacements']:
            print("\nPhrase Replacements:")
            for phrase, replacements in suggestions['phrase_replacements'].items():
                print(f"  - {phrase} → {', '.join(replacements)}")
        
        # Also save to a text file
        output_file = os.path.join(args.output, f"analysis_{timestamp}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("AI CONTENT ANALYSIS\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Total Words: {results['total_words']}\n")
            f.write(f"Total Sentences: {results['total_sentences']}\n")
            f.write(f"Unique Words: {results['unique_words']}\n")
            f.write(f"AI Markers Found: {results['ai_markers']}\n")
            f.write(f"AI Word Percentage: {results['ai_word_percentage']:.2f}%\n")
            f.write(f"AI Phrase Percentage: {results['ai_phrase_percentage']:.2f}%\n")
            f.write(f"Weighted AI Score: {results['weighted_ai_score']:.2f}/10\n\n")
            
            if results['word_counts']:
                f.write("Top AI Words Detected:\n")
                for word, count in sorted(results['word_counts'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  - {word}: {count}\n")
                f.write("\n")
            
            if results['phrase_counts']:
                f.write("Top AI Phrases Detected:\n")
                for phrase, count in sorted(results['phrase_counts'].items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  - {phrase}: {count}\n")
                f.write("\n")
            
            f.write("Suggestions:\n")
            
            if suggestions['general']:
                f.write("\nGeneral:\n")
                for suggestion in suggestions['general']:
                    f.write(f"  - {suggestion}\n")
            
            if suggestions['word_replacements']:
                f.write("\nWord Replacements:\n")
                for word, replacements in suggestions['word_replacements'].items():
                    f.write(f"  - {word} → {', '.join(replacements)}\n")
            
            if suggestions['phrase_replacements']:
                f.write("\nPhrase Replacements:\n")
                for phrase, replacements in suggestions['phrase_replacements'].items():
                    f.write(f"  - {phrase} → {', '.join(replacements)}\n")
    
    if args.format == 'csv' or args.format == 'all':
        csv_file = os.path.join(args.output, f"analysis_{timestamp}.csv")
        analyzer.export_analysis_to_csv(results, csv_file)
        print(f"\nCSV output saved to: {csv_file}")
    
    if args.format == 'html' or args.format == 'all':
        html_file = os.path.join(args.output, f"analysis_{timestamp}.html")
        analyzer.export_analysis_to_html(text, results, html_file)
        print(f"\nHTML output saved to: {html_file}")
    
    if args.visualize:
        visualization_files = analyzer.visualize_analysis(results, args.output)
        if visualization_files:
            print("\nVisualizations saved to:")
            for vis_file in visualization_files:
                print(f"  - {vis_file}")
    
    # Clean up
    analyzer.close()


if __name__ == "__main__":
    main()
>"
            html += "</ul>"
        
        # Add word replacements
        if suggestions["word_replacements"]:
            html += "<h3>Word Replacements</h3><ul>"
            for word, replacements in suggestions["word_replacements"].items():
                html += f"<li><strong>{word}</strong> → {', '.join(replacements)}</li>"
            html += "</ul>"
        
        # Add phrase replacements
        if suggestions["phrase_replacements"]:
            html += "<h3>Phrase Replacements</h3><ul>"
            for phrase, replacements in suggestions["phrase_replacements"].items():
                html += f"<li><strong>{phrase}</strong> → {', '.join(replacements)}</li>"
            html += "</ul>"
        
        # Add structure suggestions
        if suggestions["structure"]:
            html += "<h3>Structure</h3><ul>"
            for suggestion in suggestions["structure"]:
                html += f"<li>{suggestion}</li