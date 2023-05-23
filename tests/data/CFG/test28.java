public class Test {

    public boolean isCancelled() {
      lock.lock();
      try {
        return pm.isCancelled();
      } finally {
        lock.unlock();
      }
    }
  }