public class Test {

    private static int prepareCodeForToken(final JBBPToken token, final JBBPCustomFieldTypeProcessor customTypeFieldProcessor) {
      int result = -1;
      switch (token.getType()) {
        case ATOM: {
          final JBBPFieldTypeParameterContainer descriptor = token.getFieldTypeParameters();
  
          result = descriptor.getByteOrder() == JBBPByteOrder.LITTLE_ENDIAN ? FLAG_LITTLE_ENDIAN : 0;
  
          final boolean hasExpressionAsExtraNumber = descriptor.hasExpressionAsExtraData();
  
          result |= token.getArraySizeAsString() == null ? 0 : (token.isVarArrayLength() ? FLAG_ARRAY | FLAG_WIDE | (EXT_FLAG_EXPRESSION_OR_WHOLESTREAM << 8) : FLAG_ARRAY);
          result |= hasExpressionAsExtraNumber ? FLAG_WIDE | (EXT_FLAG_EXTRA_AS_EXPRESSION << 8) : 0;
          result |= token.getFieldTypeParameters().isSpecialField() ? FLAG_WIDE | (EXT_FLAG_EXTRA_DIFF_TYPE << 8) : 0;
          result |= token.getFieldName() == null ? 0 : FLAG_NAMED;
  
          final String name = descriptor.getTypeName().toLowerCase(Locale.ENGLISH);
          switch (name) {
            case "skip":
            case "val":
              result |= CODE_SKIP;
              break;
            case "align":
              result |= CODE_ALIGN;
              break;
            case "bit":
              result |= CODE_BIT;
              break;
            case "var":
              result |= CODE_VAR;
              break;
            case "bool":
            case JBBPFieldString.TYPE_NAME:
              result |= CODE_BOOL;
              break;
            case "ubyte":
              result |= CODE_UBYTE;
              break;
            case "byte":
              result |= CODE_BYTE;
              break;
            case "ushort":
              result |= CODE_USHORT;
              break;
            case "short":
              result |= CODE_SHORT;
              break;
            case "int":
            case JBBPFieldFloat.TYPE_NAME:
              result |= CODE_INT;
              break;
            case "long":
            case JBBPFieldDouble.TYPE_NAME:
              result |= CODE_LONG;
              break;
            case "reset$$":
              result |= CODE_RESET_COUNTER;
              break;
            default:
              boolean unsupportedType = true;
              if (customTypeFieldProcessor != null) {
                for (final String s : customTypeFieldProcessor.getCustomFieldTypes()) {
                  if (name.equals(s)) {
                    result |= CODE_CUSTOMTYPE;
                    unsupportedType = false;
                    break;
                  }
                }
              }
              if (unsupportedType) {
                throw new JBBPCompilationException("Unsupported type [" + descriptor.getTypeName() + ']', token);
              }
              break;
          }
        }
        break;
        case COMMENT: {
          // doesn't contain code
        }
        break;
        case STRUCT_START: {
          result = token.getArraySizeAsString() == null ? 0 : (token.isVarArrayLength() ? FLAG_ARRAY | FLAG_WIDE | (EXT_FLAG_EXPRESSION_OR_WHOLESTREAM << 8) : FLAG_ARRAY);
          result |= token.getFieldName() == null ? 0 : FLAG_NAMED;
          result |= CODE_STRUCT_START;
        }
        break;
        case STRUCT_END: {
          result = CODE_STRUCT_END;
        }
        break;
        default:
          throw new Error("Unsupported type detected, contact developer! [" + token.getType() + ']');
      }
      return result;
    }
  }
  
  
    
  
  
    
  
  
    
  
  
    
  