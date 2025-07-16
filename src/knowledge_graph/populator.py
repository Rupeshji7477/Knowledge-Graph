# class GraphPopulator:
#     def __init__(self, driver):
#         self.driver = driver

#     def populate(self, data: dict):
#         """Populates the Neo4j graph, handling multi-valued conditions."""
#         rule_name = data.get("ruleName")
#         conditions = data.get("conditions", {})

#         if not rule_name or not conditions:
#             print("Skipping invalid data (missing rule name or conditions)")
#             return

#         print(f"--- Populating graph with rule: {rule_name}")
#         with self.driver.session() as session:
#             session.execute_write(self._create_rule_and_conditions, rule_name, conditions)

#     @staticmethod
#     def _create_rule_and_conditions(tx, rule_name, conditions):
#         tx.run("MERGE (rule:Rule {name: $rule_name})", rule_name=rule_name)

#         for key, values in conditions.items():
#             if isinstance(values, list) and values:
#                 node_label = key.capitalize()
#                 for value in values:
#                     query = f"""
#                     MERGE (rule:Rule {{name: $rule_name}})
#                     MERGE (c:{node_label} {{name: $value}})
#                     MERGE (rule)-[:APPLIES_TO]->(c)
#                     """
#                     tx.run(query, rule_name=rule_name, value=value)

class GraphPopulator:
    def __init__(self, driver):
        self.driver = driver

    def populate(self, data: dict):
        """Populates the graph by setting ruleContent on entity nodes."""
        fragments = data.get("fragments", [])
        if not fragments:
            print("No fragments found in data to populate.")
            return

        with self.driver.session() as session:
            for fragment in fragments:
                session.execute_write(self._create_or_update_node, fragment)

    @staticmethod
    def _create_or_update_node(tx, fragment: dict):
        """
        Creates a node if it doesn't exist and sets its ruleContent property.
        """
        entity_type = fragment.get("entityType")
        entity_name = fragment.get("entityName")
        content = fragment.get("content")

        if not all([entity_type, entity_name, content]):
            return

        # Capitalize the node label dynamically (e.g., 'state' -> 'State')
        node_label = entity_type.capitalize()
        
        print(f"--- Populating node {node_label}({entity_name})")

        # Use MERGE to create the node if it doesn't exist,
        # then use SET to add or update its ruleContent.
        query = f"""
        MERGE (n:{node_label} {{name: $name}})
        SET n.ruleContent = $content
        """
        tx.run(query, name=entity_name, content=content)
