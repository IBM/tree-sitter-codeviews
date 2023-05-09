public class Test {
    @Implementation(minSdk = LOLLIPOP_MR1)
     protected AccountManagerFuture<Bundle> removeAccount(
         Account account,
         Activity activity,
         AccountManagerCallback<Bundle> callback,
         Handler handler) {
       if (account == null) {
         throw new IllegalArgumentException("account is null");
       }
       return start(
           new BaseRoboAccountManagerFuture<Bundle>(callback, handler) {
             @Override
             public Bundle doWork()
                 throws OperationCanceledException, IOException, AuthenticatorException {
               Bundle result = new Bundle();
               if (removeAccountIntent == null) {
                 result.putBoolean(
                     AccountManager.KEY_BOOLEAN_RESULT, removeAccountExplicitly(account));
               } else {
                 result.putBoolean(AccountManager.KEY_BOOLEAN_RESULT, false);
                 result.putParcelable(AccountManager.KEY_INTENT, removeAccountIntent);
               }
               return result;
             }
           });
     }
   }