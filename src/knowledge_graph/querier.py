# class GraphQuerier:
#     def __init__(self, driver):
#         self.driver = driver

#     def find_rule(self, payload: dict) -> list:
#         """Finds all rules matching the payload, ordered by most specific first."""
#         with self.driver.session() as session:
#             return session.execute_read(self._match_rule_transaction, payload)

#     @staticmethod
#     def _match_rule_transaction(tx, payload):
#         """
#         This Cypher query is the heart of the production API.
#         It is manually written for maximum performance and reliability.
#         """
#         where_clauses = []
#         for key, value in payload.items():
#             if value:
#                 node_label = key.capitalize()
#                 clause = f"EXISTS((rule)-[:APPLIES_TO]->(:{node_label} {{name: '{value}'}}))"
#                 where_clauses.append(clause)
        
#         if not where_clauses:
#             return []

#         # The query finds all rules that match the payload, then counts their
#         # total number of conditions to determine specificity.
#         query = f"""
#         MATCH (rule:Rule)
#         WHERE {' AND '.join(where_clauses)}
#         WITH rule
#         MATCH (rule)-[r:APPLIES_TO]->()
#         RETURN rule.name AS ruleName, COUNT(r) as specificity
#         ORDER BY specificity DESC
#         """
#         print("--- Executing Deterministic Cypher Query for API ---")
#         print(query)
#         result = tx.run(query)
#         return [record["ruleName"] for record in result]
    
class GraphQuerier:
    def __init__(self, driver):
        self.driver = driver

    def get_aggregated_rules(self, payload: dict) -> list:
        """
        Finds all relevant rule fragments from the payload and returns their content.
        """
        with self.driver.session() as session:
            return session.execute_read(self._match_and_aggregate_transaction, payload)

    @staticmethod
    def _match_and_aggregate_transaction(tx, payload: dict):
        """
        This query dynamically finds nodes based on the payload and collects
        their ruleContent property.
        """
        # This is a more advanced Cypher query that dynamically builds the final query.
        # It iterates through the payload keys (state, form, etc.) and
        # finds the ruleContent for each.
        
        base_query = []
        params = {}
        i = 0
        for key, value in payload.items():
            if value:
                node_label = key.capitalize()
                # If the value is a list (like for multiple forms), we use the IN operator
                if isinstance(value, list):
                    query_part = f"MATCH (n:{node_label}) WHERE n.name IN $value{i} RETURN n.ruleContent AS content"
                    params[f"value{i}"] = value
                # Otherwise, we match a single value
                else:
                    query_part = f"MATCH (n:{node_label} {{name: $value{i}}}) RETURN n.ruleContent AS content"
                    params[f"value{i}"] = value
                base_query.append(query_part)
                i += 1
        
        # Combine all parts with UNION
        full_query = " UNION ALL ".join(base_query)
        
        print("--- Executing Dynamic Aggregation Cypher Query ---")
        print(f"Query: {full_query}")
        print(f"Params: {params}")

        if not full_query:
            return []

        result = tx.run(full_query, **params)
        
        # Collect all non-null content strings into a list
        return [record["content"] for record in result if record["content"]]
