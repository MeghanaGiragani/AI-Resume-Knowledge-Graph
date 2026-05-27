# =========================================================
# AI RESUME CODE GRAPH QUERY
# =========================================================

import kuzu

# =========================================================
# DATABASE CONNECTION
# =========================================================

db = kuzu.Database("resume_db")

conn = kuzu.Connection(db)

# =========================================================
# PRINT RESULTS
# =========================================================

def print_results(result):

    while result.has_next():

        row = result.get_next()

        print(row)

# =========================================================
# SHOW ALL FILES
# =========================================================

def show_all_files():

    print("\n📄 ALL PYTHON FILES\n")

    result = conn.execute("""

    MATCH (f:PyFile)

    RETURN f.path

    """)

    print_results(result)

# =========================================================
# SHOW IMPORTS BY FILE
# =========================================================

def show_imports(file_name):

    print(f"\n📌 IMPORTS IN {file_name}\n")

    result = conn.execute(f"""

    MATCH (f:PyFile)-[:IMPORTS]->(m:CodeModule)

    WHERE f.name='{file_name}'

    RETURN m.name

    """)

    print_results(result)

# =========================================================
# SHOW FUNCTIONS BY FILE
# =========================================================

def show_functions(file_name):

    print(f"\n📌 FUNCTIONS IN {file_name}\n")

    result = conn.execute(f"""

    MATCH (f:PyFile)-[:CONTAINS_FUNCTION]->(fn:PyFunction)

    WHERE f.name='{file_name}'

    RETURN fn.name

    """)

    print_results(result)

# =========================================================
# SHOW CYPHER QUERIES
# =========================================================

def show_queries(file_name):

    print(f"\n📌 CYPHER QUERIES IN {file_name}\n")

    result = conn.execute(f"""

    MATCH (f:PyFile)-[:EXECUTES_QUERY]->(q:CypherQuery)

    WHERE f.name='{file_name}'

    RETURN q.query_text

    """)

    print_results(result)

# =========================================================
# MAIN MENU
# =========================================================

while True:

    print("\n========== AI RESUME CODE GRAPH ==========")

    print("1. Show All Files")

    print("2. Show Imports By File")

    print("3. Show Functions By File")

    print("4. Show Cypher Queries By File")

    print("5. Exit")

    choice = input("\nEnter Choice: ")

    if choice == "1":

        show_all_files()

    elif choice == "2":

        file_name = input("Enter File Name: ")

        show_imports(file_name)

    elif choice == "3":

        file_name = input("Enter File Name: ")

        show_functions(file_name)

    elif choice == "4":

        file_name = input("Enter File Name: ")

        show_queries(file_name)

    elif choice == "5":

        print("👋 Exiting")

        break

    else:

        print("❌ Invalid Choice")
