public class Test {
    public static Optional<Boolean> isTarget(EventModel eventModel, Identifiable identifiable) {
            if (eventModel.getListResourceContainer()
                    .providesResource(Collections.singletonList(SelectorResource.RESOURCE_ID))) {
                   return Optional.of(eventModel.getListResourceContainer()
                           .provideResource(SelectorResource.RESOURCE_ID)
                           .stream()
                           .map(ResourceModel::getResource)
                           .filter(resource -> resource instanceof Identification)
                           .map(object -> (Identification) object)
                           .anyMatch(identifiable::isOwner));
            } else {
                return Optional.empty();
            }
        }
    }