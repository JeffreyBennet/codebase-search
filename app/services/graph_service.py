import boto3

class GraphService:
    def __init__(self, neptune_endpoint, aws_access_key, aws_secret_key):
        self.neptune_client = boto3.client(
            'neptune-data',
            endpoint_url=neptune_endpoint,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

    def add_entities_and_relationships(self, entities, relationships):
        """Add extracted entities and relationships to AWS Neptune."""
        for entity in entities:
            query = f"g.addV('Entity').property('name', '{entity}')"
            self.neptune_client.execute_gremlin_query(query)

        for relationship in relationships:
            query = f"g.V().has('name', '{relationship[0]}').addE('relatedTo').to(g.V().has('name', '{relationship[1]}'))"
            self.neptune_client.execute_gremlin_query(query)

    def query_graph(self, query):
        """Query the knowledge graph for relevant entities."""
        gremlin_query = f"g.V().has('name', '{query}').out('relatedTo')"
        response = self.neptune_client.execute_gremlin_query(gremlin_query)
        return [res['name'] for res in response['result']['data']['@value']['objects']]
