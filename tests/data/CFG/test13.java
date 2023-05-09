class CFG_test3 {
    public static void main(String[] args) {
        boolean foundIt = false;

    search:
        for (i = 0; i < arrayOfInts.length; i++) {
            for (j = 0; j < arrayOfInts[i].length; j++) {
                if (arrayOfInts[i][j] == searchfor) {
                    foundIt = true;
                    break search;
                }
            }
        }

        if (foundIt) {
            System.out.println("Found " + searchfor + " at " + i + ", " + j);
        } else {
            System.out.println(searchfor + " not in the array");
        }
      Task:
      for (i = 0; i < arrayOfInts.length; i++) {
      for(int i=0; i<10; i++){
          if (i==8){
             continue Task;
          }
          System.out.println("......."+i );
       }
      }
    }
}


