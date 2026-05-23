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
# AI JOB RECOMMENDATION SYSTEM
# ==========================================

# This query traverses the graph
# and recommends jobs based on skills

result = conn.execute("""

MATCH (p:Person)-[:KNOWS]->(s:Skill)<-[:REQUIRES]-(j:Job)

RETURN p.name,
       s.skill_name,
       j.job_role,
       j.company

""")


print("\n🚀 AI JOB RECOMMENDATIONS:\n")


while result.has_next():

    print(result.get_next())
