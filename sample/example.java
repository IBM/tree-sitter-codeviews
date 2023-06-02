import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
    //    static String INPUT = "5\n3 2 2 4 1\n1 2 2 2 1";
    static String INPUT = "";

    public static void main(String[] args) {
        InputStream is = INPUT.isEmpty() ? System.in : new ByteArrayInputStream(INPUT.getBytes());

        Scanner scanner = new Scanner(is);

        final int n = scanner.nextInt();
        List<Position> positionList = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            positionList.add(
                    new Position(
                            scanner.nextInt(),
                            scanner.nextInt(),
                            scanner.nextInt()
                    )
            );
        }

        System.out.println(solve(positionList) ? "Yes" : "No");
    }

    static class Position {
        int t;
        int x;
        int y;

        public Position(int t, int x, int y) {
            this.t = t;
            this.x = x;
            this.y = y;
        }
    }

    static boolean solve(List<Position> positionList) {
        Position currentPosition = new Position(0, 0, 0);
        for (int i = 0; i < positionList.size(); i++) {
            Position nextPosition = positionList.get(i);
            if (!possibleMove(currentPosition.t, nextPosition.t, currentPosition.x, nextPosition.x, currentPosition.y, nextPosition.y)) {
                return false;
            }
            currentPosition = nextPosition;
        }
        return true;
    }

    static boolean possibleMove(int t1, int t2, int x1, int x2, int y1, int y2) {
        int tDiff = t2 - t1;
        int absX = Math.abs(x1 - x2);
        int absY = Math.abs(y1 - y2);

        if (absX + absY <= tDiff) {
            if (tDiff % 2 == (absX + absY) % 2) {
                return true;
            }
        }
        return false;
    }

}