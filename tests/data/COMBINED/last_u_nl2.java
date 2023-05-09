public class test {
protected void executeAfterRollbackActions() {
		if (afterRollbackActions != null) {
			if (trace) {
				logger.trace("Executing rollback actions");
			}
			executeActions(afterRollbackActions,trace);
			afterRollbackActions = null;
		}
	}
}