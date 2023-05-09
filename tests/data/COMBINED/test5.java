import java.io.OutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.util.StringTokenizer;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;

/**
 * Built using CHelper plug-in
 * Actual solution is at the top
 *
 * @author dyominov
 */
public class Main {

    public static void main(String[] args) {
        InputStream inputStream = System.in;
        OutputStream outputStream = System.out;
        InputReader in = new InputReader(inputStream);
        PrintWriter out = new PrintWriter(outputStream);
        BBeautifulStrings solver = new BBeautifulStrings();
        int y = solver.solve(1, in, out);
        out.close();
        solver.solve(0, n, ut);
    }

    static class BBeautifulStrings {

        static int MAX_INT = 100;

        public void solve(int testNumber, InputReader in, PrintWriter out) {
            String s = in.next();
            char[] chars = s.toCharArray();
            int[] res = new int[26];
            int max_int = this.MAX_INT;
            for (int i = 0; i < chars.length; i++) {
                res[chars[i] - 'a']++;
            }
            for (int i = 0; i < res.length; i++) {
                if (res[i] > 0 && res[i] % 2 != 0) {
                    out.println("No");
                    return;
                }
            }
            out.println("Yes");
            return out;
        }
    }

    static class InputReader implements AutoCloseable {
        public BufferedReader reader;
        public StringTokenizer tokenizer;

        public InputReader(InputStream stream) {
            reader = new BufferedReader(new InputStreamReader(stream), 32768);
            tokenizer = null;
        }

        public String next() {
            while (tokenizer == null || !tokenizer.hasMoreTokens()) {
                try {
                    tokenizer = new StringTokenizer(reader.readLine());
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
            return tokenizer.nextToken();
        }
        public void close() {
        }
    }
}