# =========================================================
# AI RESUME CODE GRAPH INGESTION
# =========================================================

import os
import ast
import re
import hashlib
import kuzu

# =========================================================
# DATABASE PATH
# =========================================================

DB_PATH = "ai_resume_db"

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    db = kuzu.Database(DB_PATH)

    conn = kuzu.Connection(db)

    return conn

# =========================================================
# ESCAPE STRINGS
# =========================================================

def escape(value):

    if value is None:
        return ""

    return str(value).replace("\\", "\\\\").replace("'", "\\'")

# =========================================================
# CREATE SCHEMA
# =========================================================

def create_code_graph_schema(conn):

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE PyFile(
            path STRING,
            name STRING,
            PRIMARY KEY(path)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE CodeModule(
            name STRING,
            PRIMARY KEY(name)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE PyFunction(
            full_name STRING,
            name STRING,
            file_path STRING,
            PRIMARY KEY(full_name)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE CypherQuery(
            id STRING,
            query_type STRING,
            query_text STRING,
            PRIMARY KEY(id)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE CodeNodeLabel(
            name STRING,
            PRIMARY KEY(name)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE NODE TABLE CodeRelLabel(
            name STRING,
            PRIMARY KEY(name)
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE REL TABLE IMPORTS(
            FROM PyFile TO CodeModule
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE REL TABLE CONTAINS_FUNCTION(
            FROM PyFile TO PyFunction
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE REL TABLE EXECUTES_QUERY(
            FROM PyFile TO CypherQuery
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE REL TABLE USES_NODE_LABEL(
            FROM PyFile TO CodeNodeLabel
        )
        """)
    except:
        pass

    # -----------------------------------------------------

    try:
        conn.execute("""
        CREATE REL TABLE USES_REL_LABEL(
            FROM PyFile TO CodeRelLabel
        )
        """)
    except:
        pass

    print("✅ Code graph schema ready")

# =========================================================
# GET PYTHON FILES
# =========================================================

def get_python_files(project_path="."):

    python_files = []

    ignore_folders = {
        ".git",
        "__pycache__",
        "venv",
        ".venv",
        "env",
        ".env",
        "ai_resume_db"
    }

    for root, dirs, files in os.walk(project_path):

        dirs[:] = [
            d for d in dirs
            if d not in ignore_folders
        ]

        for file in files:

            if file.endswith(".py"):

                file_path = os.path.join(root, file)

                file_path = file_path.replace("\\", "/")

                if file_path.startswith("./"):
                    file_path = file_path[2:]

                python_files.append(file_path)

    return python_files

# =========================================================
# EXTRACT IMPORTS
# =========================================================

def extract_imports(tree):

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:

                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            if node.module:

                imports.append(node.module)

    return list(set(imports))

# =========================================================
# EXTRACT FUNCTIONS
# =========================================================

def extract_functions(tree, file_path):

    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            function_name = node.name

            full_name = f"{file_path}::{function_name}"

            functions.append({
                "name": function_name,
                "full_name": full_name,
                "file_path": file_path
            })

    return functions

# =========================================================
# EXTRACT CYPHER QUERIES
# =========================================================

def extract_cypher_queries(tree):

    queries = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Attribute):

                if node.func.attr == "execute":

                    if len(node.args) > 0:

                        arg = node.args[0]

                        query_text = None

                        if isinstance(arg, ast.Constant):

                            if isinstance(arg.value, str):

                                query_text = arg.value

                        if query_text:

                            clean_query = query_text.strip()

                            queries.append(clean_query)

    return queries

# =========================================================
# QUERY TYPE
# =========================================================

def get_query_type(query):

    query_upper = query.strip().upper()

    if query_upper.startswith("CREATE NODE TABLE"):
        return "CREATE_NODE_TABLE"

    if query_upper.startswith("CREATE REL TABLE"):
        return "CREATE_REL_TABLE"

    if query_upper.startswith("MERGE"):
        return "MERGE_DATA"

    if query_upper.startswith("MATCH"):
        return "MATCH_QUERY"

    if "RETURN" in query_upper:
        return "RETURN_QUERY"

    return "OTHER"

# =========================================================
# EXTRACT NODE LABELS
# =========================================================

def extract_node_labels(query):

    labels = set()

    node_pattern = r"\([a-zA-Z_]*:([A-Za-z_][A-Za-z0-9_]*)"

    for match in re.findall(node_pattern, query):

        labels.add(match)

    create_node_pattern = r"CREATE\s+NODE\s+TABLE\s+([A-Za-z_][A-Za-z0-9_]*)"

    for match in re.findall(create_node_pattern, query, re.IGNORECASE):

        labels.add(match)

    return list(labels)

# =========================================================
# EXTRACT REL LABELS
# =========================================================

def extract_relationship_labels(query):

    labels = set()

    rel_pattern = r"\[:([A-Za-z_][A-Za-z0-9_]*)\]"

    for match in re.findall(rel_pattern, query):

        labels.add(match)

    create_rel_pattern = r"CREATE\s+REL\s+TABLE\s+([A-Za-z_][A-Za-z0-9_]*)"

    for match in re.findall(create_rel_pattern, query, re.IGNORECASE):

        labels.add(match)

    return list(labels)

# =========================================================
# CREATE QUERY ID
# =========================================================

def create_query_id(file_path, query):

    raw_text = file_path + "::" + query

    return hashlib.md5(raw_text.encode("utf-8")).hexdigest()

# =========================================================
# INSERT FILE
# =========================================================

def insert_file(conn, file_path):

    file_name = os.path.basename(file_path)

    conn.execute(f"""
    MERGE (f:PyFile {{
        path: '{escape(file_path)}',
        name: '{escape(file_name)}'
    }})
    """)

# =========================================================
# INSERT IMPORTS
# =========================================================

def insert_imports(conn, file_path, imports):

    for module in imports:

        conn.execute(f"""
        MERGE (m:CodeModule {{
            name: '{escape(module)}'
        }})
        """)

        conn.execute(f"""
        MATCH (f:PyFile), (m:CodeModule)
        WHERE f.path = '{escape(file_path)}'
        AND m.name = '{escape(module)}'
        MERGE (f)-[:IMPORTS]->(m)
        """)

# =========================================================
# INSERT FUNCTIONS
# =========================================================

def insert_functions(conn, file_path, functions):

    for function in functions:

        conn.execute(f"""
        MERGE (fn:PyFunction {{
            full_name: '{escape(function["full_name"])}',
            name: '{escape(function["name"])}',
            file_path: '{escape(function["file_path"])}'
        }})
        """)

        conn.execute(f"""
        MATCH (f:PyFile), (fn:PyFunction)
        WHERE f.path = '{escape(file_path)}'
        AND fn.full_name = '{escape(function["full_name"])}'
        MERGE (f)-[:CONTAINS_FUNCTION]->(fn)
        """)

# =========================================================
# INSERT CYPHER QUERIES
# =========================================================

def insert_cypher_queries(conn, file_path, queries):

    for query in queries:

        query_id = create_query_id(file_path, query)

        query_type = get_query_type(query)

        conn.execute(f"""
        MERGE (q:CypherQuery {{
            id: '{escape(query_id)}',
            query_type: '{escape(query_type)}',
            query_text: '{escape(query)}'
        }})
        """)

        conn.execute(f"""
        MATCH (f:PyFile), (q:CypherQuery)
        WHERE f.path = '{escape(file_path)}'
        AND q.id = '{escape(query_id)}'
        MERGE (f)-[:EXECUTES_QUERY]->(q)
        """)

# =========================================================
# INSERT NODE LABELS
# =========================================================

def insert_node_labels(conn, file_path, labels):

    for label in labels:

        conn.execute(f"""
        MERGE (l:CodeNodeLabel {{
            name: '{escape(label)}'
        }})
        """)

        conn.execute(f"""
        MATCH (f:PyFile), (l:CodeNodeLabel)
        WHERE f.path = '{escape(file_path)}'
        AND l.name = '{escape(label)}'
        MERGE (f)-[:USES_NODE_LABEL]->(l)
        """)

# =========================================================
# INSERT REL LABELS
# =========================================================

def insert_relationship_labels(conn, file_path, labels):

    for label in labels:

        conn.execute(f"""
        MERGE (r:CodeRelLabel {{
            name: '{escape(label)}'
        }})
        """)

        conn.execute(f"""
        MATCH (f:PyFile), (r:CodeRelLabel)
        WHERE f.path = '{escape(file_path)}'
        AND r.name = '{escape(label)}'
        MERGE (f)-[:USES_REL_LABEL]->(r)
        """)

# =========================================================
# PROCESS FILE
# =========================================================

def process_file(conn, file_path):

    print(f"\n📄 Processing: {file_path}")

    try:

        with open(file_path, "r", encoding="utf-8") as file:

            source_code = file.read()

        tree = ast.parse(source_code)

    except Exception as error:

        print(f"⚠️ Error: {error}")

        return

    imports = extract_imports(tree)

    functions = extract_functions(tree, file_path)

    queries = extract_cypher_queries(tree)

    all_node_labels = set()

    all_rel_labels = set()

    for query in queries:

        for label in extract_node_labels(query):

            all_node_labels.add(label)

        for label in extract_relationship_labels(query):

            all_rel_labels.add(label)

    insert_file(conn, file_path)

    insert_imports(conn, file_path, imports)

    insert_functions(conn, file_path, functions)

    insert_cypher_queries(conn, file_path, queries)

    insert_node_labels(conn, file_path, list(all_node_labels))

    insert_relationship_labels(conn, file_path, list(all_rel_labels))

    print(f"   ✅ Imports found: {len(imports)}")
    print(f"   ✅ Functions found: {len(functions)}")
    print(f"   ✅ Queries found: {len(queries)}")
    print(f"   ✅ Node labels found: {len(all_node_labels)}")
    print(f"   ✅ Relationship labels found: {len(all_rel_labels)}")

# =========================================================
# MAIN
# =========================================================

def main():

    print("\n🚀 AI RESUME CODE GRAPH INGESTION STARTED\n")

    conn = get_connection()

    create_code_graph_schema(conn)

    python_files = get_python_files(".")

    print(f"✅ Found {len(python_files)} Python files\n")

    for file_path in python_files:

        process_file(conn, file_path)

    print("\n✅ Code graph ingestion completed successfully")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
