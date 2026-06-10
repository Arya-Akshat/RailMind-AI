import chromadb
from config import settings
from models.incident import Incident

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        _collection = _client.get_or_create_collection(name="incident_memory")
    return _collection

def get_similar_incidents(classification: str, location: str, top_k=3) -> list[dict]:
    """
    Embed the query string f"{classification} at {location}" using ChromaDB's
    default embedding function.
    Return the top_k most similar past incidents as dicts.
    """
    query_text = f"{classification} at {location}"
    try:
        col = get_collection()
        if col.count() == 0:
            return []
        
        # limit n_results to not exceed count
        k = min(top_k, col.count())
        if k <= 0:
            return []

        results = col.query(
            query_texts=[query_text],
            n_results=k
        )
        
        output = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            ids = results["ids"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            documents = results["documents"][0] if results.get("documents") else []
            distances = results["distances"][0] if results.get("distances") else []
            
            for i in range(len(ids)):
                meta = metadatas[i] if i < len(metadatas) else {}
                doc = documents[i] if i < len(documents) else ""
                dist = distances[i] if i < len(distances) else 0.0
                output.append({
                    "incident_id": ids[i],
                    "classification": meta.get("classification", ""),
                    "location": meta.get("location", ""),
                    "resolution_summary": doc,
                    "distance": dist
                })
        return output
    except Exception as e:
        print(f"Error querying ChromaDB: {e}")
        return []

def store_resolved_incident(incident: Incident):
    """
    After resolution, upsert the incident into ChromaDB so future incidents
    can retrieve it as a reference. Document = resolution_summary.
    Metadata = {incident_id, classification, location, severity}.
    """
    if not incident.resolution_summary:
        return
    try:
        col = get_collection()
        col.upsert(
            documents=[incident.resolution_summary],
            metadatas=[{
                "incident_id": incident.incident_id,
                "classification": incident.classification,
                "location": incident.sensor_event.location,
                "severity": incident.severity.value
            }],
            ids=[incident.incident_id]
        )
    except Exception as e:
        print(f"Error writing to ChromaDB: {e}")

def clear_chroma():
    global _client, _collection
    try:
        if _client is None:
            _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        try:
            _client.delete_collection("incident_memory")
        except Exception:
            pass
        _collection = _client.get_or_create_collection(name="incident_memory")
    except Exception as e:
        print(f"Error resetting ChromaDB: {e}")
