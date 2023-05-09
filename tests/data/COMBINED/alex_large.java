import java.io.OutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.util.Arrays;
import java.io.BufferedWriter;
import java.io.Writer;
import java.io.OutputStreamWriter;
import java.util.InputMismatchException;
import java.io.IOException;
import java.io.InputStream;

/**
 * Built using CHelper plug-in
 * Actual solution is at the top
 */
public class Main {
    public static void main(String[] args) {
        InputStream inputStream = System.in;
        OutputStream outputStream = System.out;
        InputReader in = new InputReader(inputStream);
        OutputWriter out = new OutputWriter(outputStream);
        CGrandGarden solver = new CGrandGarden();
        solver.solve(1, in, out);
        out.close();
    }

    static class CGrandGarden {
        int ans = 0;

        public void solve(int testNumber, InputReader in, OutputWriter out) {

            int n = in.nextInt();

            int[] h = new int[n + 1];

            for (int i = 1; i <= n; i++) h[i] = in.nextInt();

            int[] a = new int[n + 1];

            Arrays.fill(a, 0);

            recurse(a, h, 1, n);

            out.println(ans);
        }

        private void recurse(int[] a, int[] h, int start, int n) {
            int s = start;

            // System.out.println(ans);
            if (start > n) {
                return;
            }

            boolean flag = false;
            for (int i = start; i <= n; i++) {
                if (h[i] == 0) {
                    flag = true;
                    recurse(a, h, s, i - 1);
                    s = i + 1;
                }
            }

            if (flag == true) {
                recurse(a, h, s, n);
                return;
            }
            for (int i = start; i <= n; i++) {
                a[i]++;
            }

            ans++;

            for (int i = start; i <= n; i++) {
                if (a[i] == h[i]) {
                    recurse(a, h, s, i - 1);
                    s = i + 1;
                    //   continue;
                }
            }

            recurse(a, h, s, n);
        }

    }

    static class OutputWriter {
        private final PrintWriter writer;

        public OutputWriter(OutputStream outputStream) {
            writer = new PrintWriter(new BufferedWriter(new OutputStreamWriter(outputStream)));
        }

        public OutputWriter(Writer writer) {
            this.writer = new PrintWriter(writer);
        }

        public void close() {
            writer.close();
        }

        public void println(int i) {
            writer.println(i);
        }

    }

    static class InputReader {
        private InputStream stream;
        private byte[] buf = new byte[1024];
        private int curChar;
        private int numChars;
        private InputReader.SpaceCharFilter filter;

        public InputReader(InputStream stream) {
            this.stream = stream;
        }

        public int read() {
            if (numChars == -1) {
                throw new InputMismatchException();
            }
            if (curChar >= numChars) {
                curChar = 0;
                try {
                    numChars = stream.read(buf);
                } catch (IOException e) {
                    throw new InputMismatchException();
                }
                if (numChars <= 0) {
                    return -1;
                }
            }
            return buf[curChar++];
        }

        public int nextInt() {
            int c = read();
            while (isSpaceChar(c)) {
                c = read();
            }
            int sgn = 1;
            if (c == '-') {
                sgn = -1;
                c = read();
            }
            int res = 0;
            do {
                if (c < '0' || c > '9') {
                    throw new InputMismatchException();
                }
                res *= 10;
                res += c - '0';
                c = read();
            } while (!isSpaceChar(c));
            return res * sgn;
        }

        public boolean isSpaceChar(int c) {
            if (filter != null) {
                return filter.isSpaceChar(c);
            }
            return isWhitespace(c);
        }

        public static boolean isWhitespace(int c) {
            return c == ' ' || c == '\n' || c == '\r' || c == '\t' || c == -1;
        }

        public interface SpaceCharFilter {
            public boolean isSpaceChar(int ch);

        }

    }
}