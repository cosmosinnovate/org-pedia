import os
from elasticsearch import Elasticsearch
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class ElasticsearchService:
    @staticmethod
    def create_index(es: Elasticsearch, index_name: str):
        try:
            es.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "content": {"type": "text"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 768  # Match nomic-embed-text dimensions
                            },
                            "timestamp": {"type": "date"}
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")

    @staticmethod
    def delete_index(es: Elasticsearch, index_name: str):
        """Delete an Elasticsearch index if it exists."""
        try:
            if es.indices.exists(index=index_name):
                logger.info(f"Deleting existing index: {index_name}")
                es.indices.delete(index=index_name)
                logger.info(f"Successfully deleted index: {index_name}")
            else:
                logger.info(f"Index {index_name} does not exist, no need to delete")
        except Exception as e:
            logger.error(f"Error deleting index: {str(e)}")
            raise

    @staticmethod
    def clean_content(content: str) -> str:
        """Clean content by normalizing whitespace and removing excessive newlines."""
        if not content:
            return ""
        # Replace multiple newlines with a single newline
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        # Replace multiple spaces with a single space
        content = ' '.join(content.split())
        return content

    @staticmethod
    def index_document(es: Elasticsearch, content, embedding):
        try:
            index_name = os.getenv("ELASTICSEARCH_INDEX", "documents")
            logger.info(f"Using index: {index_name}")
            
            # Validate inputs
            if not content or not isinstance(content, str):
                raise ValueError(f"Invalid content type: {type(content)}")
            if not embedding or not isinstance(embedding, list):
                raise ValueError(f"Invalid embedding type: {type(embedding)}")
            if len(embedding) != 768:  # Match nomic-embed-text dimensions
                raise ValueError(f"Invalid embedding dimensions: {len(embedding)}")
            
            # Clean content
            cleaned_content = ElasticsearchService.clean_content(content)
            if not cleaned_content:
                raise ValueError("Content is empty after cleaning")
            
            # Check if index exists with wrong mapping
            try:
                if es.indices.exists(index=index_name):
                    mapping = es.indices.get_mapping(index=index_name)
                    current_dims = mapping[index_name]['mappings']['properties']['embedding'].get('dims')
                    if current_dims != 768:
                        logger.info(f"Index exists with wrong dimensions ({current_dims}), recreating...")
                        ElasticsearchService.delete_index(es, index_name)
                        ElasticsearchService.create_index(es, index_name)
            except Exception as e:
                logger.error(f"Error checking index mapping: {str(e)}")
                # If there's any error with the existing index, recreate it
                ElasticsearchService.delete_index(es, index_name)
                ElasticsearchService.create_index(es, index_name)
            
            # Create index if it doesn't exist
            if not es.indices.exists(index=index_name):
                logger.info(f"Index {index_name} does not exist, creating it...")
                ElasticsearchService.create_index(es, index_name)
                logger.info("Index created successfully")
                
                # Verify index was created
                if not es.indices.exists(index=index_name):
                    raise Exception("Failed to create index")
                
                # Get and log the mapping
                mapping = es.indices.get_mapping(index=index_name)
                logger.info(f"Created index mapping: {mapping}")
            
            doc_id = hashlib.md5(cleaned_content.encode()).hexdigest()
            
            logger.info(f"Indexing document with ID: {doc_id}")
            logger.info(f"Content length: {len(cleaned_content)} characters")
            logger.info(f"Embedding dimensions: {len(embedding)}")
            
            # Create document body
            doc_body = {
                "content": cleaned_content,
                "embedding": embedding,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat()
            }
            
            logger.info(f"Document body keys: {doc_body.keys()}")
            
            # Index the document
            es.index(
                index=index_name,
                id=doc_id,
                body=doc_body,
                refresh=True
            )
            logger.info(f"Successfully indexed document {doc_id} to {index_name}")

            # Verify document was indexed
            if es.exists(index=index_name, id=doc_id):
                logger.info("Document verified in index")
                doc = es.get(index=index_name, id=doc_id)
                logger.info(f"Retrieved document fields: {list(doc['_source'].keys())}")
                logger.info(f"Retrieved embedding dimensions: {len(doc['_source']['embedding'])}")
            else:
                raise Exception("Document not found in index after indexing!")

        except Exception as e:
            logger.error(f"Indexing failed for content: {content[:100]}...")
            logger.error(f"Full error: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    @staticmethod
    def search_documents(es: Elasticsearch, query_embedding, size=3, min_score=0.3):  # Lower min_score for better recall
        try:
            index_name = os.getenv("ELASTICSEARCH_INDEX", "org_pedia")
            logger.info(f"Searching in index: {index_name}")
            
            if not es.indices.exists(index=index_name):
                logger.error(f"Index {index_name} does not exist")
                return []

            try:
                stats = es.indices.stats(index=index_name)
                doc_count = stats['indices'][index_name]['total']['docs']['count']
                
                logger.info(f"Index contains {doc_count} org_pedia")
            except Exception as e:
                logger.error(f"Failed to get index stats: {str(e)}")

            response = es.search(
                index=index_name,
                body={
                    "size": size,
                    "query": {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_embedding}
                            }
                        }
                    },
                    "_source": ["content", "timestamp"],  # Also retrieve timestamp for debugging
                    "sort": [{"_score": "desc"}]
                }
            )
            
            hits = response["hits"]["hits"]
            total_hits = response["hits"]["total"]["value"]
            logger.info(f"Total hits before filtering: {total_hits}")
            
            if hits:
                logger.info(f"Top hit score: {hits[0]['_score']}")
                # Log more details about top hits
                for i, hit in enumerate(hits[:3]):  # Log top 3 hits
                    score = hit["_score"] - 1.0
                    preview = hit["_source"]["content"][:100] + "..."
                    logger.info(f"Hit {i+1}:")
                    logger.info(f"  Score: {score:.3f}")
                    logger.info(f"  Preview: {preview}")
                    if "timestamp" in hit["_source"]:
                        logger.info(f"  Timestamp: {hit['_source']['timestamp']}")
            
            relevant_docs = []
            for hit in hits:
                score = hit["_score"] - 1.0  # Adjust for the +1.0 in the script_score
                logger.info(f"Document score (raw): {hit['_score']}, adjusted: {score}")
                if score >= min_score:
                    logger.info(f"Including document with score: {score:.3f}")
                    content = hit["_source"]["content"]
                    # Clean content before returning
                    cleaned_content = ElasticsearchService.clean_content(content)
                    if cleaned_content:
                        relevant_docs.append(cleaned_content)
                else:
                    logger.info(f"Excluding document with score too low: {score:.3f}")
            
            logger.info(f"Found {len(relevant_docs)} relevant documents")
            # Log a preview of each document
            for i, doc in enumerate(relevant_docs):
                preview = doc[:100] + "..." if len(doc) > 100 else doc
                logger.info(f"Document {i+1} preview: {preview}")
                
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []