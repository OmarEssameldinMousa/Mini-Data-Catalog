import json
import urllib.request
import urllib.error
import os

SERVICES = [
    {"name": "Registry", "url": "http://localhost/api/registry/openapi.json"},
    {"name": "Validator", "url": "http://localhost/api/validator/openapi.json"},
    {"name": "Lineage", "url": "http://localhost/api/lineage/openapi.json"},
    {"name": "Ingestion", "url": "http://localhost/api/ingestion/openapi.json"}
]

def merge_openapis():
    merged = {
        "openapi": "3.1.0",
        "info": {
            "title": "Mini Data Catalog API",
            "description": "Unified API Documentation for all Microservices",
            "version": "1.0.0"
        },
        "servers": [{"url": "/"}],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {}
        },
        "tags": []
    }

    for service in SERVICES:
        print(f"Fetching {service['name']} OpenAPI from {service['url']}...")
        try:
            req = urllib.request.urlopen(service['url'])
            data = json.loads(req.read())
            
            # Merge paths
            if "paths" in data:
                for path, methods in data["paths"].items():
                    merged["paths"][path] = methods
            
            # Merge components
            if "components" in data:
                if "schemas" in data["components"]:
                    for schema_name, schema_def in data["components"]["schemas"].items():
                        # We could prefix with service name if conflicts happen,
                        # but typically FastAPIs unique class names suffice.
                        merged["components"]["schemas"][schema_name] = schema_def
                        
            # Merge tags
            if "tags" in data:
                existing_tag_names = [t["name"] for t in merged["tags"]]
                for tag in data["tags"]:
                    if tag["name"] not in existing_tag_names:
                        merged["tags"].append(tag)
                        existing_tag_names.append(tag["name"])

            print(f"✅ Successfully merged {service['name']}")

        except urllib.error.URLError as e:
            print(f"❌ Failed to fetch {service['name']}: {e}")
        except Exception as e:
            print(f"❌ Error processing {service['name']}: {e}")

    # Output file
    out_file = os.path.join(os.path.dirname(__file__), "..", "nginx", "merged_openapi.json")
    with open(out_file, "w") as f:
        json.dump(merged, f, indent=2)
    
    print(f"\nMerged OpenAPI schema saved to {out_file}")

if __name__ == "__main__":
    merge_openapis()
