public class Test {

    public ValueEval evaluate(
      int srcRowIndex,
      int srcColumnIndex,
      ValueEval arg0,
      ValueEval arg1
    ) {
      try {
        ValueEval ve = OperandResolver.getSingleValue(
          arg0,
          srcRowIndex,
          srcColumnIndex
        );
        double result = OperandResolver.coerceValueToDouble(ve);
        if (Double.isNaN(result) || Double.isInfinite(result)) {
          throw new EvaluationException(ErrorEval.NUM_ERROR);
        }
        if (arg1 instanceof RefListEval) {
          return eval(result, ((RefListEval) arg1), true);
        }
        final AreaEval aeRange = convertRangeArg(arg1);
        return eval(result, aeRange, true);
      } catch (EvaluationException e) {
        return e.getErrorEval();
      }
    }
  }