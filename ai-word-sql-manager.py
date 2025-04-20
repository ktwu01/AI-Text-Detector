import sqlite3
import os
import pandas as pd

class AIWordDatabaseManager:
    """
    A class to manage AI words and phrases in a SQLite database.
    This can be used to create, update, and query a database of words/phrases
    commonly found in AI-generated content.
    """
    
    def __init__(self, db_path="ai_words.db"):
        """
        Initialize the database connection and create tables if they don't exist.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
    
    def setup_database(self):
        """Create the necessary tables if they don't exist"""
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
        
        self.conn.commit()

    def add_word(self, word, frequency=1, category="general", source="user"):
        """
        Add a new word to the database or update if it already exists.
        
        Args:
            word (str): The word to add
            frequency (int): How common this word is in AI text (1-10)
            category (str): Category of the word (verb, noun, adjective, etc.)
            source (str): Source of the word (user, research, etc.)
        
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            self.cursor.execute('''
            INSERT INTO ai_words (word, frequency, category, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(word) DO UPDATE SET
                frequency = excluded.frequency,
                category = excluded.category,
                source = excluded.source
            ''', (word.lower(), frequency, category, source))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False

    def add_phrase(self, phrase, frequency=1, category="general", source="user"):
        """
        Add a new phrase to the database or update if it already exists.
        
        Args:
            phrase (str): The phrase to add
            frequency (int): How common this phrase is in AI text (1-10)
            category (str): Category of the phrase
            source (str): Source of the phrase
        
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            self.cursor.execute('''
            INSERT INTO ai_phrases (phrase, frequency, category, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(phrase) DO UPDATE SET
                frequency = excluded.frequency,
                category = excluded.category,
                source = excluded.source
            ''', (phrase.lower(), frequency, category, source))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding phrase: {e}")
            return False

    def delete_word(self, word):
        """
        Delete a word from the database.
        
        Args:
            word (str): The word to delete
        
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            self.cursor.execute('DELETE FROM ai_words WHERE word = ?', (word.lower(),))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting word: {e}")
            return False

    def delete_phrase(self, phrase):
        """
        Delete a phrase from the database.
        
        Args:
            phrase (str): The phrase to delete
        
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            self.cursor.execute('DELETE FROM ai_phrases WHERE phrase = ?', (phrase.lower(),))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting phrase: {e}")
            return False

    def get_all_words(self, category=None, source=None, min_frequency=None):
        """
        Get all words from the database, with optional filtering.
        
        Args:
            category (str, optional): Filter by category
            source (str, optional): Filter by source
            min_frequency (int, optional): Filter by minimum frequency
        
        Returns:
            list: List of tuples (word, frequency, category, source)
        """
        query = 'SELECT word, frequency, category, source FROM ai_words'
        params = []
        
        # Add filters if provided
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
        
        query += ' ORDER BY frequency DESC, word ASC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_all_phrases(self, category=None, source=None, min_frequency=None):
        """
        Get all phrases from the database, with optional filtering.
        
        Args:
            category (str, optional): Filter by category
            source (str, optional): Filter by source
            min_frequency (int, optional): Filter by minimum frequency
        
        Returns:
            list: List of tuples (phrase, frequency, category, source)
        """
        query = 'SELECT phrase, frequency, category, source FROM ai_phrases'
        params = []
        
        # Add filters if provided
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
        
        query += ' ORDER BY frequency DESC, phrase ASC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_words(self, search_term):
        """
        Search for words containing the given term.
        
        Args:
            search_term (str): Term to search for
        
        Returns:
            list: List of matching words
        """
        self.cursor.execute(
            'SELECT word, frequency, category, source FROM ai_words WHERE word LIKE ? ORDER BY frequency DESC',
            (f'%{search_term}%',)
        )
        return self.cursor.fetchall()

    def search_phrases(self, search_term):
        """
        Search for phrases containing the given term.
        
        Args:
            search_term (str): Term to search for
        
        Returns:
            list: List of matching phrases
        """
        self.cursor.execute(
            'SELECT phrase, frequency, category, source FROM ai_phrases WHERE phrase LIKE ? ORDER BY frequency DESC',
            (f'%{search_term}%',)
        )
        return self.cursor.fetchall()

    def import_from_csv(self, file_path, table_type):
        """
        Import words or phrases from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            table_type (str): Either 'words' or 'phrases'
        
        Returns:
            tuple: (success, message)
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        try:
            df = pd.read_csv(file_path)
            
            if table_type == 'words':
                required_columns = ['word', 'frequency']
                if all(col in df.columns for col in required_columns):
                    count = 0
                    for _, row in df.iterrows():
                        category = row.get('category', 'general')
                        source = row.get('source', 'csv_import')
                        if self.add_word(row['word'], row['frequency'], category, source):
                            count += 1
                    return True, f"Successfully imported {count} words"
                else:
                    return False, "CSV must have columns: word, frequency (optional: category, source)"
            
            elif table_type == 'phrases':
                required_columns = ['phrase', 'frequency']
                if all(col in df.columns for col in required_columns):
                    count = 0
                    for _, row in df.iterrows():
                        category = row.get('category', 'general')
                        source = row.get('source', 'csv_import')
                        if self.add_phrase(row['phrase'], row['frequency'], category, source):
                            count += 1
                    return True, f"Successfully imported {count} phrases"
                else:
                    return False, "CSV must have columns: phrase, frequency (optional: category, source)"
            
            else:
                return False, "Invalid table_type. Use 'words' or 'phrases'"
        
        except Exception as e:
            return False, f"Error importing from CSV: {str(e)}"

    def export_to_csv(self, file_path, table_type):
        """
        Export words or phrases to a CSV file.
        
        Args:
            file_path (str): Path to save the CSV file
            table_type (str): Either 'words' or 'phrases'
        
        Returns:
            tuple: (success, message)
        """
        try:
            if table_type == 'words':
                words = self.get_all_words()
                df = pd.DataFrame(words, columns=['word', 'frequency', 'category', 'source'])
                df.to_csv(file_path, index=False)
                return True, f"Successfully exported {len(words)} words to {file_path}"
            
            elif table_type == 'phrases':
                phrases = self.get_all_phrases()
                df = pd.DataFrame(phrases, columns=['phrase', 'frequency', 'category', 'source'])
                df.to_csv(file_path, index=False)
                return True, f"Successfully exported {len(phrases)} phrases to {file_path}"
            
            else:
                return False, "Invalid table_type. Use 'words' or 'phrases'"
        
        except Exception as e:
            return False, f"Error exporting to CSV: {str(e)}"

    def populate_default_data(self):
        """
        Populate the database with default AI words and phrases.
        This is useful for initializing a new database.
        
        Returns:
            tuple: (words_added, phrases_added)
        """
        # Default words with their frequency, category, and source
        default_words = [
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
        ]
        
        # Default phrases with their frequency, category, and source
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
        ]
        
        words_added = 0
        for word, frequency, category, source in default_words:
            if self.add_word(word, frequency, category, source):
                words_added += 1
        
        phrases_added = 0
        for phrase, frequency, category, source in default_phrases:
            if self.add_phrase(phrase, frequency, category, source):
                phrases_added += 1
        
        return words_added, phrases_added

    def get_word_categories(self):
        """
        Get all unique word categories in the database.
        
        Returns:
            list: List of categories
        """
        self.cursor.execute('SELECT DISTINCT category FROM ai_words ORDER BY category')
        return [row[0] for row in self.cursor.fetchall()]

    def get_phrase_categories(self):
        """
        Get all unique phrase categories in the database.
        
        Returns:
            list: List of categories
        """
        self.cursor.execute('SELECT DISTINCT category FROM ai_phrases ORDER BY category')
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_sources(self):
        """
        Get all unique sources in the database.
        
        Returns:
            list: List of sources
        """
        self.cursor.execute('SELECT DISTINCT source FROM ai_words UNION SELECT DISTINCT source FROM ai_phrases ORDER BY source')
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    # Create a new database manager instance
    db_manager = AIWordDatabaseManager("ai_words.db")
    
    # Populate with default data
    words_added, phrases_added = db_manager.populate_default_data()
    print(f"Added {words_added} words and {phrases_added} phrases to the database")
    
    # Get all words and phrases
    words = db_manager.get_all_words()
    phrases = db_manager.get_all_phrases()
    
    # Print some examples
    print("\nSample AI Words:")
    for word, freq, cat, src in words[:5]:
        print(f"- {word} (Frequency: {freq}, Category: {cat}, Source: {src})")
    
    print("\nSample AI Phrases:")
    for phrase, freq, cat, src in phrases[:5]:
        print(f"- {phrase} (Frequency: {freq}, Category: {cat}, Source: {src})")
    
    # Get categories and sources
    word_categories = db_manager.get_word_categories()
    phrase_categories = db_manager.get_phrase_categories()
    sources = db_manager.get_sources()
    
    print(f"\nWord Categories: {', '.join(word_categories)}")
    print(f"Phrase Categories: {', '.join(phrase_categories)}")
    print(f"Sources: {', '.join(sources)}")
    
    # Close the connection
    db_manager.close()
