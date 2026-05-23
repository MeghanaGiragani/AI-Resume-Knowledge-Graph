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
# QUERY PERSON SKILLS
# ==========================================

result = conn.execute("""

MATCH (p:Person)-[:KNOWS]->(s:Skill)

RETURN p.name, s.skill_name

""")


print("\n🎯 PERSON SKILLS:\n")


while result.has_next():

    print(result.get_next())


# ==========================================
# QUERY JOB REQUIREMENTS
# ==========================================

result = conn.execute("""

MATCH (j:Job)-[:REQUIRES]->(s:Skill)

RETURN j.job_role, s.skill_name

""")


print("\n💼 JOB REQUIREMENTS:\n")


while result.has_next():

    print(result.get_next())
