import ast, os
from logs.logs import logger
import pandas as pd


def parse_node(node,classdef_name,called_functions,dfs,calling_function):
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            value_id = node.func.value.id
            if value_id == 'self':
                value_id = classdef_name
            elif value_id == "logger":
                logger.info(f"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                return
            called_function_name = value_id + '.' + node.func.attr
            called_functions.add(called_function_name)
            dfs.append(pd.DataFrame({'head': [calling_function], 'relation': ['calls'], 'tail': [called_function_name]}))
        elif isinstance(node.func.value, ast.Call):
            parse_node(node.func.value, classdef_name, called_functions, dfs,calling_function)

def get_called_functions(tree,classdef_name,dfs):
    logger.debug(f'Complete Function \n *****1111111111***** : ${ast.dump(tree, indent=4)} ******1111111111******* ')
    called_functions = set()
    calling_function = classdef_name + '.' + tree.name
    node_index = 0
    for node in ast.walk(tree):
        node_index = node_index + 1
        if isinstance(node, ast.Call):
            logger.debug(f"nodeIndex {node_index}-{type(node.func)}")
            parse_node(node,classdef_name,called_functions,dfs,calling_function)
        else:
            logger.debug(f"No Function call found {node_index} - \n Fields {node._fields}")
    return called_functions


def process_classdef(tree,classdef_name,dfs):
    function_calls = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)):
            logger.debug(f"Function Def = {node.name}")
            called_functions = get_called_functions(node,classdef_name,dfs)
            function_calls[node.name] = list(called_functions)
    return dfs


def process_components(tree):
    imports = {}
    add_prefix = ""
    node_index = 0
    dfs = []
    for node in ast.walk(tree):
        node_index = node_index + 1
        logger.debug(f"nodeIndex {node_index} Node {node}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                alias.name = add_prefix + alias.name + '.py'
                logger.debug(f" Import = {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                node.module = add_prefix + node.module + '.py'
                imports[node.module] = [name.name for name in node.names]
                logger.debug(f"ImportFrom = {imports[node.module]}")
        elif isinstance(node, ast.ClassDef):
            classdef_name = node.name
            logger.debug(f"class Def ={classdef_name}")
            dfs = process_classdef(node,classdef_name,dfs)
    return dfs, imports


def write2_neo4j(df):
    from neo4j import GraphDatabase
    # Assuming 'df' is the DataFrame containing your data
    # Neo4j connection details
    uri = "bolt://localhost:7687"  # Update with your Neo4j server URI
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "neoNeo@1"

    # Connect to the Neo4j database
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        # Create a session
        with driver.session() as session:
            # Iterate over rows in the DataFrame and create nodes and relationships
            for _, row in df.iterrows():
                head, tail, relation = row['head'], row['tail'], row['relation']

                # Create nodes
                session.run("MERGE (head:Node {name: $head})", head=head)
                session.run("MERGE (tail:Node {name: $tail})", tail=tail)

                # Create relationship with a label
                session.run(
                    """
                    MATCH (head:Node {name: $head})
                    MATCH (tail:Node {name: $tail})
                    MERGE (head)-[r:DEPENDS_ON]->(tail)
                    ON CREATE SET r.label = $relation
                    """,
                    head=head,
                    tail=tail,
                    relation=relation
                )


def write_imports2_neo4j(imports,file_path):
    dfs = []
    folder_path = os.path.dirname(os.path.abspath(file_path))
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            head = file
            for tail, functions in imports.items():
                if functions is not None:
                    for relation in functions:
                        dfs.append(pd.DataFrame({'head': [head], 'relation': [relation], 'tail': [tail]}))
    df = pd.concat(dfs, ignore_index=True)
    write2_neo4j(df)


def analyze_file(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
    # logger.debug(f"Source code {source_code}")
    tree = ast.parse(source_code)
    logger.debug(f"****** complete tree ***")
    logger.debug(f"{ast.dump(tree, indent=4)}")
    logger.debug(f"************ {file_path} ")
    dfs, imports = process_components(tree)
    if(len(dfs) > 0):
        df = pd.concat(dfs, ignore_index=True)
        write2_neo4j(df)
        logger.info(f"***********AAAAA***** Finished file {file_name} DF with {len(df)}")
    if (len(imports) > 0):
        # write_imports2_neo4j(imports,file_path)
        logger.info(f"***********AAAAA***** Finished file {file_name} imports with {len(imports)}")



if __name__ == "__main__":
    # actions / design_api.py
    # roles/engineer.py
    file_name = "/Users/kp/Desktop/work/MetaGPT/metagpt/actions/design_api.py"
    project_folder_path = "/Users/kp/Desktop/work/MetaGPT/metagpt/"
    analyze_file(file_name)
    file_count = 0
    for root, dirs, files in os.walk(project_folder_path):
        for file in files:
            if file.endswith(".py"):
                file_count = file_count +1
                file_name = os.path.join(root, file)
                logger.info(f"***AAAAAAAAAAA***** Starting processing {file_count}-{file_name}")
                analyze_file(file_name)
