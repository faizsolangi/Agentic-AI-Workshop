#!/usr/bin/env python3
"""
Educational Content Generator with Streamlit Frontend
Generates assignments and quiz questions from provided text or topics.
"""

import re
import random
import streamlit as st
from typing import List, Dict, Tuple

class ContentGenerator:
    def __init__(self):
        # Question starters for different types of assignments
        self.essay_starters = [
            "Analyze and discuss",
            "Compare and contrast",
            "Evaluate the significance of",
            "Explain the relationship between",
            "Critically examine",
            "Describe the impact of",
            "What are the main factors that contribute to",
            "How does",
            "Why is it important to understand"
        ]
        
        # Question words for multiple choice
        self.mc_starters = [
            "What is",
            "Which of the following",
            "What best describes",
            "According to the text, what",
            "Which statement is true about",
            "What can be inferred about",
            "The main idea of",
            "What is the primary purpose of"
        ]
        
        # Common wrong answer patterns
        self.distractor_words = [
            "not", "never", "always", "only", "except", "opposite", "contrary",
            "unrelated", "irrelevant", "incorrect", "false"
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize input text."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text

    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text using simple heuristics."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Find important terms (capitalized words, repeated words)
        concepts = []
        word_freq = {}
        
        for sentence in sentences:
            words = re.findall(r'\b[A-Za-z]+\b', sentence)
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_lower = word.lower()
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
                    
                    # Add capitalized words as potential concepts
                    if word[0].isupper() and word.lower() not in ['the', 'this', 'that', 'they', 'there']:
                        concepts.append(word)
        
        # Add frequently mentioned terms
        frequent_words = [word for word, freq in word_freq.items() 
                         if freq > 1 and len(word) > 4]
        concepts.extend(frequent_words[:5])  # Top 5 frequent words
        
        return list(set(concepts))[:10]  # Return unique concepts, max 10

    def generate_assignments(self, text: str, concepts: List[str]) -> List[str]:
        """Generate essay assignment prompts."""
        assignments = []
        
        # First assignment - general analysis
        if concepts:
            main_concept = random.choice(concepts)
            starter = random.choice(self.essay_starters)
            assignment1 = f"{starter} {main_concept.lower()} as discussed in the provided material. Support your analysis with specific examples and explain its broader implications."
            assignments.append(assignment1)
        else:
            assignments.append("Analyze the main themes presented in the provided text and discuss their significance with supporting examples.")
        
        # Second assignment - comparative or evaluative
        if len(concepts) >= 2:
            concept1, concept2 = random.sample(concepts, 2)
            assignment2 = f"Compare and contrast {concept1.lower()} and {concept2.lower()}. Discuss how these concepts relate to each other and their importance in the overall context."
            assignments.append(assignment2)
        else:
            assignments.append("Evaluate the effectiveness of the arguments presented in the text. What evidence supports the main points, and what questions remain unanswered?")
        
        return assignments

    def create_multiple_choice_question(self, sentence: str, concepts: List[str]) -> Dict:
        """Create a multiple choice question from a sentence."""
        # Basic question generation logic
        sentence = sentence.strip()
        if not sentence:
            return None
            
        # Extract a key fact or concept from the sentence
        words = sentence.split()
        
        # Find potential answer in the sentence
        answer_candidates = [word for word in words if len(word) > 4 and word.lower() not in 
                           ['through', 'because', 'however', 'therefore', 'although']]
        
        if not answer_candidates:
            return None
            
        correct_answer = random.choice(answer_candidates).strip('.,!?')
        
        # Create question by replacing the answer with a blank or question format
        question_text = sentence.replace(correct_answer, "______")
        
        if "______" not in question_text:
            # Alternative question format
            starter = random.choice(self.mc_starters)
            question_text = f"{starter} mentioned in the following context: '{sentence[:50]}...'?"
        
        # Generate distractors
        distractors = self.generate_distractors(correct_answer, concepts)
        
        # Combine all options
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        # Find correct answer index after shuffling
        correct_index = options.index(correct_answer)
        correct_letter = chr(65 + correct_index)  # A, B, C, D
        
        return {
            'question': question_text,
            'options': options,
            'correct_answer': correct_letter,
            'correct_text': correct_answer
        }

    def generate_distractors(self, correct_answer: str, concepts: List[str]) -> List[str]:
        """Generate plausible wrong answers."""
        distractors = []
        
        # Use other concepts as distractors
        other_concepts = [c for c in concepts if c.lower() != correct_answer.lower()]
        distractors.extend(other_concepts[:2])
        
        # Generate generic distractors if not enough concepts
        generic_distractors = [
            f"Not {correct_answer.lower()}",
            f"Opposite of {correct_answer.lower()}",
            "None of the above"
        ]
        
        distractors.extend(generic_distractors)
        
        # Return first 3 distractors
        return distractors[:3]

    def generate_quiz_questions(self, text: str, concepts: List[str]) -> List[Dict]:
        """Generate multiple choice quiz questions."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]
        
        questions = []
        attempts = 0
        max_attempts = len(sentences) * 2
        
        while len(questions) < 3 and attempts < max_attempts:
            if sentences:
                sentence = random.choice(sentences)
                question = self.create_multiple_choice_question(sentence, concepts)
                if question and question not in questions:
                    questions.append(question)
            attempts += 1
        
        # Fill remaining questions with generic ones if needed
        while len(questions) < 3:
            generic_q = self.create_generic_question(concepts, len(questions))
            questions.append(generic_q)
        
        return questions

    def create_generic_question(self, concepts: List[str], index: int) -> Dict:
        """Create a generic question when text processing fails."""
        if concepts:
            concept = random.choice(concepts)
            question_text = f"What is the significance of {concept.lower()} in the provided material?"
            options = [
                f"It is a central theme",
                f"It is mentioned briefly",
                f"It is not relevant",
                f"It contradicts the main argument"
            ]
        else:
            question_text = f"Based on the provided material, which statement is most accurate?"
            options = [
                "The content presents a clear argument",
                "The content lacks supporting evidence", 
                "The content is purely descriptive",
                "The content is contradictory"
            ]
        
        return {
            'question': question_text,
            'options': options,
            'correct_answer': 'A',
            'correct_text': options[0]
        }

    def generate_content(self, input_text: str) -> Dict:
        """Main method to generate all educational content."""
        # Clean input text
        text = self.clean_text(input_text)
        
        # Extract key concepts
        concepts = self.extract_key_concepts(text)
        
        # Generate assignments
        assignments = self.generate_assignments(text, concepts)
        
        # Generate quiz questions
        quiz_questions = self.generate_quiz_questions(text, concepts)
        
        return {
            'assignments': assignments,
            'quiz_questions': quiz_questions,
            'concepts_found': concepts
        }

def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Educational Content Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 0.5rem;
    }
    .assignment-box {
        background-color: #f0f8ff;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .quiz-box {
        background-color: #f5f5f5;
        border-left: 5px solid #2ca02c;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .concept-tag {
        display: inline-block;
        background-color: #e7f3ff;
        color: #0066cc;
        padding: 0.25rem 0.5rem;
        margin: 0.25rem;
        border-radius: 15px;
        font-size: 0.8rem;
        border: 1px solid #b3d9ff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<div class="main-header">📚 Educational Content Generator</div>', unsafe_allow_html=True)
    st.markdown("Generate assignments and quiz questions from any text or topic!")
    
    # Sidebar
    with st.sidebar:
        st.header("📝 Instructions")
        st.write("""
        1. Enter your text or topic in the text area
        2. Click 'Generate Content' to create assignments and quizzes
        3. Use the sample text to see how it works
        """)
        
        st.header("✨ Features")
        st.write("""
        - **2 Assignment Questions**: Essay prompts for deeper analysis
        - **3 Quiz Questions**: Multiple-choice with correct answers
        - **Key Concept Extraction**: Automatically identifies important terms
        """)
        
        # Sample text button
        if st.button("📋 Use Sample Text"):
            st.session_state.sample_text = """
            Artificial Intelligence (AI) is revolutionizing many aspects of modern life. 
            Machine learning algorithms can analyze vast amounts of data to identify patterns 
            and make predictions. Deep learning, a subset of machine learning, uses neural 
            networks with multiple layers to process information. These technologies have 
            applications in healthcare, finance, transportation, and education. However, 
            AI also raises important ethical questions about privacy, job displacement, 
            and algorithmic bias. As AI systems become more sophisticated, it's crucial 
            to develop frameworks for responsible AI development and deployment.
            """
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input section
        st.header("📄 Input Your Content")
        
        # Use sample text if button was clicked
        default_text = st.session_state.get('sample_text', '')
        
        input_text = st.text_area(
            "Enter your text, document, or topic:",
            value=default_text,
            height=200,
            placeholder="Paste your text here or click 'Use Sample Text' in the sidebar to see an example..."
        )
        
        # Generate button
        generate_button = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    
    with col2:
        # Settings
        st.header("⚙️ Settings")
        
        st.info("**Current Configuration:**\n- Assignment Questions: 2\n- Quiz Questions: 3\n- Answer Options: 4 per question")
        
        if st.button("🔄 Clear All", use_container_width=True):
            if 'sample_text' in st.session_state:
                del st.session_state.sample_text
            st.rerun()
    
    # Generate content when button is clicked
    if generate_button and input_text.strip():
        with st.spinner("Generating educational content..."):
            generator = ContentGenerator()
            content = generator.generate_content(input_text)
        
        st.success("✅ Content generated successfully!")
        
        # Display results
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Assignments section
            st.markdown('<div class="section-header">📋 Assignment Questions</div>', unsafe_allow_html=True)
            
            for i, assignment in enumerate(content['assignments'], 1):
                st.markdown(f"""
                <div class="assignment-box">
                    <strong>Assignment {i}:</strong><br>
                    {assignment}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Quiz section
            st.markdown('<div class="section-header">🎯 Quiz Questions</div>', unsafe_allow_html=True)
            
            for i, question in enumerate(content['quiz_questions'], 1):
                options_html = ""
                for j, option in enumerate(question['options']):
                    letter = chr(65 + j)  # A, B, C, D
                    style = "font-weight: bold; color: #2ca02c;" if letter == question['correct_answer'] else ""
                    options_html += f"<div style='{style}'>{letter}. {option}</div>"
                
                st.markdown(f"""
                <div class="quiz-box">
                    <strong>Question {i}:</strong><br>
                    {question['question']}<br><br>
                    {options_html}<br>
                    <strong>✅ Correct Answer: {question['correct_answer']}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Key concepts section
        if content['concepts_found']:
            st.markdown('<div class="section-header">🔍 Key Concepts Identified</div>', unsafe_allow_html=True)
            
            concepts_html = ""
            for concept in content['concepts_found'][:8]:  # Show max 8 concepts
                concepts_html += f'<span class="concept-tag">{concept}</span>'
            
            st.markdown(concepts_html, unsafe_allow_html=True)
        
        # Export options
        st.markdown("---")
        st.header("📤 Export Options")
        
        # Create downloadable content
        export_content = f"""
# Educational Content Generated

## Assignment Questions:
1. {content['assignments'][0]}

2. {content['assignments'][1]}

## Quiz Questions:
"""
        for i, question in enumerate(content['quiz_questions'], 1):
            export_content += f"""
### Question {i}: {question['question']}
"""
            for j, option in enumerate(question['options']):
                letter = chr(65 + j)
                export_content += f"{letter}. {option}\n"
            export_content += f"**Correct Answer: {question['correct_answer']}**\n"
        
        export_content += f"""
## Key Concepts:
{', '.join(content['concepts_found'])}
"""
        
        st.download_button(
            label="📄 Download as Text File",
            data=export_content,
            file_name="educational_content.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    elif generate_button and not input_text.strip():
        st.warning("⚠️ Please enter some text before generating content!")
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit • Educational Content Generator v1.0*")

if __name__ == "__main__":
    main()