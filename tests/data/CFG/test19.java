public class Test {

    public String toString() {
      if (
        getChildren() == null || getChildren().size() == 0
      ) return "<boolean operation='and'/>";
      StringBuilder sb = new StringBuilder();
      sb.append("<boolean operation='and'>");
      for (QueryNode child : getChildren()) {
        sb.append("\n");
        sb.append(child.toString());
      }
      sb.append("\n</boolean>");
      return sb.toString();
    }
  }