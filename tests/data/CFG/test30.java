public class Test {

    public static String createSafeSheetName(
      final String nameProposal,
      char replaceChar
    ) {
      if (nameProposal == null) {
        return "null";
      }
      if (nameProposal.length() < 1) {
        return "empty";
      }
      final int length = Math.min(31, nameProposal.length());
      final String shortenname = nameProposal.substring(0, length);
      final StringBuilder result = new StringBuilder(shortenname);
      for (int i = 0; i < length; i++) {
        char ch = result.charAt(i);
        switch (ch) {
          case '\u0000':
          case '\u0003':
          case ':':
          case '/':
          case '\\':
          case '?':
          case '*':
          case ']':
          case '[':
            result.setCharAt(i, replaceChar);
            break;
          case '\'':
            if (i == 0 || i == length - 1) {
              result.setCharAt(i, replaceChar);
            }
            break;
          default:
        }
      }
      return result.toString();
    }
  }
  