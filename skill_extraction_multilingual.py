"""
Multilingual Skill Extractor - Aggressive Pattern Matching
Optimized for Indian informal sector workers
Supports: English, Hindi, Tamil, Telugu, Kannada
"""

import pandas as pd
import re
from typing import List, Dict
from pathlib import Path


class MultilingualSkillExtractor:
    """
    Aggressive multilingual skill extraction
    Designed for high recall on worker utterances
    """
    
    def __init__(self, skill_taxonomy_path="datasets/skill_taxonomy.csv"):
        """Initialize with comprehensive multilingual mappings"""
        self.skill_taxonomy = pd.read_csv(skill_taxonomy_path)
        
        # Comprehensive multilingual skill keywords
        self.multilingual_keywords = {
            # ELECTRICAL WORK
            'Electrical Wiring': [
                'wiring', 'wire', 'electrical', 'electric', 'इलेक्ट्रिक', 'वायरिंग',
                'மின்சாரம்', 'வயரிங்', 'విద్యుత్', 'వైరింగ్', 'ವಿದ್ಯುತ್', 'ವೈರಿಂಗ್',
                'house wiring', 'घर की वायरिंग', 'வீட்டு வயரிங்'
            ],
            'Fan Installation': [
                'fan', 'पंखा', 'விசிறி', 'ఫ్యాన్', 'ಫ್ಯಾನ್',
                'fan installation', 'fan fitting', 'पंखा लगाना'
            ],
            'Switch Board Repair': [
                'switch', 'board', 'स्विच', 'स्विच बोर्ड', 'சுவிட்ச்', 'స్విచ్', 'ಸ್ವಿಚ್',
                'switchboard', 'switch board'
            ],
            'Motor Winding': [
                'motor', 'winding', 'मोटर', 'वाइंडिंग', 'மோட்டார்', 'మోటార్', 'ಮೋಟಾರ್',
                'motor repair', 'motor winding'
            ],
            
            # PLUMBING
            'Pipe Fitting': [
                'pipe', 'plumbing', 'पाइप', 'प्लंबिंग', 'குழாய்', 'పైప్', 'ಪೈಪ್',
                'pipe fitting', 'pipe work', 'पाइप फिटिंग'
            ],
            'Tap Repair': [
                'tap', 'नल', 'குழாய்', 'కుళాయి', 'ಟ್ಯಾಪ್',
                'tap repair', 'नल की मरम्मत', 'leak', 'leakage'
            ],
            
            # WELDING
            'Arc Welding': [
                'weld', 'welding', 'वेल्डिंग', 'வெல்டிங்', 'వెల్డింగ్', 'ವೆಲ್ಡಿಂಗ್',
                'arc welding'
            ],
            'Steel Fabrication': [
                'steel', 'fabrication', 'स्टील', 'फैब्रिकेशन', 'இரும்பு', 'ఉక్కు', 'ಉಕ್ಕು',
                'steel work', 'steel fabrication'
            ],
            'Gate Making': [
                'gate', 'गेट', 'வாயில்', 'గేట్', 'ಗೇಟ್',
                'gate making', 'gate work'
            ],
            
            # CARPENTRY
            'Wood Cutting': [
                'wood', 'लकड़ी', 'மரம்', 'చెక్క', 'ಮರ',
                'wood cutting', 'लकड़ी काटना', 'மரம் வெட்டுதல்'
            ],
            'Furniture Making': [
                'furniture', 'फर्नीचर', 'பர்னிச்சர்', 'ఫర్నిచర్', 'ಪೀಠೋಪಕರಣ',
                'carpenter', 'carpentry', 'बढ़ई', 'தச்சு', 'వడ్రంగి', 'ಬಡಗಿ',
                'furniture making', 'फर्नीचर बनाना'
            ],
            'Door Fitting': [
                'door', 'दरवाजा', 'கதவு', 'తలుపు', 'ಬಾಗಿಲು',
                'door fitting', 'door installation', 'दरवाजा लगाना', 'கதவு பொருத்துதல்'
            ],
            
            # PAINTING
            'Wall Painting': [
                'paint', 'painting', 'पेंटिंग', 'रंग', 'வண்ணம்', 'పెయింటింగ్', 'ಪೇಂಟಿಂಗ್',
                'wall paint', 'house painting', 'दीवार पेंटिंग'
            ],
            'Color Mixing': [
                'color', 'रंग', 'வண்ணம்', 'రంగు', 'ಬಣ್ಣ',
                'color mixing'
            ],
            
            # DRIVING
            'Vehicle Driving': [
                'drive', 'driving', 'driver', 'ड्राइविंग', 'ड्राइवर', 'ஓட்டுதல்', 'డ్రైవింగ్', 'ಚಾಲನೆ',
                'car driving', 'truck driving'
            ],
            
            # TAILORING
            'Dress Stitching': [
                'stitch', 'stitching', 'tailor', 'सिलाई', 'दर्जी', 'தையல்', 'కుట్టు', 'ಹೊಲಿಗೆ',
                'dress', 'cloth', 'कपड़ा'
            ],
            'Blouse Stitching': [
                'blouse', 'ब्लाउज', 'புடவை', 'బ్లౌజ్', 'ಬ್ಲೌಸ್'
            ],
            'Saree Fall': [
                'saree', 'साड़ी', 'புடவை', 'చీర', 'ಸೀರೆ',
                'fall', 'saree fall'
            ],
            'Churidar Making': [
                'churidar', 'चूड़ीदार', 'சுரிதார்', 'చుడిదార్', 'ಚುಡಿದಾರ'
            ],
            
            # MECHANICS
            'General Repair': [
                'repair', 'mechanic', 'मरम्मत', 'मैकेनिक', 'பழுது', 'రిపేర్', 'ದುರಸ್ತಿ',
                'fix', 'fixing'
            ],
            'Two Wheeler Repair': [
                'bike', 'motorcycle', 'scooter', 'बाइक', 'स्कूटर', 'பைக்', 'బైక్', 'ಬೈಕ್',
                'two wheeler'
            ],
            'Four Wheeler Repair': [
                'car', 'vehicle', 'कार', 'गाड़ी', 'கார்', 'కార్', 'ಕಾರು',
                'four wheeler'
            ],
            
            # MOBILE REPAIR
            'Mobile Repair': [
                'mobile', 'phone', 'मोबाइल', 'फोन', 'மொபைல்', 'ఫోన్', 'ಮೊಬೈಲ್',
                'mobile repair', 'phone repair'
            ],
            'Screen Replacement': [
                'screen', 'display', 'स्क्रीन', 'डिस्प्ले', 'திரை', 'స్క్రీన్', 'ಪರದೆ',
                'screen replacement', 'screen repair'
            ],
            'Battery Replacement': [
                'battery', 'बैटरी', 'பேட்டரி', 'బ్యాటరీ', 'ಬ್ಯಾಟರಿ',
                'battery change', 'battery replacement'
            ],
            'Software Troubleshooting': [
                'software', 'सॉफ्टवेयर', 'மென்பொருள்', 'సాఫ్ట్‌వేర్', 'ಸಾಫ್ಟ್‌ವೇರ್',
                'software issue', 'software problem'
            ],
            
            # BEAUTY/SALON
            'Hair Cutting': [
                'hair', 'haircut', 'बाल', 'हेयरकट', 'முடி', 'హెయిర్', 'ಕೂದಲು',
                'hair cut', 'हेयर कट', 'ஹேர் கட்'
            ],
            'Facial Treatment': [
                'facial', 'फेशियल', 'முக', 'ఫేషియల్', 'ಫೇಶಿಯಲ್',
                'face treatment'
            ],
            'Makeup': [
                'makeup', 'मेकअप', 'ஒப்பனை', 'మేకప్', 'ಮೇಕಪ್',
                'make up', 'मेक अप'
            ],
            'Beauty Parlor': [
                'beauty', 'parlor', 'parlour', 'salon', 'ब्यूटी', 'पार्लर',
                'அழகு', 'సెలూన్', 'ಬ್ಯೂಟಿ', 'ಪಾರ್ಲರ್'
            ],
        }
        
        # Job title patterns
        self.job_titles = {
            'Electrician': [
                'electrician', 'electric', 'इलेक्ट्रीशियन', 'மின்சார', 'ఎలక్ట్రీషియన్', 'ಎಲೆಕ್ಟ್ರಿಷಿಯನ್'
            ],
            'Plumber': [
                'plumber', 'plumbing', 'प्लंबर', 'பிளம்பர்', 'ప్లంబర్', 'ಪ್ಲಂಬರ್'
            ],
            'Carpenter': [
                'carpenter', 'carpentry', 'बढ़ई', 'தச்சு', 'వడ్రంగి', 'ಬಡಗಿ'
            ],
            'Welder': [
                'welder', 'welding', 'वेल्डर', 'வெல்டர்', 'వెల్డర్', 'ವೆಲ್ಡರ್'
            ],
            'Painter': [
                'painter', 'painting', 'पेंटर', 'ஓவியர்', 'పెయింటర్', 'ಪೇಂಟರ್'
            ],
            'Driver': [
                'driver', 'driving', 'ड्राइवर', 'ஓட்டுநர்', 'డ్రైవర్', 'ಚಾಲಕ'
            ],
            'Tailor': [
                'tailor', 'दर्जी', 'தையல்காரர்', 'దర్జీ', 'ಟೈಲರ್'
            ],
            'Mechanic': [
                'mechanic', 'मैकेनिक', 'மெக்கானிக்', 'మెకానిక్', 'ಮೆಕ್ಯಾನಿಕ್'
            ],
            'Beautician': [
                'beautician', 'beauty', 'parlor', 'ब्यूटीशियन', 'அழகு', 'బ్యూటీషియన్', 'ಬ್ಯೂಟಿ'
            ],
        }
    
    def extract_skills(self, text: str) -> List[Dict]:
        """Extract skills with aggressive multilingual matching"""
        text_lower = text.lower()
        extracted = []
        seen_skills = set()
        
        # Match against all multilingual keywords
        for skill_name, keywords in self.multilingual_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if skill_name not in seen_skills:
                        category = self._get_category(skill_name)
                        extracted.append({
                            'skill': skill_name,
                            'category': category,
                            'confidence': 0.95,
                            'method': 'multilingual_keyword'
                        })
                        seen_skills.add(skill_name)
                        break  # Found this skill, move to next
        
        return extracted
    
    def _get_category(self, skill_name: str) -> str:
        """Get category for a skill"""
        match = self.skill_taxonomy[self.skill_taxonomy['skill_name'] == skill_name]
        if not match.empty:
            return match.iloc[0]['category']
        return 'General Skills'
    
    def extract_experience_years(self, text: str) -> int:
        """Extract years of experience - multilingual"""
        patterns = [
            # English
            r'(\d+)\s*(?:years?|yrs?|year)',
            # Hindi
            r'(\d+)\s*(?:साल|वर्ष|वर्षों)',
            # Tamil
            r'(\d+)\s*(?:வருட|வருடம்|வருடங்கள்)',
            # Telugu
            r'(\d+)\s*(?:సంవత్సర|సంవత్సరాల)',
            # Kannada
            r'(\d+)\s*(?:ವರ್ಷ|ವರ್ಷದ)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        
        return 0
    
    def extract_job_title(self, text: str) -> str:
        """Extract job title - multilingual"""
        text_lower = text.lower()
        
        for title, keywords in self.job_titles.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return title
        
        return ""
    
    def extract_from_utterance(self, text: str) -> Dict:
        """Complete extraction"""
        skills = self.extract_skills(text)
        experience = self.extract_experience_years(text)
        job_title = self.extract_job_title(text)
        
        # Get categories
        categories = list(set([s['category'] for s in skills]))
        primary_category = categories[0] if categories else ""
        
        return {
            'text': text,
            'skills': skills,
            'num_skills': len(skills),
            'experience_years': experience,
            'job_title': job_title,
            'categories': categories,
            'primary_category': primary_category
        }


# Quick test
if __name__ == "__main__":
    extractor = MultilingualSkillExtractor()
    
    test_cases = [
        "I have 8 years experience in electrical work. I can do house wiring, fan installation.",
        "मैं वेल्डिंग का काम करता हूं। स्टील फैब्रिकेशन, गेट बनाना सब आता है।",
        "நான் தச்சு வேலை செய்கிறேன். மரம் வெட்டுதல், பர்னிச்சர் செய்தல் தெரியும்।",
        "Mobile repair mechanic. Screen replacement, battery change, software issues all I fix.",
        "ನಾನು ಬ್ಯೂಟಿ ಪಾರ್ಲರ್ ನಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ. ಹೇರ್ ಕಟ್, ಫೇಶಿಯಲ್, ಮೇಕಪ್ ಎಲ್ಲಾ ತಿಳಿದಿದೆ.",
    ]
    
    print("\n" + "="*70)
    print("Multilingual Skill Extraction Test")
    print("="*70)
    
    for i, text in enumerate(test_cases, 1):
        result = extractor.extract_from_utterance(text)
        print(f"\n{i}. Text: {text[:60]}...")
        print(f"   Skills: {[s['skill'] for s in result['skills']]}")
        print(f"   Job: {result['job_title']}")
        print(f"   Experience: {result['experience_years']} years")
    
    print("\n" + "="*70)
