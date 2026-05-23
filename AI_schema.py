# ==========================================
# AI RESUME KNOWLEDGE GRAPH PROJECT
# ==========================================

# Import Kuzu library
import kuzu


# ==========================================
# CONNECT DATABASE
# ==========================================

# Create database connection
db = kuzu.Database("./resume_db.kuzu")

conn = kuzu.Connection(db)


# ==========================================
# CREATE PERSON NODE TABLE
# ==========================================

conn.execute("""

CREATE NODE TABLE Person(

    id INT64,
    name STRING,
    education STRING,
    experience INT64,

    PRIMARY KEY(id)

)

""")


# ==========================================
# CREATE SKILL NODE TABLE
# ==========================================

conn.execute("""

CREATE NODE TABLE Skill(

    id INT64,
    skill_name STRING,

    PRIMARY KEY(id)

)

""")


# ==========================================
# CREATE JOB NODE TABLE
# ==========================================

conn.execute("""

CREATE NODE TABLE Job(

    id INT64,
    job_role STRING,
    company STRING,

    PRIMARY KEY(id)

)

""")


# ==========================================
# CREATE RELATIONSHIP TABLES
# ==========================================

conn.execute("""

CREATE REL TABLE KNOWS(

    FROM Person TO Skill

)

""")


conn.execute("""

CREATE REL TABLE REQUIRES(

    FROM Job TO Skill

)

""")


print("✅ Schema Created Successfully")
