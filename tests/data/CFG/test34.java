public class Test {
    protected void delete() {
           String question = "Are you sure you want to delete the data from the server?";
           ConfirmDialog.show(getUI(), question, new ConfirmDialog.Listener() {
               @Override
               public void onClose(ConfirmDialog cd) {
                   if (cd.isConfirmed()) {
                       try {
                           endpoint.delete();
                           close();
                       } catch (IOException | IllegalArgumentException | IllegalAccessException | IllegalStateException ex) {
                           onError(ex);
                       } catch (RuntimeException ex) {
                           // Must explicitly send unhandled exceptions to error handler.
                           // Would otherwise get swallowed silently within callback handler.
                           getUI().getErrorHandler().error(new com.vaadin.server.ErrorEvent(ex));
                       }
                   }
               }
           });
       }
   }