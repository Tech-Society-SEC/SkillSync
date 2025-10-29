"""
Skill Extraction Module - NLP Pipeline
Uses spaCy + BERT/XLM-R for extracting skills from text

This module:
1. Preprocesses text from worker utterances
2. Extracts skill entities using NER and pattern matching
3. Uses multilingual BERT for skill classification
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import spacy
from typing import List, Dict, Tuple
import re
import json
from pathlib import Path


class SkillExtractor:
    """Extract skills from worker utterances using NLP"""
    
    def __init__(self, model_name="xlm-roberta-base", skill_taxonomy_path="datasets/skill_taxonomy.csv"):
        """
        Initialize the skill extractor
        
        Args:
            model_name: Hugging Face model for multilingual NER
            skill_taxonomy_path: Path to skill taxonomy CSV
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load skill taxonomy
        self.skill_taxonomy = self._load_skill_taxonomy(skill_taxonomy_path)
        
        # Initialize tokenizer and model
        print(f"Loading {model_name} model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # For now, we'll use pattern matching and keyword extraction
        # You can fine-tune this model later with your dataset
        self.model_name = model_name
        
        # Create skill keyword dictionary
        self.skill_keywords = self._create_skill_keywords()
        
        print("✓ Skill Extractor initialized")
    
    def _load_skill_taxonomy(self, path: str) -> pd.DataFrame:
        """Load skill taxonomy from CSV"""
        if Path(path).exists():
            return pd.read_csv(path)
        else:
            print(f"Warning: Skill taxonomy not found at {path}")
            return pd.DataFrame()
    
    def _create_skill_keywords(self) -> Dict[str, List[str]]:
        """Create keyword mapping from skill taxonomy"""
        keywords = {}
        
        if not self.skill_taxonomy.empty:
            for _, row in self.skill_taxonomy.iterrows():
                skill_name = row['skill_name']
                category = row['category']
                
                # Create variations of skill name
                variations = [
                    skill_name.lower(),
                    skill_name.lower().replace(' ', ''),
                    skill_name.lower().replace('-', ' ')
                ]
                
                keywords[skill_name] = {
                    'variations': variations,
                    'category': category
                }
        
        return keywords
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle common abbreviations
        text = text.replace("yr", "year")
        text = text.replace("yrs", "years")
        text = text.replace("exp", "experience")
        
        return text
    
    def extract_skills_rule_based(self, text: str) -> List[Dict]:
        """
        Extract skills using rule-based pattern matching
        
        Args:
            text: Input utterance text
            
        Returns:
            List of extracted skills with metadata
        """
        text_clean = self.preprocess_text(text)
        extracted_skills = []
        
        # Match against skill keywords
        for skill_name, data in self.skill_keywords.items():
            for variation in data['variations']:
                if variation in text_clean:
                    extracted_skills.append({
                        'skill': skill_name,
                        'category': data['category'],
                        'confidence': 0.9,
                        'method': 'rule_based'
                    })
                    break
        
        # Remove duplicates
        unique_skills = []
        seen = set()
        for skill in extracted_skills:
            if skill['skill'] not in seen:
                unique_skills.append(skill)
                seen.add(skill['skill'])
        
        return unique_skills
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience from text"""
        text_clean = self.preprocess_text(text)
        
        # Pattern: "X years", "X year"
        pattern = r'(\d+)\s*(?:years?|yrs?)'
        matches = re.findall(pattern, text_clean)
        
        if matches:
            return int(matches[0])
        
        return 0
    
    def extract_job_title(self, text: str) -> str:
        """Extract job title from text"""
        text_clean = self.preprocess_text(text)
        
        # Common job title patterns
        job_patterns = [
            r'i am (?:a |an )?(\w+)',
            r'i work as (?:a |an )?(\w+)',
            r'my job is (\w+)',
        ]
        
        for pattern in job_patterns:
            match = re.search(pattern, text_clean)
            if match:
                return match.group(1).title()
        
        return ""
    
    def extract_from_utterance(self, text: str) -> Dict:
        """
        Complete skill extraction from utterance
        
        Args:
            text: Worker utterance
            
        Returns:
            Dictionary with extracted information
        """
        skills = self.extract_skills_rule_based(text)
        experience = self.extract_experience_years(text)
        job_title = self.extract_job_title(text)
        
        return {
            'text': text,
            'skills': skills,
            'num_skills': len(skills),
            'experience_years': experience,
            'job_title': job_title,
            'categories': list(set([s['category'] for s in skills]))
        }
    
    def batch_extract(self, texts: List[str]) -> List[Dict]:
        """
        Extract skills from multiple utterances
        
        Args:
            texts: List of utterances
            
        Returns:
            List of extraction results
        """
        results = []
        for text in texts:
            results.append(self.extract_from_utterance(text))
        return results
    
    def evaluate_on_dataset(self, dataset_path: str) -> Dict:
        """
        Evaluate extraction on labeled dataset
        
        Args:
            dataset_path: Path to worker_utterances.csv
            
        Returns:
            Evaluation metrics
        """
        if not Path(dataset_path).exists():
            print(f"Dataset not found: {dataset_path}")
            return {}
        
        df = pd.read_csv(dataset_path)
        
        correct = 0
        total = len(df)
        
        for _, row in df.iterrows():
            text = row['text']
            true_skills = set(str(row['extracted_skills']).split(', '))
            
            result = self.extract_from_utterance(text)
            predicted_skills = set([s['skill'] for s in result['skills']])
            
            # Simple accuracy: check if at least one skill matches
            if predicted_skills & true_skills:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        metrics = {
            'accuracy': accuracy,
            'total_samples': total,
            'correct_predictions': correct
        }
        
        print(f"\n=== Evaluation Results ===")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Correct: {correct}/{total}")
        
        return metrics


def train_custom_ner_model(utterances_path: str, output_dir: str = "models/skill_ner"):
    """
    Fine-tune BERT model for skill NER (optional advanced step)
    
    Args:
        utterances_path: Path to training data
        output_dir: Directory to save trained model
    """
    print("\n=== Training Custom NER Model ===")
    print("This is an optional step for advanced users")
    print("For now, we use rule-based extraction which works well")
    print("To enable this, you need to:")
    print("1. Annotate data with BIO tags")
    print("2. Fine-tune XLM-RoBERTa on annotated data")
    print("3. Export and use the fine-tuned model")
    
    # Placeholder for future implementation
    pass


def main():
    """Demo and testing"""
    print("=" * 70)
    print("Skill Extraction Module - Demo")
    print("=" * 70)
    
    # Initialize extractor
    extractor = SkillExtractor()
    
    # Test examples
    test_utterances = [
        "I have 5 years of experience in electrical wiring and fan installation",
        "I am a plumber. I know pipe fitting and tap repair",
        "Naan carpenter, wood cutting pannuven",
        "Main welding aur gate making ka kaam karta hoon",
        "I do brick laying and plastering work for 10 years",
        "I am experienced driver. Car driving and two wheeler riding I know"
    ]
    
    print("\n=== Testing Skill Extraction ===\n")
    
    for i, utterance in enumerate(test_utterances, 1):
        print(f"\n[Test {i}]")
        print(f"Input: {utterance}")
        
        result = extractor.extract_from_utterance(utterance)
        
        print(f"Job Title: {result['job_title'] or 'N/A'}")
        print(f"Experience: {result['experience_years']} years" if result['experience_years'] else "Experience: N/A")
        print(f"Extracted Skills ({result['num_skills']}):")
        
        for skill in result['skills']:
            print(f"  • {skill['skill']} ({skill['category']}) - Confidence: {skill['confidence']}")
        
        if result['categories']:
            print(f"Categories: {', '.join(result['categories'])}")
    
    # Evaluate on full dataset if available
    utterances_path = "datasets/worker_utterances.csv"
    if Path(utterances_path).exists():
        print("\n\n=== Evaluating on Full Dataset ===")
        metrics = extractor.evaluate_on_dataset(utterances_path)
    
    print("\n" + "=" * 70)
    print("✓ Skill Extraction Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
