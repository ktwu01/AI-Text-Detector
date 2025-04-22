# streamlit run xxxx
# import sys
import re
import sqlite3
import pandas as pd
from collections import Counter
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from get_default_word_bank import get_default_word_bank

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
        default_words, default_phrases = self.get_default_word_bank()
    
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
        # print(f"Words from database: {len(words)}, sample: {words[:5] if words else 'none'}")
        # print(f"Phrases from database: {len(phrases)}, sample: {phrases[:5] if phrases else 'none'}")

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
                # col4.metric("AI Word %", f"{results['ai_word_percentage']:.2f}%")
                
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

    # Running directly with python, show instructions
    print("\n" + "="*70)
    print("STREAMLIT APP LAUNCH INSTRUCTIONS")
    print("="*70)
    print("\nThis is a Streamlit app and should be run using the Streamlit command:")
    print(f"\n    streamlit run {__file__}")
    print("\nRunning the script directly with Python won't work correctly.")
    print("="*70 + "\n")

    # Close the database connection when done
    highlighter.close()

# Run the Streamlit app if this script is run directly
if __name__ == "__main__":
    create_streamlit_app()
