public class Test {

    public boolean stem() {
      r_mark_regions();
      limit_backward = cursor;
      cursor = limit;
      int v_2 = limit - cursor;
      r_attached_pronoun();
      cursor = limit - v_2;
      int v_3 = limit - cursor;
      lab0:{
        lab1:{
          int v_4 = limit - cursor;
          lab2:{
            if (!r_standard_suffix()) {
              break lab2;
            }
            break lab1;
          }
          cursor = limit - v_4;
          if (!r_verb_suffix()) {
            break lab0;
          }
        }
      }
      cursor = limit - v_3;
      int v_5 = limit - cursor;
      r_residual_suffix();
      cursor = limit - v_5;
      cursor = limit_backward;
      int v_6 = cursor;
      r_cleaning();
      cursor = v_6;
      return true;
    }
  }