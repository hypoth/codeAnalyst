import xml.etree.ElementTree as ET
from logs.logs import logger

def parse_dgml(file_path):



    string text = ReadString(DGMLFileName);

    if (text.StartsWith("") + 2):
    }
    DebugLog("DGML text ... " + text);
    XDocument doc = XDocument.Parse(text);
    var root = doc.Elements("DirectedGraph");
    var elements = root.Elements("Nodes").Elements("Node");
    foreach (var item in elements)
    {
    var name = item.Attribute("Id").Value;
    }



    # Parse the DGML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    node_id_label_dict = {}
    node_id_cat_dict = {}

    # Define the DGML namespace
    namespace = {'dgml': 'http://schemas.microsoft.com/vs/2009/dgml'}

    # Extract information from nodes
    nodes = root.findall('.//dgml:Node', namespaces=namespace)
    for node in nodes:
        # logger.info(f"Node ID: {node.get('Id')}, Category : {node.get('Category')} Label: {node.get('Label')}")
        node_id_label_dict[node.get('Id')] = node.get('Label')
        node_id_cat_dict[node.get('Id')] = node.get('Category')


    logger.info(f"{set(node_id_label_dict.values())}")
    logger.info(f"*********************************")
    logger.info(f"{set(node_id_cat_dict.values())}")
    # Extract information from links
    links = root.findall('.//dgml:Link', namespaces=namespace)
    for link in links:
        # logger.info(f"Link Source: {link.get('Source')}, Target: {link.get('Target')}")
        logger.info(f"{node_id_label_dict[link.get('Source')]} calls {node_id_label_dict[link.get('Target')]}")

if __name__ == "__main__":
    # Example usage
    dgml_file_path = '/Users/kp/Desktop/work/pythonProject/codeAnalyst/sampleDGML.xml'
    parse_dgml(dgml_file_path)
    print('done')
