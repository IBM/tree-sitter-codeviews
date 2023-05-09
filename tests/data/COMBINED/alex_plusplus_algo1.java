public class Max {
	int mx;

	public static void array(int n) {
		int[] arr = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
		System.out.println(n);
	}
    protected void executeAfterRollbackActions() {
		if (afterRollbackActions != null) {
			if (logger.isDebugEnabled()) {
				logger.debug("Executing rollback actions");
			}
			executeActions(afterRollbackActions);
		}
		executeActions(afterRollbackActions);
		// int parameter = 4;
		executeActions(afterRollbackActions);
		afterRollbackActions = null;
		afterRollbackActions = "wow";
		executeActions(afterRollbackActions);
		afterRollbackActions = "somethingIAdded";
		executeActions(afterRollbackActions);array(parameter);
		array(parameter+1);
	}
}