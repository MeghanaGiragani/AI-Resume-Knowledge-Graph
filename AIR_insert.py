# ==========================================
# IMPORT KUZU
# ==========================================

import kuzu


# ==========================================
# CONNECT DATABASE
# ==========================================

db = kuzu.Database("./resume_db.kuzu")

conn = kuzu.Connection(db)


# ==========================================
# INSERT PERSON DATA
# ==========================================

# Meghana

conn.execute("""

MERGE (:Person {

    id:1,
    name:'Meghana',
    education:'BTech',
    experience:1

})

""")


# Rahul

conn.execute("""

MERGE (:Person {

    id:2,
    name:'Rahul',
    education:'MCA',
    experience:2

})

""")


# Priya

conn.execute("""

MERGE (:Person {

    id:3,
    name:'Priya',
    education:'BSc',
    experience:1

})

""")


# ==========================================
# INSERT SKILLS
# ==========================================

conn.execute("""

MERGE (:Skill {

    id:1,
    skill_name:'Python'

})

""")


conn.execute("""

MERGE (:Skill {

    id:2,
    skill_name:'SQL'

})

""")


conn.execute("""

MERGE (:Skill {

    id:3,
    skill_name:'Java'

})

""")


conn.execute("""

MERGE (:Skill {

    id:4,
    skill_name:'Machine Learning'

})

""")


# ==========================================
# INSERT JOBS
# ==========================================

conn.execute("""

MERGE (:Job {

    id:1,
    job_role:'AI Engineer',
    company:'Google'

})

""")


conn.execute("""

MERGE (:Job {

    id:2,
    job_role:'Backend Developer',
    company:'Microsoft'

})

""")


conn.execute("""

MERGE (:Job {

    id:3,
    job_role:'Data Analyst',
    company:'Amazon'

})

""")


# ==========================================
# PERSON KNOWS SKILLS
# ==========================================

# Meghana knows Python

conn.execute("""

MATCH (p:Person), (s:Skill)

WHERE p.name='Meghana'
AND s.skill_name='Python'

MERGE (p)-[:KNOWS]->(s)

""")


# Meghana knows SQL

conn.execute("""

MATCH (p:Person), (s:Skill)

WHERE p.name='Meghana'
AND s.skill_name='SQL'

MERGE (p)-[:KNOWS]->(s)

""")


# Rahul knows Java

conn.execute("""

MATCH (p:Person), (s:Skill)

WHERE p.name='Rahul'
AND s.skill_name='Java'

MERGE (p)-[:KNOWS]->(s)

""")


# Priya knows Machine Learning

conn.execute("""

MATCH (p:Person), (s:Skill)

WHERE p.name='Priya'
AND s.skill_name='Machine Learning'

MERGE (p)-[:KNOWS]->(s)

""")


# ==========================================
# JOB REQUIRES SKILLS
# ==========================================

# AI Engineer requires Python

conn.execute("""

MATCH (j:Job), (s:Skill)

WHERE j.job_role='AI Engineer'
AND s.skill_name='Python'

MERGE (j)-[:REQUIRES]->(s)

""")


# AI Engineer requires ML

conn.execute("""

MATCH (j:Job), (s:Skill)

WHERE j.job_role='AI Engineer'
AND s.skill_name='Machine Learning'

MERGE (j)-[:REQUIRES]->(s)

""")


# Backend Developer requires Java

conn.execute("""

MATCH (j:Job), (s:Skill)

WHERE j.job_role='Backend Developer'
AND s.skill_name='Java'

MERGE (j)-[:REQUIRES]->(s)

""")


# Data Analyst requires SQL

conn.execute("""

MATCH (j:Job), (s:Skill)

WHERE j.job_role='Data Analyst'
AND s.skill_name='SQL'

MERGE (j)-[:REQUIRES]->(s)

""")


print("✅ Resume Graph Data Inserted Successfully")
