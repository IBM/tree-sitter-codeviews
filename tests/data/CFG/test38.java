public class Test {
    protected void handleBodyLinks(JsonNode jsonBody, Map<String, Map<URI, String>> links, Map<String, String> linkTemplates) {
            if (jsonBody.getNodeType() != JsonNodeType.OBJECT) {
                return;
            }
    
            JsonNode linksNode = jsonBody.get("_links");
            if (linksNode == null) {
                linksNode = jsonBody.get("links");
            }
            if (linksNode == null) {
                return;
            }
    
            linksNode.fields().forEachRemaining(x -> {
                String rel = x.getKey();
                Map<URI, String> linksForRel = getOrAdd(links, rel);
    
                switch (x.getValue().getNodeType()) {
                    case ARRAY:
                        x.getValue().forEach(subobj -> {
                            if (subobj.getNodeType() == JsonNodeType.OBJECT) {
                                parseLinkObject(rel, (ObjectNode) subobj, linksForRel, linkTemplates);
                            }
                        });
                        break;
                    case OBJECT:
                        parseLinkObject(rel, (ObjectNode) x.getValue(), linksForRel, linkTemplates);
                        break;
                }
            });
        }
    }