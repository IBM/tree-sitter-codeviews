import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;

import java.util.StringTokenizer;


public class Main {

    private final static FastReader in = new FastReader();
    private static final PrintWriter out = new PrintWriter(System.out);


    public static int solve(String s) {
        if (s.contains("R")) {
            if (s.charAt(0) == 'R' && s.charAt(1) == 'R' && s.charAt(2) == 'R') {
                return 3;
            } else if (s.charAt(0) == 'R' && s.charAt(1) == 'R' ||
                    s.charAt(1) == 'R' && s.charAt(2) == 'R') {
                return 2;
            } else {
                return 1;
            }
        }
        return 0;

    }

    public static void main(String[] args) {

        out.println(solve(in.next()));

        out.flush();
    }

    private static final class FastReader {
        private static BufferedReader BF;
        private static StringTokenizer ST;

        public FastReader() {
            BF = new BufferedReader(new InputStreamReader(System.in));
            ST = null;
        }


        public final String next() {
            while (ST == null || !ST.hasMoreTokens()) {
                try {
                    ST = new StringTokenizer(BF.readLine());
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return ST.nextToken();

        }

        final int nextInt() {
            return Integer.parseInt(next());
        }

    }


}