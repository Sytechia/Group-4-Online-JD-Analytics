
from controllers.db_connections import get_db_connection
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import io
import time
import spacy
nlp = spacy.load('en_core_web_md') #python -m spacy download en_core_web_md
session_username = 123


# Skill Set Metrics 
categories = {
    'soft_skills': {
        'Collaboration': ['Interpersonal skills', 'Teamwork', 'Leadership', 'Empathy', 'Conflict resolution', 
                          'Public speaking', 'Tolerance', 'Communication', 'Trust building', 'Cultural sensitivity', 
                          'Active listening', 'Feedback'],
        'Adaptability': ['Flexibility', 'Follows instructions', 'Improves based on feedback', 'Stress management', 
                         'Can adapt to working independently', 'Resilience', 'Learning agility', 'Self-motivation', 
                         'Openmindedness'],
        'Resourcefulness': ['Works well under pressure', 'Creative thinking', 'Troubleshooting', 'Problem-solving', 
                            'Innovative solutions', 'Organization', 'Problem identification', 'Risk management', 
                            'Critical thinking', 'Prioritization'],
        'Positive Attitude': ['Charismatic', 'Outgoing', 'Friendly', 'Welcoming', 'Patient', 'Motivating', 'Inspires others', 
                              'Gratitude', 'Humility', 'Constructive communication', 'Kindness', 'Mindfulness'],
        'Work Ethic': ['Motivated', 'Physical or mental stamina', 'Perform effectively in a deadline environment', 
                       'Positive work ethic', 'Determined', 'Focused', 'Concentration', 'Accountability', 'Initiative', 
                       'Continuous learning', 'Discipline', 'Reliability'],
        'Willingness to learn': ['Active listener', 'Ability to follow instructions', 'Accepts feedback well', 
                                 'Self-awareness', 'Professionalism', 'Willingness to try new things', 'Curiosity', 
                                 'Growth mindset', 'Reflection', 'Information gathering', 'Self-directed learning'],
        'Critical Thinking': ['Efficiency', 'Strategic planning', 'Artistic ability', 'Scheduling', 'Negotiation', 
                              'Critical observation', 'Workflow management', 'Implementing change', 'Data interpretation', 
                              'Problem analysis', 'Risk assessment', 'Hypothesis testing', 'Systematic thinking', 
                              'Contextual understanding']
    },
    'hard_skills': {
        'Years of Experience': '0-10000 HRS',  
        'Industry Certifications': 'Certifications',  
        'Qualifications': 'Education in the field'  
    }
}
#Plot Soft Skills
def soft_skills(proportions_soft_skills):
    time.sleep(1)
    labels = ['Collaboration', 'Adaptability', 'Resourcefulness', 'Positive Attitude', 'Work Ethic', 'Willingness to Learn', 'Critical Thinking']
    N_SOFT_SKILLS = len(proportions_soft_skills)
    proportions_soft_skills = np.append(proportions_soft_skills, 1)
    theta = np.linspace(0, 2 * np.pi, N_SOFT_SKILLS, endpoint=False)
    x = np.append(np.sin(theta), 0)
    y = np.append(np.cos(theta), 0)
    triangles_soft_skills = [[N_SOFT_SKILLS, i, (i + 1) % N_SOFT_SKILLS] for i in range(N_SOFT_SKILLS)]
    triang_backgr = tri.Triangulation(x, y, triangles_soft_skills)
    triang_foregr = tri.Triangulation(x * proportions_soft_skills, y * proportions_soft_skills, triangles_soft_skills)
    
    cmap = plt.cm.rainbow_r
    colors = np.linspace(0, 1, N_SOFT_SKILLS + 1)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    ax.tripcolor(triang_backgr, colors, cmap=cmap, shading='gouraud', alpha=0.4)
    ax.tripcolor(triang_foregr, colors, cmap=cmap, shading='gouraud', alpha=0.8)
    ax.triplot(triang_backgr, color='white', lw=2)
    
    for label, proportion, xi, yi in zip(labels, proportions_soft_skills[:-1], x, y):
        ax.text(xi * 1.1, yi * 1.1, f'{label}: {int(proportion * 100)}%',
                ha='left' if xi > 0.1 else 'right' if xi < -0.1 else 'center',
                va='bottom' if yi > 0.1 else 'top' if yi < -0.1 else 'center')
    
    ax.axis('off')
    ax.set_aspect('equal')
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

    img_io2 = io.BytesIO()
    plt.savefig(img_io2, format='png', transparent=True, bbox_inches='tight')
    img_io2.seek(0)
    plt.close(fig)
    print("Soft skills plot generated")
    return img_io2

#Plot Hard Skills
def hard_skills(proportions_hard_skills):
        
        labels = ['Year(s) of Experience', 'Industry Certifications', 'Qualifications']
        N_HARD_SKILLS = len(proportions_hard_skills)
        proportions_hard_skills = np.append(proportions_hard_skills, 1)
        theta = np.linspace(0, 2 * np.pi, N_HARD_SKILLS, endpoint=False)
        x = np.append(np.sin(theta), 0)
        y = np.append(np.cos(theta), 0)
        triangles_HARD_SKILLS = [[N_HARD_SKILLS, i, (i + 1) % N_HARD_SKILLS] for i in range(N_HARD_SKILLS)]
        triang_backgr = tri.Triangulation(x, y, triangles_HARD_SKILLS)
        triang_foregr = tri.Triangulation(x * proportions_hard_skills, y * proportions_hard_skills, triangles_HARD_SKILLS)
        
        cmap = plt.cm.rainbow_r
        colors = np.linspace(0, 1, N_HARD_SKILLS + 1)
        
        fig1, ax = plt.subplots(figsize=(6, 6))
        
        ax.tripcolor(triang_backgr, colors, cmap=cmap, shading='gouraud', alpha=0.4)
        ax.tripcolor(triang_foregr, colors, cmap=cmap, shading='gouraud', alpha=0.8)
        ax.triplot(triang_backgr, color='white', lw=2)
        
        for label, proportion, xi, yi in zip(labels, proportions_hard_skills[:-1], x, y):
            ax.text(xi * 1.1, yi * 1.1, f'{label}: {int(proportion * 100)}%',
                    ha='left' if xi > 0.1 else 'right' if xi < -0.1 else 'center',
                    va='bottom' if yi > 0.1 else 'top' if yi < -0.1 else 'center')
        
        ax.axis('off')
        ax.set_aspect('equal')
        plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)

        img_io = io.BytesIO()
        plt.savefig(img_io, format='png', transparent=True, bbox_inches='tight')
        img_io.seek(0)
        plt.close()
        print("Hard skills plot generated")
        
        return img_io
        
    
def check_metrics_for_plot(session_username):
    # check if the skills metric is not None
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT soft_skills, hard_skills FROM userdata WHERE username = ?", (session_username,))
    row = cur.fetchone()

    if row:
        soft_skills_str = row['soft_skills']  # Should be a comma-separated string from the database
        hard_skills_str = row['hard_skills']

        if soft_skills_str and hard_skills_str:
            # Ensure proper conversion of strings to float
            try:
                soft_skills_list = [float(skill.strip()) for skill in soft_skills_str.split(',')]
                hard_skills_list = [float(skill.strip()) for skill in hard_skills_str.split(',')]
                return soft_skills_list, hard_skills_list  
            except ValueError:
                # Handle conversion errors
                print("Error: Could not convert soft or hard skills to float.")
                return None, None
    return None, None  

# Example user-provided skills and hard skills
user_soft_skills = ['Teamwork', 'Leadership', 'Communication', 'Problem-solving', 'Critical thinking']
user_experience_hours = 5000  # Example hours of experience (halfway to 10,000)
user_certifications = 3  # Example certifications
user_qualification = 'Bachelor\'s Degree'  # Example education qualification

# Function to check similarity using spacy
def get_skill_similarity(skill1, skill2):
    doc1 = nlp(skill1)
    doc2 = nlp(skill2)
    return doc1.similarity(doc2)

# Function to check if a user-provided skill matches or is similar to any skill in a category
def match_skills_with_synonyms(user_skills, category_skills):
    matched_skills = []
    similarity_threshold = 0.7  # Set similarity threshold (0 to 1, 1 being identical)
    
    for user_skill in user_skills:
        # Ensure user_skill is a string
        if not isinstance(user_skill, str):
            raise ValueError("User skill should be a string.")
        for skill in category_skills:
            # Ensure skill is a string
            if not isinstance(skill, str):
                raise ValueError("Category skill should be a string.")
            similarity = get_skill_similarity(user_skill, skill)
            if similarity >= similarity_threshold:
                matched_skills.append((user_skill, skill, similarity))
    
    return matched_skills

# Function to score each soft skill category considering synonyms/similar skills
def calculate_soft_skills_score(user_skills, soft_skill_categories):
    category_scores = {}
    max_score_per_category = 1  # Each category worth 1.0 points
    
    for category, skills in soft_skill_categories.items():
        matched_skills = match_skills_with_synonyms(user_skills, skills)
        matched_count = len(matched_skills)
        # Normalize to 1.0 (scale the number of matched skills relative to total skills)
        category_scores[category] = min(matched_count / len(skills), 1.0)

    return category_scores

# Function to score hard skills (experience, certifications, qualifications)
def calculate_hard_skills_score(user_experience, user_certifications, user_qualification):
    # Experience score based on hours (scaled to 100 points, normalized to 1.0)
    max_experience_hours = 10000
    experience_score = min(user_experience / max_experience_hours, 1.0)
    
    # Certifications score (scaled to 100 points, normalized to 1.0)
    max_certifications = 5  # Assume 5+ certifications gets full points
    certification_score = min(user_certifications / max_certifications, 1.0)
    
    # Qualification score (scaled to 100 points, normalized to 1.0)
    qualifications_score_map = {
        'High School': 0.4,
        'Associate Degree': 0.6,
        'Bachelor\'s Degree': 0.8,
        'Master\'s Degree': 0.9,
        'PhD': 1.0
    }
    qualification_score = qualifications_score_map.get(user_qualification, 0)
    
    # Hard skills result as a dictionary
    return {
        'Experience': experience_score,
        'Certifications': certification_score,
        'Qualifications': qualification_score
    }

# Calculate total profile score
def calculate_total_score(user_soft_skills, user_experience, user_certifications, user_qualification, categories):
    # Soft Skills Score
    soft_skills_scores = calculate_soft_skills_score(user_soft_skills, categories['soft_skills'])
    
    # Hard Skills Score
    hard_skills_scores = calculate_hard_skills_score(user_experience, user_certifications, user_qualification)
    
    return soft_skills_scores, hard_skills_scores, # Cap score at 10.0

# Calculate the score for the user profile
soft_skills_scores, hard_skills_scores = calculate_total_score(user_soft_skills, user_experience_hours, user_certifications, user_qualification, categories)

formatted_soft_skills_scores = {k: float(format(v, '.2f')) for k, v in soft_skills_scores.items()}
formatted_hard_skills_scores = {k: float(format(v, '.2f')) for k, v in hard_skills_scores.items()}


soft_skills_scores_only = str(tuple(list(formatted_soft_skills_scores.values())))[1:-1]
hard_skills_scores_only = str(tuple(list(formatted_hard_skills_scores.values())))[1:-1]


# Output the result

# con = get_db_connection()
# cur = con.cursor()
# cur.execute("UPDATE userdata SET soft_skills = ?, hard_skills = ?  WHERE username = ?",(soft_skills_scores_only,hard_skills_scores_only,session_username,))
# con.commit()
# con.close()