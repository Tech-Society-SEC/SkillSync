"""
SkillSync Dataset Generator
Generates synthetic datasets for ML pipeline:
1. Skill Taxonomy (standard skill categories)
2. Worker Utterances (for skill extraction training)
3. Job Listings (for recommendation system)
4. Worker Profiles (for testing)
5. Learning Resources (for upskilling recommendations)

Total: ~50,000 entries across all datasets
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# ============================================================================
# 1. SKILL TAXONOMY DATA
# ============================================================================

SKILL_CATEGORIES = {
    "Electrical Work": {
        "skills": [
            "Electrical Wiring", "Fan Installation", "Light Fitting", "Switch Board Repair",
            "Electrical Appliance Repair", "Motor Rewinding", "Voltage Testing",
            "Cable Installation", "Circuit Troubleshooting", "Generator Maintenance",
            "Inverter Installation", "Solar Panel Installation", "Transformer Repair",
            "Electrical Safety", "Three Phase Wiring", "Conduit Installation"
        ],
        "jobs": ["Electrician", "Electrical Helper", "Maintenance Electrician", "Industrial Electrician"]
    },
    "Plumbing": {
        "skills": [
            "Pipe Fitting", "Tap Repair", "Drainage Fixing", "Water Tank Installation",
            "Bathroom Fitting", "Leak Detection", "Sewage Line Repair", "Water Pump Installation",
            "Pipeline Welding", "Sanitary Fitting", "Water Heater Installation", "PVC Pipe Joining",
            "Bore Well Repair", "Water Purifier Installation", "Gutter Cleaning"
        ],
        "jobs": ["Plumber", "Plumber Assistant", "Sanitary Worker", "Pipeline Technician"]
    },
    "Carpentry": {
        "skills": [
            "Wood Cutting", "Furniture Making", "Door Fitting", "Window Installation",
            "Wood Polishing", "Cabinet Making", "Chair Repair", "Table Making",
            "Wood Carving", "Laminate Fitting", "Veneer Work", "Modular Kitchen Installation",
            "Bed Making", "Almirah Making", "Wood Finishing", "Furniture Assembly"
        ],
        "jobs": ["Carpenter", "Furniture Maker", "Wood Worker", "Carpentry Assistant"]
    },
    "Masonry & Construction": {
        "skills": [
            "Brick Laying", "Plastering", "Wall Painting", "Tile Fixing",
            "Concrete Mixing", "Cement Work", "Floor Leveling", "Roof Casting",
            "Building Construction", "Wall Demolition", "Marble Fitting", "Granite Fitting",
            "Waterproofing", "Building Estimation", "Foundation Work", "Column Construction"
        ],
        "jobs": ["Mason", "Construction Worker", "Painter", "Tiling Expert", "Construction Helper"]
    },
    "Welding & Metal Work": {
        "skills": [
            "Arc Welding", "Gas Welding", "Metal Cutting", "Gate Making",
            "Grill Fabrication", "Iron Work", "Steel Welding", "Aluminum Welding",
            "Metal Polishing", "Sheet Metal Work", "Metal Bending", "Welding Rod Selection",
            "Spot Welding", "TIG Welding", "MIG Welding", "Plasma Cutting"
        ],
        "jobs": ["Welder", "Fabricator", "Metal Worker", "Welding Helper"]
    },
    "Automotive Repair": {
        "skills": [
            "Two Wheeler Repair", "Four Wheeler Repair", "Engine Repair", "Brake Repair",
            "Battery Replacement", "Tyre Changing", "Oil Change", "Clutch Repair",
            "Suspension Repair", "Electrical Wiring (Auto)", "AC Repair (Auto)", "Denting",
            "Painting (Auto)", "Body Work", "Gear Box Repair", "Engine Tuning"
        ],
        "jobs": ["Mechanic", "Auto Electrician", "Two Wheeler Mechanic", "Denting Painter"]
    },
    "Tailoring & Garments": {
        "skills": [
            "Stitching", "Dress Making", "Alteration", "Blouse Stitching",
            "Saree Fall", "Pant Stitching", "Shirt Making", "Kids Dress Making",
            "Embroidery", "Hand Stitching", "Machine Stitching", "Pattern Cutting",
            "Fabric Selection", "Zipper Fixing", "Button Stitching", "Churidar Making"
        ],
        "jobs": ["Tailor", "Dress Maker", "Alteration Specialist", "Embroidery Worker"]
    },
    "Driving": {
        "skills": [
            "Car Driving", "Two Wheeler Riding", "Heavy Vehicle Driving", "Auto Driving",
            "Taxi Driving", "Goods Transport", "Route Knowledge", "Defensive Driving",
            "GPS Navigation", "Vehicle Maintenance", "Night Driving", "Highway Driving",
            "City Driving", "License Holding", "Customer Service (Driver)", "Loading Unloading"
        ],
        "jobs": ["Car Driver", "Truck Driver", "Auto Driver", "Delivery Driver", "Taxi Driver"]
    },
    "Cleaning & Housekeeping": {
        "skills": [
            "Floor Cleaning", "Toilet Cleaning", "Window Cleaning", "Dusting",
            "Mopping", "Vacuum Cleaning", "Dish Washing", "Laundry", "Ironing",
            "Kitchen Cleaning", "Garden Cleaning", "Waste Disposal", "Sanitization",
            "Deep Cleaning", "Office Cleaning", "Hospital Cleaning"
        ],
        "jobs": ["Cleaner", "Housekeeper", "Office Boy", "Janitor", "Sanitation Worker"]
    },
    "Cooking & Food Service": {
        "skills": [
            "South Indian Cooking", "North Indian Cooking", "Roti Making", "Curry Making",
            "Rice Cooking", "Snack Making", "Breakfast Making", "Tiffin Service",
            "Catering", "Food Serving", "Kitchen Management", "Knife Skills",
            "Food Hygiene", "Spice Mixing", "Sweet Making", "Tandoor Cooking"
        ],
        "jobs": ["Cook", "Chef Assistant", "Catering Worker", "Food Server", "Kitchen Helper"]
    },
    "Painting & Decoration": {
        "skills": [
            "Wall Painting", "Ceiling Painting", "Texture Painting", "Spray Painting",
            "Color Mixing", "Putty Work", "Primer Application", "Brush Work",
            "Roller Painting", "Stencil Work", "Asian Paints", "Exterior Painting",
            "Interior Painting", "Wood Painting", "Metal Painting", "Wall Paper Installation"
        ],
        "jobs": ["Painter", "Painting Contractor", "Decorator", "Painting Helper"]
    },
    "Mobile & Electronics Repair": {
        "skills": [
            "Mobile Screen Replacement", "Mobile Software Repair", "Battery Replacement",
            "Charging Port Repair", "Camera Repair", "Speaker Repair", "Water Damage Repair",
            "TV Repair", "Laptop Repair", "Computer Repair", "Hardware Troubleshooting",
            "Software Installation", "Data Recovery", "Motherboard Repair", "Soldering"
        ],
        "jobs": ["Mobile Technician", "Electronics Repair", "Computer Technician", "Hardware Engineer"]
    },
    "Agriculture & Farming": {
        "skills": [
            "Crop Cultivation", "Seed Sowing", "Harvesting", "Tractor Driving",
            "Irrigation", "Pesticide Spraying", "Fertilizer Application", "Weeding",
            "Animal Husbandry", "Dairy Farming", "Poultry Farming", "Organic Farming",
            "Fruit Picking", "Vegetable Farming", "Farm Maintenance", "Crop Protection"
        ],
        "jobs": ["Farm Worker", "Tractor Driver", "Agricultural Helper", "Dairy Worker"]
    },
    "Beauty & Salon": {
        "skills": [
            "Hair Cutting", "Hair Styling", "Beard Trimming", "Facial", "Massage",
            "Makeup", "Mehendi Application", "Nail Art", "Hair Coloring", "Hair Straightening",
            "Pedicure", "Manicure", "Threading", "Waxing", "Bridal Makeup", "Hair Spa"
        ],
        "jobs": ["Barber", "Beautician", "Salon Assistant", "Makeup Artist", "Hair Stylist"]
    },
    "Delivery & Logistics": {
        "skills": [
            "Package Delivery", "Food Delivery", "Route Planning", "Cash Collection",
            "Customer Service", "Two Wheeler Riding", "GPS Navigation", "Loading Unloading",
            "Warehouse Work", "Inventory Management", "Order Picking", "Packing",
            "Last Mile Delivery", "COD Collection", "Delivery Apps", "Time Management"
        ],
        "jobs": ["Delivery Boy", "Courier", "Warehouse Worker", "Logistics Helper"]
    },
    "Security & Safety": {
        "skills": [
            "Security Patrol", "CCTV Monitoring", "Gate Checking", "Visitor Management",
            "Fire Safety", "First Aid", "Emergency Response", "Access Control",
            "Night Duty", "Crowd Control", "Vehicle Checking", "Security Equipment",
            "Incident Reporting", "Physical Fitness", "Communication Skills", "Alert Monitoring"
        ],
        "jobs": ["Security Guard", "Watchman", "Security Supervisor", "Bouncer"]
    }
}

# ============================================================================
# 2. UTTERANCE PATTERNS (for generating worker speech)
# ============================================================================

UTTERANCE_PATTERNS = {
    "experience": [
        "I have {years} years of experience in {skill}",
        "I have been doing {skill} for {years} years",
        "I work as {job} for {years} years",
        "I know {skill} very well, worked for {years} years",
        "For the past {years} years I am doing {skill}",
        "{years} years experience in {skill} work"
    ],
    "skills_list": [
        "I know {skill1}, {skill2} and {skill3}",
        "I can do {skill1}, {skill2}, {skill3}",
        "I am expert in {skill1} and {skill2}",
        "My skills are {skill1}, {skill2}, {skill3}",
        "I do {skill1}, {skill2} and also {skill3}",
        "I specialize in {skill1} and {skill2}"
    ],
    "simple": [
        "I do {skill}",
        "I know {skill}",
        "I work in {skill}",
        "I am {job}",
        "{skill} is my work",
        "I am doing {skill}"
    ],
    "detailed": [
        "I am {job} with {years} years experience. I can do {skill1}, {skill2} and {skill3}",
        "I work as {job}. I know {skill1} and {skill2} very well",
        "My name is {name}. I do {skill1}, {skill2}. I have {years} years experience",
        "I am experienced {job}. I specialize in {skill1}, {skill2} and {skill3}",
        "I have been working as {job} for {years} years. My skills include {skill1}, {skill2}, {skill3}"
    ],
    "local_mixed": [
        "Naan {skill} pannuven",
        "Main {skill} ka kaam karta hoon",
        "I can do {skill} work very well",
        "{skill} aur {skill2} mujhe aata hai",
        "Enakku {skill} theriyum",
        "{years} saal se {skill} kar raha hoon"
    ]
}

# Common Indian names
NAMES = [
    "Ravi", "Kumar", "Ramesh", "Suresh", "Vijay", "Arun", "Prakash", "Selvam",
    "Murugan", "Raja", "Balu", "Ganesh", "Senthil", "Mani", "Manoj", "Dinesh",
    "Rajesh", "Karthik", "Vinod", "Santosh", "Gopal", "Mohan", "Ashok", "Sanjay",
    "Deepak", "Naveen", "Surya", "Arjun", "Krishna", "Shankar", "Anbu", "Saravanan"
]

# ============================================================================
# DATASET GENERATION FUNCTIONS
# ============================================================================

def create_skill_taxonomy():
    """Create standardized skill taxonomy dataset"""
    skills_data = []
    skill_id = 1
    
    for category, data in SKILL_CATEGORIES.items():
        for skill in data["skills"]:
            skills_data.append({
                "skill_id": skill_id,
                "skill_name": skill,
                "category": category,
                "related_jobs": ", ".join(data["jobs"]),
                "skill_level": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "popularity_score": round(random.uniform(0.5, 1.0), 2)
            })
            skill_id += 1
    
    return pd.DataFrame(skills_data)


def generate_worker_utterances(n=15000):
    """Generate synthetic worker utterances with labeled skills"""
    utterances = []
    
    for i in range(n):
        # Select random category and skills
        category = random.choice(list(SKILL_CATEGORIES.keys()))
        skills = SKILL_CATEGORIES[category]["skills"]
        jobs = SKILL_CATEGORIES[category]["jobs"]
        
        # Select pattern type
        pattern_type = random.choice(list(UTTERANCE_PATTERNS.keys()))
        pattern = random.choice(UTTERANCE_PATTERNS[pattern_type])
        
        # Generate utterance
        skill1 = random.choice(skills)
        skill2 = random.choice([s for s in skills if s != skill1])
        skill3 = random.choice([s for s in skills if s not in [skill1, skill2]])
        job = random.choice(jobs)
        years = random.randint(1, 20)
        name = random.choice(NAMES)
        
        utterance = pattern.format(
            skill=skill1,
            skill1=skill1,
            skill2=skill2,
            skill3=skill3,
            job=job,
            years=years,
            name=name
        )
        
        # Extract skills mentioned in utterance
        mentioned_skills = []
        for skill in skills:
            if skill.lower() in utterance.lower():
                mentioned_skills.append(skill)
        
        utterances.append({
            "utterance_id": i + 1,
            "text": utterance,
            "category": category,
            "extracted_skills": ", ".join(mentioned_skills) if mentioned_skills else skill1,
            "language": random.choice(["English", "Tamil", "Hindi", "Mixed"]),
            "confidence": round(random.uniform(0.7, 1.0), 2)
        })
    
    return pd.DataFrame(utterances)


def generate_job_listings(n=10000):
    """Generate job listings dataset"""
    jobs = []
    job_id = 1
    
    cities = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Kolkata", 
              "Coimbatore", "Madurai", "Trichy", "Salem", "Erode"]
    
    for category, data in SKILL_CATEGORIES.items():
        num_jobs = n // len(SKILL_CATEGORIES)
        
        for _ in range(num_jobs):
            job_title = random.choice(data["jobs"])
            num_skills = random.randint(2, 5)
            required_skills = random.sample(data["skills"], num_skills)
            
            salary_min = random.randint(8000, 25000)
            salary_max = salary_min + random.randint(5000, 15000)
            
            jobs.append({
                "job_id": job_id,
                "job_title": job_title,
                "category": category,
                "required_skills": ", ".join(required_skills),
                "experience_required": random.choice(["0-1 years", "1-3 years", "3-5 years", "5+ years"]),
                "salary_range": f"₹{salary_min}-{salary_max}",
                "location": random.choice(cities),
                "job_type": random.choice(["Full-time", "Part-time", "Contract", "Daily Wage"]),
                "posted_date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "company_type": random.choice(["Individual", "Small Business", "Company", "Contractor"]),
                "urgency": random.choice(["Low", "Medium", "High"])
            })
            job_id += 1
    
    return pd.DataFrame(jobs)


def generate_worker_profiles(n=15000):
    """Generate synthetic worker profiles"""
    profiles = []
    
    for i in range(n):
        # Select random category
        category = random.choice(list(SKILL_CATEGORIES.keys()))
        skills = SKILL_CATEGORIES[category]["skills"]
        
        # Generate profile
        num_skills = random.randint(2, 6)
        worker_skills = random.sample(skills, min(num_skills, len(skills)))
        
        age = random.randint(18, 60)
        experience = min(random.randint(0, age-18), 30)
        
        profiles.append({
            "worker_id": i + 1,
            "name": random.choice(NAMES),
            "age": age,
            "gender": random.choice(["Male", "Female"]),
            "primary_category": category,
            "skills": ", ".join(worker_skills),
            "years_experience": experience,
            "location": random.choice(["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Kolkata"]),
            "preferred_language": random.choice(["Tamil", "Hindi", "English", "Telugu", "Kannada"]),
            "phone_verified": random.choice([True, False]),
            "avg_rating": round(random.uniform(3.0, 5.0), 1),
            "jobs_completed": random.randint(0, 500),
            "availability": random.choice(["Available", "Busy", "Part-time"]),
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(profiles)


def generate_learning_resources(n=5000):
    """Generate learning resources (courses/videos) mapped to skills"""
    resources = []
    resource_id = 1
    
    resource_types = ["Video Tutorial", "Course", "Workshop", "Certification", "Hands-on Training"]
    platforms = ["YouTube", "Udemy", "Coursera", "Local Training Center", "Government Scheme", "NGO Program"]
    languages = ["Tamil", "Hindi", "English", "Telugu", "Multilingual"]
    
    for category, data in SKILL_CATEGORIES.items():
        num_resources = n // len(SKILL_CATEGORIES)
        
        for _ in range(num_resources):
            skill = random.choice(data["skills"])
            
            resources.append({
                "resource_id": resource_id,
                "title": f"Learn {skill} - Complete Guide",
                "skill_covered": skill,
                "category": category,
                "resource_type": random.choice(resource_types),
                "platform": random.choice(platforms),
                "language": random.choice(languages),
                "duration": f"{random.randint(1, 50)} hours" if random.choice([True, False]) else f"{random.randint(5, 60)} mins",
                "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "is_free": random.choice([True, True, False]),  # More free content
                "url": f"https://example.com/learn/{skill.lower().replace(' ', '-')}"
            })
            resource_id += 1
    
    return pd.DataFrame(resources)


def main():
    """Generate all datasets and save to files"""
    print("=" * 70)
    print("SkillSync Dataset Generator")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("datasets")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Skill Taxonomy
    print("\n[1/5] Generating Skill Taxonomy...")
    skill_taxonomy = create_skill_taxonomy()
    skill_taxonomy.to_csv(output_dir / "skill_taxonomy.csv", index=False)
    print(f"✓ Generated {len(skill_taxonomy)} skills across {len(SKILL_CATEGORIES)} categories")
    
    # 2. Worker Utterances
    print("\n[2/5] Generating Worker Utterances (for skill extraction)...")
    utterances = generate_worker_utterances(15000)
    utterances.to_csv(output_dir / "worker_utterances.csv", index=False)
    print(f"✓ Generated {len(utterances)} training utterances")
    
    # 3. Job Listings
    print("\n[3/5] Generating Job Listings...")
    jobs = generate_job_listings(10000)
    jobs.to_csv(output_dir / "job_listings.csv", index=False)
    print(f"✓ Generated {len(jobs)} job listings")
    
    # 4. Worker Profiles
    print("\n[4/5] Generating Worker Profiles...")
    profiles = generate_worker_profiles(15000)
    profiles.to_csv(output_dir / "worker_profiles.csv", index=False)
    print(f"✓ Generated {len(profiles)} worker profiles")
    
    # 5. Learning Resources
    print("\n[5/5] Generating Learning Resources...")
    resources = generate_learning_resources(5000)
    resources.to_csv(output_dir / "learning_resources.csv", index=False)
    print(f"✓ Generated {len(resources)} learning resources")
    
    # Summary
    total = len(skill_taxonomy) + len(utterances) + len(jobs) + len(profiles) + len(resources)
    print("\n" + "=" * 70)
    print(f"✓ DATASET GENERATION COMPLETE!")
    print(f"Total entries: {total:,}")
    print(f"Saved to: {output_dir.absolute()}")
    print("=" * 70)
    
    # Save summary
    summary = {
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_entries": total,
        "datasets": {
            "skill_taxonomy": len(skill_taxonomy),
            "worker_utterances": len(utterances),
            "job_listings": len(jobs),
            "worker_profiles": len(profiles),
            "learning_resources": len(resources)
        },
        "categories": list(SKILL_CATEGORIES.keys()),
        "total_unique_skills": len(skill_taxonomy)
    }
    
    with open(output_dir / "dataset_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✓ Summary saved to: {output_dir / 'dataset_summary.json'}")
    print("\nNext steps:")
    print("1. Review the generated datasets")
    print("2. Use 'worker_utterances.csv' for NLP skill extraction model training")
    print("3. Use 'job_listings.csv' for recommendation system")
    print("4. Use 'skill_taxonomy.csv' for skill normalization")
    print("5. Use 'learning_resources.csv' for upskilling recommendations")


if __name__ == "__main__":
    main()
