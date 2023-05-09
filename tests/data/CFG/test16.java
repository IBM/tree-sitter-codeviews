public class Test {

    public final QueryNode TopLevelQuery(CharSequence field)
      throws ParseException {
      QueryNode q;
      q = Query(field);
      jj_consume_token(0);
      {
        if (true) return q;
      }
      throw new Error("Missing return statement in function");
    }
  }