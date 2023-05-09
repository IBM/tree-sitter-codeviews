public class Test {

    public CharSequence toQueryString(EscapeQuerySyntax escaper) {
      StringBuilder path = new StringBuilder();
      path.append("/").append(getFirstPathElement());
      for (QueryText pathelement : getPathElements(1)) {
        CharSequence value = escaper.escape(
          pathelement.value,
          Locale.getDefault(),
          Type.STRING
        );
        path.append("/\"").append(value).append("\"");
      }
      return path.toString();
    }
  }