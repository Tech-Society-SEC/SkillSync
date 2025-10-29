"""
Skill Normalization Module - Semantic Matching
Uses Sentence-BERT to map extracted skills to standardized skill names

This module:
1. Loads skill taxonomy as reference
2. Creates embeddings for all standard skills
3. Maps user-mentioned skills to closest standard skill
4. Uses cosine similarity for matching
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
from pathlib import Path
import torch
import pickle


class SkillNormalizer:
    """Normalize and standardize skill names using semantic similarity"""
    
    def __init__(
        self, 
        skill_taxonomy_path: str = "datasets/skill_taxonomy.csv",
        model_name: str = "all-MiniLM-L6-v2"  # Smaller, faster model (80MB vs 400MB)
    ):
        """
        Initialize skill normalizer
        
        Args:
            skill_taxonomy_path: Path to standard skill taxonomy
            model_name: Sentence-BERT model name (multilingual)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load Sentence-BERT model
        print(f"Loading {model_name}...")
        self.model = SentenceTransformer(model_name, device=self.device)
        
        # Load skill taxonomy
        self.skill_taxonomy = self._load_taxonomy(skill_taxonomy_path)
        
        # Create embeddings for standard skills
        if not self.skill_taxonomy.empty:
            self._create_skill_embeddings()
        
        print("✓ Skill Normalizer initialized")
    
    def _load_taxonomy(self, path: str) -> pd.DataFrame:
        """Load skill taxonomy"""
        if Path(path).exists():
            df = pd.read_csv(path)
            print(f"Loaded {len(df)} standard skills")
            return df
        else:
            print(f"Warning: Taxonomy not found at {path}")
            return pd.DataFrame()
    
    def _create_skill_embeddings(self):
        """Create embeddings for all standard skills"""
        print("Creating embeddings for standard skills...")
        
        # Get all skill names
        skill_names = self.skill_taxonomy['skill_name'].tolist()
        
        # Generate embeddings
        self.skill_embeddings = self.model.encode(
            skill_names,
            convert_to_tensor=True,
            show_progress_bar=True
        )
        
        print(f"✓ Created embeddings for {len(skill_names)} skills")
    
    def normalize_skill(
        self, 
        skill_text: str, 
        threshold: float = 0.5,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Normalize a skill to standard taxonomy
        
        Args:
            skill_text: Raw skill text to normalize
            threshold: Minimum similarity threshold (0-1)
            top_k: Number of top matches to return
            
        Returns:
            List of matched skills with similarity scores
        """
        if self.skill_taxonomy.empty:
            return []
        
        # Create embedding for input skill
        skill_embedding = self.model.encode(skill_text, convert_to_tensor=True)
        
        # Calculate cosine similarity with all standard skills
        similarities = util.cos_sim(skill_embedding, self.skill_embeddings)[0]
        
        # Get top k matches
        top_results = torch.topk(similarities, k=min(top_k, len(similarities)))
        
        matches = []
        for score, idx in zip(top_results.values, top_results.indices):
            score_val = score.item()
            
            if score_val >= threshold:
                skill_row = self.skill_taxonomy.iloc[idx.item()]
                matches.append({
                    'original_skill': skill_text,
                    'normalized_skill': skill_row['skill_name'],
                    'category': skill_row['category'],
                    'similarity': round(score_val, 3),
                    'skill_id': skill_row['skill_id']
                })
        
        return matches
    
    def normalize_skill_list(
        self, 
        skills: List[str], 
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Normalize multiple skills
        
        Args:
            skills: List of raw skill texts
            threshold: Minimum similarity threshold
            
        Returns:
            List of normalized skills (best match for each)
        """
        normalized = []
        
        for skill in skills:
            matches = self.normalize_skill(skill, threshold=threshold, top_k=1)
            if matches:
                normalized.append(matches[0])
        
        return normalized
    
    def find_similar_skills(
        self, 
        skill_text: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find similar skills for recommendation
        
        Args:
            skill_text: Input skill
            top_k: Number of similar skills to return
            
        Returns:
            List of similar skills
        """
        return self.normalize_skill(skill_text, threshold=0.3, top_k=top_k)
    
    def save_embeddings(self, filepath: str):
        """Save embeddings to disk"""
        data = {
            'embeddings': self.skill_embeddings.cpu().numpy(),
            'taxonomy': self.skill_taxonomy.to_dict()
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"✓ Saved embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str):
        """Load pre-computed embeddings"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.skill_embeddings = torch.tensor(data['embeddings']).to(self.device)
        self.skill_taxonomy = pd.DataFrame(data['taxonomy'])
        
        print(f"✓ Loaded embeddings from {filepath}")


def main():
    """Demo and testing"""
    print("=" * 70)
    print("Skill Normalization Module - Demo")
    print("=" * 70)
    
    # Initialize normalizer
    normalizer = SkillNormalizer()
    
    # Test examples - raw skills that need normalization
    test_skills = [
        "fan fixing",  # Should map to "Fan Installation"
        "electric work",  # Should map to "Electrical Wiring"
        "pipe work",  # Should map to "Pipe Fitting"
        "wood work",  # Should map to "Wood Cutting" or "Carpentry"
        "wall construction",  # Should map to "Brick Laying"
        "vehicle repair",  # Should map to automotive skills
        "cloth stitching",  # Should map to "Stitching"
        "cooking food",  # Should map to cooking skills
    ]
    
    print("\n=== Testing Skill Normalization ===\n")
    
    for skill in test_skills:
        print(f"\nInput: '{skill}'")
        matches = normalizer.normalize_skill(skill, threshold=0.4, top_k=3)
        
        if matches:
            print(f"  Top Matches:")
            for i, match in enumerate(matches, 1):
                print(f"    {i}. {match['normalized_skill']}")
                print(f"       Category: {match['category']}")
                print(f"       Similarity: {match['similarity']:.2%}")
        else:
            print("  No matches found")
    
    # Test finding similar skills
    print("\n\n=== Finding Similar Skills ===\n")
    base_skill = "Electrical Wiring"
    print(f"Finding skills similar to: '{base_skill}'")
    
    similar = normalizer.find_similar_skills(base_skill, top_k=5)
    for i, skill in enumerate(similar, 1):
        print(f"  {i}. {skill['normalized_skill']} - {skill['similarity']:.2%}")
    
    # Save embeddings for future use
    print("\n\n=== Saving Embeddings ===")
    normalizer.save_embeddings("models/skill_embeddings.pkl")
    
    print("\n" + "=" * 70)
    print("✓ Skill Normalization Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
