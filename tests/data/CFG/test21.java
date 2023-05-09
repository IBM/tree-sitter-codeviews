public class Test {

    public void run() {
      long lastReopenStartNS = System.nanoTime();
      while (!finish) {
        while (!finish) {
          reopenLock.lock();
          try {
            boolean hasWaiting = waitingGen > searchingGen;
            final long nextReopenStartNS =
              lastReopenStartNS +
              (hasWaiting ? targetMinStaleNS : targetMaxStaleNS);
            final long sleepNS = nextReopenStartNS - System.nanoTime();
            if (sleepNS > 0) {
              reopenCond.awaitNanos(sleepNS);
            } else {
              break;
            }
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            return;
          } finally {
            reopenLock.unlock();
          }
        }
        if (finish) {
          break;
        }
        lastReopenStartNS = System.nanoTime();
        refreshStartGen = writer.getMaxCompletedSequenceNumber();
        try {
          manager.maybeRefreshBlocking();
        } catch (IOException ioe) {
          throw new RuntimeException(ioe);
        }
      }
    }
  }
  

