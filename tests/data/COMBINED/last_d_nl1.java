public class test {
public int executeRemaining() throws SQLException {
        if (currentBatchSize > 0) {
            totalRecordsProcessed += currentBatchSize;
            preparedStatement.executeBatch();
            currentBatchSize = 0;
        }
        // Avoid reuse, signal that this was cleanly closed.
        preparedStatement = null;
        LOG.info(String.format("Processed %d %s records", totalRecordsProcessed, recordType));
        return totalRecordsProcessed;
    }
}