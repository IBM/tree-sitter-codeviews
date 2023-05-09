public class Test {

    public final ValueEval evaluate(
      ValueEval[] args,
      int srcRowIndex,
      int srcColumnIndex
    ) {
      switch (args.length) {
        case 3:
          return evaluate(srcRowIndex, srcColumnIndex, args[0], args[1], args[2]);
        case 4:
          return evaluate(
            srcRowIndex,
            srcColumnIndex,
            args[0],
            args[1],
            args[2],
            args[3]
          );
      }
      return ErrorEval.VALUE_INVALID;
    }
  }