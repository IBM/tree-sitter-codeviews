public class Test {

    public final QueryNode DisjQuery(CharSequence field) throws ParseException {
      QueryNode first, c;
      Vector<QueryNode> clauses = null;
      first = ConjQuery(field);
      label_2:while (true) {
        switch ((jj_ntk == -1) ? jj_ntk() : jj_ntk) {
          case OR:
            break;
          default:
            jj_la1[3] = jj_gen;
            break label_2;
        }
        jj_consume_token(OR);
        c = ConjQuery(field);
        if (clauses == null) {
          clauses = new Vector<QueryNode>();
          clauses.addElement(first);
        }
        clauses.addElement(c);
      }
      if (clauses != null) {
        {
          if (true) return new OrQueryNode(clauses);
        }
      } else {
        {
          if (true) return first;
        }
      }
      throw new Error("Missing return statement in function");
    }
  }
  
