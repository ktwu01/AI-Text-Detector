import re
import sqlite3
import pandas as pd
from collections import Counter
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

class AIWordHighlighter:
    def __init__(self, db_path=":memory:"):
        """Initialize with database path (default is in-memory database)"""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.load_default_words()

    def initialize_database(self):
        """Create the necessary tables if they don't exist"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_terms (
            id INTEGER PRIMARY KEY,
            term TEXT NOT NULL,
            term_type TEXT NOT NULL, -- 'word' or 'phrase'
            frequency INTEGER DEFAULT 1
        )
        ''')
        
        # Create index for faster lookups
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_term ON ai_terms(term)')
        self.conn.commit()

    def load_default_words(self):
        """Load a default set of commonly used AI words and phrases"""
        # Common words from various sources
        default_words = [
            # Words identified from multiple sources as common in AI text
            ("delve", "word", 10),
            ("whilst", "word", 9),
            ("furthermore", "word", 8),
            ("navigate", "word", 8),
            ("indeed", "word", 7),
            ("utilize", "word", 7),
            ("leverage", "word", 7),
            ("robust", "word", 7),
            ("optimal", "word", 7),
            ("showcase", "word", 6),
            ("essentially", "word", 6),
            ("ultimately", "word", 6),
            ("myriad", "word", 6),
            ("seamless", "word", 6),
            ("plethora", "word", 6),
            ("harness", "word", 6),
            ("elevate", "word", 10),
            ("tapestry", "word", 9),
            ("captivate", "word", 8),
            ("testament", "word", 8),
            ("nuanced", "word", 7),
            ("enhance", "word", 7),
            ("facilitate", "word", 7),
            ("comprehensive", "word", 7),
            ("innovative", "word", 6),
            ("streamline", "word", 6),
            ("synergy", "word", 6),
            ("paradigm", "word", 6),
            ("empower", "word", 6),
            ("revolutionize", "word", 6),
            ("transformative", "word", 6),
            ("ecosystem", "word", 5),
            ("unprecedented", "word", 5),
            ("cultivate", "word", 5),
            ("catalyst", "word", 5),
            ("disrupt", "word", 5),
            ("holistic", "word", 5),
            ("cutting-edge", "word", 5),
            ("sustainable", "word", 5),
            ("strategic", "word", 5),
            ("foster", "word", 5),
            ("streamlined", "word", 5),
            ("implementation", "word", 5),
            ("integration", "word", 5),
            ("methodology", "word", 5),
            ("functionality", "word", 5),
            ("optimization", "word", 5),
            ("infrastructure", "word", 5),
            ("initiative", "word", 5),
            
            # Common phrases
            ("in this article", "phrase", 10),
            ("delve into", "phrase", 9),
            ("it's important to note", "phrase", 9),
            ("on the other hand", "phrase", 8),
            ("in the realm of", "phrase", 8),
            ("a wide range of", "phrase", 8),
            ("it is worth mentioning", "phrase", 7),
            ("plays a crucial role", "phrase", 7),
            ("in conclusion", "phrase", 7),
            ("in summary", "phrase", 7),
            ("to summarize", "phrase", 6),
            ("as we have seen", "phrase", 6),
            ("moving forward", "phrase", 6),
            ("when it comes to", "phrase", 6),
            ("as mentioned earlier", "phrase", 6),
            ("in the context of", "phrase", 6),
            ("it goes without saying", "phrase", 5),
            ("it is essential to", "phrase", 5),
            ("needless to say", "phrase", 5),
            ("it's worth noting that", "phrase", 5),
            ("a plethora of", "phrase", 9),
            ("treasure trove of", "phrase", 8),
            ("in today's fast-paced world", "phrase", 8),
            ("in the digital age", "phrase", 7),
            ("embark on a journey", "phrase", 7),
            ("unlock the potential", "phrase", 7),
            ("harness the power", "phrase", 6),
            ("foster a culture of", "phrase", 6),
            ("curated collection", "phrase", 6),
            ("seamless integration", "phrase", 6),
            ("rich tapestry", "phrase", 5),
            ("paradigm shift", "phrase", 5),
            ("as an AI language model", "phrase", 10),
            ("I don't have access to", "phrase", 9),
            ("as of my last update", "phrase", 9),
            ("I cannot provide", "phrase", 8),
            ("I cannot browse the internet", "phrase", 8),
        ]
        
        # Clear existing data
        self.cursor.execute('DELETE FROM ai_terms')
        
        # Insert terms
        self.cursor.executemany(
            'INSERT INTO ai_terms (term, term_type, frequency) VALUES (?, ?, ?)',
            default_words
        )
        
        self.conn.commit()

    def add_term(self, term, term_type, frequency=1):
        """Add a new AI term to the database"""
        self.cursor.execute(
            'INSERT INTO ai_terms (term, term_type, frequency) VALUES (?, ?, ?)',
            (term.lower(), term_type.lower(), frequency)
        )
        self.conn.commit()

    def get_all_terms(self):
        """Get all AI terms from the database"""
        self.cursor.execute('SELECT term, term_type, frequency FROM ai_terms ORDER BY frequency DESC')
        return self.cursor.fetchall()
        
    def get_all_words(self):
        """Get all AI words from the database"""
        self.cursor.execute('SELECT term, frequency FROM ai_terms WHERE term_type = "word" ORDER BY frequency DESC')
        return self.cursor.fetchall()

    def get_all_phrases(self):
        """Get all AI phrases from the database"""
        self.cursor.execute('SELECT term, frequency FROM ai_terms WHERE term_type = "phrase" ORDER BY frequency DESC')
        return self.cursor.fetchall()

    def import_terms_from_csv(self, file_path):
        """Import terms from a CSV file"""
        try:
            df = pd.read_csv(file_path)
            required_columns = ['term', 'term_type', 'frequency']
            
            # Check if all required columns exist
            if all(col in df.columns for col in required_columns):
                for index, row in df.iterrows():
                    self.add_term(row['term'], row['term_type'], row['frequency'])
                return True, f"Successfully imported {len(df)} terms"
            else:
                # Try to handle old format CSVs
                if 'word' in df.columns and 'frequency' in df.columns:
                    for index, row in df.iterrows():
                        self.add_term(row['word'], 'word', row['frequency'])
                    return True, f"Successfully imported {len(df)} words"
                elif 'phrase' in df.columns and 'frequency' in df.columns:
                    for index, row in df.iterrows():
                        self.add_term(row['phrase'], 'phrase', row['frequency'])
                    return True, f"Successfully imported {len(df)} phrases"
                else:
                    return False, "CSV must have columns: term, term_type, frequency"
        except Exception as e:
            return False, f"Error importing CSV: {str(e)}"

    def highlight_text(self, text):
        """Highlight AI words and phrases in the given text"""
        # Get all terms
        terms = self.get_all_terms()
        
        # Create a copy of the text for highlighting
        highlighted_text = text
        found_items = []
        
        # First detect phrases (to avoid highlighting parts of phrases as individual words)
        phrases = [term for term in terms if term[1] == 'phrase']
        words = [term for term in terms if term[1] == 'word']
        
        # Process phrases first
        for term, term_type, frequency in phrases:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                found_items.append((term_type, term, match.start(), match.end(), frequency))
        
        # Then detect individual words
        for term, term_type, frequency in words:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Check if this word is part of a detected phrase
                is_part_of_phrase = False
                for item_type, item_text, start, end, _ in found_items:
                    if item_type == "phrase" and start <= match.start() and match.end() <= end:
                        is_part_of_phrase = True
                        break
                
                if not is_part_of_phrase:
                    found_items.append((term_type, term, match.start(), match.end(), frequency))
        
        # Sort found items by position (start index) in reverse order
        # This way we can replace from end to beginning without affecting positions
        found_items.sort(key=lambda x: x[2], reverse=True)
        
        # Replace matches with highlighted versions
        for item_type, item_text, start, end, frequency in found_items:
            original_text = text[start:end]
            highlighted = f"**{original_text}**"  # Bold for Markdown
            highlighted_text = highlighted_text[:start] + highlighted + highlighted_text[end:]
        
        return highlighted_text, found_items

    def analyze_text(self, text):
        """Analyze the text and return statistics"""
        _, found_items = self.highlight_text(text)
        
        # Count word frequencies
        word_counts = Counter()
        phrase_counts = Counter()
        
        for item_type, item_text, _, _, frequency in found_items:
            if item_type == "word":
                word_counts[item_text] += 1
            else:
                phrase_counts[item_text] += 1
        
        # Calculate statistics
        total_words = len(re.findall(r'\b\w+\b', text))
        unique_words = len(set(re.findall(r'\b\w+\b', text.lower())))
        ai_markers = len(found_items)
        ai_word_percentage = (len([i for i in found_items if i[0] == "word"]) / total_words) * 100 if total_words > 0 else 0
        
        # Prepare results
        results = {
            "total_words": total_words,
            "unique_words": unique_words,
            "ai_markers": ai_markers,
            "ai_word_percentage": ai_word_percentage,
            "word_counts": word_counts,
            "phrase_counts": phrase_counts
        }
        
        return results

    def export_terms_to_csv(self, file_path):
        """Export all terms to a CSV file"""
        terms = self.get_all_terms()
        df = pd.DataFrame(terms, columns=['term', 'term_type', 'frequency'])
        df.to_csv(file_path, index=False)
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()



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