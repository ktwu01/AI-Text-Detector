#!/usr/bin/env python3
"""
AI SEO Analyzer - Usage Example
This script demonstrates how to use the AI SEO Analyzer to check text for AI patterns
and get improvement suggestions.
"""

import sys
import os
from ai_seo_analyzer import AIContentAnalyzer

def main():
    # Sample AI-generated text
    sample_text = """
    In this article, we will delve into the fascinating realm of artificial intelligence and its implications for modern content creation. 
    It's important to note that AI technology has evolved significantly over the past decade, transforming the landscape of digital marketing and content strategy.
    
    When it comes to SEO, a plethora of techniques have been developed to enhance website visibility. 
    Indeed, the field has witnessed a paradigm shift, with machine learning algorithms playing a crucial role in determining search rankings.
    
    Furthermore, content creators must navigate the ethical considerations that arise from utilizing AI-generated text. 
    On the other hand, the benefits of leveraging AI tools cannot be overstated, as they provide unprecedented efficiency and scalability.
    
    In conclusion, as we have seen, the journey of integrating AI into content strategy is both challenging and rewarding. 
    To summarize, businesses that harness the power of this technology responsibly will likely gain a competitive edge in the digital landscape.
    """
    
    # Initialize the analyzer
    analyzer = AIContentAnalyzer()
    
    print("=" * 50)
    print("AI SEO Analyzer - Example Usage")
    print("=" * 50)
    
    print("\nAnalyzing sample text...")
    
    # Analyze the text
    results = analyzer.analyze_text(sample_text)
    
    # Print basic results
    print(f"\nTotal Words: {results['total_words']}")
    print(f"AI Markers Found: {results['ai_markers']}")
    print(f"AI Word Percentage: {results['ai_word_percentage']:.2f}%")
    print(f"Weighted AI Score: {results['weighted_ai_score']:.2f}/10")
    
    # Print detected words and phrases
    if results['word_counts']:
        print("\nAI Words Detected:")
        for word, count in sorted(results['word_counts'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {word}: {count}")
    
    if results['phrase_counts']:
        print("\nAI Phrases Detected:")
        for phrase, count in sorted(results['phrase_counts'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {phrase}: {count}")
    
    # Get improvement suggestions
    suggestions = analyzer.generate_suggestions(results)
    
    print("\nImprovement Suggestions:")
    
    if suggestions['general']:
        print("\n  General:")
        for suggestion in suggestions['general']:
            print(f"    - {suggestion}")
    
    if suggestions['word_replacements']:
        print("\n  Word Replacements:")
        for word, replacements in suggestions['word_replacements'].items():
            print(f"    - {word} → {', '.join(replacements)}")
    
    if suggestions['phrase_replacements']:
        print("\n  Phrase Replacements:")
        for phrase, replacements in suggestions['phrase_replacements'].items():
            print(f"    - {phrase} → {', '.join(replacements)}")
    
    # Export to HTML with highlighting
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    html_file = os.path.join(output_dir, "ai_analysis.html")
    analyzer.export_analysis_to_html(sample_text, results, html_file)
    print(f"\nDetailed HTML analysis saved to: {html_file}")
    
    # Generate visualizations
    vis_files = analyzer.visualize_analysis(results, output_dir)
    print(f"\nVisualizations saved to the '{output_dir}' directory")
    
    # Close the analyzer
    analyzer.close()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
