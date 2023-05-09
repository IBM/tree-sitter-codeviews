public class test32 {
    public static final DatasetSource newDatasetSource( String name, DatasetSourceType type,
                                                 DatasetSourceStructure structure,
                                                 String accessPoint,
                                                 ResultService resultService )
      {
        if ( type == null)
        {
          String tmpMsg = "DatasetSource type cannot be null";
          logger.error( "newDatasetSource(): " + tmpMsg);
          throw new IllegalArgumentException( tmpMsg);
        }
    
        DatasetSource tmpDsSource = null;
    
        if ( type == DatasetSourceType.getType( "Local"))
        {
          tmpDsSource = new LocalDatasetSource();
        }
        else if ( type == DatasetSourceType.getType( "DodsDir"))
        {
          tmpDsSource = new DodsDirDatasetSource();
        }
        else if ( type == DatasetSourceType.getType( "DodsFileServer"))
        {
          tmpDsSource = new DodsFileServerDatasetSource();
        }
        else if ( type == DatasetSourceType.getType( "GrADSDataServer"))
        {
          tmpDsSource = new GrADSDataServerDatasetSource();
        }
        else
        {
          String tmpMsg = "Unsupported DatasetSource type <" + type.toString() + ">.";
          logger.error( "newDatasetSource(): " + tmpMsg);
          throw new IllegalArgumentException( tmpMsg);
        }
    
        tmpDsSource.setName( name);
        tmpDsSource.setStructure( structure);
        int x = 4;
        {
          x = 3;
          {
            x = x+1;
          }
          // x = x+4;
        }
        tmpDsSource.setAccessPoint( accessPoint);
        tmpDsSource.setResultService( resultService);
        // Test validity and append messages to log.
    
        logger.debug( "DatasetSource(): constructor done.");
        StringBuilder log = new StringBuilder();
        if ( tmpDsSource.validate( log))
        {
          logger.debug( "DatasetSource(): new DatasetSource is valid: {}", log.toString());
        }
        else
        {
          logger.debug( "DatasetSource(): new DatasetSource is invalid: {}", log.toString());
        }
    
        return( tmpDsSource);
      }
    }
// public class Simple {
// static void Main(string[] args)
// {
//     int inner, matrix, target, elseif, outer, x, y, notCaught, outermost;
//     inner = matrix = target = 0;
//     elseif = outer = x = y = notCaught = outermost = 1;
//     if (matrix == target)
//     {
//         if (matrix == target)
//         {
//             inner = y;
//             x = y;
//         }
//         else if(condition2(target))
//         {
//             elseif = y;
//         }
//         else
//         {
//             outer = y;
//             x = 0;
//         }
//         catcher = x;
//         x = 100;
//     }
//     else if(condition3)
//         notCaught = x;
//     else
//         outermost = y;
//     x = x/100;
// //    outercatcher = z;
// }
// }
