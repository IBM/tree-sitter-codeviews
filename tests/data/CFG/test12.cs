public class Test {
    public short FindNewDrawingGroupId(){
        short dgId = 1;
        while (DrawingGroupExists(dgId))
            dgId++;
        return dgId;
        }
        }