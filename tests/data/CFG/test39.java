public class Test {
    @Override
      public OCommandRequestAbstract onAsyncReplicationError(final OAsyncReplicationError iCallback) {
        if (iCallback != null) {
          onAsyncReplicationError = new OAsyncReplicationError() {
            int retry = 0;
    
            @Override
            public ACTION onAsyncReplicationError(Throwable iException, final int iRetry) {
              switch (iCallback.onAsyncReplicationError(iException, ++retry)) {
              case RETRY:
                execute();
                break;
    
              case IGNORE:
    
              }
    
              return ACTION.IGNORE;
            }
          };
        } else
          onAsyncReplicationError = null;
        return this;
      }
    }